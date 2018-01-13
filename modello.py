from vision import *

def RoutineModello(image_file, bgr, box):

    hsv = ToHSV(bgr)

    mask_green = MaskForTone(hsv, 'basilico.pkl', 60)
    mask_dead = MaskForTone(hsv, 'dead.pkl', 30)
    mask_holes = MaskForTone(hsv, 'holes-color.pkl', 1)
    # mask_bianco = MaskForTone(hsv, 'bianco-firenze.pkl', 2)

    mask_tutto = mask_green + mask_dead + mask_holes

    bianco_hsv,bianco_stddev = LoadColorStats('bianco-firenze.pkl')
    ignored1, ignored2, circles = FillHoles(mask_tutto, bgr, hsv,
                                            bianco_hsv,
                                            1.0 / (bianco_stddev ** 2),
                                            30,
                                            max_area = 400, greater_than = True)

    mask_tutto = Erode(mask_tutto, 5, 1)

    tutto = MaskedImage(bgr, mask_tutto)

    box.Update(mask_tutto, tutto)

    DrawCircles(tutto, circles, white)

    # bianco = MaskedImage(bgr, mask_bianco)
    holes = MaskedImage(bgr, mask_holes)
    dead = MaskedImage(bgr, mask_dead)
    green = MaskedImage(bgr, mask_green)

    # mean,stddev = ComputeStatsOfMaskedImage(hsv, mask)
    # UpdateWindow('mean', ImageWithColor(bgr, mean))

    # UpdateWindow('bianco', bianco)
    UpdateWindow('holes', holes)
    UpdateWindow('dead', dead)
    UpdateWindow('green', green)
    UpdateWindow('all', tutto)

    UpdateWindow('hsv', hsv)
 
