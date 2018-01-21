from vision import *

def CompareLabels(labels, ground_truth, result, name):
    h,w = labels.shape
    means = []
    pixel_lists = {}
    label_count = np.max(labels)
    for n in range(0, label_count + 1):
        pixel_lists[n] = []
    for x in range(0, w):
        for y in range(0, h):
            pixel_lists[labels[y][x]].append(ground_truth[y][x])
    error = 0.0
    for n in range(0, len(pixel_lists)):
        mean = np.mean(np.float32(pixel_lists[n]), axis=0)
        count = len(pixel_lists[n])
        if mean > 127:
            error = error + count * (255 - mean)
        else:
            error = error + count * mean
    error = error / 255
    for t in range(14, 15):
        mask = MaskForTone(result, 'foglie-kappa.pkl', t)
        diff = cv2.absdiff(mask, ground_truth)
        diff_mean = cv2.mean(diff)[0]
        # print(str(t) + ' diff = ' + str(diff_mean))
    UpdateWindow(name, diff)
    print(name + ' bins=' + str(len(pixel_lists)) + ' error=' + str(int(error)) + ' diff=' + str(diff_mean))

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')

    bgr_small = Resize(bgr, 0.2)
    hsv = ToHSV(bgr_small)

    m,s = LoadColorStats('foglie-kappa.pkl')
    mask_tone = MaskForTone(hsv, 'foglie-kappa.pkl', 20.0)
    mask_sat = SaturationThreshold(hsv, 90)  # contains purple mylar
    mask_combined = cv2.bitwise_and(mask_tone, mask_sat)
    accepted_holes_mask,refused_holes_mask,circles =      FillHoles(mask_combined, hsv,
                                                                    m,
                                                                    s,
                                                                    20.0)
    UpdateWindow('sat and tone', mask_combined)

    small = hsv  # bgr_small, hsv

    if True:
        before = time.time()
        compactness,result,labels,means,stddevs = KMeans(small, 16, stats=True)
        # print(str(time.time() - before) + 's KMEANS')
        CompareLabels(labels, mask_combined, result, 'kmeans')

    if True:
        before = time.time()
        (result, labels, number_regions) = MeanShift(small, 2, 2, 10)
        # print(str(time.time() - before) + 's MEANSHIFT')
        CompareLabels(labels, mask_combined, result, 'meanshift')

    if True:
        before = time.time()
        result,labels,means,stddevs = Superpixel(small)
        # print(str(time.time() - before) + 's SUPERPIXEL')
        CompareLabels(labels, mask_combined, result, 'superpixel')
