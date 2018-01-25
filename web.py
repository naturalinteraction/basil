from utility import OpenCVVersion
from utility import GitHash
from utility import GitCommitMessage
from utility import GitRevCount
from utility import GitBranch
from utility import PiTemperature
from twisted.web import server, resource
from twisted.internet import reactor
import globa
import socket
import psutil
import os

'''
AWB Blue Gain  2.0 <0.76953125>
AWB Mode  off <auto>
AWB Red Gain  1.3 <0.859375>
Brightness  60 <50>
Contrast  10 <0>
DRC Strength  off <off>
Exp Compensation  0 <0>
Exp Meter Mode  average <average>
Exposure Mode  off <auto>
ISO  100 <0>
Saturation  0 <0>
Sharpness  100 <0>
Shutter Speed  1500 <0>
Exp Speed (READONLY) <62960>
Analog Gain (READONLY) <8.0>
Digital Gain (READONLY) <1.421875>
Zoom <0.0, 0.0, 1.0, 1.0>
started 2018/01/25 23:53
now     2018/01/25 23:53
uptime minutes 0
P - Take Picture Now
last picture taken at...
link to last picture
'''

def Page():
    hostname = socket.gethostname()
    mem = psutil.virtual_memory()
    disk = os.statvfs('/')
    disk_percent = 100 - 100 * disk.f_bavail / disk.f_blocks
    return (hostname + ' <p>\n' +
            'color calibration = ' + str(globa.color_calibrate) + ' <p>\n' +
            'show = ' + str(globa.show) + ' <p>\n' +
            'just started = ' + str(globa.just_started) + ' <p>\n' +
            'just started but done = ' + str(globa.just_started_but_done) + ' <p>\n' +
            'prev analog gain = ' + str(globa.previous_analog_gain) + ' <p>\n' +
            'prev digital gain = ' + str(globa.previous_digital_gain) + ' <p>\n' +
            'gain dist = ' + str(globa.gain_distance) + ' <p>\n' +
            'last picture taken ticks = ' + str(globa.last_picture_taken_ticks) + ' <p>\n' +
            'campaign = ' + globa.campaign + ' <p>\n' +
            'v0.' + GitRevCount() + ' <p>\n' +
            GitBranch() + ' <p>\n' +
            OpenCVVersion() + ' <p>\n' +
            'locations = ' + str(len(globa.locations)) + ' <p>\n' +
            'started at = ' + globa.time_process_started_string + ' <p>\n' +
            'cpu = ' + str(psutil.cpu_percent()) + ' <p>\n' +
            'memory = ' + str(mem.percent) + ' <p>\n' +
            'disk = ' + str(disk_percent) + ' <p>\n' +
            'temperature = ' + str(PiTemperature()) + ' <p>\n' +
            'started at ticks = ' + str(globa.time_process_started) + ' <p>\n'
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
