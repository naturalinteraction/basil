from vision import *

measurements = []

def RoutineBieta(image_file, bgr, box):
    print(image_file.replace('.jpg', '').replace('downloaded/', '').replace('_', '-').split('-'))
    # print(image_file)
    
    bgr,hsv = ResizeBlur(bgr, 0.2, 11)

    UpdateWindow('bgr', bgr)

    global previous
    try:
        previous
    except:
        previous = bgr
    motion = cv2.absdiff(bgr, previous)
    motion = BGRToGray(motion)
    ret,motion = cv2.threshold(motion, 20, 20, cv2.THRESH_TOZERO)
    UpdateWindow('motion', motion)
    print(int(cv2.mean(motion)[0]))
    previous = bgr
