from xpl import xplHandler

xpl = xplHandler()

xpl.sendXplMessage(port=xpl.xpl_port)
listener = xpl.startListener(xpl.UDPSock)
while listener:
    pass
else:
    print "Could Not Find Listener"
