import time
from twisted.web import server, resource
from twisted.internet import reactor
from globals import *
import socket

# wget -qO- http://127.0.0.1:50000?ciao

class WebPage(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        if not 'plantsensor' in str(request):
            return ''
        hostname = socket.gethostname()
        return "%s cc = %s\n" % (hostname, str(color_calibrate))

def StartWebServer():
    site = server.Site(WebPage())
    reactor.listenTCP(50000, site)
    reactor.startRunning(False)

def WebServerIterate():
    reactor.iterate()
