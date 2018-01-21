import numpy as np
import pickle

cpdef Segment(unsigned char [:, :, :] image, float t0, float t1, float t2,
                                             float w0, float w1, float w2, int threshold):
    h = image.shape[0]
    w = image.shape[1]
    hp = image.shape[0] - 4  # padding to exclude image edges, 4 pixels wide on all sides
    wp = image.shape[1] - 4
    # print(t0, t1, t2, w0, w1, w2)
    result = np.zeros((h, w), np.uint8)
    for x in range(4, wp):
        for y in range (4, hp):
            if (w0 * (image[y, x, 0] - t0) ** 2 + w1 * (image[y, x, 1] - t1) ** 2 + w2 * (image[y, x, 2] - t2) ** 2) <= threshold:
                result[y, x] = 255
    return result


cpdef SegmentWithMask(unsigned char [:, :, :] image, float t0, float t1, float t2,
                                                     float w0, float w1, float w2, int threshold, unsigned char [:, :] mask):
        h = image.shape[0]
        w = image.shape[1]
        hp = image.shape[0] - 4  # padding to exclude image edges, 4 pixels wide on all sides
        wp = image.shape[1] - 4
        # print(t0, t1, t2, w0, w1, w2)
        result = np.zeros((h, w), np.uint8)
        for x in range(4, wp):
            for y in range (4, hp):
                if (mask[y, x]):
                    if (w0 * (image[y, x, 0] - t0) ** 2 + w1 * (image[y, x, 1] - t1) ** 2 + w2 * (image[y, x, 2] - t2) ** 2) <= threshold:
                        result[y, x] = 255
        return result



cpdef SegmentWithPalette(unsigned char [:, :, :] image, filename):
    with open(filename, 'r') as f:
        (means,stddevs,good,bad) = pickle.load(f)
    goodness = []
    colors = len(means)
    for i in range(0, colors):
        goodness.append(i in good)
        stddevs[i] = 1.0 / stddevs[i]
    h = image.shape[0]
    w = image.shape[1]
    result = np.zeros((h, w), np.uint8)
    for x in range(0, w):
        for y in range (0, h):
            best = -1
            best_dist = 1000000000
            dist = 0
            im = image[y, x]
            for i in range(0, colors):
                dist = stddevs[i] * abs(im - means[i])
                dist = sum(dist)
                if dist < best_dist:
                    best_dist = dist
                    best = i
            if goodness[best] == True:
                result[y, x] = 255
    return result
