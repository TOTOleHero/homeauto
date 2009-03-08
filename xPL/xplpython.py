from socket import *
from SensorLookup import Sensor
import re,select,sys
import json
import urllib

message_buffer = 1500
messageDict = {}
jsonRequest = {}
xpl_port = 50002
computername = gethostname()
xpl_ip = gethostbyname(gethostname())
xpl_instance = "monitor." + computername
UDPSock = socket(AF_INET,SOCK_DGRAM)
addr = ("0.0.0.0",xpl_port)

def validInstance (computername):
    newComputerName = re.sub('(-|\.|!|;)', '',  computername)
    newComputerName = newComputerName[:16]
    return newComputerName

def sendxplmsg (msgType='xpl-stat', source='mikesha.monitor', target='*', appName='hbeat.app', interval=5, port=50002):
    hbSock = socket(AF_INET,SOCK_DGRAM)
    hbSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
    msg = msgType + "\n{\nhop=1\nsource=" + source + "\ntarget=" + target + "\n}\n" + appName + "\n{\ninterval=" + str(interval) + "\nport=" + str(port) + "\n}\n"
    hbSock.sendto(msg,("255.255.255.255",3865))

computername = validInstance(computername)

try :
    UDPSock.bind(addr)
except :
    xpl_port = 50000
    addr = (xpl_ip,xpl_port)
    
    try :
        UDPSock.bind(addr)
    except :
        xpl_port += 1
        
print "xPL Monitor bound to port: " + str(xpl_port)

sendxplmsg(port=xpl_port)

while UDPSock :
    readable, writeable, errored = select.select([UDPSock],[],[],60)

    if len(readable) == 1 :
        data,addr = UDPSock.recvfrom(message_buffer)
        messageArray = data.splitlines()
        try:
            for msgLine in messageArray:
                if msgLine == '{':
                    messageArray.remove(msgLine)
                elif msgLine == '}':
                    messageArray.remove(msgLine)
        except:
            print "No Curly Braces To Remove"

        if messageArray[0] == 'xpl-trig':
            for msgLine in messageArray:
                if msgLine.find('=') != -1:
                    kvArray = msgLine.partition('=')
                    messageDict[kvArray[0]] = kvArray[2]

            deviceId = re.match('([a-z|A-Z]+.*[0-9]+.*).([0-9]+[a-z]+)', messageDict['device'])
            sensorType = deviceId.group(1)
            sensorHexId = deviceId.group(2)

            sensor = Sensor()
            ds10a = sensor.getSingleSensor('id',1)


            if messageDict['command'] == 'alert':               
                jsonRequest = {'jsId': ds10a['name'], 'sensorStatus': 'alert'}
                print "Sensor (Type:" + sensorType + ", ID: " + sensorHexId + ") is reporting its status as: OPEN"
            if messageDict['command'] == 'normal':
                jsonRequest = {'jsId': ds10a['name'], 'sensorStatus': 'normal'}
                print "Sensor (Type:" + sensorType + ", ID: " + sensorHexId + ") is reporting its status as: CLOSED"
            
            # send http-post
            request = urllib.urlopen("http://localhost/cgi-bin/acceptJSON.cgi", urllib.urlencode(jsonRequest))
