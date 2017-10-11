from CameraProperties import CameraProperties
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import os
import cv2
import math
import subprocess
from UtilityS3 import UploadFileToS3
from pyexif import ExifEditor
import glob
import shutil
    
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# (2560, 1920) for camera v1.3
camera.framerate = 5
try:
    camera.resolution = (2592, 1952) # (2160, 1632) (2112, 1568) (2000, 1504) (1920, 1088) (1640, 1232)
except:
    camera.resolution = (2560, 1920)
    print('old camera version')
else:
    print('new camera version')
finally:
    print(camera.resolution)
    rawCapture = PiRGBArray(camera, size=camera.resolution)
     
show = True

cp = CameraProperties(camera)
cp.Load()

last_picture_taken_ticks = -1  # todo: read this from disk
just_started = True
previous_digital_gain = -1.0
previous_analog_gain = -1.0

def UpdateGainDistance():
    global gain_distance
    global previous_analog_gain
    global previous_digital_gain
    gain_distance = math.fabs(camera.digital_gain - previous_digital_gain)
    gain_distance += math.fabs(camera.analog_gain - previous_analog_gain)
    previous_digital_gain = previous_digital_gain * .8 + .2 * camera.digital_gain
    previous_analog_gain = previous_analog_gain * .8 + .2 * camera.analog_gain
    print('analog %s  digital %s distance %s' % (float(camera.analog_gain),
                                                 float(camera.digital_gain),
                                                 gain_distance))

def PrintHelp():
    print('*' * 10)
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
    print('*' * 10)

def TakePicture(img, cam):
    print('Before saving picture, let me attempt to upload three files in cache.')
    AttemptUpload()
    AttemptUpload()
    AttemptUpload()
    print('Saving picture.')
    res = cam.resolution
    note = os.environ['BASIL_NOTE']
    filename = 'cache/' + note + '_' + str(res[0]) + 'x' + str(res[1]) + '_' + time.strftime("%Y_%m_%d-%H_%M.jpg")
    print(filename)
    cv2.imwrite(filename, img)
    global last_picture_taken_ticks
    last_picture_taken_ticks = time.time()  # todo: write this to disk
    # add EXIF keywords
    exif = ExifEditor(filename)
    # exif.addKeyword('tre')
    exif.addKeywords([git_hash,
                      git_commit_message_pretty,
                      time_process_started_string,
                      'cam.shutter_speed = ' + str(cam.shutter_speed),
                      'cam.drc_strength = ' + str(cam.drc_strength),
                      'cam.brightness = ' + str(cam.brightness),
                      'cam.iso = ' + str(cam.iso),
                      'cam.exposure_compensation = ' + str(cam.exposure_compensation),
                      'cam.contrast = ' + str(cam.contrast),
                      'cam.meter_mode = ' + str(cam.meter_mode),
                      'cam.sharpness = ' + str(cam.sharpness),
                      'cam.saturation = ' + str(cam.saturation),
                      'cam.exposure_mode = ' + str(cam.exposure_mode),
                      'cam.awb_mode = ' + str(cam.awb_mode),
                      'cam.awb_gains[0] = ' + str(float(cam.awb_gains[0])),
                      'cam.awb_gains[1] = ' + str(float(cam.awb_gains[1])),
                      'cam.exposure_speed = ' + str(cam.exposure_speed),
                      'cam.analog_gain = ' + str(float(cam.analog_gain)),
                      'cam.digital_gain = ' + str(float(cam.digital_gain)),
                      'cam.zoom = ' + str(cam.zoom[0]) + ' ' + str(cam.zoom[1]) + ' ' + str(cam.zoom[2]) + ' ' + str(cam.zoom[3]) 
                     ])
    # print('getKeywords', exif.getKeywords())
    print('getTag Keywords', exif.getTag("Keywords"))
    AttemptUpload()  # after taking the picture, immediately attempt to upload it
    
    
def AttemptUpload():
    print('Attempting upload.')
    images_in_cache = glob.glob("cache/*.jpg")
    if len(images_in_cache) < 1:
        print('No images in cache. Nothing to do.')
        return
    uploaded = UploadFileToS3(images_in_cache[0])
    if uploaded == True:
        print('Upload succeeded. Moving image out of cache.')
        shutil.move(images_in_cache[0], "uploaded/") 
    else:
        print('There was a problem uploading. Nothing done.')


# allow the camera to warmup
print('Wait...')
time.sleep(1)

git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
print(git_hash)
git_commit_message = subprocess.check_output(["git", "log", "-1"]).strip()  # , "--pretty=%B"
print(git_commit_message)
git_commit_message_pretty = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()
print(git_commit_message_pretty)

time_process_started = time.time()
time_process_started_string = time.strftime("started %Y/%m/%d %H:%M")

cv2.namedWindow('cap', cv2.WINDOW_NORMAL)
      
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
	# grab the raw NumPy array representing the image
	image = frame.array  # todo: maybe we can avoid this if not just started and not showing and not taking the picture
 
	# show the frame
	if show:
            cv2.imshow('cap', image)

        if just_started:
            UpdateGainDistance()
            if gain_distance < 0.05:
                just_started = False
                cp.SetAllPropertiesOnCamera()
                # todo: do the rest after one second or so...
                PrintHelp()
                cp.PrintCurrentProperty()
                show = False
                print('Display disabled.')
        else:
          ticks = time.time()
          if (ticks - last_picture_taken_ticks) > 61.0:
              localtime = time.localtime(ticks) # gmtime for UTC
              if localtime.tm_min == 19:  # one per hour
                  # if localtime.tm_hour == 10:  # one per day
                  TakePicture(image, camera)
        
        key = cv2.waitKey(50) & 0xFF  # milliseconds
        
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
        
        if key == ord('f'):
            cp.FreezeExposureAWB()

        if key == ord('p'):
            TakePicture(image, camera)

        if key == 10:  # enter
            cp.SetPropertyOnCamera(cp.CurrentPropertyName(),
                                   cp.CurrentPropertyValue())
    
        if key == 9:  # tab
            cp.PrintAllProperties()
            # print(git_hash)
            print(git_commit_message)
            uptime_minutes = int((time.time() - time_process_started) / (60.0))
            print(time_process_started_string) 
            print(time.strftime("now     %Y/%m/%d %H:%M"))
            print('uptime minutes %s' % uptime_minutes)
            print('*' * 20)

            
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
		break
		
camera.close()
print('Camera closed.')
cv2.destroyAllWindows()
print('Windows destroyed.')

# UploadFileToS3('somefile.txt')
