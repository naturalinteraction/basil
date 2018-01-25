from git import OpenCVVersion
from git import GitHash
from git import GitCommitMessage
from twisted.web import server, resource
from twisted.internet import reactor
import globa
import socket

# wget -qO- http://127.0.0.1:50000?plantsensor

def Page():
    hostname = socket.gethostname()
    return (hostname + ' <p>\n' +
            'colcal ' + str(globa.color_calibrate) + ' <p>\n' +
            'show ' + str(globa.show) + ' <p>\n' +
            'just started ' + str(globa.just_started) + ' <p>\n' +
            str(globa.just_started_but_done) + ' <p>\n' +
            str(globa.previous_analog_gain) + ' <p>\n' +
            str(globa.previous_digital_gain) + ' <p>\n' +
            str(globa.gain_distance) + ' <p>\n' +
            str(globa.last_picture_taken_ticks) + ' <p>\n' +
            GitCommitMessage() + ' <p>\n' +
            OpenCVVersion() + ' <p>\n' +
            globa.campaign + ' <p>\n' +
            str(len(globa.locations)) + ' <p>\n' +
            globa.time_process_started_string + ' <p>\n' +
            str(globa.time_process_started) + ' <p>\n'
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
