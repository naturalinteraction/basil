from vision import *

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    # UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    hsv = ToHSV(bgr)
    hsv = Resize(hsv, 0.2)
    Lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2Lab)
    Luv = cv2.cvtColor(bgr, cv2.COLOR_BGR2Luv)
    YUV = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)

    m,s = LoadColorStats('foglie-kappa.pkl')
    mask_tone = MaskForTone(hsv, 'foglie-kappa.pkl', 20.0)
    mask_sat = SaturationThreshold(hsv, 90)  # contains purple mylar
    mask_combined = cv2.bitwise_and(mask_tone, mask_sat)
    accepted_holes_mask,refused_holes_mask,circles =      FillHoles(mask_combined, hsv,
                                                                    m,
                                                                    s,
                                                                    20.0)
    UpdateWindow('sat and tone', mask_combined)

    small = hsv  # bgr, hsv, Lab, Luv, YUV

    if True:
        before = time.time()
        compactness,result,labels,means,stddevs = KMeans(small, 8, stats=True)
        print(str(time.time() - before) + 's KMEANS')
        UpdateWindow('kmeans', result)

    if True:
        before = time.time()
        (segmented_image, labels_image, number_regions) = MeanShift(small, 1, 1, 10)
        print(str(time.time() - before) + 's MEANSHIFT')
        UpdateWindow('meanshift', segmented_image)

    if True:
        before = time.time()
        result,segments,means,stddevs = Superpixel(small)
        print(str(time.time() - before) + 's SUPERPIXEL')
        UpdateWindow("superpixel", result)

    if True:
        before = time.time()
        result,labels = Slic(small)
        print(str(time.time() - before) + 's SLIC')
        UpdateWindow("slic", result)
