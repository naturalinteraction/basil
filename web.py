from twisted.web import server, resource
from twisted.internet import reactor
from globals import *
import socket

# wget -qO- http://127.0.0.1:50000?plantsensor

def Page():
    hostname = socket.gethostname()
    return (hostname + '\n' +
            str(color_calibrate) + '\n' +
            GitCommitMessage() + '\n' +
            OpenCVVersion() + '\n' +
            campaign + '\n' +
            time_process_started_string + '\n' +
            str(time_process_started) + '\n'
           )

class WebPage(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        if not 'plantsensor' in str(request):
            return ''
        return Page()

def StartWebServer():
    site = server.Site(WebPage())
    reactor.listenTCP(50000, site)
    reactor.startRunning(False)

def WebServerIterate():
    reactor.iterate()

print(Page())
