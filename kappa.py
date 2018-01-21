from vision import *

def rag_weight_mean_color(graph, src, dst, n):
    diff = graph.node[dst]['mean color'] - graph.node[n]['mean color']
    diff = np.linalg.norm(diff)
    return {'weight': diff}

def rag_merge_mean_color(graph, src, dst):
    graph.node[dst]['total color'] += graph.node[src]['total color']
    graph.node[dst]['pixel count'] += graph.node[src]['pixel count']
    graph.node[dst]['mean color'] = (graph.node[dst]['total color'] /
                                     graph.node[dst]['pixel count'])


def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    hsv = ToHSV(bgr)
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

    small = Resize(hsv, 0.2)  # bgr, hsv, Lab, Luv, YUV

    if False:
        for i in range(2, 8):
            c,result = KMeans(small, i)

    if False:
        before = time.time()
        compactness,result,means,stddevs = KMeans(small, 6, stats=True)
        print(str(time.time() - before) + 's KMEANS')
        UpdateWindow('kmeans', result)

    if False:
        before = time.time()
        (segmented_image, labels_image, number_regions) = MeanShift(small, 6, 4.5, 50)  # MeanShift(small, 2, 2, 20)
        print(str(time.time() - before) + 's MEANSHIFT')
        # print(number_regions)
        UpdateWindow('orig', small)
        UpdateWindow('meanshift', segmented_image)
        UpdateWindow('labels', np.uint8(labels_image))

    if False:
        before = time.time()
        result,segments,means,stddevs = Superpixel(small)
        print(str(time.time() - before) + 's SUPERPIXEL')
        UpdateWindow("segments", np.uint8(segments))
        UpdateWindow("orig", small)
        UpdateWindow("superpixel", result)

    if True:
        before = time.time()
        labels1 = slic(small, compactness=30, n_segments=400)
        print(str(time.time() - before) + 's SLIC')
        out1 = color.label2rgb(labels1, small, kind='avg')
        before = time.time()
        g = graph.rag_mean_color(small, labels1, mode='similarity')
        labels2 = graph.cut_normalized(labels1, g)
        print(str(time.time() - before) + 's GRAPH AND NORMALIZED CUT')
        out2 = color.label2rgb(labels2, small, kind='avg')
        UpdateWindow("slic", out1)
        UpdateWindow("normalized cut", out2)
        before = time.time()
        g = graph.rag_mean_color(small, labels1)
        labels2 = graph.cut_threshold(labels1, g, 29)
        print(str(time.time() - before) + 's GRAPH AND THRESHOLD CUT')
        out2 = color.label2rgb(labels2, small, kind='avg')
        UpdateWindow("threshold cut", out2)
        before = time.time()
        labels2 = graph.merge_hierarchical(labels1, g, thresh=35, rag_copy=False,
                                           in_place_merge=True,
                                           merge_func=rag_merge_mean_color,
                                           weight_func=rag_weight_mean_color)
        print(str(time.time() - before) + 's MERGE HIERARCHICAL')
        out2 = color.label2rgb(labels2, small, kind='avg')
        UpdateWindow("merge hierarchical", out2)
