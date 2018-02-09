from vision import *

measurements = []
jitter = []

def SimilarityToReference(channel, value):
    reference = np.zeros(channel.shape, np.uint8)
    reference[:] = round(value)
    return 255 - cv2.absdiff(reference, channel)

def Normalize(channel):
    cv2.normalize(channel, channel, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

def TruncateAndZero(channel, sigma, trunc_sigmas, zero_sigmas):
    ret,result = cv2.threshold(channel, 255 - trunc_sigmas * sigma, 255 - trunc_sigmas * sigma, cv2.THRESH_TRUNC)
    ret,result = cv2.threshold(result, 255 - zero_sigmas * sigma, 255 - zero_sigmas * sigma, cv2.THRESH_TOZERO)
    Normalize(result)
    return result

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    hsv = MedianBlurred(hsv, size=11)
    try:
        read_mean,read_std = LoadColorStats('kappa.temp')
    except:
        read_mean = (45, 141, 125)
        read_std = (4, 28, 10)
    h = cv2.split(hsv)[0]
    s = cv2.split(hsv)[1]
    v = cv2.split(hsv)[2]

    v = 255 - v
    threshold = read_mean[2] - 1.0 * max(10, read_std[2])
    ret,v = cv2.threshold(v, threshold, threshold, cv2.THRESH_TRUNC)
    Normalize(v)

    hue_sim = SimilarityToReference(h, read_mean[0])

    hue_sim = TruncateAndZero(hue_sim, max(4, read_std[0]), 0.0, 6.0)

    UpdateWindow('hue', hue_sim)

    threshold = read_mean[1] - 1.25 * max(28, read_std[1])
    ret,s = cv2.threshold(s, threshold, threshold, cv2.THRESH_TRUNC)
    threshold = read_mean[1] - 1.8 * max(28, read_std[1])
    ret,s = cv2.threshold(s, threshold, threshold, cv2.THRESH_TOZERO)
    s = cv2.multiply(s, v, scale=1.0/255.0)

    mult = cv2.multiply(hue_sim, s, scale=1.0/255.0)
    Normalize(mult)

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
    ret,mask = cv2.threshold(mult, 250, 255, cv2.THRESH_BINARY)
    # UpdateWindow('mask', mask)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    print(mean_biomass, stddev_biomass)
    print('')
    mean_biomass[0] = read_mean[0] * 0.0 + 1.0 * mean_biomass[0]
    SaveColorStats(mean_biomass, stddev_biomass, 'kappa.temp')
