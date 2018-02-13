from vision import *

measurements = []
jitter = []

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    hsv = MedianBlurred(hsv, size=5)

    default_std = (3.4, 27, 26)

    if len(measurements) == 0:
        SaveColorStats((21, 137, 84), default_std, 'alfalfaredshift.temp')

    read_mean,read_std = LoadColorStats('alfalfaredshift.temp')
    dist = DistanceFromTone(hsv, 'alfalfaredshift.temp')
    dist = Dilate(dist, kernel_size=11, iterations=1)
    dist = Erode(dist, kernel_size=5, iterations=1)
    dist = MedianBlurred(dist, size=7)
    dist = TruncateAndZero(dist, 255, 1, 4, 1000)
    dist = 255 - dist
    dist = cv2.addWeighted(dist, 10.0, dist, 0.0, 0.0)
    dist = 255 - dist
    UpdateWindow('hsv', hsv)
    UpdateWindow('dist', dist)
    dist_bgr = GrayToBGR(dist)
    inv_dist_bgr = GrayToBGR(255 - dist)
    foreground = cv2.multiply(dist_bgr, bgr, scale=1.0/255.0)
    background = cv2.multiply(inv_dist_bgr, bgr, scale=1.0/255.0)
    UpdateWindow('back', background)
    biomass = cv2.mean(dist)[0] / 231.0 * 100.0
    Echo(foreground, 'biomass p-index %.1f' % (biomass))
    biomass = biomass - 80
    if len(measurements) > 1:
        smooth_biomass = 0.5 * biomass + 0.5 * measurements[-1]
        predicted_biomass = smooth_biomass + (measurements[-2] -smooth_biomass)
        jitter.append(biomass - predicted_biomass)
        biomass = smooth_biomass
        jit = np.std(jitter)
        print('jitter %.3f' % (jit))
    measurements.append(biomass)
    ret,mask = cv2.threshold(dist, 254, 255, cv2.THRESH_BINARY)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    for i in range(3):
        mean_biomass[i] = 0.1 * mean_biomass[i] + 0.9 * read_mean[i]
        stddev_biomass[i] = 0.1 * stddev_biomass[i] + 0.9 * read_std[i]
        if False and stddev_biomass[i] < default_std[i]:
            stddev_biomass[i] = default_std[i]
    # print(mean_biomass)
    SaveColorStats(mean_biomass, stddev_biomass, 'alfalfaredshift.temp')
    h,w = bgr.shape[:2]
    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
