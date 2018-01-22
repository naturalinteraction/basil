from vision import *

def RoutineBieta(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='bieta')

    bgr = Resize(bgr, 0.99)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=24)

    mask = SegmentGoodPalette(hsv, 'palette-bieta.pkl', 14.0, debug=False)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', bgr - foreground)
