from vision import *

def RoutineModello(image_file, bgr, box):    
    bgr = Blurred(bgr, 33)
    UpdateWindow('bgr', bgr)
    global back
    try:
        back
    except:
        back = bgr
    UpdateWindow('foreground', cv2.absdiff(bgr, back))

