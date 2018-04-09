from vision import *

from datetime import datetime

smooth_curves = False

minutes_since_epoch = []
topped_sat_mean = []
brightness = []
motion_values = []
substrate = []

'''
VISIBLE-CEPPI
short, sensor falls

BLUESHIFT-CEPPI
all OK

NOIR-CEPPI
investigate changes in brightness
ravanello?

REDSHIFT-CEPPI
short, microgreens cut
investigate changes in brightness
ravanello?

REDSHIFT-HAWK
investigate changes in brightness
biomass goes down at the end
ravanello?

BLUESHIFT-HAWK
investigate changes in brightness

VISIBLE-HAWK
investigate changes in brightness
biomass goes down at the end

NOIR-HAWK
investigate changes in brightness
'''

def RoutineCurves(image_file, bgr, box):
    dt = image_file.replace('.jpg', '').replace('downloaded/', '').replace('_', '-').split('-')
    date = datetime.now()
    date = date.replace(microsecond=0, minute=int(dt[-1]), hour=int(dt[-2]), second=0, year=int(dt[-5]), month=int(dt[-4]), day=int(dt[-3]))
    print(date)
    timediff = date - datetime.fromtimestamp(0)
    minutes = timediff.days * 86400 / 60 + timediff.seconds / 60
    minutes_since_epoch.append(minutes)

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

    curve_alpha = 1.0
    if smooth_curves and len(minutes_since_epoch) > 1:
        minutes_since_previous = minutes_since_epoch[-1] - minutes_since_epoch[-2]
        curve_alpha = LinearMapping(minutes_since_previous + motion_value * 7, 60, 60 * 24, 0.1, 1.0)

    bright = FrameBrightness(bgr)
    if False:  # len(brightness) > 0:
        brightness.append(bright * curve_alpha + (1.0 - curve_alpha) * brightness[-1])
    else:
        brightness.append(bright)

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

    if 'noir-ceppi' in image_file or 'redshift-ceppi' in image_file or 'redshift-hawk' in image_file or 'visible-callalta' in image_file or 'blueshift-callalta' in image_file:  # ravanello
        ravanello = DistanceFromToneBlurTopBottom(hsv, "ravanello.pkl", 1, 1, 1, 240, 10.0)
        UpdateWindow('ravanello', ravanello)
        bluastro = DistanceFromToneBlurTopBottom(hsv, "bluastro.pkl", 1, 1, 1, 240, 10.0)
        UpdateWindow('bluastro', bluastro)
        saturation = cv2.addWeighted(saturation, 1.0, ravanello, 0.5, 0.0) 
        saturation = cv2.addWeighted(saturation, 1.0, bluastro, 0.5, 0.0)
    if 'noir-doublecalib' in image_file or'visible-doublecalib' in image_file or 'blueshift-doublecalib' in image_file or 'redshift-sanbiagio1' in image_file or 'noir-sanbiagio1' in image_file:  # algae
        print('removing algae')
        algae = DistanceFromToneBlurTopBottom(hsv, "alga.pkl", 1, 1, 1, 255, 10.0)
        UpdateWindow('algae', algae)
        saturation = cv2.addWeighted(saturation, 1.0, algae, -0.5, 0.0)  # or -1.0?
    if '-hawk' in image_file:  # stripe
        print('removing stripe')
        stripe = DistanceFromToneBlurTopBottom(hsv, "stripe.pkl", 1, 1, 1, 255, 10.0)
        UpdateWindow('stripe', stripe)
        saturation = cv2.addWeighted(saturation, 1.0, stripe, -1.0, 0.0)
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

    DrawChart(foreground, minutes_since_epoch, motion_values, color=(0, 0, 0), bars=True)
    DrawChart(foreground, minutes_since_epoch, substrate, color=(255, 0, 0))
    DrawChart(foreground, minutes_since_epoch, brightness, color=(0, 255, 255))
    DrawChart(foreground, minutes_since_epoch, topped_sat_mean, color=(255, 255, 255))  # biomass
    Echo(foreground, dt[0] + ' ' + dt[1] + ' ' + str(date).replace(':00:00', '.00'))

    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
