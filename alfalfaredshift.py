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

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    bgr = Resize(bgr, 0.5)
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=32)
    if True:
        mask = SegmentGoodPalette(hsv, 'palette-alfalfaredshift.pkl', 15.0, debug=False)
        mask = Dilate(mask, kernel_size=3, iterations=1)
        foreground = MaskedImage(bgr, mask)
        UpdateWindow('background', bgr - foreground)
        UpdateWindow('foreground', foreground)

    if True:
        foreground = cv2.addWeighted(foreground, 0.6, bgr, 0.4, 0)
        mean = cv2.mean(bgr, mask=mask)[0:3]
        greenness = mean[1] / (mean[0] + mean[1] + mean[2]) * 100.0 / 35.0
        M = cv2.moments(mask)
        biomass = (M['m00'] / 2000000) + greenness
        Echo(foreground, 'biomass index ' + str(int(biomass)))
        biomass = biomass - 80
        if len(measurements) > 0:
            biomass = 0.5 * biomass + 0.5 * measurements[-1]
        measurements.append(biomass)
        h,w = hsv.shape[:2]
        for i in range(1, len(measurements)):
            last = measurements[i]
            previous = measurements[i - 1]
            cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
        UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')

    return

    edges = np.uint8(feature.canny(BGRToGray(bgr), sigma=2.0, low_threshold=20, high_threshold=50, use_quantiles=False)) * 255
    edges = cv2.bitwise_and(edges, mask)
    edged_auto = cv2.bitwise_and(auto_canny(bgr), mask)
    edged = cv2.bitwise_and(cv2.Canny(bgr, 100, 200), mask)
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
