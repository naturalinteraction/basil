from vision import *

def RoutineBasilico(image_file, bgr, box):
    hsv = ToHSV(bgr)

    segmentation_threshold = 20.0
    biomass_mask = MaskForTone(MedianBlurred(hsv, 5), 'foglie-kappa.pkl', segmentation_threshold)
    # erosion does not affect the edges of the image!
    # biomass_mask = Erode(biomass_mask)  # to remove isolated pixels (noise), alternative to median blur
    # UpdateWindow('biomass_mask NOT FILLED', biomass_mask)  # this is still the raw mask, without the holes filled

    basilico_hsv,basilico_stddev = LoadColorStats('foglie-kappa.pkl')
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

    # UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    # UpdateWindow('accepted-holes', MaskedImage(bgr, accepted_holes_mask))
    # UpdateWindow('refused-holes', MaskedImage(bgr, refused_holes_mask))
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    # UpdateWindow('biomass_mask FILLED', biomass_mask)
