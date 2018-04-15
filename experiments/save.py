from vision import *

def RoutineSave(image_file, bgr, box):
    UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')

