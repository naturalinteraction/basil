# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1600, 1200)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(1600, 1200))
 
# allow the camera to warmup
time.sleep(4)


camera.brightness = 70  # 0..100
camera.contrast = 70  # 0..100
camera.awb_mode = 'off'
# The awb options are: off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, and horizon. The default is auto
camera.awb_gains = (0.5, 0.5)
camera.exposure_mode = 'night'
# The options are: off, auto, night, nightpreview, backlight, spotlight, sports, snow, beach, verylong, fixedfps, antishake, and fireworks. The default is auto


print (camera.iso)  # With iso settings other than 0 (auto), the exposure_mode property becomes non-functional.
print (camera.analog_gain)
print (camera.awb_mode)
print (camera.awb_gains)
print (camera.brightness)
print (camera.contrast)
print (camera.digital_gain)
print (camera.drc_strength)
print (camera.exposure_mode)
print (camera.exposure_compensation)
print (camera.exposure_speed)
print (camera.meter_mode)
print (camera.saturation)
print (camera.sharpness)
print (camera.shutter_speed)
print (camera.zoom)


'''
0
1395/256
auto
(Fraction(3, 4), Fraction(191, 256))
50
0
317/256
off
auto
0
62941
average
0
0
0
(0.0, 0.0, 1.0, 1.0)
'''
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
 
	# show the frame
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
