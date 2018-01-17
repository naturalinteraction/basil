from vision import *

def RoutineRucola(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='rucola')
    UpdateWindow('bgr', bgr)
