from utility import OpenCVVersion, GitHash, GitCommitMessage, GitRevCount, GitBranch, PiTemperature, NumberOfUploadsInQueue, MemoryPercent, CPUPercent, DiskPercent, SensorFunctioningOK, UpdateFirmware, RebootSensor, RestartSensor, Macduff
from twisted.web import server, resource
from twisted.internet import reactor
import pickle
import globa
import socket
import time
import cv2

def Page():
    try:
        prop = globa.cameraproperties.AllPropertiesString()
        prop = prop + '<p>\nProperties OK? ' + str(globa.cameraproperties.AllPropertiesOK()) + '<br>\n'
    except:
        prop = 'No camera properties.'
    hostname = socket.gethostname()
    if len(globa.last_picture_filename) > 0:
        link = '<a href="http://natural-interaction.s3-website-eu-west-1.amazonaws.com/' + globa.last_picture_filename + '">last picture</a> taken at ' + time.ctime(int(globa.last_picture_taken_ticks)) + '<br>\n'
    else:
        link = ''
    status = 'running...'
    if globa.initial_calibrate:
        status = 'initial calibration... (' + globa.calib_error + ')'
    if globa.cameraproperties.auto_calibrate:
        status = 'auto calibration... (' + globa.calib_error + ')'
    if globa.color_calibrate:
        status = 'color calibration... (' + globa.calib_error + ')'
    return ('sensor ' + hostname + '<br>\n' +
            'firmware v0.' + GitRevCount() + ' ' + GitBranch() + '<br>\n' +
            OpenCVVersion() + '<p>\n' +
            'cpu ' + str(CPUPercent()) + '%<br>\n' +
            'memory ' + str(MemoryPercent()) + '%<br>\n' +
            'disk ' + str(DiskPercent()) + '%<br>\n' +
            'temperature ' + str(PiTemperature()) + '<p>\n' +
            status + '<p>\n' +
            # 'locations ' + str(len(globa.locations) == 24) + '<p>\n' +
            prop + '<p>\n' +
            'Sensor OK? ' + str(SensorFunctioningOK()) + '<br>\n'
            'series ' + globa.series + '<br>\n' +
             link +
            '' + NumberOfUploadsInQueue() + ' uploads in queue<br>\n' +
            'started at ' + globa.time_process_started_string + '<br>\n' +
            'now ' + time.strftime("%Y/%m/%d %H:%M") + '<br>\n' +
            'uptime ' + str(int((time.time() - globa.time_process_started) / (60.0))) + ' minutes<p>\n'
           )

class WebPage(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        if not 'plantsensor' in str(request):
            return ''
        if 'macduff-result.jpg' in str(request):
            try:
                request.setHeader('content-type', "image/jpeg")
                f = open('colorcalibration/output.jpg', 'rb')
                return f.read()
            except:
                request.setHeader('content-type', "text/html")
                return 'Macduff result not available.'
        if 'plantsensorthumbnail.jpg' in str(request):
            thumbnail = cv2.resize(globa.image, (0, 0), fx=0.1, fy=0.1)
            print('Saving thumbnail as requested from web.')
            cv2.imwrite('uploaded/thumbnail.jpg', thumbnail, [int(cv2.IMWRITE_JPEG_QUALITY), 70])  # up to 100, default 95
            try:
                request.setHeader('content-type', "image/jpeg")
                f = open('uploaded/thumbnail.jpg', 'rb')
                return f.read()
            except:
                request.setHeader('content-type', "text/html")
                return 'Thumbnail not available.'
        thumb = '<p><a href="plantsensor?refresh-thumbnail">Thumbnail Refresh</a><br>\n'
        if 'admin-admin' in str(request):
            thumb = '<p><a href="plantsensor?admin-admin&refresh-thumbnail">Thumbnail Refresh</a><br>\n'
        if 'refresh-thumbnail' in str(request):
            thumb = thumb + '<p><img src="uploaded/plantsensorthumbnail.jpg">'
        if 'update-firmware' in str(request):
            firmware_result = UpdateFirmware()
            print(firmware_result)
            thumb = thumb + '<p><pre><code>' + firmware_result + '</pre></code>'
        if 'restart-sensor' in str(request):
            globa.should_restart = True
            return '<head><link rel="icon" href="http://naturalinteraction.org/favicon.ico"><meta http-equiv="refresh" content="0; URL=http://www.naturalinteraction.org/" /></head><body>Restarting...</body>'
        if 'reboot-sensor' in str(request):
            globa.should_reboot = True
            return '<head><link rel="icon" href="http://naturalinteraction.org/favicon.ico"><meta http-equiv="refresh" content="0; URL=http://www.naturalinteraction.org/" /></head><body>Rebooting...</body>'
        if 'quit-quit' in str(request):
            globa.should_quit = True
        if 'change-series' in str(request):
            parts = str(request).replace(' ', '=').split('=')
            print(parts)
            for i,p in enumerate(parts):
                if 'change-series' in p:
                        globa.series = parts[i + 1].replace('clientproto', '')
                        print('saving globa.series = %s' % globa.series)
                        with open('series.pkl', 'w') as f:
                            pickle.dump(globa.series, f, 0)
        macduff = ''
        if 'find-colorchecker' in str(request):
            print('finding colorchecker')
            macduff = Macduff()
            if macduff == '':
                macduff = '<img src="plantsensor/macduff-result.jpg">'
        macduff = '<p>' + macduff + '<br>\n'
        refresh = ''
        if 'start-color-calibration' in str(request):
            print('setting globa.start_color_calibration to True')
            globa.start_color_calibration = True
            refresh = '<meta http-equiv="refresh" content="3; URL=plantsensor" />'
            if 'admin-admin' in str(request):
                refresh = refresh + '?admin-admin'
        if 'admin-admin' in str(request):
            thumb = thumb + '<p><a href="plantsensor?admin-admin&update-firmware">Update Firmware</a><br>\n'
            thumb = thumb + '<a href="plantsensor?admin-admin&restart-sensor">Restart Sensor</a><br>\n'
            thumb = thumb + '<a href="plantsensor?admin-admin&quit-quit">Quit Sensor</a><br>\n'
            thumb = thumb + '<a href="plantsensor?admin-admin&change-series=new-series-name">Change Series</a><br>\n'
            thumb = thumb + '<a href="plantsensor?admin-admin&reboot-sensor">Reboot Sensor</a><br>\n'
            thumb = thumb + '<a href="plantsensor?admin-admin&find-colorchecker">Find Colorchecker</a><br>\n'
            thumb = thumb + '<a href="plantsensor?admin-admin&start-color-calibration">Toggle Color Calibration</a><br>\n'
        else:
            thumb = thumb + '<p>Update Firmware (disabled)<br>\n'
            thumb = thumb + 'Restart Sensor (disabled)<br>\n'
            thumb = thumb + 'Reboot Sensor (disabled)<br>\n'
            thumb = thumb + 'Find Colorchecker (disabled)<br>\n'
            thumb = thumb + 'Start Color Calibration (disabled)<br>\n'
        return '<head><link rel="icon" href="http://naturalinteraction.org/favicon.ico">' + refresh + '</head><body><font face="Arial">' + Page() + thumb + macduff + '</font></body>'

def StartWebServer():
    site = server.Site(WebPage())
    reactor.listenTCP(50000, site)
    reactor.startRunning(False)

def WebServerIterate():
    reactor.iterate()
