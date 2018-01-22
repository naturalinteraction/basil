from vision import *

def RoutineBataviaRossa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='bataviarossa')
    
    bgr = Resize(bgr, 0.99)
    hsv = ToHSV(bgr)

    # PurgePalette('palette-bataviarossa.pkl', 11)
    # EnablePaletteCreator(bgr, hsv, bins=24)
    mask = SegmentGoodPalette(hsv, 'palette-bataviarossa.pkl', 14.0, debug=False)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', bgr - foreground)
