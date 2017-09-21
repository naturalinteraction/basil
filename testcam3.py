from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180
camera.resolution = (2592, 1944)
camera.framerate = 15
camera.brightness = 70  # 0..100
camera.contrast = 70  # 0..100
camera.awb_mode = 'shade'
# The awb options are: off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, and horizon. The default is auto
camera.exposure_mode = 'night'
# The options are: off, auto, night, nightpreview, backlight, spotlight, sports, snow, beach, verylong, fixedfps, antishake, and fireworks. The default is auto

camera.start_preview()
for i in range(1):	#2
	sleep(2)
	camera.capture('/home/pi/Desktop/pic%s.jpg' % i)
camera.stop_preview()
