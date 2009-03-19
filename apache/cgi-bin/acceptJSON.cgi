#!C:/Python26/python.exe

import cgi,json

form = cgi.FieldStorage()
formFirst = form.getfirst('zone')

#*** UNSAFE STEP - NEVER TRUST USER INPUT! ***
ffDict = eval(formFirst)

finalDict = {'zone':ffDict}
jsonReply = json.dumps(finalDict)

file_object = open("C:/Apache2/htdocs/sensorStatus.json","w")
file_object.write(jsonReply)
file_object.close()

print "Content-Type: text/plain\n"
print "JSON Reply: " + jsonReply
