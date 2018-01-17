from vision import *

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)