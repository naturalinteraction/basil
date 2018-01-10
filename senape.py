from vision import *

def Process(image_file, bgr, box):

    hsv = ToHSV(bgr)

    senape_hsv = (12, 60, 230)

    weight_hsv = (3, 3, 1)

    segmentation_threshold = 46

    biomass_mask = SegmentBiomass(hsv, senape_hsv, weight_hsv, segmentation_threshold * segmentation_threshold * 3)

    # erosion does not affect the edges of the image!
    # biomass_mask = Erode(biomass_mask)  # to remove isolated pixels (noise), alternative to median blur

    # before inverting it
    UpdateWindow('background', MaskedImage(bgr, biomass_mask))

    biomass_mask = Inverted(biomass_mask)

    UpdateWindow('biomass_mask', biomass_mask)

    h,s,v = cv2.split(hsv)
    
    UpdateWindow('foreground', MaskedImage(bgr, biomass_mask))
    UpdateWindow('hsv', hsv)
    UpdateWindow('bgr', bgr)
    UpdateWindow('h', h)
    UpdateWindow('s', s)
    UpdateWindow('v', v)

