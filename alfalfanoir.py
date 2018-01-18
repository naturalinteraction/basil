from vision import *

def RoutineAlfalfaNoir(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='noir')
    UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)
    box.Update(SaturationThreshold(hsv, 0))
