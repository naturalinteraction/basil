from vision import *

from datetime import datetime

minutes_since_start = []
topped_sat_mean = []
brightness = []
motion_values = []
substrate = []

'''
VISIBLE-CEPPI
rucola
on 13/3 at 15 find hole above the last yellow points
short, sensor falls

BLUESHIFT-CEPPI
rucola
all OK

NOIR-CEPPI
cavolo rosso (like ravanello but more green, with purple fruits)
change in brightness at the end due to lamps

REDSHIFT-CEPPI
ravanello rosso
short, microgreens cut
investigate changes in brightness

REDSHIFT-HAWK
cavolo rosso
investigate irregularity
biomass goes down at the end

BLUESHIFT-HAWK
crescione
investigate irregularity

VISIBLE-HAWK
chia
white overfitting?

NOIR-HAWK
crescione
investigate irregularity

REDSHIFT-APRILE
cavolo rosso

BLUESHIFT-APRILE
ravanello rosso

NOIR-APRILE
chia

VISIBLE-APRILE
senape (like rucola)
'''

def RoutineCurves(image_file, bgr, box):
    dt = image_file.replace('.jpg', '').replace('downloaded/', '').replace('_', '-').split('-')
    date = datetime.now()
    date = date.replace(microsecond=0, minute=int(dt[-1]), hour=int(dt[-2]), second=0, year=int(dt[-5]), month=int(dt[-4]), day=int(dt[-3]))
    print(date)

    global batch_start  # not to be confused with globa.batch_start in cap.py
    try:
        batch_start
    except:
        batch_start = ExifBatchStart(image_file)
    if batch_start > -1:
        timediff = date - datetime.fromtimestamp(batch_start)
    else:
        batch_start = time.mktime(date.timetuple())
        timediff = date - date
    minutes = timediff.days * 86400 / 60 + timediff.seconds / 60
    minutes_since_start.append(minutes)
    print('minutes', locals()['minutes'])
    print('batch_start', time.ctime(batch_start))
    print('this image taken at', time.ctime(batch_start + minutes * 60))

    hires = bgr
    bgr,hsv = ResizeBlur(bgr, 0.5, 5)

    # motion detection
    motion_bgr = Resize(bgr, 0.2)
    motion_bgr = MedianBlurred(motion_bgr, 33)
    global previous
    try:
        previous
    except:
        previous = motion_bgr
    motion = cv2.absdiff(motion_bgr, previous)
    motion = BGRToGray(motion)
    ret,motion = cv2.threshold(motion, 6, 6, cv2.THRESH_TOZERO)
    motion_value = int(cv2.mean(motion)[0])
    motion_value = motion_value * motion_value / 8
    if motion_value > 255:
        motion_value = 255
    motion_values.append(motion_value)
    previous = motion_bgr
    # end of motion detection

    brightness.append(FrameBrightness(bgr))

    # UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)

    saturation = cv2.split(hsv)[1]

    ret,colorful_mask = cv2.threshold(saturation, 70, 255, cv2.THRESH_BINARY)
    substrate_white = cv2.split(hsv)[2]
    UpdateWindow('colorful_mask', colorful_mask)
    ret,substrate_mask = cv2.threshold(substrate_white, 200, 255, cv2.THRESH_BINARY)
    substrate_mask = cv2.addWeighted(substrate_mask, 1.0, colorful_mask, -1.0, 0.0)
    UpdateWindow('substrate_mask', substrate_mask)
    substrate_value = cv2.mean(substrate_mask)[0]
    print(substrate_value)
    substrate.append(substrate_value)

    Normalize(saturation)  # normalization tested: stable ratio of 1.5
    ret,saturation = cv2.threshold(saturation, 170, 170, cv2.THRESH_TRUNC)
    Normalize(saturation)

    if 'noir-ceppi' in image_file or 'redshift-ceppi' in image_file or 'redshift-hawk' in image_file or 'visible-callalta' in image_file or 'blueshift-callalta' in image_file:
        reddish = DistanceFromToneBlurTopBottom(hsv, "colors/reddish.pkl", 1, 1, 1, 240, 10.0)
        UpdateWindow('reddish', reddish)
        bluish = DistanceFromToneBlurTopBottom(hsv, "colors/bluish.pkl", 1, 1, 1, 240, 10.0)
        UpdateWindow('bluish', bluish)
        saturation = cv2.addWeighted(saturation, 1.0, reddish, 0.5, 0.0) 
        saturation = cv2.addWeighted(saturation, 1.0, bluish, 0.5, 0.0)
    if 'noir-doublecalib' in image_file or'visible-doublecalib' in image_file or 'blueshift-doublecalib' in image_file or 'redshift-sanbiagio1' in image_file or 'noir-sanbiagio1' in image_file:  # algae
        print('removing algae')
        algae = DistanceFromToneBlurTopBottom(hsv, "colors/algae.pkl", 1, 1, 1, 255, 10.0)
        UpdateWindow('algae', algae)
        saturation = cv2.addWeighted(saturation, 1.0, algae, -0.5, 0.0)  # or -1.0?
    if '-hawk' in image_file:  # stripe
        print('removing stripe')
        stripe = DistanceFromToneBlurTopBottom(hsv, "colors/stripe.pkl", 1, 1, 1, 255, 10.0)
        UpdateWindow('stripe', stripe)
        saturation = cv2.addWeighted(saturation, 1.0, stripe, -1.0, 0.0)
    Normalize(saturation)
    UpdateWindow('topped normalized saturation', saturation)
    topped_sat_mean.append(cv2.mean(saturation)[0])

    # foreground = cv2.multiply(GrayToBGR(saturation), bgr, scale=1.0/255.0)
    foreground = hires  # bgr
    # UpdateWindow('background', cv2.multiply(GrayToBGR(255 - saturation), bgr, scale=1.0/255.0))

    DrawChart(foreground, minutes_since_start, motion_values, color=(0, 0, 255), bars=True)
    DrawSmoothChart(foreground, minutes_since_start, brightness, color=(0, 255, 255))
    DrawSmoothChart(foreground, minutes_since_start, substrate, color=(255, 0, 0), spline_value=720)  # 480

    parts = 8
    print(len(minutes_since_start))
    for j in range(0, parts):
        j1 = j * len(minutes_since_start) / parts
        j2 = (j + 1) * len(minutes_since_start) / parts
        print(j1, j2)
        DrawSmoothChart(foreground, minutes_since_start[j1:j2], topped_sat_mean[j1:j2], color=(255, 255, 255), spline_value=1240)  # biomass
 
    Echo(foreground, dt[0] + ' ' + dt[1] + ' ' + str(date).replace(':00:00', '.00'))

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')

    SaveTimeSeries(minutes_since_start, topped_sat_mean, 'biomass.pkl')
    SaveTimeSeries(minutes_since_start, motion_values, 'motion.pkl')
