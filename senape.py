from vision import *

def Process(image_file, bgr, box):

    hsv = ToHSV(bgr)

    senape_hsv,senape_stddev = LoadColorStats('senape.pkl')
    # senape_hsv,senape_stddev = LoadColorStats('trifoglio.pkl')
    senape_variance = senape_stddev ** 2
    weight_hsv = 1.0 / senape_variance
    segmentation_threshold = 4.0  # todo: guess this from the weights
    # print(senape_hsv, senape_stddev, senape_variance, weight_hsv)
    biomass_mask = SegmentBiomass(hsv, senape_hsv, weight_hsv, segmentation_threshold * segmentation_threshold * 3)

    # erosion does not affect the edges of the image!
    # eroding here would be a mistake because I would erode the backing!
    # biomass_mask = Erode(biomass_mask)  # to remove isolated pixels (noise), alternative to median blur

    # before inverting it
    # todo: we assumed in Segment() that all the edges are black (0); this way they will be inverted and become foreground!
    UpdateWindow('background', MaskedImage(bgr, biomass_mask))

    biomass_mask = Inverted(biomass_mask)

    UpdateWindow('biomass_mask', biomass_mask)
    UpdateWindow('foreground', MaskedImage(bgr, biomass_mask))
    UpdateWindow('hsv', hsv)
    UpdateWindow('bgr', bgr)
    # h,s,v = cv2.split(hsv)
    # UpdateWindow('h', h)
    # UpdateWindow('s', s)
    # UpdateWindow('v', v)
