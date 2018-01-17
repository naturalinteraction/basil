from vision import *

def RoutineAlfalfaNoir(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='noir')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)