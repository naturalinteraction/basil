from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

def PrintFullCameraState():
    print("-----------------------------------------------------------")
    print("ISO", camera.iso)  # With iso settings other than 0 (auto), the exposure_mode property becomes non-functional.
    print("AWB mode", camera.awb_mode)  # The default is auto
    print("AWB gains", camera.awb_gains) # with awbmode off, (red, blue) tuple  Typical values for the gains are between 0.9 and 1.9
    print("brightness", camera.brightness)
    print("constrast", camera.contrast)
    print("saturation", camera.saturation)
    print("sharpness", camera.sharpness)
    print("exposure mode", camera.exposure_mode) # The default is auto
    print("exposure compensation", camera.exposure_compensation)
    print("meter mode", camera.meter_mode)  # for exposure
    print("shutter speed", camera.shutter_speed)  # microseconds, or 0 which indicates that the speed will be automatically determined by the auto-exposure algorithm
    print("DRC strength", camera.drc_strength) # off, low, medium, high
    # still not in the menu:
    print("zoom", camera.zoom)  # (x, y, w, h) not interesting at the moment
    print('exposure speed', camera.exposure_speed) # READONLY
    print("analog gain", camera.analog_gain) # READONLY
    print("digital gain", camera.digital_gain) # READONLY

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1280, 1024)
camera.framerate = 3
rawCapture = PiRGBArray(camera, size=camera.resolution)
 
# allow the camera to warmup
time.sleep(1)

#camera.brightness = 99  
#camera.contrast = 50  
#camera.saturation = 90 
#camera.sharpness = 30
camera.awb_mode = 'off'
camera.awb_gains = (1.0, 1.0)
camera.iso = 800
camera.exposure_mode = 'auto'
camera.exposure_compensation = 25
camera.shutter_speed = 54510L
'''
camera = PiCamera(resolution=(1280, 720), framerate=30)
# Set ISO to the desired value
camera.iso = 100
# Wait for the automatic gain control to settle
sleep(2)
# Now fix the values
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
# Finally, take several photos with the fixed settings
camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])

'''

show = True

valori_iso = [100, 200, 320, 400, 500, 640, 800]
indice_iso = 0
print(len(valori_iso))

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
        
        PrintFullCameraState()
        
        #if key < 255: print (key)
        if key == 82: print ("up")
        if key == 84: 
            print ("down")
            camera.drc_strength = 'high'
            camera.shutter_speed = 59000
        if key == 81: 
            print ("left")
            if indice_iso > 0:
              indice_iso-=1
            print (valori_iso[indice_iso])
            camera.iso = valori_iso[indice_iso]
        if key == 83:
            print ("right")
            if indice_iso < len(valori_iso)-1:
              indice_iso+=1
            print (valori_iso[indice_iso])
            camera.iso = valori_iso[indice_iso]
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` or ESC key was pressed, break from the loop
	if key == ord("q") or key == 27:
		break
camera.close()
print('camera closed')