import numpy as np

cpdef Segment(unsigned char [:, :, :] image, unsigned char t0, unsigned char t1, unsigned char t2, char w0, char w1, char w2, int threshold):
    h = image.shape[0]
    w = image.shape[1]
    result = np.zeros((h, w), np.uint8)
    for x in range(w):
        for y in range (h):
            if (w0 * pow(image[y, x, 0] - t0, 2) + w1 * pow(image[y, x, 1] - t1, 2) + w2 * pow(image[y, x, 2] - t2, 2)) <= threshold:
                result[y, x] = 255
    return result
