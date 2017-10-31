def segment(image):
    h = image.shape[0]
    w = image.shape[1]
    x, y = 0, 0
    while x < w:
        while y < h:
            greenness = + image.item(y, x, 1)  \
                        - image.item(y, x, 0)  \
                        - image.item(y, x, 2)
            if greenness < 0.0:
                image.itemset((y, x, 0), 255)
                image.itemset((y, x, 1), 0)
                image.itemset((y, x, 2), 0)
            y += 1
        y = 0
        x += 1

