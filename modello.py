from vision import *

def MaskForTone(image, filename, threshold):
    mean,stddev = LoadColorStats(filename)
    variance = stddev ** 2
    weight_hsv = 1.0 / variance
    return SegmentBiomass(image, mean, weight_hsv, threshold)

def RoutineModello(image_file, bgr, box):

    hsv = ToHSV(bgr)

    mask_green = MaskForTone(hsv, 'basilico.pkl', 60)
    mask_dead = MaskForTone(hsv, 'dead.pkl', 30)
    mask_holes = MaskForTone(hsv, 'holes-color.pkl', 2)
    mask_bianco = MaskForTone(hsv, 'bianco-firenze.pkl', 2)

    bianco = MaskedImage(bgr, mask_bianco)
    holes = MaskedImage(bgr, mask_holes)
    dead = MaskedImage(bgr, mask_dead)
    green = MaskedImage(bgr, mask_green)

    # mean,stddev = ComputeStatsOfMaskedImage(hsv, mask)
    # UpdateWindow('mean', ImageWithColor(bgr, mean))

    UpdateWindow('bianco', bianco)
    UpdateWindow('holes', holes)
    UpdateWindow('dead', dead)
    UpdateWindow('green', green)

    UpdateWindow('hsv', hsv)
 
