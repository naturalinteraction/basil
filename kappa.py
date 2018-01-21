from vision import *

def ReplaceLabelWithColor(labels, selected, result, color):
    h,w = labels.shape
    for x in range(0, w):
        for y in range(0, h):
            if labels[y][x] == selected:
                result[y][x] = color
    UpdateWindow('interactive', result)
    cv2.setMouseCallback('interactive', mouseCallbackGoodBad)

def mouseCallbackGoodBad(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        selected = labels[y,x]
        print('adding to good ' + str(means[selected]) + ' ' + str(selected))
        try:
            good.add(selected)
            bad.remove(selected)
        except:
            pass
        ReplaceLabelWithColor(labels, selected, result, (255, 0, 0))
    if event == cv2.EVENT_RBUTTONDOWN:
        selected = labels[y,x]
        print('adding to bad ' + str(means[selected]) + ' ' + str(selected))
        try:
            bad.add(selected)
            good.remove(selected)
        except:
            pass
        ReplaceLabelWithColor(labels, selected, result, (0, 255, 255))
    if event == cv2.EVENT_MBUTTONDOWN:
        print('good', good)
        print('bad', bad)
        with open('colors.pkl', 'w') as f:
            pickle.dump((means,stddevs,good,bad), f, 0)
        with open('colors.pkl', 'r') as f:
            (mm,ss,gg,bb) = pickle.load(f)
            print(mm)
            print(ss)
            print(gg)
            print(bb)

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
        count = len(pixel_lists[n])
        if count > 0:
            mean = np.mean(np.float32(pixel_lists[n]), axis=0)
        else:
            mean = 0.0
            print('no mean possible')
        if mean > 127:
            error = error + count * (255 - mean)
        else:
            error = error + count * mean
    error = error / 255
    for t in range(14, 15):
        mask = MaskForTone(result, 'foglie-kappa.pkl', t)
        diff = cv2.absdiff(mask, ground_truth)
        diff_mean = cv2.mean(diff)[0]
    UpdateWindow(name, result)
    print(name + ' bins=' + str(len(pixel_lists)) + ' error=' + str(int(error)) + ' diff=' + str(diff_mean))

def RoutineKappa(image_file, bgr, box):
    global good
    global bad
    global labels
    global means
    global stddevs
    global result
    good = set()
    bad = set()

    bgr = CropImage(bgr, cropname='blueshift')

    bgr_small = Resize(bgr, 0.5)
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
    UpdateWindow('small', small)

    if False:
        before = time.time()
        compactness,result,labels,means,stddevs = KMeans(small, 16, stats=True)
        # print(str(time.time() - before) + 's KMEANS')
        CompareLabels(labels, mask_combined, result, 'kmeans')

    if False:
        before = time.time()
        (result, labels, number_regions) = MeanShift(small, 2, 2, 10)
        # print(str(time.time() - before) + 's MEANSHIFT')
        CompareLabels(labels, mask_combined, result, 'meanshift')

    if True:
        before = time.time()
        result,labels,means,stddevs = Superpixel(small)
        # print(str(time.time() - before) + 's SUPERPIXEL')
        CompareLabels(labels, mask_combined, result, 'superpixel')

    if False:
        before = time.time()
        g = graph.rag_mean_color(small, labels)
        # labels2 = graph.cut_threshold(labels, g, 29)
        # print(str(time.time() - before) + 's GRAPH AND THRESHOLD CUT')
        # result = color.label2rgb(labels2, small, kind='avg')
        # CompareLabels(labels2, mask_combined, result, 'threshold')
        before = time.time()
        labels2 = graph.merge_hierarchical(labels, g, thresh=35, rag_copy=False,
                                           in_place_merge=True,
                                           merge_func=rag_merge_mean_color,
                                           weight_func=rag_weight_mean_color)
        # print(str(time.time() - before) + 's MERGE HIERARCHICAL')
        result = color.label2rgb(labels2, small, kind='avg')
        CompareLabels(labels2, mask_combined, result, 'merge')

    if True:
        compactness,result,labels,means,stddevs = KMeans(result, 16, stats=True)
        CompareLabels(labels, mask_combined, result, 'interactive')
        cv2.setMouseCallback('interactive', mouseCallbackGoodBad)
        # this is a very basic selection based on hue
        for n,mean in enumerate(means):
            bad.add(n)
            if abs(mean[0] - m[0]) < 4:
                print(str(mean) + 'foreground' + str(stddevs[n]))
            else:
                print(str(mean) + 'no')
