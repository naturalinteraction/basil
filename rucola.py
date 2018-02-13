from vision import *

measurements = []
jitter = []

def RoutineRucola(image_file, bgr, box):
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    mean,stddev = FindDominantTone(hsv)
    print(mean, stddev)
    
