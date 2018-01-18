from vision import *

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    UpdateWindow('bgr', bgr)
    hsv = ToHSV(bgr)
    UpdateWindow('hsv', hsv)

    if False:
        for i in range(2, 8):
            c,result = KMeans(hsv, i)

    compactness,result,means,stddevs = KMeans(hsv, 4, stats=True)
    UpdateWindow('kmeans', result)

    # SaveColorStats(means[3],stddevs[3], 'foglie-kappa.pkl')
    print(LoadColorStats('foglie-kappa.pkl'))
