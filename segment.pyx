cpdef unsigned char [:, :, :] segment(unsigned char [:, :, :] image):
    h = image.shape[0]
    w = image.shape[1]
    for x in range(w):
        for y in range (h):
            if (image[y, x, 1] - image[y, x, 0] - image[y, x, 2]) < 2:
                image[y, x, 0] = 255
                image[y, x, 1] = 0
                image[y, x, 2] = 0
    return image

