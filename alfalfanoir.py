from vision import *

def RoutineAlfalfaNoir(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='noir')
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    UpdateWindow('bgr', bgr)
    # EnablePaletteCreator(bgr, hsv, bins=16)
    # GrowPalette('palette-alfalfanoir.pkl', 13)
    # PurgePalette('palette-alfalfanoir.pkl', 5)
    if True:
        mask = SegmentGoodPalette(hsv, 'palette-alfalfanoir.pkl' , 10.0, debug=True)
        # mask = Dilate(mask)
        foreground = MaskedImage(bgr, mask)
        UpdateWindow('foreground', foreground)
        UpdateWindow('background', bgr - foreground)
