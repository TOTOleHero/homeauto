from socket import *
from Sensors import Sensor
from Zones import Zone
import re,select,sys
import json
import urllib

class xplHandler:
    message_buffer = 1500
    jsonRequest = {}
    xpl_port = 50002
    computername = gethostname()
    xpl_ip = gethostbyname(gethostname())
    xpl_instance = "monitor." + computername
    UDPSock = socket(AF_INET,SOCK_DGRAM)
    addr = ("0.0.0.0",xpl_port)
    
    def __init__(self):
    
        try :
            self.UDPSock.bind(self.addr)
        except :
            self.xpl_port = 50000
            self.addr = (self.xpl_ip, self.xpl_port)
            
            try :
                self.UDPSock.bind(self.addr)
            except :
                self.xpl_port += 1
            
        print "xPL Monitor bound to port: " + str(self.xpl_port)

    def validInstance (self, computername):
        newComputerName = re.sub('(-|\.|!|;)', '',  computername)
        newComputerName = newComputerName[:16]
        return newComputerName
    
    def sendXplMessage (self, msgType='xpl-stat', source='mikesha.monitor', target='*', appName='hbeat.app', interval=5, port=50002):
        hbSock = socket(AF_INET,SOCK_DGRAM)
        hbSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        msg = msgType + "\n{\nhop=1\nsource=" + source + "\ntarget=" + target + "\n}\n" + appName + "\n{\ninterval=" + str(interval) + "\nport=" + str(port) + "\n}\n"
        hbSock.sendto(msg,("255.255.255.255",3865))
    
    def startListener (self, UDPSock = None):
        
        self.computername = self.validInstance(self.computername)

        while UDPSock :
            readable, writeable, errored = select.select([UDPSock],[],[],60)
    
            if len(readable) == 1 :
                data,addr = UDPSock.recvfrom(self.message_buffer)
                messageArray = data.splitlines()
               
                # logLineHeader = "\nFULL XPL MESSAGE FOLOWING:\n"
                # logLineFooter = "\nEND XPL MESSAGE\n\n"

                try:
                    for msgLine in messageArray:
                        if msgLine == '{':
                            messageArray.remove(msgLine)
                        elif msgLine == '}':
                            messageArray.remove(msgLine)
                except:
                    print "No Curly Braces To Remove"
            
                # xplmsglog = open("xplmsglog.log", "a")
                # xplmsglog.write(logLineHeader)
                # xplmsglog.write(str(messageArray))
                # xplmsglog.write(logLineFooter)
                # xplmsglog.close()

                xplMsg = xplMessage(messageArray)
                xplMsg.parseMessage()
                        
                zDen = Zone()
                zDen.getZoneByName('den')
                zDen.getLinkedSensors()
        
                if xplMsg.type == "xpl-trig":
                    if xplMsg.statusDict['command'] == 'alert':               
                        zDen.sensors[xplMsg.statusDict['sensorHexId']].setStatus(zDen.sensors[xplMsg.statusDict['sensorHexId']].id,'alert')
                        self.xplToJSON('den')
                        print "Sensor (Type:" + xplMsg.statusDict['sensorType'] + ", ID: " + xplMsg.statusDict['sensorHexId'] + ") is reporting status: ALERT"
                    if xplMsg.statusDict['command'] == 'normal':
                        zDen.sensors[xplMsg.statusDict['sensorHexId']].setStatus(zDen.sensors[xplMsg.statusDict['sensorHexId']].id,'normal')
                        self.xplToJSON('den')
                        print "Sensor (Type:" + xplMsg.statusDict['sensorType'] + ", ID: " + xplMsg.statusDict['sensorHexId'] + ") is reporting status: NORMAL"

    def xplToJSON (self, zoneName = None):
        
        if zoneName != None:
            i = 0

            zone = Zone()
            zone.getZoneByName(zoneName)
            zone.getLinkedSensors()
            zone.isReady()

            jsonRequest = {'zone':{}}

            if zone.statusReady == True:
                jsonRequest['zone']['isReady'] = "true"
            elif zone.statusReady == False:
                jsonRequest['zone']['isReady'] = "false"
            else:
                jsonRequest['zone']['isReady'] = "NOSTATUS"

            jsonRequest['zone']['id'] = zone.id
            jsonRequest['zone']['name'] = zone.name

            for sensor in zone.sensors:
                jsonRequest['zone']['sensor' + str(i)] = {}
                jsonRequest['zone']['sensor' + str(i)]['id'] = zone.sensors[sensor].id
                jsonRequest['zone']['sensor' + str(i)]['hexid'] = zone.sensors[sensor].hexid
                jsonRequest['zone']['sensor' + str(i)]['name'] = zone.sensors[sensor].name
                jsonRequest['zone']['sensor' + str(i)]['type'] = zone.sensors[sensor].type
                jsonRequest['zone']['sensor' + str(i)]['status'] = zone.sensors[sensor].status
                i = i + 1

            #http-post
            #print "PARAMS: " + str(jsonRequest)
            params = urllib.urlencode(jsonRequest)
            request = urllib.urlopen("http://localhost/cgi-bin/acceptJSON.cgi", params)
        else:
            print "You must pass the Zone object"


class xplMessage:
    fullMessage = None
    schema = None
    type = None
    statusDict = {}

    def __init__(self, messageArray = None):
        if messageArray != None:
            self.fullMessage = messageArray
            self.schema = self.fullMessage[4]

            if self.fullMessage[0] == 'xpl-trig':
                self.type = 'xpl-trig'
            elif self.fullMessage[0] == 'xpl-stat':
                self.type = 'xpl-stat'
            else:
                self.type = 'OTHER'
            
        else:
            print "You must pass the message array"
            return None

    def parseMessage(self):
        if self.type != None:
            if self.type == "xpl-trig":
                if self.schema == "x10.security":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            kvArray = msgLine.partition('=')
                            self.statusDict[kvArray[0]] = kvArray[2]

                    deviceId = re.match('([a-z|A-Z]+.*[0-9]+.*).([0-9]+[a-z]+)', self.statusDict['device'])
                    self.statusDict['sensorType'] = deviceId.group(1)
                    self.statusDict['sensorHexId'] = deviceId.group(2)
                    
                else:
                    print "Unkown xpl-trig schema"
                    return None
            elif self.type == "xpl-stat":
               print "xpl-stat Message, ignoring."
            
            else:
                print "Unknown Message Type"
                return None
        else:
            print "Your instance must have a message type"
            return None
