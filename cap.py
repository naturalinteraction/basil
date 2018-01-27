
import time
from CameraProperties import CameraProperties
from picamera import PiCamera
from picamera.array import PiRGBArray
import os
import cv2
import math
from S3 import UploadFileToS3
from pyexif import ExifEditor
import glob
import shutil
import pickle
from audio import AudioLevelPi
import numpy as np
import globa
from web import *

def SaveLastPictureTicks(ticks, filename):
    with open('last-picture-taken-ticks.pkl', 'wb') as f:
        pickle.dump((ticks,filename), f, 0)
    print('Saved time of last picture.')

def LoadLastPictureTicks():
    with open('last-picture-taken-ticks.pkl', 'rb') as f:
        (ticks,filename) = pickle.load(f)
    print('Loaded time of last picture (and last filename).')
    return (ticks,filename)

def UpdateGainDistance():
    gdi = globa.gain_distance
    pag = globa.previous_analog_gain
    pdg = globa.previous_digital_gain
    gdi = math.fabs(camera.digital_gain - pdg)
    gdi += math.fabs(camera.analog_gain - pag)
    pdg = pdg * .8 + .2 * camera.digital_gain
    pag = pag * .8 + .2 * camera.analog_gain
    print(('analog %s  digital %s distance %s' % (float(camera.analog_gain),
                                                 float(camera.digital_gain),
                                                 gdi)))
    globa.previous_analog_gain = pag
    globa.previous_digital_gain = pdg
    return gdi

def PrintHelp():
    print(('*' * 10))
    print('TAB - Print All Properties')
    print('Arrow Keys - Navigate Properties And Values')
    print('Enter - Set Current Property')
    print('F - Freeze')
    print('L - Reset Color Calibration Locations')
    print('C - Color Calibration')
    print('S - Save')
    print('D - Disable Display')
    print('H - Help')
    print('P - Take Picture Now')
    print('ESC - Exit')
    print('Z - Zoom To Focus')
    print(('*' * 10))

def TakePicture(img, cam):
    print('Before saving picture, let me attempt to upload quite a few files in cache.')
    for i in range(10):
        AttemptUpload()

    audio_level = AudioLevelPi()

    print('Saving picture.')
    res = cam.resolution
    note = os.environ['BASIL_NOTE']
    filename = 'cache/' + note + '-' + globa.campaign + '_' + time.strftime("%Y_%m_%d-%H_%M.jpg")
    print(filename)
    # cv2.imwrite(filename + '_quality95.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])  # up to 100, default 95
    cv2.imwrite(filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # up to 100, default 95
    # cv2.imwrite(filename + '.png', img)  # test: save PNG as well
    ticks = time.time()
    globa.last_picture_filename = filename
    SaveLastPictureTicks(ticks, filename)
    # add EXIF keywords
    exif = ExifEditor(filename)
    keywords =       [GitHash(),
                      'started=' + globa.time_process_started_string,
                      'shutter_speed=' + str(cam.shutter_speed),
                      'drc_strength=' + str(cam.drc_strength),
                      'brightness=' + str(cam.brightness),
                      'iso=' + str(cam.iso),
                      'exposure_compensation=' + str(cam.exposure_compensation),
                      'contrast=' + str(cam.contrast),
                      'meter_mode=' + str(cam.meter_mode),
                      'sharpness=' + str(cam.sharpness),
                      'saturation=' + str(cam.saturation),
                      'exposure_mode=' + str(cam.exposure_mode),
                      'awb_mode=' + str(cam.awb_mode),
                      'awb_gains[r]=' + str(float(cam.awb_gains[0])),
                      'awb_gains[b]=' + str(float(cam.awb_gains[1])),
                      'exposure_speed=' + str(cam.exposure_speed),
                      'analog_gain=' + str(float(cam.analog_gain)),
                      'digital_gain=' + str(float(cam.digital_gain)),
                      'zoom=' + str(cam.zoom[3]),
                      'audio=' + str(audio_level)
                     ]
    print(keywords)
    exif.addKeywords(keywords)
    # print('getKeywords', exif.getKeywords())
    print(('getTag Keywords', exif.getTag("Keywords")))
    AttemptUpload()  # after taking the picture, immediately attempt to upload it
    return ticks
    
def AttemptUpload():
    images_in_cache = glob.glob("cache/*.jpg")
    if len(images_in_cache) < 1:
        # print('No images in cache. Nothing to do.')
        return
    print('Attempting upload.')
    uploaded = UploadFileToS3(images_in_cache[0])
    if uploaded:
        print('Upload succeeded. Moving image out of cache.')
        try:
            shutil.move(images_in_cache[0], "uploaded/")
        except:
            print('could not move image: file already exists')
    else:
        print('There was a problem uploading. Nothing done.')

def Red(bgr):
    return float(bgr[2])

def Green(bgr):
    return float(bgr[1])

def Blue(bgr):
    return float(bgr[0])

def Redness(bgr):
    return float(bgr[2]) / float(bgr[0] + bgr[1] + bgr[2])

def Greenness(bgr):
    return float(bgr[1]) / float(bgr[0] + bgr[1] + bgr[2])

def Blueness(bgr):
    return float(bgr[0]) / float(bgr[0] + bgr[1] + bgr[2])

def Luminance(bgr):
    return bgr[0] * 0.1140 + bgr[1] * 0.5870 + bgr[2] * 0.2989

def mouseCallbackCalib(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(globa.locations) < 24:
            print ('X' + str(x) + ' Y' + str(y) + ' location ' + str(len(globa.locations)))
            globa.locations.append((x,y))
            if len(globa.locations) == 24:
                with open('calibration-locations.pkl', 'w') as f:
                    pickle.dump(globa.locations, f, 0)
                    print('color calibration locations saved')
    if event == cv2.EVENT_RBUTTONDOWN:
        globa.locations = []
        print('restarting color calibration: pick the 24 locations')

def DefineColorCheckerColorsAndWeights()
    weight = []
    for i in range(0, 24):
        weight.append(1.0)
    targetbgr = []
    targetbgr.append((68,82,115))  # 0 dark skin
    targetbgr.append((130,150,194))  # 1 light skin
    targetbgr.append((157,122,98))  # 2 blue sky
    targetbgr.append((67,108,87))  # 3 foliage
    targetbgr.append((177,128,133))  # 4 blue flower
    targetbgr.append((170,189,103))  # 5 bluish green
    targetbgr.append((44,126,214))  # 6 orange
    targetbgr.append((166,91,80))  # 7 purplish blue
    targetbgr.append((99,90,193))  # 8 moderate red
    targetbgr.append((108,60,94))  # 9 purple
    targetbgr.append((64,188,157))  # 10 yellow green
    targetbgr.append((46,163,224))  # 11 orange yellow
    targetbgr.append((150,61,56))  # 12 blue
    targetbgr.append((73,148,70))  # 13 green
    targetbgr.append((60,54,175))  # 14 red
    targetbgr.append((31,199,231))  # 15 yellow
    targetbgr.append((149,86,187))  # 16 magenta
    targetbgr.append((161,133,8))  # 17 cyan
    targetbgr.append((242,243,243))  # 18 white 9.5
    targetbgr.append((200,200,200))  # 19 neutral 8
    targetbgr.append((160,160,160))  # 20 neutral 6.5
    targetbgr.append((121,122,122))  # 21 neutral 5
    targetbgr.append((85,85,85))  # 22 neutral 3.5
    targetbgr.append((52,52,52))  # 23 black 2
    return targetbgr,weight

def SetInitialCameraProperties(camera):
    camera.iso = 0
    camera.exposure_mode = 'auto'
    camera.awb_mode = 'auto'
    camera.shutter_speed = 0
    camera.saturation = 0
    camera.brightness = 50
    camera.contrast = 0
    camera.framerate = 5
    camera.resolution = (2560, 1920)

def ColorCalibrationIterate():
      globa.show = True
      diff = []
      kernel = 49
      half = int(kernel / 2 + 3)
      BF = 1.2 # brightness factor, max 1.049
      blurred = cv2.blur(globa.image, (kernel, kernel))
      for n,(xx, yy) in enumerate(globa.locations):
          cv2.rectangle(globa.image, (xx - half, yy - half),
                                     (xx + half, yy + half), (0,0,0), 3)
          c = blurred[yy,xx].tolist()
          t = targetbgr[n]
          diff.append((
                       Redness(c) - Redness(t),
                       Greenness(c) - Greenness(t),
                       Blueness(c) - Blueness(t),
                       Luminance(c) - Luminance(t) * BF,
                       (Red(c) - Red(t) * BF) * weight[n],
                       (Green(c) - Green(t) * BF) * weight[n],
                       (Blue(c) - Blue(t) * BF) * weight[n]
                     ))
          # print(str(n) + ' '+ str(int(diff[-1][4] / weight[n])) + ' '+ str(int(diff[-1][5] / weight[n])) + ' '+ str(int(diff[-1][6] / weight[n])))
      diff = np.array(diff)
      # print('diff', diff)
      mean = np.mean(np.float32(diff), axis=0)
      squared = diff ** 2
      msq = np.mean(squared, axis=0)
      mean_squared_rgb = (msq[4] + msq[5] + msq[6]) / 3.0
      if (abs(mean[4]) + abs(mean[5]) + abs(mean[6])) < 1.0:
          print('finished! exiting color calibration. Saving!')
          print(len(diff))
          print('mean %.2f %.2f %.2f' % (mean[4], mean[5], mean[6]))
          globa.color_calibrate = False
          print(int(color_calibration_shutter), color_calibration_red, color_calibration_blue)
          cp.Save()
          cp.Load()
          print(cp.loaded_values['Shutter Speed'], cp.loaded_values['AWB Red Gain'], cp.loaded_values['AWB Blue Gain'])
      else:
          color_calibration_red = color_calibration_red - (mean[4] - 0.0 * mean[5]) /  133.0 / 3.0
          color_calibration_blue = color_calibration_blue - (mean[6] - 0.0 * mean[5]) / 133.0 / 3.0
          color_calibration_shutter = color_calibration_shutter - mean[5] * 9.0 / 6.0  # no need to use L because with Green() its error goes to zero
          color_calibration_red = max(0, min(8, color_calibration_red))
          color_calibration_blue = max(0, min(8, color_calibration_blue))
          color_calibration_shutter = max(0, min(80000, color_calibration_shutter))
          print("[colorcalib] shutter %d Rgain%.3f Bgain%.3f R%.1f G%.1f B%.1f err%d" % (int(color_calibration_shutter), color_calibration_red, color_calibration_blue, mean[4], mean[5], mean[6], mean_squared_rgb))
          cp.SetPropertyOnCamera('Shutter Speed', int(color_calibration_shutter), mute=True)
          cp.SetFreakingGains(color_calibration_red, color_calibration_blue)

targetbgr,weight = DefineColorCheckerColorsAndWeights()
# initialize the camera and grab a reference to the raw camera capture
try:
    camera = PiCamera()
except:
    print('No camera. Exiting.')
    quit()
SetInitialCameraProperties(camera)
rawCapture = PiRGBArray(camera, size=camera.resolution)

globa.cameraproperties = CameraProperties(camera)
cp = globa.cameraproperties
cp.Load()

try:
    (globa.last_picture_taken_ticks, globa.last_picture_filename) = LoadLastPictureTicks()
except:
    print('Could not load time of last picture.')

print(Page())

cv2.namedWindow('cap', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('cap', mouseCallbackCalib)

try:
    with open('calibration-locations.pkl', 'r') as f:
        globa.locations = pickle.load(f)
        print('loaded calibration locations')
except:
    pass

StartWebServer()

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
        WebServerIterate()
        globa.image = frame.array
 
        if (globa.just_started and globa.just_started_but_done):
            PrintHelp()
            cp.PrintCurrentProperty()
            globa.show = False
            print('Display disabled.')
            globa.just_started = False
            globa.just_started_but_done = False

        if globa.just_started:
            globa.gain_distance = UpdateGainDistance()
            if globa.gain_distance < 0.05:  # 0.02
                cp.SetAllPropertiesOnCamera()
                globa.just_started_but_done = True                
        else:
          ticks = time.time()

          if globa.color_calibrate:
              if not len(globa.locations) == 24:
                  print('pick the 24 locations first')
              else:
                  ColorCalibrationIterate()

          if not cp.freeze_calibrate and not globa.color_calibrate:
              # force this to avoid frames fading to black
              # print('forcing shutter ' + str(cp.loaded_values['Shutter Speed']))
              cp.SetPropertyOnCamera('Shutter Speed', cp.loaded_values['Shutter Speed'], mute=True)

          if cp.freeze_calibrate and not globa.color_calibrate:
              print('[freezecalib] ' + str(camera.exposure_speed)+ ' ' + str(float(camera.awb_gains[0])) + ' ' + str(float(camera.awb_gains[1])))
              # todo: must stop automatically

          if (ticks - globa.last_picture_taken_ticks) > 61.0:
              localtime = time.localtime(ticks)  # gmtime for UTC
              if localtime.tm_min == 00 and localtime.tm_hour > 9 and localtime.tm_hour < 21:  # one per hour, from 10am to 8pm
                  # if localtime.tm_hour == 10:  # one per day, at 10am
                  globa.last_picture_taken_ticks = TakePicture(globa.image, camera)
                  print('Turning zoom off.')
                  camera.zoom = (0.0, 0.0, 1.0, 1.0)  # will not take effect immediately, but at least next one will be ok
                  print('Disabling display.')
                  globa.show = False
        
        # show the frame
        if globa.show:
            cv2.imshow('cap', globa.image)
        key = cv2.waitKey(25) & 0xFF  # milliseconds

        if (key < 255 and key != ord('d')):
            if not globa.show:
              print('Display enabled.')
              globa.show = True
        
        if key == ord('d'):
            print('Display disabled.')
            globa.show = False
        
        if key == ord('h'):
            PrintHelp()

        if key == ord('s'):
            cp.Save()

        if key == ord('l'):
            print('color checker locations reset')
            globa.locations = []

        if key == ord('c'):
            globa.color_calibrate = not globa.color_calibrate
            if cp.freeze_calibrate or len(globa.locations) != 24 or globa.just_started:
                print('freeze_calibrate or no 24 locations or just started')
                globa.color_calibrate = False
            if globa.color_calibrate:
                camera.zoom = (0.0, 0.0, 1.0, 1.0)
                color_calibration_shutter = cp.loaded_values['Shutter Speed']
                color_calibration_red = cp.loaded_values['AWB Red Gain']
                color_calibration_blue = cp.loaded_values['AWB Blue Gain']
                print('starting values for shutter and gains set', color_calibration_shutter, color_calibration_red, color_calibration_blue)

        if key == ord('f'):
            if not globa.color_calibrate and not globa.just_started:
                cp.FreezeExposureAWB()
            else:
                print('hold on, cowboy!')

        if key == ord('p'):
            if not globa.just_started:
                globa.last_picture_taken_ticks = TakePicture(globa.image, camera)
            else:
                print('hold on, cowboy!')

        if key == 10:  # enter
            cp.SetPropertyOnCamera(cp.CurrentPropertyName(),
                                   cp.CurrentPropertyValue())

        if key == 9:  # tab
            cp.PrintAllProperties()
            print(GitCommitMessage())
            uptime_minutes = int((time.time() - globa.time_process_started) / (60.0))
            print('started at ' + globa.time_process_started_string) 
            print((time.strftime("now     %Y/%m/%d %H:%M")))
            print(('uptime minutes %s' % uptime_minutes))
            print(('*' * 20))

        if key == ord('z') and not globa.color_calibrate and not globa.just_started and not cp.freeze_calibrate:
            if camera.zoom[0] == 0.0:
                camera.zoom = (0.333, 0.333, 0.333, 0.333)
            else:
                camera.zoom = (0.0, 0.0, 1.0, 1.0)
                   
        if key == 82:  # up
            cp.DecProperty()
        
        if key == 84: # down
            cp.IncProperty()
            
        if key == 81: # left
            cp.DecValue()
            
        if key == 83:  # right
            cp.IncValue()
 
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
 
        # if the `q` or ESC key was pressed, break from the loop
        if key == ord('q') or key == 27:
                print('exiting')
                break
		
camera.close()
print('Camera closed.')
cv2.destroyAllWindows()
print('Windows destroyed.')

