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
time.sleep(1)

camera.brightness = 50  
camera.contrast = 50  
camera.saturation = 90 
camera.sharpness = 30
camera.awb_mode = 'off'
camera.awb_gains = (0.9, 1.0)
camera.iso = 100
camera.exposure_mode = 'off'
camera.exposure_compensation = +3

print('--- ISO AWB')
print (camera.iso)  # valid values are 100, 200, 320, 400, 500, 640, 800 With iso settings other than 0 (auto), the exposure_mode property becomes non-functional.
print (camera.awb_mode)  # The awb options are: off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, and horizon. The default is auto
print (camera.awb_gains) # with awbmode off, (red, blue) tuple, between 0.0 and 8.0. Typical values for the gains are between 0.9 and 1.9

print('--- BRI CON SAT SHARP')
print (camera.brightness) # 0..100
print (camera.contrast) # 0..100
print (camera.saturation)  # integer between -100 and 100
print (camera.sharpness)  # integer between -100 and 100

# print('--- DRC')
# print (camera.drc_strength) # off, low, medium, high

print('--- EXPOSURE')
print (camera.exposure_mode) # The options are: off, auto, night, nightpreview, backlight, spotlight, sports, snow, beach, verylong, fixedfps, antishake, and fireworks. The default is auto
print (camera.exposure_compensation)  # -25 to +25, default 0
print (camera.meter_mode)  # for exposure: average, spot, matrix, backlit
print (camera.shutter_speed)  # microseconds, or 0 which indicates that the speed will be automatically determined by the auto-exposure algorithm

# print('--- ZOOM')
# print (camera.zoom)  # (x, y, w, h)

show = True

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
 
	# show the frame
	if show:
            cv2.imshow("Frame", image)
	# show = False
        key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` or ESC key was pressed, break from the loop
	if key == ord("q") or key == 27:
		break
