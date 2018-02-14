from vision import *

measurements = []
jitter = []
tone_filename = 'alfalfaredshift.temp'

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    bgr,hsv = ResizeBlur(bgr, 0.5, 5)

    if len(measurements) == 0:
        default_mean,default_std = FindDominantTone(hsv)
        print('dominant', default_mean, default_std)
        SaveColorStats(default_mean, default_std, tone_filename)

    read_mean,read_std = LoadColorStats(tone_filename)
    print('read', read_mean, read_std)

    dist = DistanceFromToneBlurTopBottom(hsv, tone_filename, 11, 5, 7, 251, 10.0)

    UpdateWindow('hsv', hsv)
    UpdateWindow('dist', dist)

    foreground = cv2.multiply(GrayToBGR(dist), bgr, scale=1.0/255.0)
    UpdateWindow('background', cv2.multiply(GrayToBGR(255 - dist), bgr, scale=1.0/255.0))

    Echo(foreground, 'biomass p-index %.1f' % (AppendMeasurementJitter(dist, measurements, jitter)))

    UpdateToneStats(dist, hsv, read_mean, read_std, tone_filename)

    DrawChart(foreground, measurements)

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
