import time
from twisted.web import server, resource
from twisted.internet import reactor

# wget -qO- http://127.0.0.1:50000?ciao

class WebPage(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        print(request)
        return "<html>string = %s</html>\n" % str(targetbgr[0])

def StartWebServer():
    site = server.Site(WebPage())
    reactor.listenTCP(50000, site)
    reactor.startRunning(False)

def WebServerIterate():
    reactor.iterate()
