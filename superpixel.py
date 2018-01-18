# import the necessary packages
from skimage.segmentation import *
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io
import matplotlib.pyplot as plt
from vision import *

# load the image and convert it to a floating point data type
#image = img_as_float(io.imread('downloaded/test-test_2560x1920_2000_01_30-00_00.jpg'))
image = img_as_float(io.imread('downloaded/blueshift-sanbiagio1_2560x1920_2018_01_18-17_00.jpg'))
image = Resize(image, 0.2)
print('fz')
segments = felzenszwalb(image, scale=100, sigma=0.5, min_size=50)
print('quick')
#segments = quickshift(image, kernel_size=5, max_dist=16, ratio=0.5)
print(segments.shape)
# show the output
fig = plt.figure("Superpixels")
ax = fig.add_subplot(1, 1, 1)
ax.imshow(mark_boundaries(image, segments))
plt.axis("off")

UpdateWindow("segments", np.uint8(segments))
ProcessKeystrokes()
# show the plots
plt.show()

