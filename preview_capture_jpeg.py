from picamera import PiCamera
from time import sleep

camera = PiCamera()
#camera.rotation = 180
camera.resolution = (2592, 1944)
camera.framerate = 15

camera.start_preview()
for i in range(1):	#2
	sleep(2)
	camera.capture('/home/pi/Desktop/pic%s.jpg' % i)
camera.stop_preview()
