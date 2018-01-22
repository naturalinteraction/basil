from vision import *

def RoutineBasilicoRosso(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='basilicorosso')
    bgr = Resize(bgr, 0.99)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=24)
    mask = SegmentGoodPalette(MedianBlurred(hsv), 'palette-basilicorosso.pkl', 8.0, debug=False)
    # mask = Erode(mask)
    # mask = Dilate(mask, iterations=4)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', bgr - foreground)
