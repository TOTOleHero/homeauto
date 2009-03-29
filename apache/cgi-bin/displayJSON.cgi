#!C:/Python26/python.exe

import os, urllib2

host = os.environ.get("HTTP_HOST", "NOHOST")
  
file_object = urllib2.urlopen("http://" + host + "/sensorStatus.json")
jsonReply = file_object.read()

print "Content-Type: text/plain\n"
print jsonReply
