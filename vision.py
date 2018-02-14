from __future__ import print_function  # provides Python 3's print() with end=''
import cv2
import numpy as np
from utility import *
from segment import *
from collections import namedtuple
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pymeanshift as pms
from skimage.segmentation import *
from skimage import color
from skimage.future import graph


white = (255, 255, 255)


def DistanceFromToneBlurTopBottom(hsv, tone_filename, dilate_kernel, erode_kernel, blur_size, top, multiplicator):
    dist = DistanceFromTone(hsv, tone_filename)
    dist = Dilate(dist, kernel_size=dilate_kernel, iterations=1)
    dist = Erode(dist, kernel_size=erode_kernel, iterations=1)
    dist = MedianBlurred(dist, size=blur_size)
    dist = TruncateAndZero(dist, 255, 1, 255 - top, 1000)
    dist = 255 - dist
    dist = cv2.addWeighted(dist, multiplicator, dist, 0.0, 0.0)
    return 255 - dist

def ResizeBlur(bgr, resize_factor, blur_size):
    bgr = Resize(bgr, resize_factor)
    hsv = ToHSV(bgr)
    hsv = MedianBlurred(hsv, size=blur_size)
    return bgr,hsv

def DrawChart(foreground, measurements):
    h,w = foreground.shape[:2]
    for i in range(1, len(measurements)):
        baseline = measurements[0]
        last = measurements[i] - baseline
        previous = measurements[i - 1] - baseline
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9 - 150)), (i * 10 + 50, int(h - last * 9 - 150)), (255, 255, 255), 3)

def AppendMeasurementJitter(dist, measurements, jitter):
    biomass = cv2.mean(dist)[0]
    if len(measurements) > 1:
        smooth_biomass = 0.5 * biomass + 0.5 * measurements[-1]
        predicted_biomass = smooth_biomass + (measurements[-2] -smooth_biomass)
        jitter.append(biomass - predicted_biomass)
        biomass = smooth_biomass
        jit = np.std(jitter)
        print('jitter %.3f' % (jit))
    measurements.append(biomass)
    return biomass

def UpdateToneStats(dist, hsv, previous_mean, previous_std, filename, min_distance=254):
    ret,mask = cv2.threshold(dist, min_distance, 255, cv2.THRESH_BINARY)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    for i in range(3):
        mean_biomass[i] = 0.1 * mean_biomass[i] + 0.9 * previous_mean[i]
        stddev_biomass[i] = 0.1 * stddev_biomass[i] + 0.9 * previous_std[i]
    SaveColorStats(mean_biomass, stddev_biomass, filename)

def FindDominantTone(hsv):
    s = cv2.split(hsv)[1]
    # UpdateWindow('FindDominantTone saturation', s)
    ret,mask = cv2.threshold(s, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    # UpdateWindow('FindDominantTone mask', mask)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    # print(mean_biomass, stddev_biomass)
    return mean_biomass, stddev_biomass

def SimilarityToReference(channel, value):
    reference = np.zeros(channel.shape, np.uint8)
    reference[:] = round(value)
    return 255 - cv2.absdiff(reference, channel)

def Normalize(channel):
    cv2.normalize(channel, channel, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

def TruncateAndZero(channel, reference, sigma, trunc_sigmas, zero_sigmas, normalize=True):
    ret,result = cv2.threshold(channel, reference - trunc_sigmas * sigma, reference - trunc_sigmas * sigma, cv2.THRESH_TRUNC)
    ret,result = cv2.threshold(result,  reference -  zero_sigmas * sigma, reference -  zero_sigmas * sigma, cv2.THRESH_TOZERO)
    if normalize:
        Normalize(result)
    return result


def ScatterPlotHSV(image, title='HSV'):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    small = cv2.resize(image, (0, 0), fx=0.01, fy=0.01)
    height, width, depth = small.shape
    for x in range(0, width):
       for y in range (0, height):
           col = small[y, x]
           ax.scatter(col[0], col[1], col[2], c='#%02x%02x%02x' % (col[2], col[1], col[0]))  # BGR >>> RGB
    ax.set_xlabel('H')
    ax.set_ylabel('S')
    ax.set_zlabel('V')
    plt.gcf().canvas.set_window_title(title)
    plt.show()


def SaturationThreshold(hsv, threshold, min_value=-1):
    s = cv2.split(hsv)[1]
    ret,thresholded = cv2.threshold(s,threshold,255,cv2.THRESH_BINARY)
    if min_value > -1:
        v = cv2.split(hsv)[2]
        ret,v_thresholded = cv2.threshold(v,min_value,255,cv2.THRESH_BINARY)
        thresholded = cv2.multiply(thresholded, v_thresholded, scale=1.0/255.0)
    return thresholded


'''
rectangle
'''
rectangle = namedtuple('rectangle', 'xmin ymin xmax ymax')

def rectangle_union(a, b):
    return rectangle(min(a.xmin, b.xmin), min(a.ymin, b.ymin), max(a.xmax, b.xmax), max(a.ymax, b.ymax))


'''
blurs
'''
def GaussianBlurred(image, size=3):
    return cv2.GaussianBlur(image, (size, size), 0)

def Blurred(image, size=3):
    return cv2.blur(image, (size, size))

def MedianBlurred(image, size=3):
    return cv2.medianBlur(image, size)  # supposed to be good against salt-and-pepper noise


'''
image derivatives
'''
def ComputeImageDerivative(for_derivation, mask=None):
    # laplacian = cv2.Laplacian(for_derivation, cv2.CV_64F)
    mult = 5
    if False:
        sobelx = cv2.Sobel(for_derivation, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(for_derivation, cv2.CV_64F, 0, 1, ksize=3)
    else:
        sobelx = cv2.Scharr(for_derivation, cv2.CV_64F, 1, 0)
        sobely = cv2.Scharr(for_derivation, cv2.CV_64F, 0, 1)
        mult = 1.3
    if False:
        abs_sobelx = np.absolute(sobelx)
        abs_sobely = np.absolute(sobely)
        abs_sobelx = np.uint8(abs_sobelx)
        abs_sobely = np.uint8(abs_sobely)
    else:
        abs_sobelx = cv2.convertScaleAbs(sobelx)
        abs_sobely = cv2.convertScaleAbs(sobely)
    sobel = cv2.addWeighted(abs_sobelx, 0.5 * mult, abs_sobely, 0.5 * mult, 0.0)
    sobel = cv2.bitwise_and(sobel, sobel, mask=mask)
    return sobel

def Echo(image, string):
    h,w = image.shape[:2]
    cv2.putText(image, str(string), (50, h - h / 10), cv2.FONT_HERSHEY_SIMPLEX, h / 300, (255, 255, 255), h / 150, cv2.LINE_AA)

def Histogram(channel, output):
    hist = cv2.calcHist([channel], [0], None, [64], [1,256])
    max_hist = max(hist)
    for i in range(len(hist)):
        cv2.line(output, (i * 30, 1000), (i * 30, 1000 - hist[i] * 1000 / max_hist), (0, 255, 255), 30)


def rag_weight_mean_color(graph, src, dst, n):
    diff = graph.node[dst]['mean color'] - graph.node[n]['mean color']
    diff = np.linalg.norm(diff)
    return {'weight': diff}

def rag_merge_mean_color(graph, src, dst):
    graph.node[dst]['total color'] += graph.node[src]['total color']
    graph.node[dst]['pixel count'] += graph.node[src]['pixel count']
    graph.node[dst]['mean color'] = (graph.node[dst]['total color'] /
                                     graph.node[dst]['pixel count'])

# spatial_radius    1 to 6 (integer) small numbers --> faster, more clusters, finer spatial resolution (?)
# range_radius      1.0 to 6.0 (float) somewhat related to the above radius, equal or smaller, seldomly up to x1.2
# min_density       10 to 300 the smaller the more it preserves fine details
# common combinations include 2,2,20 and 6,4.5,50
def MeanShift(image, spatial_radius, range_radius, min_density):
    return pms.segment(image, spatial_radius, range_radius, min_density)  # returns (segmented_image, labels_image, number_regions)

# works on reduced image to 20% on both axes, works on BGR and HSV, returns different sets of data whether stats is True
def KMeans(img, K, stats=False):
    pixels = img.reshape((-1,3))
    Z = np.float32(pixels)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    compactness,label,center=cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape(img.shape)
    if not stats:
        print('K=' + str(K) + ' compactness=' + str(compactness))
        return compactness,result
    means = []
    stddevs = []
    pixel_lists = {}
    for n in range(0, K):
        pixel_lists[n] = []
    for n,p in enumerate(pixels):
        l = label[n]
        pixel_lists[l[0]].append(p)
    for n in range(0, K):
        mean = np.mean(np.float32(pixel_lists[n]), axis=0)
        stddev = np.std(np.float32(pixel_lists[n]), axis=0)
        # print(str(n) + ' ' + str(mean) + ' ' + str(stddev))
        means.append(mean)
        stddevs.append(stddev)
    return compactness,result,label.reshape(img.shape[:2]),means,stddevs

def Superpixel(image):
    segments = felzenszwalb(image, scale=20, sigma=0.2, min_size=5)  # was 100 0.5 50
    # segments = quickshift(image, kernel_size=5, max_dist=16, ratio=0.5)
    h,w = image.shape[:2]
    means = []
    stddevs = []
    pixel_lists = {}
    for n in range(0, np.max(segments) + 1):
        pixel_lists[n] = []
    for x in range(0, w):
        for y in range(0, h):
            pixel_lists[segments[y][x]].append(image[y][x])
    for n in range(0, len(pixel_lists)):
        mean = np.mean(np.float32(pixel_lists[n]), axis=0)
        stddev = np.std(np.float32(pixel_lists[n]), axis=0)
        # print('' + str(n) + ' ' + str(mean) + ' ' + str(stddev))
        means.append(mean)
        stddevs.append(stddev)
    result = np.uint8(means)[segments.flatten()]
    result = result.reshape(image.shape)
    return result,segments,means,stddevs

def Slic(image):
    labels = slic(image, compactness=5, n_segments=2000, slic_zero=True)
    out = color.label2rgb(labels, image, kind='avg')
    return out,labels


def Resize(image, factor):
    return cv2.resize(image, (0, 0), fx=factor, fy=factor)

def CropImage(image, top=0, bottom=0, left=0, right=0, cropname=None):
    height, width, depth = image.shape
    if (cropname == 'redshift'):  # redshift: alfalfa (verde salvia) (che su internet e' 126,149,125)
        top = 550
        bottom = 0
        left = 0
        right = 0
    if (cropname == 'noir'):  # noir: alfalfa (verde salvia) (che su internet e' 126,149,125)
        top = 50
        bottom = 280
        left = 0
        right = 250
    if (cropname == 'blueshift'):  # blueshift: pianta kappa
        top = 120
        bottom = 0
        left = 0
        right = 0
    if (cropname == 'visible'):  # visible
        top = 330
        bottom = 180
        left = 0
        right = 0
    if (cropname == 'rucola'):  # visible upper left rucola
        top = 330
        bottom = 1170
        left = 0
        right = 1560
    if (cropname == 'basilicorosso'):  # visible lower left basilico rosso (sul blu/viola)
        top = 830
        bottom = 0
        left = 0
        right = 1800
    if (cropname == 'bieta'):  # visible upper right bieta
        top = 330
        bottom = 1200
        left = 1000
        right = 200
    if (cropname == 'bataviarossa'):  # visible lower right batavia rossa (sul rosso)
        top = 850
        bottom = 160
        left = 1000
        right = 0
    return image[top:height-bottom, left:width-right]

# kernel_size 3, 5, 7, 9, 11 ...
def Erode(input, kernel_size=3, iterations=1):
    return cv2.erode(input, np.ones((kernel_size, kernel_size), np.uint8), iterations)

# kernel_size 3, 5, 7, 9, 11 ...
def Dilate(input, kernel_size=3, iterations=1):
    return cv2.dilate(input, np.ones((kernel_size, kernel_size), np.uint8), iterations)

def ImageWithColor(image_for_shape, color):
    image = np.zeros(image_for_shape.shape[:], np.uint8)
    image[:] = color
    return image

def ComputeStatsOfMaskedImage(image, mask):
    mean,stddev = cv2.meanStdDev(image, mask=mask)
    return (float(mean[0]), float(mean[1]), float(mean[2])),(float(stddev[0]), float(stddev[1]), float(stddev[2]))

def ToHSV(bgr_image):
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

def BGRToGray(bgr_image):
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

def GrayToBGR(one_channel_image):
    return cv2.cvtColor(one_channel_image, cv2.COLOR_GRAY2BGR)

def Inverted(image):
    return 255 - image

def MaskedImage(image, mask):
    return cv2.bitwise_and(image, image, mask=mask)

def MaskForTone(image, filename, threshold):
    mean,stddev = LoadColorStats(filename)
    variance = stddev ** 2
    return SegmentBiomass(image, mean, 1.0 / variance, threshold)

def DistanceFromTone(image, filename):
    mean,stddev = LoadColorStats(filename)
    variance = stddev ** 2
    return SegmentBiomassNoThreshold(image, mean, 1.0 / variance)

def CompareLabels(labels, ground_truth, result, name):
    h,w = labels.shape
    means = []
    pixel_lists = {}
    label_count = np.max(labels)
    for n in range(0, label_count + 1):
        pixel_lists[n] = []
    for x in range(0, w):
        for y in range(0, h):
            pixel_lists[labels[y][x]].append(ground_truth[y][x])
    error = 0.0
    for n in range(0, len(pixel_lists)):
        count = len(pixel_lists[n])
        if count > 0:
            mean = np.mean(np.float32(pixel_lists[n]), axis=0)
        else:
            mean = 0.0
            print('no mean possible')
        if mean > 127:
            error = error + count * (255 - mean)
        else:
            error = error + count * mean
    error = error / 255
    for t in range(14, 15):
        mask = MaskForTone(result, 'foglie-kappa.pkl', t)
        diff = cv2.absdiff(mask, ground_truth)
        diff_mean = cv2.mean(diff)[0]
    UpdateWindow(name, result)
    print(name + ' bins=' + str(len(pixel_lists)) + ' error=' + str(int(error)) + ' diff=' + str(diff_mean))

def PurgePalette(filename, label):
    with open(filename, 'r') as f:
        (means,stddevs,good,bad) = pickle.load(f)
    try:
        good.remove(label)
        bad.add(label)
    except:
        pass
    with open(filename, 'w') as f:
        pickle.dump((means,stddevs,good,bad), f, 0)

def GrowPalette(filename, label):
    with open(filename, 'r') as f:
        (means,stddevs,good,bad) = pickle.load(f)
    try:
        bad.remove(label)
        good.add(label)
    except:
        pass
    with open(filename, 'w') as f:
        pickle.dump((means,stddevs,good,bad), f, 0)

def EnablePaletteCreator(bgr, hsv, bins=16):
    UpdateWindow('bgr', bgr)
    compactness,result,labels,means,stddevs = KMeans(hsv, bins, stats=True)
    for i,m in enumerate(means):
        print(i, m)
    UpdateWindow('labels', labels)
    SetMouseMeansDevsLabels(means, stddevs, labels)

def SegmentGoodPalette(image, filename, threshold, debug=False):
    with open(filename, 'r') as f:
        (means,stddevs,good,bad) = pickle.load(f)
    mask = np.zeros(image.shape[:2], np.uint8)
    if debug:
        print(good)
        for i,m in enumerate(means):
            print(i, m)
    for i in range(0, len(means)):
        if i in good:
            temp_mask = SegmentBiomass(image, means[i], 1.0 / (stddevs[i] ** 2), threshold)
            if debug:
                # print(i, means[i])
                UpdateWindow(str(i), temp_mask)
            mask = mask + temp_mask
    return mask

def SegmentBiomass(hsv_image, target,
                              weight, segmentation_threshold):
    return         Segment(hsv_image,  target[0],
                                       target[1],
                                       target[2],
                                       weight[0],
                                       weight[1],
                                       weight[2],
                                       segmentation_threshold)

def SegmentBiomassNoThreshold(hsv_image, target,
                              weight):
    return         SegmentNoThreshold(hsv_image,  target[0],
                                       target[1],
                                       target[2],
                                       weight[0],
                                       weight[1],
                                       weight[2])

def FillHoles(biomass_mask, hsv, target, stddev, segmentation_threshold, max_area=30 * 30, greater_than=False):
    weight = 1.0 / (stddev ** 2)
    ignored, contours, hierarchy = cv2.findContours(biomass_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    accepted_holes_mask = np.zeros(hsv.shape[:2], np.uint8)
    refused_holes_mask = np.zeros(hsv.shape[:2], np.uint8)
    circles = list()
    # cs = ColorStatistics()
    for index,cnt in enumerate(contours):
        # print(ContourStats(cnt))
        if hierarchy[0][index][3] >= 0 and cv2.contourArea(cnt) <= max_area:
            hole_mask = np.zeros(hsv.shape[:2], np.uint8)
            cv2.drawContours(hole_mask, [cnt], -1, 255, -1)
            mean = cv2.mean(hsv, mask=hole_mask)[0:3]
            color_distance = (mean[0] - target[0]) ** 2 * weight[0] +  \
                             (mean[1] - target[1]) ** 2 * weight[1] +  \
                             (mean[2] - target[2]) ** 2 * weight[2]

            if ((not greater_than) and color_distance <= segmentation_threshold) or (greater_than and color_distance > segmentation_threshold):
                # cs.Update(mean)
                cv2.fillPoly(biomass_mask, pts = [cnt], color=(255))
                cv2.fillPoly(accepted_holes_mask, pts = [cnt], color=(255))
                # print(" area " + str(cv2.contourArea(cnt)) + ' dist ' + str(color_distance) + ' mean ' + str(mean))
                circles.append(cv2.minEnclosingCircle(cnt))
            else:
                cv2.fillPoly(refused_holes_mask, pts = [cnt], color=(255))
                # print("REFUSED  area " + str(cv2.contourArea(cnt)) + ' dist ' + str(color_distance) + ' mean ' + str(mean))
    # print(cs.ComputeStats())
    return accepted_holes_mask,refused_holes_mask,circles


class BoundingBox:
    rect = None

    def Reset(self):
        self.rect = None

    def Update(self, biomass_mask, output_image=False):
        nonzero = cv2.findNonZero(biomass_mask)
        if not(nonzero is None):
            count = len(nonzero)
            # print(('biomass count ' + str(count)))
            bbx,bby,bbw,bbh = cv2.boundingRect(nonzero)
            current_rect = rectangle(int(bbx), int(bby), int(bbx + bbw), int(bby + bbh))
            if self.rect == None:
                self.rect = current_rect
                # print('initializing', self.rect)
            # else:
            #     print('valid', self.rect)
            self.rect = rectangle_union(self.rect, current_rect)
            if output_image.__class__.__name__ == 'ndarray':
                cv2.rectangle(output_image, (self.rect.xmin, self.rect.ymin),
                                            (self.rect.xmax, self.rect.ymax), white, 2)
            return count
        else:
            return 0


def ContourStats(cnt):
    area = cv2.contourArea(cnt)
    x,y,w,h = cv2.boundingRect(cnt)
    rect_area = w * h
    if rect_area > 0:
        extent = float(area) / rect_area
    else:
      extent = 0
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    if hull_area > 0:
        solidity = float(area) / hull_area
    else:
        solidity = 0
    perimeter = cv2.arcLength(cnt, True)
    if perimeter > 0:
        jaggedness = len(cnt) / perimeter
    else:
        jaggedness = 0
    return area,extent,solidity,jaggedness

def DrawEllipses(image, ellipses, color):
    for e in ellipses:
        center,axes,angle = e
        center = (int(center[0]), int(center[1]))
        axes = (int(axes[0] * 0.5 + 4), int(axes[1] * 0.5 + 4))
        cv2.ellipse(image, center, axes, angle, 0.0, 360.0, color, 1)

def DrawCircles(image, circles, color):
    for c in circles:
        center,radius = c
        cv2.circle(image, (int(center[0]), int(center[1])), int(radius) + 4, color, 1)
