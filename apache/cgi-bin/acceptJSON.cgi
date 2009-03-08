#!C:/Python26/python.exe

import cgi,json

#print "Content-Type: text/x-json\n"
form = cgi.FieldStorage()     

jsId = form['jsId'].value
sensorStatus = form['sensorStatus'].value

jsonReply = {'sensor':{'jsId':jsId,'sensorStatus':sensorStatus}}
jsonReply = json.dumps(jsonReply)

file_object = open("C:/Apache2/htdocs/sensorStatus.json","w")
file_object.write(jsonReply)
file_object.close()

print "Content-Type: text/plain\n"
print "jsId Is: " + jsId + ", sensorStatus Is: " + sensorStatus

