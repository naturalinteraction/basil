from vision import *
from skimage import feature
from scipy import ndimage as ndi

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    # print(lower,upper)
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

measurements = []
jitter = []

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    bgr = Resize(bgr, 0.5)
    # UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    hsv = GaussianBlurred(hsv, size=33)

    # EnablePaletteCreator(bgr, hsv, bins=32)
    if False:
        mask = SegmentGoodPalette(hsv, 'palette-alfalfaredshift.pkl', 15.0, debug=False)
        mask = Dilate(mask, kernel_size=3, iterations=1)
        foreground = MaskedImage(bgr, mask)
        UpdateWindow('background', bgr - foreground)
        UpdateWindow('foreground', foreground)

    if False:
        foreground = cv2.addWeighted(foreground, 0.6, bgr, 0.4, 0)
        mean = cv2.mean(bgr, mask=mask)[0:3]
        greenness = mean[1] / (mean[0] + mean[1] + mean[2]) * 100.0 / 35.0
        M = cv2.moments(mask)
        biomass = (M['m00'] / 2000000) + greenness
        Echo(foreground, 'biomass index ' + str(int(biomass)))
        biomass = biomass - 80
        # if len(measurements) > 0:
        #     biomass = 0.5 * biomass + 0.5 * measurements[-1]
        measurements.append(biomass)
        h,w = hsv.shape[:2]
        for i in range(1, len(measurements)):
            last = measurements[i]
            previous = measurements[i - 1]
            cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
        # UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')

    if False:
        edges = np.uint8(feature.canny(BGRToGray(bgr), sigma=2.0, low_threshold=20, high_threshold=50, use_quantiles=False)) * 255
        edges = cv2.multiply(edges, mask, scale=1.0/255.0)
        edged_auto = cv2.multiply(auto_canny(bgr), mask, scale=1.0/255.0)
        edged = cv2.multiply(cv2.Canny(bgr, 100, 200), mask, scale=1.0/255.0)
        # edged = cv2.resize(edged, (0, 0), fx=0.1, fy=0.1, interpolation=cv2.INTER_AREA)  # not using Resize () so we can specify the custom interpolation algorithm
        # UpdateWindow('canny2', edged)
        luminance = BGRToGray(bgr)
        deriv = ComputeImageDerivative(GaussianBlurred(luminance, 5), mask)
        # deriv = MedianBlurred(deriv, 11)
        ret,deriv = cv2.threshold(deriv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ret,edged_auto = cv2.threshold(edged_auto, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ret,edged = cv2.threshold(edged, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ret,edges = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # UpdateWindow('derivative', thresholded)
        area = cv2.mean(mask)[0]
        print(cv2.mean(edged_auto)[0] / area, cv2.mean(edged)[0] / area, cv2.mean(deriv)[0] / area, cv2.mean(edges)[0] / area)
        UpdateWindow('autocanny', edged_auto)
        UpdateWindow('canny', edged)
        UpdateWindow('deriv', deriv)
        UpdateWindow('feat', edges)

    try:
        read_mean,read_std = LoadColorStats('alfalfaredshift.temp')
    except:
        read_mean = (20, 125, 85)
        read_std = (3.4, 12, 13)

    h = cv2.split(hsv)[0]
    s = cv2.split(hsv)[1]
    v = cv2.split(hsv)[2]

    v = TruncateAndZero(255 - v, read_mean[2], max(20, read_std[1]), 0.0, 1.0)

    h = SimilarityToReference(h, read_mean[0])
    Normalize(h)
    # h = TruncateAndZero(h, 255, max(4, read_std[0]), 4.0, 8.0, normalize=False)
    # print(255 - 4.0 * max(4, read_std[0]), 255 -  8.0 * max(4, read_std[0]))
    ret,h = cv2.threshold(h, 230, 230, cv2.THRESH_TRUNC)
    ret,h = cv2.threshold(h, 210, 210, cv2.THRESH_TOZERO)

    # s = TruncateAndZero(s, read_mean[1], max(14, read_std[1]), 2.8, 5.4, normalize=False)
    # print(read_mean[1] - 3.6 * max(14, read_std[1]), read_mean[1] -  6.4 * max(14, read_std[1]))
    ret,s = cv2.threshold(s, 70, 70, cv2.THRESH_TRUNC)
    ret,s = cv2.threshold(s, 30, 30, cv2.THRESH_TOZERO)

    UpdateWindow('hsv', hsv)
    UpdateWindow('dh', h)
    UpdateWindow('ds', s)
    UpdateWindow('dv', v)

    mult = cv2.multiply(h, cv2.multiply(v, s, scale=1.0/255.0), scale=1.0/255.0)
    Normalize(mult)
    mult_bgr = GrayToBGR(mult)
    inv_mult_bgr = GrayToBGR(255 - mult)
    foreground = cv2.multiply(mult_bgr, bgr, scale=1.0/255.0)
    background = cv2.multiply(inv_mult_bgr, bgr, scale=1.0/255.0)
    UpdateWindow('back', background)
    biomass = cv2.mean(mult)[0] / 231.0 * 100.0
    Echo(foreground, 'biomass p-index %.1f' % (biomass))
    biomass = biomass - 80
    if len(measurements) > 0:
        smooth_biomass = 0.5 * biomass + 0.5 * measurements[-1]
        jitter.append(biomass - smooth_biomass)
        biomass = smooth_biomass
    measurements.append(biomass)
    h,w = bgr.shape[:2]
    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    jit = np.std(jitter)
    print('jitter %.3f hue %.1f' % (jit, read_mean[0]))
    # update stats
    ret,mask = cv2.threshold(mult, 250, 255, cv2.THRESH_BINARY)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    print(mean_biomass, stddev_biomass)
    SaveColorStats(mean_biomass, stddev_biomass, 'alfalfaredshift.temp')
