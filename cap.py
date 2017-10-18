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
import pickle
    
# initialize the camera and grab a reference to the raw camera capture
try:
    camera = PiCamera()
except:
    print('No camera. Exiting.')
    quit()

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
    print('analog %s  digital %s distance %s' % (float(camera.analog_gain),
                                                 float(camera.digital_gain),
                                                 gdi))
    return gdi, pag, pdg

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
    # cv2.imwrite(filename + '_quality95.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])  # up to 100, default 95
    cv2.imwrite(filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # up to 100, default 95
    # cv2.imwrite(filename + '.png', img)  # test: save PNG as well
    ticks = time.time()
    SaveLastPictureTicks(ticks)
    # add EXIF keywords
    exif = ExifEditor(filename)
    keywords =       [git_hash,
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
                      'zoom=' + str(cam.zoom[3])
                     ]
    print(keywords)
    exif.addKeywords(keywords)
    # print('getKeywords', exif.getKeywords())
    print('getTag Keywords', exif.getTag("Keywords"))
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
	image = frame.array  # maybe we can avoid this if not just started and not showing and not taking the picture
 
	# show the frame
	if show:
            cv2.imshow('cap', image)

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
          if (ticks - last_picture_taken_ticks) > 61.0:
              localtime = time.localtime(ticks)  # gmtime for UTC
              if localtime.tm_min == 19:  # one per hour
                  # if localtime.tm_hour == 10:  # one per day
                  last_picture_taken_ticks = TakePicture(image, camera)
                  print(last_picture_taken_ticks)
                  print(ticks)
        
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
