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

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    bgr = Resize(bgr, 0.3)
    hsv = ToHSV(bgr)

    # EnablePaletteCreator(bgr, hsv, bins=32)

    if False:
        mask = SegmentGoodPalette(hsv, 'palette-alfalfaredshift.pkl', 10.0, debug=True)
        # mask = Dilate(mask)
        foreground = MaskedImage(bgr, mask)
        UpdateWindow('foreground', foreground)
        UpdateWindow('background', bgr - foreground)

    edges = np.uint8(feature.canny(BGRToGray(bgr), sigma=2.0, low_threshold=20, high_threshold=50, use_quantiles=False)) * 255
    UpdateWindow('canny1', edges)

    edged = auto_canny(bgr)
    edged = cv2.Canny(bgr, 100, 200)
    edged = cv2.resize(edged, (0, 0), fx=0.1, fy=0.1, interpolation=cv2.INTER_AREA)  # not using Resize () so we can specify the custom interpolation algorithm
    UpdateWindow('canny2', edged)

    # filled = ndi.binary_fill_holes(edged)
    # UpdateWindow('filled', np.uint8(filled) * 255)

    luminance = BGRToGray(bgr)
    deriv = ComputeImageDerivative(GaussianBlurred(luminance, 5))  # , mask)
    deriv = MedianBlurred(deriv, 11)
    ret,thresholded = cv2.threshold(deriv, 200, 255, cv2.THRESH_BINARY)
    UpdateWindow('derivative', thresholded)
