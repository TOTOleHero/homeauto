#!C:/Python26/python.exe

import cgi,json

apacheRoot = "C:/Apache2/htdocs/"
form = cgi.FieldStorage()
formFirst = form.getfirst('zone')
ffDict = eval(formFirst)

finalDict = {'zone':ffDict}
jsonReply = json.dumps(finalDict)

file_object = open(apacheRoot + "sensorStatus.json","w")
file_object.write(jsonReply)
file_object.close()

print "Content-Type: text/plain\n"
print "JSON Reply: " + jsonReply
