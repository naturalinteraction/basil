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
import time

# todo: number of uploads in queue
def Page():
    try:
        prop = globa.cameraproperties.AllPropertiesString()
    except:
        prop = 'No camera properties.'
    hostname = socket.gethostname()
    mem = psutil.virtual_memory()
    disk = os.statvfs('/')
    if len(globa.last_picture_filename) > 0:
        link = 'link to last picture = http://natural-interaction.s3-website-eu-west-1.amazonaws.com/' + globa.last_picture_filename + '<br>\n'
    else
        link = ''
    disk_percent = 100 - 100 * disk.f_bavail / disk.f_blocks
    return ('PlantSensor: ' + hostname + ' <br>\n' +
            'PlantSensor Firmware v0.' + GitRevCount() + ' <br>\n' +
            GitBranch() + ' <p>\n' +
            OpenCVVersion() + ' <p>\n' +
            'cpu = ' + str(psutil.cpu_percent()) + ' <br>\n' +
            'memory = ' + str(mem.percent) + ' <br>\n' +
            'disk = ' + str(disk_percent) + ' <br>\n' +
            'temperature = ' + str(PiTemperature()) + ' <p>\n' +
            'just started = ' + str(globa.just_started) + ' <br>\n' +
            'color calibration = ' + str(globa.color_calibrate) + ' <br>\n' +
            'col cal locations = ' + str(len(globa.locations)) + ' <br>\n' +
            'freeze ' + str(globa.cameraproperties.freeze_calibrate) + ' <br>\n' +
            'show = ' + str(globa.show) + ' <p>\n' +
            prop + ' <p>\n' +
            'campaign = ' + globa.campaign + ' <br>\n' +
             link +
            'last picture taken at = ' + time.ctime(int(globa.last_picture_taken_ticks)) + ' <br>\n' +
            'started at = ' + globa.time_process_started_string + ' <br>\n' +
            'now = ' + time.strftime("%Y/%m/%d %H:%M") + ' <br>\n' +
            'uptime_minutes = ' + str(int((time.time() - globa.time_process_started) / (60.0))) + ' <p>\n'
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
