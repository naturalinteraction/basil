from vision import *

def RoutineRucola(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='rucola')
    bgr = Resize(bgr, 0.99)
    hsv = ToHSV(bgr)

    # PurgePalette('palette-.pkl', 11)
    # EnablePaletteCreator(bgr, hsv, bins=24)

    mask = SegmentGoodPalette(hsv, 'palette-rucola.pkl', 14.0, debug=False)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', bgr - foreground)
