import numpy as np

cpdef Segment(unsigned char [:, :, :] image, unsigned char t0, unsigned char t1, unsigned char t2, unsigned char w0, unsigned char w1, unsigned char w2, int threshold):
    h = image.shape[0]
    w = image.shape[1]
    hp = image.shape[0] - 4  # padding to exclude image edges, 4 pixels wide on all sides
    wp = image.shape[1] - 4
    result = np.zeros((h, w), np.uint8)
    for x in range(4, wp):
        for y in range (4, hp):
            d0 = image[y, x, 0] - t0
            d1 = image[y, x, 1] - t1
            d2 = image[y, x, 2] - t2
            if (w0 * d0 * d0 + w1 * d1 * d1 + w2 * d2 * d2) <= threshold:
                result[y, x] = 255
    return result
