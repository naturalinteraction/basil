from vision import *

def RoutineBataviaRossa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='bataviarossa')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)
