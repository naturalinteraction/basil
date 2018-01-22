from vision import *

measurements = []

def RoutineAlfalfaNoir(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='noir')
    bgr = Resize(bgr, 0.6)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)
    UpdateWindow('bgr', bgr)
    # EnablePaletteCreator(bgr, hsv, bins=16)
    # GrowPalette('palette-alfalfanoir.pkl', 13)
    # PurgePalette('palette-alfalfanoir.pkl', 5)

    mask = SegmentGoodPalette(hsv, 'palette-alfalfanoir.pkl', 4.0, debug=False)
    # mask = Dilate(mask)
    mask_sat1 = SaturationThreshold(hsv, 120, min_value=200)
    mask_sat = SaturationThreshold(hsv, 160, min_value=160)

    mask_sat = cv2.bitwise_or(mask_sat1, mask_sat)
    mask = cv2.bitwise_or(mask, mask_sat)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    UpdateWindow('background', bgr - foreground)

    foreground = cv2.addWeighted(foreground, 0.6, bgr, 0.4, 0)

    M = cv2.moments(mask)
    # cy = (M['m01']/M['m00'])
    biomass = (M['m00'] / 2000000)
    mean, std = ComputeStatsOfMaskedImage(hsv, mask)
    print(int(biomass * mean[1] / 100.0))
    biomass = biomass * mean[1] / 100.0
    Echo(foreground, 'area ' + str(int(biomass)))
    biomass = biomass - 50
    if len(measurements) > 0:
        biomass = 0.5 * biomass + 0.5 * measurements[-1]
    measurements.append(biomass)

    h,w = hsv.shape[:2]
    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 2)), (i * 10 + 50, int(h - last * 2)), (255, 255, 255), 3)

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
