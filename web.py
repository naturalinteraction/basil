from twisted.web import server, resource
from twisted.internet import reactor
from globals import *
import socket

# wget -qO- http://127.0.0.1:50000?plantsensor

def Page():
    hostname = socket.gethostname()
    return (hostname + ' <p>\n' +
            str(color_calibrate) + ' <p>\n' +
            str(show) + ' <p>\n' +
            str(just_started) + ' <p>\n' +
            str(just_started_but_done) + ' <p>\n' +
            str(previous_analog_gain) + ' <p>\n' +
            str(previous_digital_gain) + ' <p>\n' +
            str(gain_distance) + ' <p>\n' +
            str(last_picture_taken_ticks) + ' <p>\n' +
            GitCommitMessage() + ' <p>\n' +
            OpenCVVersion() + ' <p>\n' +
            campaign + ' <p>\n' +
            str(len(locations)) + ' <p>\n' +
            time_process_started_string + ' <p>\n' +
            str(time_process_started) + ' <p>\n'
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
