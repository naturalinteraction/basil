from vision import *

def RoutineSatu(image_file, bgr, box):
    hsv = ToHSV(bgr)
    mask = SaturationThreshold(MedianBlurred(hsv, 5), 120)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', MaskedImage(bgr, Inverted(mask)))
    UpdateWindow('hsv', hsv)
