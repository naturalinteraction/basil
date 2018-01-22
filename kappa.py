from vision import *

measurements = []

def RoutineKappa(image_file, bgr, box):

    bgr = CropImage(bgr, cropname='blueshift')
    # bgr = Resize(bgr, 0.4)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=24)
    
    mask = SegmentGoodPalette(MedianBlurred(hsv, 5), 'palette-kappa.pkl' , 10.0, debug=False)
    foreground = MaskedImage(bgr, mask)
    # UpdateWindow('background', bgr - foreground)

    foreground = cv2.addWeighted(foreground, 0.6, bgr, 0.4, 0)

    M = cv2.moments(mask)
    # cy = (M['m01']/M['m00'])
    biomass = (M['m00'] / 2000000)
    Echo(foreground, 'biomass area ' + str(int(biomass)))

    if len(measurements) > 0:
        biomass = 0.5 * biomass + 0.5 * measurements[-1]
    measurements.append(biomass)

    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 20 + 100, int(1900 - previous * 4)), (i * 20 + 100, int(1900 - last * 4)), (255, 255, 255), 12)

    # mean, std = ComputeStatsOfMaskedImage(hsv, mask)
    # print(mean)

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    
