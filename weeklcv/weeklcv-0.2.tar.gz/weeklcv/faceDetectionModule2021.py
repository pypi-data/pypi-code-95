

import cv2
import os
import time
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt



# Initializing media pipe segmentation class.
mp_selfie_segmentation = mp.solutions.selfie_segmentation

# Setting up Segmentation function.
segment = mp_selfie_segmentation.SelfieSegmentation(0)


class FaceDetector():
    def __init__(self, minDetectionCon=0.5):

        self.minDetectionCon = minDetectionCon
        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = self.mpFaceDetection.FaceDetection(self.minDetectionCon)

    def findFaces(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.faceDetection.process(imgRGB)
        # print(self.results)
        bboxs = []
        if self.results.detections:
            for id, detection in enumerate(self.results.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)
                bboxs.append([id, bbox, detection.score])
                if draw:
                    img = self.fancyDraw(img,bbox)

                    cv2.putText(img, f'Probability={int(detection.score[0] * 100)}%',
                            (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN,2, (255, 0, 255), 2)
        return img, bboxs

    def fancyDraw(self, img, bbox, l=30, t=5, rt= 1):
        x, y, w, h = bbox
        x1, y1 = x + w, y + h

        cv2.rectangle(img, bbox, (255, 0, 255), rt)
        # Top Left  x,y
        cv2.line(img, (x, y), (x + l, y), (255, 0, 255), t)
        cv2.line(img, (x, y), (x, y+l), (255, 0, 255), t)
        # Top Right  x1,y
        cv2.line(img, (x1, y), (x1 - l, y), (255, 0, 255), t)
        cv2.line(img, (x1, y), (x1, y+l), (255, 0, 255), t)
        # Bottom Left  x,y1
        cv2.line(img, (x, y1), (x + l, y1), (255, 0, 255), t)
        cv2.line(img, (x, y1), (x, y1 - l), (255, 0, 255), t)
        # Bottom Right  x1,y1
        cv2.line(img, (x1, y1), (x1 - l, y1), (255, 0, 255), t)
        cv2.line(img, (x1, y1), (x1, y1 - l), (255, 0, 255), t)
        return img

    def make_folder(self, myFolder):
        if not os.path.exists(myFolder):
            os.makedirs(myFolder)
            # print('Creating subfolder: Tim_folder')
            # print('@============ A new sub-folder created for you, sir! =================@')
        return myFolder

    def modifyBackground(self, image, background_image=255, blur=75, threshold=0.75,
                         display=True, method='changeBackground'):
        '''
        This function will replace, blur, desature or make the background transparent depending upon the passed arguments.
        Args:
            image: The input image with an object whose background is required to modify.
            background_image: The new background image for the object in the input image.
            threshold: A threshold value between 0 and 1 which will be used in creating a binary mask of the input image.
            display: A boolean value that is if true the function displays the original input image and the resultant image
                     and returns nothing.
            method: The method name which is required to modify the background of the input image.
        Returns:
            output_image: The image of the object from the input image with a modified background.
            binary_mask_3: A binary mask of the input image.
        '''

        # Convert the input image from BGR to RGB format.
        RGB_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform the segmentation.
        result = segment.process(RGB_img)

        # Get a binary mask having pixel value 1 for the object and 0 for the background.
        # Pixel values greater than the threshold value will become 1 and the remainings will become 0.
        binary_mask = result.segmentation_mask
        # threshold = 0.9

        # Stack the same mask three times to make it a three channel image.
        # binary_mask_3 = np.dstack((binary_mask, binary_mask, binary_mask)) # ## NOT working ???
        binary_mask_3 = np.stack((result.segmentation_mask,) * 3, axis=-1) > threshold

        if method == 'changeBackground':

            # Resize the background image to become equal to the size of the input image.
            background_image = cv2.resize(background_image, (image.shape[1], image.shape[0]))

            # Create an output image with the pixel values from the original sample image at the indexes where the mask have
            # value 1 and replace the other pixel values (where mask have zero) with the new background image.
            output_image = np.where(binary_mask_3, image, background_image)

        elif method == 'blurBackground':

            # Create a blurred copy of the input image.
            blurred_image = cv2.GaussianBlur(image, (blur, blur), 0)

            # Create an output image with the pixel values from the original sample image at the indexes where the mask have
            # value 1 and replace the other pixel values (where mask have zero) with the new background image.
            output_image = np.where(binary_mask_3, image, blurred_image)

        elif method == 'desatureBackground':

            # Create a gray-scale copy of the input image.
            grayscale = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2GRAY)

            # Stack the same grayscale image three times to make it a three channel image.
            grayscale_3 = np.dstack((grayscale, grayscale, grayscale))

            # Create an output image with the pixel values from the original sample image at the indexes where the mask have
            # value 1 and replace the other pixel values (where mask have zero) with the new background image.
            output_image = np.where(binary_mask_3, image, grayscale_3)

        elif method == 'transparentBackground':

            # Stack the input image and the mask image to get a four channel image.
            # Here the mask image will act as an alpha channel.
            # Also multiply the mask with 255 to convert all the 1s into 255.
            # output_image = np.dstack((image, binary_mask * 255)) # ## NOT working
            # Create the output image to have white background where ever black is present in the mask.
            output_image = np.where(binary_mask_3, image, 255)


        else:
            # Display the error message.
            print('Invalid Method')

            # Return
            return

        # Check if the original input image and the resultant image are specified to be displayed.
        if display:

            # Display the original input image and the resultant image.
            plt.figure(figsize=[22, 22])
            plt.subplot(121);
            plt.imshow(image[:, :, ::-1]);
            plt.title("Original Image");
            plt.axis('off');
            plt.subplot(122);
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');
            plt.show()
        # Otherwise
        else:

            # Return the output image and the binary mask.
            # Also convert all the 1s in the mask into 255 and the 0s will remain the same.
            # The mask is returned in case you want to troubleshoot.
            return output_image, (binary_mask_3 * 255).astype('uint8')


def main():
    cap = cv2.VideoCapture(2)
    detector = FaceDetector()

    while True:
        success, img = cap.read()
        img, bboxs = detector.findFaces(img)
        # print(bboxs)
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == 27:
            break
        if key == ord('q'):
            break

if __name__ == "__main__":
    main()