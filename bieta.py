from vision import *

def RoutineBieta(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='bieta')
    UpdateWindow('bgr', bgr)
