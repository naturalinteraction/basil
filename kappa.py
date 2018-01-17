from vision import *

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)
