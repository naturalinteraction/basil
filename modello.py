from vision import *

locations = []
targetbgr = []

def Red(bgr):
    return float(bgr[2]) / float(bgr[0] + bgr[1] + bgr[2])  # or divided by Luminance() ?

def Green(bgr):
    return float(bgr[1]) / float(bgr[0] + bgr[1] + bgr[2])

def Blue(bgr):
    return float(bgr[0]) / float(bgr[0] + bgr[1] + bgr[2])

def Luminance(bgr):
    return bgr[0] * 0.1140 + bgr[1] * 0.5870 + bgr[2] * 0.2989

def mouseCallbackCalib(event, x, y, flags, param):
    global locations
    global targetbgr
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(locations) < 24:
            print ('X' + str(x) + ' Y' + str(y) + ' ' + str(len(locations)))
            locations.append((x,y))
        if len(locations) == 24:
            with open('calibration-locations.pkl', 'w') as f:
                pickle.dump(locations, f, 0)
                print('saved')
    if event == cv2.EVENT_RBUTTONDOWN:
        locations = []
        print('restarting calibration')
    if event == cv2.EVENT_MBUTTONDOWN:
        if not len(locations) == 24:
            print('finish selecting the 24 locations')
        else:
            diff = []
            for n,(xx, yy) in enumerate(locations):
                c = windows['bgr'][yy,xx].tolist()
                t = targetbgr[n]
                diff.append((Red(c) - Red(t), Green(c) - Green(t), Blue(c) - Blue(t), Luminance(c) - Luminance(t)))
                print(n, diff[-1])
            diff = np.array(diff)
            # print(diff)
            mean = np.mean(np.float32(diff), axis=0)
            print('R', mean[0], 'G', mean[1], 'B', mean[2], 'L', mean[3])

def RoutineModello(image_file, bgr, box):
    global locations
    global targetbgr
    targetbgr = []
    targetbgr.append((68,82,115))  # 0 dark skin
    targetbgr.append((130,150,194))  # 1 light skin
    targetbgr.append((157,122,98))  # 2 blue sky
    targetbgr.append((67,108,87))  # 3 foliage
    targetbgr.append((177,128,133))  # 4 blue flower
    targetbgr.append((170,189,103))  # 5 bluish green
    targetbgr.append((44,126,214))  # 6 orange
    targetbgr.append((166,91,80))  # 7 purplish blue
    targetbgr.append((99,90,193))  # 8 moderate red
    targetbgr.append((108,60,94))  # 9 purple
    targetbgr.append((64,188,157))  # 10 yellow green
    targetbgr.append((46,163,224))  # 11 orange yellow
    targetbgr.append((150,61,56))  # 12 blue
    targetbgr.append((73,148,70))  # 13 green
    targetbgr.append((60,54,175))  # 14 red
    targetbgr.append((31,199,231))  # 15 yellow
    targetbgr.append((149,86,187))  # 16 magenta
    targetbgr.append((161,133,8))  # 17 cyan
    targetbgr.append((242,243,243))  # 18 white 9.5
    targetbgr.append((200,200,200))  # 19 neutral 8
    targetbgr.append((160,160,160))  # 20 neutral 6.5
    targetbgr.append((121,122,122))  # 21 neutral 5
    targetbgr.append((85,85,85))  # 22 neutral 3.5
    targetbgr.append((52,52,52))  # 23 black 2
    try:
        with open('calibration-locations.pkl', 'r') as f:
            locations = pickle.load(f)
            print('loaded')
    except:
        pass
    bgr = Blurred(bgr, 33)
    UpdateWindow('bgr', bgr)
    cv2.setMouseCallback('bgr', mouseCallbackCalib)
