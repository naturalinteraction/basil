cpdef int segment_linear(unsigned char [:, :, :] image, char w0, char w1, char w2, int threshold, int minimum_brightness):
    h = image.shape[0]
    w = image.shape[1]
    count = 0
    c1 = 0
    c2 = 0
    c3 = 0
    for x in range(w):
        for y in range (h):
            if (w0 * image[y, x, 0] + w1 * image[y, x, 1] + w2 * image[y, x, 2]) < threshold or (image[y, x, 0] + image[y, x, 1] + image[y, x, 2] < 3 * minimum_brightness):
                image[y, x, 0] = 0
                image[y, x, 1] = 0
                image[y, x, 2] = 0
            else:
                c1 += image[y, x, 0]
                c2 += image[y, x, 1]
                c3 += image[y, x, 2]
                image[y, x, 0] = 255
                image[y, x, 1] = 255
                image[y, x, 2] = 255
                count += 1
    print(str(c1/count))
    print(str(c2/count))
    print(str(c3/count))
    return count

cpdef int segment_target(unsigned char [:, :, :] image, unsigned char t0, unsigned char t1, unsigned char t2, char w0, char w1, char w2, int threshold):
    h = image.shape[0]
    w = image.shape[1]
    count = 0
    c1 = 0
    c2 = 0
    c3 = 0
    for x in range(w):
        for y in range (h):
            if (w0 * pow(image[y, x, 0] - t0, 2) + w1 * pow(image[y, x, 1] - t1, 2) + w2 * pow(image[y, x, 2] - t2, 2)) > threshold:
                image[y, x, 0] = 0
                image[y, x, 1] = 0
                image[y, x, 2] = 0
            else:
                c1 += image[y, x, 0]
                c2 += image[y, x, 1]
                c3 += image[y, x, 2]
                image[y, x, 0] = 255
                image[y, x, 1] = 255
                image[y, x, 2] = 255
                count += 1
    print(str(c1/count))
    print(str(c2/count))
    print(str(c3/count))
    return count
