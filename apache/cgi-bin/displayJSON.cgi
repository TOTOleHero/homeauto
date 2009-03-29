#!C:/Python26/python.exe

apacheRoot = "C:/Apache2/htdocs/"
file_object = open(apacheRoot + "sensorStatus.json","r")
jsonReply = file_object.read()
file_object.close()

print "Content-Type: text/plain\n"
print jsonReply
