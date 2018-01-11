from vision import *

def RoutineByPixel(image_file, bgr, box):

    hsv = ToHSV(bgr)

    basilico_hsv,basilico_stddev = LoadColorStats('basilico.pkl')
    basilico_variance = basilico_stddev ** 2
    weight_hsv = 1.0 / basilico_variance

    segmentation_threshold = 4.0  # todo: guess this from the weights

    biomass_mask = SegmentBiomass(MedianBlurred(hsv, 5), basilico_hsv,
                                                         weight_hsv, segmentation_threshold * segmentation_threshold * 3)

    UpdateWindow('biomass_mask NOT EXPANDED', biomass_mask)  # this is still the raw mask

    periphery = Dilate(biomass_mask, kernel_size=22)#,iterations=22)
    UpdateWindow('mask dilatata', periphery)

    periphery = periphery - biomass_mask

    UpdateWindow('mask RICERCA', periphery)

    nuova = SegmentWithMask(hsv, basilico_hsv[0], basilico_hsv[1], basilico_hsv[2],
                                                         weight_hsv[0], weight_hsv[1], weight_hsv[2], 4*4*3*1.33, periphery)

    UpdateWindow('nuova', nuova)

    biomass_mask = biomass_mask + nuova

    # this is done after because it needs the updated biomass_mask
    foreground = MaskedImage(bgr, biomass_mask)
    UpdateWindow('background', MaskedImage(bgr, Inverted(biomass_mask)))

    #count = box.Update(biomass_mask, foreground)
    UpdateWindow('accepted-holes', MaskedImage(bgr, nuova))
    UpdateWindow('refused-holes', MaskedImage(bgr, periphery - nuova))
    # UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    UpdateWindow('foreground', foreground)#, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    #UpdateWindow('biomass_mask EXPANDED', biomass_mask)
