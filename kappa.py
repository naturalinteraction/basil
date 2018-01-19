from vision import *

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)

    UpdateWindow('Lab', cv2.cvtColor(bgr, cv2.COLOR_BGR2Lab))
    UpdateWindow('Luv', cv2.cvtColor(bgr, cv2.COLOR_BGR2Luv))
    UpdateWindow('YUV', cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV))

    # SaveColorStats(means[3], stddevs[3], 'foglie-kappa.pkl')
    m,s = LoadColorStats('foglie-kappa.pkl')

    mask_tone = MaskForTone(hsv, 'foglie-kappa.pkl', 20.0)
    mask_sat = SaturationThreshold(hsv, 90)  # contains purple mylar

    mask_tone = cv2.bitwise_and(mask_tone, mask_sat)

    if False:
        accepted_holes_mask,refused_holes_mask,circles =      FillHoles(mask_tone, hsv,
                                                                        m,
                                                                        s,
                                                                        20.0)

    foreground = MaskedImage(bgr, mask_tone)
    UpdateWindow('foglie', foreground)

    small_hsv = Resize(hsv, 0.2)

    if False:
        for i in range(2, 8):
            c,result = KMeans(small_hsv, i)

    if True:
        before = time.time()
        compactness,result,means,stddevs = KMeans(small_hsv, 4, stats=True)
        print(str(time.time() - before) + 's KMEANS')
        UpdateWindow('kmeans', result)

    if True:
        small = Resize(bgr, 0.2)
        before = time.time()
        (segmented_image, labels_image, number_regions) = MeanShift(small, 6, 4.5, 50)  # MeanShift(small, 2, 2, 20)
        print(str(time.time() - before) + 's MEANSHIFT')
        # print(number_regions)
        UpdateWindow('orig', small)
        UpdateWindow('meanshift', segmented_image)
        UpdateWindow('labels', np.uint8(labels_image))

    if True:
        small = Resize(bgr, 0.2)
        before = time.time()
        result,segments,means,stddevs = Superpixel(small)
        print(str(time.time() - before) + 's SUPERPIXEL')
        UpdateWindow("segments", np.uint8(segments))
        UpdateWindow("orig", small)
        UpdateWindow("superpixel", result)
