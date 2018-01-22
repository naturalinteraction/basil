from vision import *

def RoutineKappa(image_file, bgr, box):

    bgr = CropImage(bgr, cropname='blueshift')
    bgr = Resize(bgr, 0.2)
    hsv = ToHSV(bgr)
    # EnablePaletteCreator(bgr, hsv)

    if True:
        mask = SegmentGoodPalette(hsv, 'palette-kappa.pkl' , 10.0)
        # mask = Dilate(mask)
        UpdateWindow('totalpalette', mask)
        UpdateWindow('inverse', Inverted(mask))

        foreground = MaskedImage(bgr, mask)
        UpdateWindow('foreground', foreground)
        UpdateWindow('background', bgr - foreground)

    if False:
        before = time.time()
        (result, labels, number_regions) = MeanShift(hsv, 2, 2, 10)
        # print(str(time.time() - before) + 's MEANSHIFT')
        CompareLabels(labels, mask, result, 'meanshift')

    if False:
        before = time.time()
        result,labels,means,stddevs = Superpixel(hsv)
        # print(str(time.time() - before) + 's SUPERPIXEL')
        CompareLabels(labels, mask, result, 'superpixel')

    if False:
        before = time.time()
        g = graph.rag_mean_color(hsv, labels)
        # labels2 = graph.cut_threshold(labels, g, 29)
        # print(str(time.time() - before) + 's GRAPH AND THRESHOLD CUT')
        # result = color.label2rgb(labels2, hsv, kind='avg')
        # CompareLabels(labels2, mask, result, 'threshold')
        before = time.time()
        labels2 = graph.merge_hierarchical(labels, g, thresh=35, rag_copy=False,
                                           in_place_merge=True,
                                           merge_func=rag_merge_mean_color,
                                           weight_func=rag_weight_mean_color)
        # print(str(time.time() - before) + 's MERGE HIERARCHICAL')
        result = color.label2rgb(labels2, hsv, kind='avg')
        CompareLabels(labels2, mask, result, 'merge')
