from socket import *
from Sensors import Sensor
import re,select,sys
import json
import urllib

class xplHandler:
    message_buffer = 1500
    messageDict = {}
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
                
                logLineHeader = "\nFULL XPL MESSAGE FOLOWING:\n"
                logLineFooter = "\nEND XPL MESSAGE\n\n"

                try:
                    for msgLine in messageArray:
                        if msgLine == '{':
                            messageArray.remove(msgLine)
                        elif msgLine == '}':
                            messageArray.remove(msgLine)
                except:
                    print "No Curly Braces To Remove"
            
                xplmsglog = open("xplmsglog.log", "a")
                xplmsglog.write(logLineHeader)
                xplmsglog.write(str(messageArray))
                xplmsglog.write(logLineFooter)
                xplmsglog.close()

                xplMsg = xplMessage()
                xplMsg.fullMessage = messageArray
                xplMsg.schema = messageArray[4]

                if messageArray[0] == 'xpl-trig':
                    xplMsg.type = 'xpl-trig'
                    for msgLine in messageArray:
                        if msgLine.find('=') != -1:
                            kvArray = msgLine.partition('=')
                            self.messageDict[kvArray[0]] = kvArray[2]

                    #-----   TODO: Replace xPL message dictionary with xplMessage class  -----#
                    # print self.messageDict

                    deviceId = re.match('([a-z|A-Z]+.*[0-9]+.*).([0-9]+[a-z]+)', self.messageDict['device'])
                    sensorType = deviceId.group(1)
                    sensorHexId = deviceId.group(2)
        
                    sensor = Sensor()
                    ds10a = sensor.getSingleSensor('id',1)
        
        
                    if self.messageDict['command'] == 'alert':               
                        self.xplToJSON(ds10a['name'], 'alert')
                        sensor.statusReady = False
                        print "Sensor (Type:" + sensorType + ", ID: " + sensorHexId + ") is reporting its status as: OPEN"
                    if self.messageDict['command'] == 'normal':
                        sensor.statusReady = True
                        self.xplToJSON(ds10a['name'], 'normal')
                        print "Sensor (Type:" + sensorType + ", ID: " + sensorHexId + ") is reporting its status as: CLOSED"
                    

    def xplToJSON (self, jsId = None, sensorStatus = None):
        
        if jsId != None and sensorStatus != None:
            jsonRequest = {'jsId': jsId, 'sensorStatus': sensorStatus}
        
            #http-post
            params = urllib.urlencode(jsonRequest)
            request = urllib.urlopen("http://localhost/cgi-bin/acceptJSON.cgi", params)
        else:
            print "You must pass the jsId and the sensorStatus variables"


class xplMessage:
    fullMessage = None
    schema = None
    type = None

    def __init__(self):
        pass
