from vision import *

def RoutineKappa(image_file, bgr, box):

    bgr = CropImage(bgr, cropname='blueshift')
    bgr = Resize(bgr, 0.2)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=24)

    mask = SegmentGoodPalette(hsv, 'palette-kappa.pkl' , 14.0, debug=False)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', bgr - foreground)

