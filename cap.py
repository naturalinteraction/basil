from CameraProperties import CameraProperties
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2
import math
    
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1280, 1024)
camera.framerate = 3
rawCapture = PiRGBArray(camera, size=camera.resolution)
 
show = True

cp = CameraProperties (camera)
cp.Load()

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
    print('ESC - Exit')
    print('*' * 10)

# allow the camera to warmup
print('Wait...')
time.sleep(2)
      
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	image = frame.array
 
	# show the frame
	if show:
            cv2.imshow("cap  |  av@naturalinteraction.org", image)
        
        if just_started:
            UpdateGainDistance()
            if gain_distance < 0.05:
                just_started = False
                cp.SetAllPropertiesOnCamera()
                PrintHelp()
                cp.PrintCurrentProperty()
                show = False
                    
        key = cv2.waitKey(1) & 0xFF
        
        if (key < 255 and key != ord('d')):
            # print (key)
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

        if key == 10:  # enter
            cp.SetPropertyOnCamera(cp.CurrentPropertyName(),
                                   cp.CurrentPropertyValue())
    
        if key == 9:  # tab
            cp.PrintAllProperties()
          
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
