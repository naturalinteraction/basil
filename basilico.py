from vision import *

def RoutineBasilico(image_file, bgr, box):

    hsv = ToHSV(bgr)

    # print(LoadColorStats('bianco-firenze.pkl'))

    basilico_hsv,basilico_stddev = LoadColorStats('basilico.pkl')
    basilico_variance = basilico_stddev ** 2
    weight_hsv = 1.0 / basilico_variance
    segmentation_threshold = 60.0

    biomass_mask = SegmentBiomass(MedianBlurred(hsv, 5), basilico_hsv,
                                                         basilico_stddev, segmentation_threshold)
    # biomass_mask = SegmentBiomass(hsv, ...)

    # erosion does not affect the edges of the image!
    # biomass_mask = Erode(biomass_mask)  # to remove isolated pixels (noise), alternative to median blur
    # UpdateWindow('biomass_mask NOT FILLED', biomass_mask)  # this is still the raw mask, without the holes filled

    accepted_holes_mask,refused_holes_mask,circles =          FillHoles(biomass_mask, hsv,
                                                                        basilico_hsv,
                                                                        basilico_stddev,
                                                                        segmentation_threshold * 1.33)

    # this is done after because it needs the updated biomass_mask
    foreground = MaskedImage(bgr, biomass_mask)

    # mean,stddev = ComputeStatsOfMaskedImage(hsv, biomass_mask)
    # UpdateWindow('mean', ImageWithColor(bgr, mean))

    UpdateWindow('background', MaskedImage(bgr, Inverted(biomass_mask)))

    # h,s,v = cv2.split(cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV))
    # luminance = BGRToGray(foreground)

    # eroded to exclude outer edges
    # UpdateWindow('derivative', ComputeImageDerivative(GaussianBlurred(luminance, 5), Erode(biomass_mask, iterations=2)))

    # Histogram(luminance, output=foreground)

    DrawCircles(foreground, circles, white)

    count = box.Update(biomass_mask, foreground)

    # UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    # UpdateWindow('accepted-holes', MaskedImage(bgr, accepted_holes_mask))
    # UpdateWindow('refused-holes', MaskedImage(bgr, refused_holes_mask))
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    # UpdateWindow('biomass_mask FILLED', biomass_mask)
