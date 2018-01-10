from vision import *

def Basilico(image_file, bgr):
    hsv = ToHSV(bgr)

    biomass_mask = SegmentBiomass(MedianBlurred(hsv, 5))
    # biomass_mask = SegmentBiomass(hsv)

    # erosion does not affect the edges of the image!
    # biomass_mask = Erode(biomass_mask)  # to remove isolated pixels (noise), alternative to median blur
    # UpdateWindow('biomass_mask NOT FILLED', biomass_mask)  # this is still the raw mask, without the holes filled

    accepted_holes_mask,refused_holes_mask,ellipses,circles = FillHoles(biomass_mask, bgr, hsv)

    # this is done after because it needs the updated biomass_mask
    foreground = MaskedImage(bgr, biomass_mask)
    UpdateWindow('background', MaskedImage(bgr, Inverted(biomass_mask)))

    # h,s,v = cv2.split(cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV))
    luminance = ToGray(foreground)
    
    # eroded to exclude outer edges
    UpdateWindow('derivative', ComputeImageDerivative(GaussianBlurred(luminance, 5), Erode(biomass_mask, iterations=2)))

    # Histogram(luminance, output=foreground)

    DrawEllipses(foreground, ellipses, white)
    DrawCircles(foreground, circles, white)

    count,crop_rect = UpdateBiomassBoundingBox(biomass_mask, foreground)

    # UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    # UpdateWindow('accepted-holes', MaskedImage(bgr, accepted_holes_mask))
    # UpdateWindow('refused-holes', MaskedImage(bgr, refused_holes_mask))
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    # UpdateWindow('biomass_mask FILLED', biomass_mask)
