from vision import *

measurements = []
h = []
s = []
v = []
jitter = []
tone_filename = 'rucola.temp'

def RoutineRucola(image_file, bgr, box):
    print(image_file)
    bgr,hsv = ResizeBlur(bgr, 0.5, 5)

    if len(measurements) == 0:
        default_mean,default_std = FindDominantTone(hsv)
        print('dominant', default_mean, default_std)
        SaveColorStats(default_mean, default_std, tone_filename)

    read_mean,read_std = LoadColorStats(tone_filename)
    print('read', read_mean, read_std)

    print('dominant', FindDominantTone(hsv))
    dom_mean, dom_std = FindDominantTone(hsv)

    alpha = 0.5
    read_mean = read_mean * alpha + dom_mean * (1.0 - alpha)
    read_std = read_std * alpha + dom_std * (1.0 - alpha)

    dist = DistanceFromToneBlurTopBottom(hsv, tone_filename, 11, 5, 7, 251, 10.0)

    UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)
    UpdateWindow('dist', dist)

    foreground = cv2.multiply(GrayToBGR(dist), bgr, scale=1.0/255.0)
    UpdateWindow('background', cv2.multiply(GrayToBGR(255 - dist), bgr, scale=1.0/255.0))

    Echo(foreground, 'biomass p-index %.1f' % (AppendMeasurementJitter(dist, measurements, jitter)))

    UpdateToneStats(dist, hsv, read_mean, read_std, tone_filename, alpha=0.1)  # 0.5

    DrawChart(foreground, measurements)

    h.append(read_mean[0])

    DrawChart(foreground, h)
    DrawChart(foreground, s)
    DrawChart(foreground, v)

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
