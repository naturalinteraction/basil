from CameraProperties import CameraProperties
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import os
import cv2
import math
from S3 import UploadFileToS3
from pyexif import ExifEditor
import glob
import shutil
import pickle
from git import OpenCVVersion
from git import GitHash
from git import GitCommitMessage
from audio import AudioLevelPi
import numpy as np

print(GitCommitMessage())
print(OpenCVVersion())

campaign = 'xxx'

# initialize the camera and grab a reference to the raw camera capture
try:
    camera = PiCamera()
except:
    print('No camera. Exiting.')
    quit()

camera.framerate = 5
camera.resolution = (2560, 1920)
rawCapture = PiRGBArray(camera, size=camera.resolution)

global image
show = True
color_calibrate = False
image = None

cp = CameraProperties(camera)
cp.Load()

def SaveLastPictureTicks(ticks):
    with open('last-picture-taken-ticks.pkl', 'wb') as f:
        pickle.dump(ticks, f, 0)
    print('Saved time of last picture.')
    print(ticks)

def LoadLastPictureTicks():
    with open('last-picture-taken-ticks.pkl', 'rb') as f:
        ticks = pickle.load(f)
    print('Loaded time of last picture.')
    print(ticks)
    return ticks
  
last_picture_taken_ticks = -1
try:
    last_picture_taken_ticks = LoadLastPictureTicks()
    print(last_picture_taken_ticks)
except:
    print('Could not load time of last picture.')
    print(last_picture_taken_ticks)

just_started = True
just_started_but_done = False

gain_distance = -1.0
previous_analog_gain = -1.0
previous_digital_gain = -1.0

def UpdateGainDistance():
    gdi = gain_distance
    pag = previous_analog_gain
    pdg = previous_digital_gain
    gdi = math.fabs(camera.digital_gain - pdg)
    gdi += math.fabs(camera.analog_gain - pag)
    pdg = pdg * .8 + .2 * camera.digital_gain
    pag = pag * .8 + .2 * camera.analog_gain
    print(('analog %s  digital %s distance %s' % (float(camera.analog_gain),
                                                 float(camera.digital_gain),
                                                 gdi)))
    return gdi, pag, pdg

def PrintHelp():
    print(('*' * 10))
    print('TAB - Print All Properties')
    print('Arrow Keys - Navigate Properties And Values')
    print('Enter - Set Current Property')
    print('F - Freeze')
    print('S - Save')
    print('D - Disable Display')
    print('H - Help')
    print('P - Take Picture Now')
    print('ESC - Exit')
    print('Z - Zoom To Focus')
    print(('*' * 10))

def TakePicture(img, cam):
    print('Before saving picture, let me attempt to upload three files in cache.')
    AttemptUpload()
    AttemptUpload()
    AttemptUpload()

    audio_level = AudioLevelPi()

    print('Saving picture.')
    res = cam.resolution
    note = os.environ['BASIL_NOTE']
    filename = 'cache/' + note + '-' + campaign + '_' + str(res[0]) + 'x' + str(res[1]) + '_' + time.strftime("%Y_%m_%d-%H_%M.jpg")
    print(filename)
    # cv2.imwrite(filename + '_quality95.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])  # up to 100, default 95
    cv2.imwrite(filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # up to 100, default 95
    # cv2.imwrite(filename + '.png', img)  # test: save PNG as well
    ticks = time.time()
    SaveLastPictureTicks(ticks)
    # add EXIF keywords
    exif = ExifEditor(filename)
    keywords =       [GitHash(),
                      time_process_started_string,
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
    print(ticks)
    return ticks
    
def AttemptUpload():
    print('Attempting upload.')
    images_in_cache = glob.glob("cache/*.jpg")
    if len(images_in_cache) < 1:
        print('No images in cache. Nothing to do.')
        return
    uploaded = UploadFileToS3(images_in_cache[0])
    if uploaded == True:
        print('Upload succeeded. Moving image out of cache.')
        try:
            shutil.move(images_in_cache[0], "uploaded/")
        except:
            print('could not move image: file already exists')
    else:
        print('There was a problem uploading. Nothing done.')

global locations
global targetbgr
locations = []
targetbgr = []

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
    global locations
    global targetbgr
    global image
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(locations) < 24:
            print ('X' + str(x) + ' Y' + str(y) + ' location ' + str(len(locations)))
            locations.append((x,y))
            if len(locations) == 24:
                with open('calibration-locations.pkl', 'w') as f:
                    pickle.dump(locations, f, 0)
                    print('color calibration locations saved')
    if event == cv2.EVENT_RBUTTONDOWN:
        locations = []
        print('restarting color calibration: pick the 24 locations')

print((os.environ['BASIL_NOTE']))
# allow the camera to warmup
print('Wait...')
time.sleep(2)

time_process_started = time.time()
time_process_started_string = time.strftime("started %Y/%m/%d %H:%M")

cv2.namedWindow('cap', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('cap', mouseCallbackCalib)

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
try:
    with open('calibration-locations.pkl', 'r') as f:
        locations = pickle.load(f)
        print('loaded calibration locations')
except:
    pass

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
        # grab the raw NumPy array representing the image
        image = frame.array  # maybe we can avoid this if not just started and not showing and not taking the picture
 
        if (just_started and just_started_but_done):
            PrintHelp()
            cp.PrintCurrentProperty()
            show = False
            print('Display disabled.')
            just_started = False
            just_started_but_done = False

        if just_started:
            gain_distance, previous_analog_gain, previous_digital_gain = UpdateGainDistance()
            if gain_distance < 0.05:
                cp.SetAllPropertiesOnCamera()
                just_started_but_done = True                
        else:
          ticks = time.time()

          if color_calibrate:
              if len(locations) == 24:
                  show = True
                  diff = []
                  BF = 1.0 # 0.95 # 1.049  # brightness factor, max 1.049
                  blurred = cv2.blur(image, (33, 33))
                  for n,(xx, yy) in enumerate(locations):
                      cv2.rectangle(image, (xx-19, yy-19),
                                            (xx+19, yy+19), (0,0,0), 3)
                      c = blurred[yy,xx].tolist()
                      t = targetbgr[n]
                      diff.append((Redness(c) - Redness(t), Greenness(c) - Greenness(t), Blueness(c) - Blueness(t), Luminance(c) - Luminance(t) * BF, Red(c) - Red(t) * BF, Green(c) - Green(t) * BF, Blue(c) - Blue(t) * BF))
                      print(str(n) + ' '+ str(int(diff[-1][4])) + ' '+ str(int(diff[-1][5])) + ' '+ str(int(diff[-1][6])))
                  diff = np.array(diff)
                  # print('diff', diff)
                  mean = np.mean(np.float32(diff), axis=0)
                  squared = diff ** 2
                  msq = np.mean(squared, axis=0)
                  mean_squared_rgb = (msq[4] + msq[5] + msq[6]) / 3.0
                  color_calibration_red = color_calibration_red - (mean[4] - mean[5]) /  133.0
                  color_calibration_blue = color_calibration_blue - (mean[6] - mean[5]) / 133.0
                  color_calibration_shutter = color_calibration_shutter - mean[5] * 9.0  # no need to use L because with Green() its error goes to zero
                  color_calibration_red = max(0, min(8, color_calibration_red))
                  color_calibration_blue = max(0, min(8, color_calibration_blue))
                  color_calibration_shutter = max(0, min(80000, color_calibration_shutter))
                  print("r%.3f g%.3f b%.3f L%.1f shutter %d Rgain%.3f Bgain%.3f R%.1f G%.1f B%.1f err%d" % (mean[0], mean[1], mean[2], mean[3], int(color_calibration_shutter), color_calibration_red, color_calibration_blue, mean[4], mean[5], mean[6], mean_squared_rgb))
                  cp.SetPropertyOnCamera('Shutter Speed', int(color_calibration_shutter), mute=True)
                  cp.SetFreakingGains(color_calibration_red, color_calibration_blue)

          if cp.calibrating == False and not color_calibrate:
              # force this to avoid frames fading to black
              print(cp.loaded_values['Shutter Speed'])
              cp.SetPropertyOnCamera('Shutter Speed', cp.loaded_values['Shutter Speed'], mute=True)

          if (ticks - last_picture_taken_ticks) > 61.0:
              localtime = time.localtime(ticks)  # gmtime for UTC
              if localtime.tm_min == 00 and localtime.tm_hour > 9 and localtime.tm_hour < 21:  # one per hour, from 10am to 8pm
                  # if localtime.tm_hour == 10:  # one per day, at 10am
                  last_picture_taken_ticks = TakePicture(image, camera)
                  print('Turning zoom off.')
                  camera.zoom = (0.0, 0.0, 1.0, 1.0)  # will not take effect immediately, but at least next one will be ok
                  print('Disabling display.')
                  show = False
                  print(last_picture_taken_ticks)
                  print(ticks)
        
        # show the frame
        if show:
            cv2.imshow('cap', image)
        key = cv2.waitKey(25) & 0xFF  # milliseconds

        if (key < 255 and key != ord('d')):
            # print(key)
            if show == False:
              print('Display enabled.')
              show = True
        
        if key == ord('d'):
            print('Display disabled.')
            show = False
        
        if key == ord('h'):
            PrintHelp()
        
        if key == ord('s'):
            cp.Save()

        if key == ord('c'):
            color_calibrate = not color_calibrate
            if color_calibrate:
                color_calibration_shutter = cp.loaded_values['Shutter Speed']
                color_calibration_red = cp.loaded_values['AWB Red Gain']
                color_calibration_blue = cp.loaded_values['AWB Blue Gain']
                print('starting values for shutter and gains set', color_calibration_shutter, color_calibration_red, color_calibration_blue)
        if key == ord('f'):
            cp.FreezeExposureAWB()

        if key == ord('p'):
            if just_started == False:
                last_picture_taken_ticks = TakePicture(image, camera)
                print(last_picture_taken_ticks)
                print(ticks)
            else:
                print('hold on, cowboy!')

        if key == 10:  # enter
            cp.SetPropertyOnCamera(cp.CurrentPropertyName(),
                                   cp.CurrentPropertyValue())
    
        if key == 9:  # tab
            cp.PrintAllProperties()
            print(GitCommitMessage())
            uptime_minutes = int((time.time() - time_process_started) / (60.0))
            print(time_process_started_string) 
            print((time.strftime("now     %Y/%m/%d %H:%M")))
            print(('uptime minutes %s' % uptime_minutes))
            print(('*' * 20))

            
        if key == ord('z'):    
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

