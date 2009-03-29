#!C:/Python26/python.exe

import cgi,json

apacheRoot = "C:/Documents And Settings/Michael/Desktop/homeauto/apache/htdocs"
# apacheRoot = "/home/mike/homeauto/apache/htdocs"

form = cgi.FieldStorage()
formFirst = form.getfirst('zone')
ffDict = eval(formFirst)

finalDict = {'zone':ffDict}
jsonReply = json.dumps(finalDict)

file_object = open(apacheRoot + "/sensorStatus.json","w")
file_object.write(jsonReply)
file_object.close()
