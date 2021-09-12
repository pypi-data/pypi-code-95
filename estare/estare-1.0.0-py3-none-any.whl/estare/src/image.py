from skimage import img_as_float
from skimage.io import imread, imsave
import numpy as np

# TODO: use class method to define an alternative constructor based on a numpy arrays saved on disk

class Image:
    
    def __init__(self, img_path):
        self.img_path = img_path
        self.img_data = imread(img_path)   # raw image data as an integer-valued array

    def print_info(self):
        """Print out the object type, datatype, and the dimensions of the input object.
        Input: data array of the image which can be of integer or floating point type
        """
        np.set_printoptions(precision=2, linewidth=155)        
        print('Image type: ', type(self.img_data))
        print('Image datatype: ', self.img_data.dtype)
        print('Image shape: ', self.img_data.shape)

    def plot(self, frame_title=None):   
        from matplotlib import pyplot as plt

        gridShow = False
        fig, ax1 = plt.subplots(1, 1)

        # TODO: can we expand imagePath and loop over if it has more than 1 path?
        ax1.imshow(self.img_data)
        ax1.set_title(frame_title, fontsize=14)
        ax1.grid(gridShow)
        plt.show()

    def save(self):
        "save the image data array to disk"
        # TODO: Find the installation path; then cd to data/
        # TODO: use hdf5
        np.save('../data/input_image', self.img_data)   

    def size(self):
        "Return the x and y ranges of the input array, which can be of integer or floating point type"
        x_max = self.img_data.shape[1]
        y_max = self.img_data.shape[0]

        return x_max, y_max


class FloatImage(Image):
    def __init__(self, img_path):
        Image.__init__(self, img_path)
        self.img_data = img_as_float(imread(self.img_path))   # image data as a floating point array

        
class GrayImage(FloatImage):
    def __init__(self, img_path):
        FloatImage.__init__(self, img_path)
        self.img_data = self.img_data @ [0.2126, 0.7152, 0.0722]  # image in gray-scale form

    def plot(self, frame_title=None):   
        from matplotlib import pyplot as plt

        gridShow = False
        fig, ax1 = plt.subplots(1, 1)

        # TODO: can we expand imagePath and loop over if it has more than 1 path?
        ax1.imshow(self.img_data, cmap='gray')
        ax1.set_title(frame_title, fontsize=14)
        ax1.grid(gridShow)
        plt.show()
        
    def extract(self, xRng=[0, 1], yRng=[0, 1], kapa=1.0):
        from copy import copy
        # Lower- and upper bounds for clipping the x-range
        xLB = xRng[0]
        xUB = xRng[1]

        # Lower- and upper bounds for clipping the yx-range
        yLB = yRng[0]
        yUB = yRng[1]
    
        # Clip the raw image into the region of interest
        imgClip = copy(self.img_data)

        # Find and count the pixels with maximum luminousity
        position = np.where(imgClip >= kapa)
        featureCount = position[1].size

        if featureCount > 0:
            for pair_0, pair_1 in zip(position[0], position[1]):
                if pair_0 > 3 and pair_1 > 3:
                    imgClip[pair_0-4:pair_0+4, pair_1-4:pair_1+4] = 0

        return featureCount, position, imgClip


    
image_path = '../tests/beam_0.jpg'
img = Image(image_path)

print(img.img_data[0:5, 0, 0])

img.print_info()

###img.plot(frame_title='Raw image')

x_range, y_range = img.size()
print(x_range, y_range)


imgFloat = FloatImage(image_path)
print(imgFloat.img_data[0:5, 0, 0])

imgFloat.print_info()

###imgFloat.plot(frame_title='Float image')

x_range, y_range = imgFloat.size()
print(x_range, y_range)


imgGray = GrayImage(image_path)
print(imgGray.img_data[0:5, 0])

imgGray.print_info()

###imgGray.plot(frame_title='Gray image')

x_range, y_range = imgGray.size()
print(x_range, y_range)

numFeatures, indices, markers = imgGray.extract(xRng=[0, x_range], yRng=[0, y_range],
                                                kapa=0.9998)

print(f'''
        Total number of features detected: {numFeatures}. If this is too many, consider increasing  
        the threshold input.
    ''')
#print(img.__dict__)



print('Done')
        
