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
import glob

def NumberOfUploadsInQueue():
    return str(len(glob.glob("cache/*.jpg")))

def Page():
    try:
        prop = globa.cameraproperties.AllPropertiesString()
    except:
        prop = 'No camera properties.'
    hostname = socket.gethostname()
    mem = psutil.virtual_memory()
    disk = os.statvfs('/')
    disk_percent = 100 - 100 * disk.f_bavail / disk.f_blocks
    if len(globa.last_picture_filename) > 0:
        link = '<a href="http://natural-interaction.s3-website-eu-west-1.amazonaws.com/' + globa.last_picture_filename + '">last picture</a><br>\n'
    else:
        link = ''
    status = 'running'
    if globa.initial_calibrate:
        status = 'initial calibration'
    if globa.cameraproperties.auto_calibrate:
        status = 'auto calibration'
    if globa.color_calibrate:
        status = 'color calibration'
    return ('PlantSensor: ' + hostname + ' <br>\n' +
            'PlantSensor Firmware v0.' + GitRevCount() + ' <br>\n' +
            GitBranch() + ' <br>\n' +
            OpenCVVersion() + ' <p>\n' +
            'cpu ' + str(psutil.cpu_percent()) + '%<br>\n' +
            'memory ' + str(mem.percent) + '%<br>\n' +
            'disk ' + str(disk_percent) + '%<br>\n' +
            'temperature ' + str(PiTemperature()) + ' <p>\n' +
            'status ' + status + ' <br>\n' +
            'locations ' + str(len(globa.locations)) + ' <br>\n' +
            'show ' + str(globa.show) + ' <p>\n' +
            prop + ' <p>\n' +
            'campaign ' + globa.campaign + ' <br>\n' +
             link +
            'last picture taken at ' + time.ctime(int(globa.last_picture_taken_ticks)) + ' <br>\n' +
            'uploads in queue ' + NumberOfUploadsInQueue() + '<br>\n' +
            'started at ' + globa.time_process_started_string + ' <br>\n' +
            'now ' + time.strftime("%Y/%m/%d %H:%M") + ' <br>\n' +
            'uptime_minutes ' + str(int((time.time() - globa.time_process_started) / (60.0))) + ' <p>\n'
           )

class WebPage(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        if not 'plantsensor' in str(request):
            return ''
        return '<font face="Arial">' + Page() + '</font>'

def StartWebServer():
    site = server.Site(WebPage())
    reactor.listenTCP(50000, site)
    reactor.startRunning(False)

def WebServerIterate():
    reactor.iterate()
