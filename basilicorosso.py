from vision import *

def RoutineBasilicoRosso(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='basilicorosso')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)
