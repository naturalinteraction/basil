from vision import *

measurements = []
jitter = []

def SimilarityToReference(channel, value):
    reference = np.zeros(channel.shape, np.uint8)
    reference[:] = round(value)
    return 255 - cv2.absdiff(reference, channel)

def Normalize(channel):
    cv2.normalize(channel, channel, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

def TruncateAndZero(channel, reference, sigma, trunc_sigmas, zero_sigmas):
    ret,result = cv2.threshold(channel, reference - trunc_sigmas * sigma, reference - trunc_sigmas * sigma, cv2.THRESH_TRUNC)
    ret,result = cv2.threshold(result,  reference -  zero_sigmas * sigma, reference -  zero_sigmas * sigma, cv2.THRESH_TOZERO)
    Normalize(result)
    return result

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    hsv = MedianBlurred(hsv, size=5)
    try:
        read_mean,read_std = LoadColorStats('kappa.temp')
    except:
        read_mean = (41, 220, 173)
        read_std = (2.2, 20, 20)
    h = cv2.split(hsv)[0]
    s = cv2.split(hsv)[1]
    v = cv2.split(hsv)[2]

    hue_sim = SimilarityToReference(h, read_mean[0])
    hue_sim = TruncateAndZero(hue_sim, 255, max(4, read_std[0]), 0.0, 2.8)

    s = TruncateAndZero(s, read_mean[1], max(28, read_std[1]), 1.0, 4.0)

    UpdateWindow('hsv', hsv)
    UpdateWindow('hue_sim', hue_sim)
    UpdateWindow('s', s)

    mult = cv2.multiply(hue_sim, s, scale=1.0/255.0)
    Normalize(mult)

    # print(ExifKeywords(image_file))

    mult_bgr = GrayToBGR(mult)
    inv_mult_bgr = GrayToBGR(255 - mult)
    foreground = cv2.multiply(mult_bgr, bgr, scale=1.0/255.0)
    background = cv2.multiply(inv_mult_bgr, bgr, scale=1.0/255.0)
    UpdateWindow('back', background)
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
