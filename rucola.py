from vision import *

measurements = []
h = []
s = []
v = []
sat_mean = []
jitter = []
tone_filename = 'rucola.temp'

def RoutineRucola(image_file, bgr, box):
    print(image_file)
    bgr,hsv = ResizeBlur(bgr, 0.5, 5)

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
    dist = DistanceFromToneBlurTopBottom(hsv, tone_filename, 11, 5, 7, 253, 10.0)  # was 251

    UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    UpdateWindow('dist', dist)

    foreground = cv2.multiply(GrayToBGR(dist), bgr, scale=1.0/255.0)
    UpdateWindow('background', cv2.multiply(GrayToBGR(255 - dist), bgr, scale=1.0/255.0))

    saturation = cv2.split(hsv)[1]
    Normalize(saturation)
    UpdateWindow('normalized saturation', saturation)
    ####ret,saturation = cv2.threshold(saturation, reference - trunc_sigmas * sigma, reference - trunc_sigmas * sigma, cv2.THRESH_TRUNC)
    sm = cv2.mean(saturation)[0]
    if len(sat_mean) > 0:
        sat_mean.append(sm * 0.1 + 0.9 * sat_mean[-1])
    else:
        sat_mean.append(sm)

    Echo(foreground, 'biomass p-index %.1f' % (AppendMeasurementJitter(dist, measurements, jitter, alpha=0.1)))

    h.append(read_mean[0])
    s.append(read_mean[1])
    v.append(read_mean[2])

    UpdateToneStats(dist, hsv, read_mean, read_std, tone_filename, alpha=0.1)

    DrawChart(foreground, measurements)
    DrawChart(foreground, sat_mean, color=(0, 255, 255))

    DrawChart(foreground, h, color=(255, 0, 0), xmult=10, xoffset=150, ymult=6, yoffset=500)
    DrawChart(foreground, s, color=(0, 255, 0), xmult=10, xoffset=150, ymult=6, yoffset=500)
    DrawChart(foreground, v, color=(0, 0, 255), xmult=10, xoffset=150, ymult=6, yoffset=500)


    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
