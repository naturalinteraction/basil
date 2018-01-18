from vision import *

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)

    if False:
        for i in range(2, 8):
            c,result = KMeans(hsv, i)

    if False:
        compactness,result,means,stddevs = KMeans(hsv, 4, stats=True)
        UpdateWindow('kmeans', result)

    # SaveColorStats(means[3],stddevs[3], 'foglie-kappa.pkl')
    print(LoadColorStats('foglie-kappa.pkl'))
    m,s = LoadColorStats('foglie-kappa.pkl')

    mask_tone = MaskForTone(hsv, 'foglie-kappa.pkl', 20.0)
    mask_sat = SaturationThreshold(hsv, 90)  # contains purple mylar

    mask_tone = cv2.bitwise_and(mask_tone, mask_sat)

    if True:
        accepted_holes_mask,refused_holes_mask,circles =      FillHoles(mask_tone, hsv,
                                                                        m,
                                                                        s,
                                                                        20.0)

    UpdateWindow('foglie', MaskedImage(bgr, mask_tone))

    small = Resize(bgr, 0.2)
    (segmented_image, labels_image, number_regions) = MeanShift(small)
    print(number_regions)
    UpdateWindow('small', small)
    UpdateWindow('segmented', segmented_image)
    UpdateWindow('labels', np.uint8(labels_image))
    # todo: COLOR_BGR2YUV COLOR_BGR2Luv COLOR_BGR2Lab
