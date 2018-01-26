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

'''
todo number of uploads in queue
todo link to last picture only if filename not empty
'''

def Page():
    try:
        prop = globa.cameraproperties.AllPropertiesString()
    except:
        prop = 'NO CAMERA PROPERTIES'
    hostname = socket.gethostname()
    mem = psutil.virtual_memory()
    disk = os.statvfs('/')
    disk_percent = 100 - 100 * disk.f_bavail / disk.f_blocks
    return (prop + ' <p>\n' +
            hostname + ' <p>\n' +
            'color calibration = ' + str(globa.color_calibrate) + ' <p>\n' +
            'show = ' + str(globa.show) + ' <p>\n' +
            'just started = ' + str(globa.just_started) + ' <p>\n' +
            'just started but done = ' + str(globa.just_started_but_done) + ' <p>\n' +
            'freeze (todo: will stay on until relaunched) ' + globa.cameraproperties.freeze_calibrate + ' <p>\n' +
            'prev analog gain = ' + str(globa.previous_analog_gain) + ' <p>\n' +
            'prev digital gain = ' + str(globa.previous_digital_gain) + ' <p>\n' +
            'gain dist = ' + str(globa.gain_distance) + ' <p>\n' +
            'campaign = ' + globa.campaign + ' <p>\n' +
            'v0.' + GitRevCount() + ' <p>\n' +
            GitBranch() + ' <p>\n' +
            OpenCVVersion() + ' <p>\n' +
            'locations = ' + str(len(globa.locations)) + ' <p>\n' +
            'last_picture_filename = ' + 'http://natural-interaction.s3-website-eu-west-1.amazonaws.com/' + globa.last_picture_filename + ' <p>\n' +
            'last picture taken at = ' + time.ctime(int(globa.last_picture_taken_ticks)) + ' <p>\n' +
            'started at = ' + globa.time_process_started_string + ' <p>\n' +
            'now = ' + time.strftime("%Y/%m/%d %H:%M") + ' <p>\n' +
            'uptime_minutes = ' + str(int((time.time() - globa.time_process_started) / (60.0))) + ' <p>\n' +
            'cpu = ' + str(psutil.cpu_percent()) + ' <p>\n' +
            'memory = ' + str(mem.percent) + ' <p>\n' +
            'disk = ' + str(disk_percent) + ' <p>\n' +
            'temperature = ' + str(PiTemperature()) + ' <p>\n' +
            '' + str('') + ' <p>\n'
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
