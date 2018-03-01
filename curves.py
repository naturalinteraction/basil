from vision import *

measurements = []
h = []
s = []
v = []
sat_mean = []
topped_sat_mean = []
jitter = []
tone_filename = 'curves.temp'
disuniformity = []
darkness = []

curve_alpha = 0.05

def RoutineCurves(image_file, bgr, box):
    print(image_file)

    hires = bgr

    bgr,hsv = ResizeBlur(bgr, 0.5, 5)

    dark = FrameBrightness(bgr)
    if len(darkness) > 0:
        darkness.append(dark * curve_alpha + (1.0 - curve_alpha) * darkness[-1])
    else:
        darkness.append(dark)

    if len(measurements) == 0:
        default_mean,default_std = FindDominantTone(hsv)
        PrintStats('dom', default_mean, default_std)
        SaveColorStats(default_mean, default_std, tone_filename)

    read_mean,read_std = LoadColorStats(tone_filename)
    PrintStats('rea', read_mean, read_std)

    dom_mean, dom_std = FindDominantTone(hsv)
    PrintStats('dom', dom_mean, dom_std)

    alpha = 0.9
    read_mean = read_mean * alpha + dom_mean * (1.0 - alpha)
    read_std = read_std * alpha + dom_std * (1.0 - alpha)

    PrintStats('med', read_mean, read_std)
    dist = DistanceFromToneBlurTopBottom(hsv, tone_filename, 11, 5, 7, 251, 10.0)

    # UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    # UpdateWindow('dist', dist)

    saturation = cv2.split(hsv)[1]
    Normalize(saturation)
    # UpdateWindow('normalized saturation', saturation)
    sm = cv2.mean(saturation)[0]
    if len(sat_mean) > 0:
        sat_mean.append(sm * curve_alpha + (1.0 - curve_alpha) * sat_mean[-1])
    else:
        sat_mean.append(sm)
    ret,saturation = cv2.threshold(saturation, 170, 170, cv2.THRESH_TRUNC)
    Normalize(saturation)
    if 'visible-callalta' in image_file or 'blueshift-callalta' in image_file:  # ravanello
        ravanello = DistanceFromToneBlurTopBottom(hsv, "ravanello.pkl", 1, 1, 1, 240, 10.0)
        UpdateWindow('ravanello', ravanello)
        saturation = cv2.addWeighted(saturation, 1.0, ravanello, 0.7, 0.0)
    if 'visible-doublecalib' in image_file or 'blueshift-doublecalib' in image_file:  # alga
        alga = DistanceFromToneBlurTopBottom(hsv, "alga.pkl", 1, 1, 1, 255, 10.0)
        UpdateWindow('alga', alga)
        saturation = cv2.addWeighted(saturation, 1.0, alga, -0.5, 0.0)
    Normalize(saturation)
    UpdateWindow('topped normalized saturation', saturation)
    sm = cv2.mean(saturation)[0]
    if len(topped_sat_mean) > 0:
        topped_sat_mean.append(sm * curve_alpha + (1.0 - curve_alpha) * topped_sat_mean[-1])
    else:
        topped_sat_mean.append(sm)

    # foreground = cv2.multiply(GrayToBGR(saturation), bgr, scale=1.0/255.0)
    foreground = hires  # bgr
    # UpdateWindow('background', cv2.multiply(GrayToBGR(255 - saturation), bgr, scale=1.0/255.0))

    disuniformity_mask = Resize(dist, 0.1)
    disuniformity_mask = cv2.Canny(disuniformity_mask, 200, 200)
    disuniformity_value,ignore = cv2.meanStdDev(disuniformity_mask)
    disuniformity_value = -disuniformity_value
    if len(disuniformity) > 0:
        disuniformity.append(disuniformity_value * curve_alpha + (1.0 - curve_alpha) * disuniformity[-1])
    else:
        disuniformity.append(disuniformity_value)
    UpdateWindow('disuniformity_mask', disuniformity_mask)

    biomass = AppendMeasurementJitter(dist, measurements, jitter, alpha=0.1)
    # Echo(foreground, 'biomass p-index %.1f' % (biomass))
    Echo(foreground, image_file.replace('downloaded/', ''))

    h.append(read_mean[0])
    s.append(read_mean[1])
    v.append(read_mean[2])

    UpdateToneStats(dist, hsv, read_mean, read_std, tone_filename, alpha=curve_alpha)

    if True:
        print('darkness')
        DrawChart(foreground, darkness, color=(0, 0, 0), ymult=0.005, yoffset=0.5)
        print('h')
        DrawChart(foreground, h, color=(255, 0, 0), ymult=0.005, yoffset=0.5)
        print('s')
        DrawChart(foreground, s, color=(0, 255, 0), ymult=0.005, yoffset=0.5)
        print('v')
        DrawChart(foreground, v, color=(0, 0, 255), ymult=0.005, yoffset=0.5)
        print('sat_mean')
        DrawChart(foreground, sat_mean, color=(0, 255, 255))

    print('disuniformity')
    DrawChart(foreground, disuniformity, color=(255, 0, 255))
    print('topped_sat_mean')
    DrawChart(foreground, topped_sat_mean, color=(255, 255, 0))

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
