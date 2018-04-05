from vision import *

from datetime import datetime

minutes_since_epoch = []
measurements = []
h = []
s = []
v = []
sat_mean = []
topped_sat_mean = []
jitter = []
tone_filename = 'curves.temp'
uniformity = []
brightness = []
motion_values = []

def LinearMapping(val, in_min, in_max, out_min, out_max):
    val = float(max(in_min, min(in_max, val)))
    # print('a', val)
    val = val - in_min
    # print('b', val)
    val = val / (in_max - in_min)
    # print('c', val)
    return out_min + val * (out_max - out_min)

def RoutineCurves(image_file, bgr, box):
    # print(image_file)
    dt = image_file.replace('.jpg', '').replace('downloaded/', '').replace('_', '-').split('-')
    # print(dt)
    date = datetime.now()
    date = date.replace(microsecond=0, minute=int(dt[-1]), hour=int(dt[-2]), second=0, year=int(dt[-5]), month=int(dt[-4]), day=int(dt[-3]))
    print(date)
    timediff = date - datetime.fromtimestamp(0)
    minutes = timediff.days * 86400 / 60 + timediff.seconds / 60
    # print('timediff', timediff)
    # print('minutes', minutes)
    minutes_since_epoch.append(minutes)

    curve_alpha = 1.0
    if len(minutes_since_epoch) > 1:
        minutes_since_previous = minutes_since_epoch[-1] - minutes_since_epoch[-2]
        # print('minutes_since_previous', minutes_since_previous)
        curve_alpha = LinearMapping(minutes_since_previous, 60, 60 * 24, 0.05, 1.0)
    # print('curve_alpha', curve_alpha)

    hires = bgr

    bgr,hsv = ResizeBlur(bgr, 0.5, 5)

    # for motion detection
    motion_bgr = Resize(bgr, 0.2)
    motion_bgr = MedianBlurred(motion_bgr, 33)
    UpdateWindow('motion_bgr', motion_bgr)
    global previous
    try:
        previous
    except:
        previous = motion_bgr
    motion = cv2.absdiff(motion_bgr, previous)
    motion = BGRToGray(motion)
    ret,motion = cv2.threshold(motion, 20, 20, cv2.THRESH_TOZERO)
    UpdateWindow('motion', motion)
    motion_value = int(cv2.mean(motion)[0])
    motion_value = motion_value * motion_value / 8
    if motion_value > 255:
        print(motion_value)
        motion_value = 255
    motion_values.append(motion_value)
    # print(motion_value)
    previous = motion_bgr
    # end of motion detection

    bright = FrameBrightness(bgr)
    if False:  # len(brightness) > 0:
        brightness.append(bright * curve_alpha + (1.0 - curve_alpha) * brightness[-1])
    else:
        brightness.append(bright)

    if len(measurements) == 0:
        default_mean,default_std = FindDominantTone(hsv)
        # PrintStats('dom', default_mean, default_std)
        SaveColorStats(default_mean, default_std, tone_filename)

    read_mean,read_std = LoadColorStats(tone_filename)
    # PrintStats('rea', read_mean, read_std)

    dom_mean, dom_std = FindDominantTone(hsv)
    # PrintStats('dom', dom_mean, dom_std)

    alpha = 0.9
    read_mean = read_mean * alpha + dom_mean * (1.0 - alpha)
    read_std = read_std * alpha + dom_std * (1.0 - alpha)

    # PrintStats('med', read_mean, read_std)
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
    if 'noir-doublecalib' in image_file or'visible-doublecalib' in image_file or 'blueshift-doublecalib' in image_file or 'redshift-sanbiagio1' in image_file or 'noir-sanbiagio1' in image_file:  # algae
        print('removing algae')
        algae = DistanceFromToneBlurTopBottom(hsv, "alga.pkl", 1, 1, 1, 255, 10.0)
        UpdateWindow('algae', algae)
        saturation = cv2.addWeighted(saturation, 1.0, algae, -0.5, 0.0)  # or -1.0?
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

    uniformity_mask = Resize(saturation, 0.1)
    ret,uniformity_mask = cv2.threshold(uniformity_mask, 100, 255, cv2.THRESH_BINARY)  # Otsu doesn't help here
    UpdateWindow('before canny', uniformity_mask)
    uniformity_mask = cv2.Canny(uniformity_mask, 200, 200)
    uniformity_value,ignore = cv2.meanStdDev(uniformity_mask)
    uniformity_value = 200 - uniformity_value
    if len(uniformity) > 0:
        uniformity.append(uniformity_value * curve_alpha + (1.0 - curve_alpha) * uniformity[-1])
    else:
        uniformity.append(uniformity_value)
    UpdateWindow('uniformity_mask', uniformity_mask)

    biomass = AppendMeasurementJitter(dist, measurements, jitter, alpha=0.1)

    h.append(read_mean[0])
    s.append(read_mean[1])
    v.append(read_mean[2])

    UpdateToneStats(dist, hsv, read_mean, read_std, tone_filename, alpha=curve_alpha)

    DrawChart(foreground, minutes_since_epoch, motion_values, color=(0, 0, 0), bars=True)
    DrawChart(foreground, minutes_since_epoch, brightness, color=(0, 255, 255))
    DrawChart(foreground, minutes_since_epoch, uniformity, color=(0, 140, 255))
    DrawChart(foreground, minutes_since_epoch, topped_sat_mean, color=(255, 255, 255))  # biomass
    Echo(foreground, dt[0] + ' ' + dt[1] + ' ' + str(date))

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
