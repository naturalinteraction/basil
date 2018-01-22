from vision import *

measurements = []

def RoutineBasilicoRosso(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='basilicorosso')
    bgr = Resize(bgr, 0.3)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=32)
    # return
    mask = SegmentGoodPalette(hsv, 'palette-basilicorosso.pkl', 8.0, debug=True)
    # mask = Erode(mask)
    # mask = Dilate(mask, iterations=4)
    foreground = MaskedImage(bgr, mask)
    UpdateWindow('foreground', foreground)
    # UpdateWindow('background', bgr - foreground)

    foreground = cv2.addWeighted(foreground, 0.6, bgr, 0.4, 0)

    M = cv2.moments(mask)
    # cy = (M['m01']/M['m00'])
    biomass = (M['m00'] / 2000000)
    Echo(foreground, 'area ' + str(int(biomass)))
    biomass = biomass - 40
    if len(measurements) > 0:
        biomass = 0.5 * biomass + 0.5 * measurements[-1]
    measurements.append(biomass)

    h,w = hsv.shape[:2]
    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
    # mean, std = ComputeStatsOfMaskedImage(hsv, mask)
    # print(mean)

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
