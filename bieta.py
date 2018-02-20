from vision import *

measurements = []

def RoutineBieta(image_file, bgr, box):
    print(image_file.replace('.jpg', '').replace('downloaded/', '').replace('_', '-').split('-'))
    # print(image_file)
    
    bgr,hsv = ResizeBlur(bgr, 0.5, 33)

    UpdateWindow('bgr', bgr)

    global previous
    try:
        previous
    except:
        previous = bgr
    motion = cv2.absdiff(bgr, previous)
    UpdateWindow('motion', motion)
    print(int(cv2.mean(BGRToGray(motion))[0]))
    previous = bgr
