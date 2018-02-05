from vision import *

measurements = []
jitter = []

def RoutineKappa(image_file, bgr, box):

    print(image_file)

    bgr = CropImage(bgr, cropname='blueshift')
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    hsv = GaussianBlurred(hsv, size=33)  # todo: or median? or smaller size?

    try:
        read_mean,read_std = LoadColorStats('kappa.temp')
    except:
        read_mean = (45, 141, 125)
        read_std = (4, 28, 10)

    s = cv2.split(hsv)[1]
    v = cv2.split(hsv)[2]
    h = cv2.split(hsv)[0]

    v = 255 - v
    threshold = 118 # read_mean[2] - 1 * read[std]  # todo: or other threshold?
    ret,v = cv2.threshold(v, threshold, threshold, cv2.THRESH_TRUNC)
    cv2.normalize(v, v, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    hue_reference = np.zeros(h.shape, np.uint8)
    hue_reference[:] = round(read_mean[0])
    hue_diff = cv2.absdiff(hue_reference, h)

    hue_diff = 255 - hue_diff
    sigma = read_std[0]
    if sigma < 3.0:
        sigma = 3.0
    cv2.normalize(hue_diff, hue_diff, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    ret,hue_diff = cv2.threshold(hue_diff, 255 - 6.0 * sigma, 255 - 6.0 * sigma, cv2.THRESH_TRUNC)  # todo: or other threshold?
    ret,hue_diff = cv2.threshold(hue_diff, 255 - 12.0 * sigma, 255 - 12.0 * sigma, cv2.THRESH_TOZERO)  # todo: or other threshold?

    ret,s = cv2.threshold(s, 106, 106, cv2.THRESH_TRUNC)  # todo: or other threshold?
    ret,s = cv2.threshold(s, 90, 90, cv2.THRESH_TOZERO)  # todo: or other threshold?
    s = cv2.multiply(s, v, scale=1.0/255.0)

    mult = cv2.multiply(hue_diff, s, scale=1.0/255.0)
    cv2.normalize(mult, mult, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    
    # print(ExifKeywords(image_file))

    mult_bgr = GrayToBGR(mult)
    foreground = cv2.multiply(mult_bgr, bgr, scale=1.0/255.0)
    biomass = cv2.mean(mult)[0] / 231.0 * 100.0
    Echo(foreground, 'biomass p-index %.1f' % (biomass))
    biomass = biomass + 10
    if len(measurements) > 0:
        smooth_biomass = 0.5 * biomass + 0.5 * measurements[-1]
        jitter.append(biomass - smooth_biomass)
        biomass = smooth_biomass
        jit = np.std(jitter)
        print('jitter %.3f hue %.1f' % (jit, read_mean[0]))
    measurements.append(biomass)
    h,w = bgr.shape[:2]
    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
    # UpdateWindow('mult', mult)
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    # update stats
    ret,mask = cv2.threshold(mult, 254, 255, cv2.THRESH_BINARY)
    # UpdateWindow('mask', mask)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    print(mean_biomass, stddev_biomass)
    print('')
    mean_biomass[0] = read_mean[0] * 0.0 + 1.0 * mean_biomass[0]
    SaveColorStats(mean_biomass, stddev_biomass, 'kappa.temp')
