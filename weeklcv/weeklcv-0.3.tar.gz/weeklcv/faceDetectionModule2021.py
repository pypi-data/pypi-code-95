

import cv2
import os
import time
import math
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt


# Initializing mediapipe pose class.
mp_pose = mp.solutions.pose

# Setting up the Pose function for image.
# pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2)

# Setup Pose function for video.
pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6, model_complexity=1)

# Initializing media pipe drawing class, useful for annotation.
mp_drawing = mp.solutions.drawing_utils

# It show colorful hands landmarks
mp_drawing_styles = mp.solutions.drawing_styles

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

    def detectPose(image, pose, draw=True, display=True):
        '''
        This function performs pose detection on an image.
        Args:
            image: The input image with a prominent person whose pose landmarks needs to be detected.
            pose: The pose setup function required to perform the pose detection.
            display: A boolean value that is if set to true the function displays the original input image, the resultant image,
                     and the pose landmarks in 3D plot and returns nothing.
        Returns:
            output_image: The input image with the detected pose landmarks drawn.
            landmarks: A list of detected landmarks converted into their original scale.
        '''

        # Create a copy of the input image.
        output_image = image.copy()

        # Convert the image from BGR into RGB format.
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform the Pose Detection.
        results = pose.process(imageRGB)

        # Retrieve the height and width of the input image.
        height, width, _ = image.shape

        # Initialize a list to store the detected landmarks.
        landmarks = []

        # Check if any landmarks are detected.
        if results.pose_landmarks and draw:

            # Draw Pose landmarks on the output image.
            mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                      connections=mp_pose.POSE_CONNECTIONS,
                                      # landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(), #  colorful landmarks.
                                      landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=5,
                                                                                   circle_radius=8),
                                      connection_drawing_spec=mp_drawing.DrawingSpec(color=(49, 125, 237), thickness=5,
                                                                                     circle_radius=2)
                                      )

            # Iterate over the detected landmarks.
            for landmark in results.pose_landmarks.landmark:
                # Append the landmark into the list.
                landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                  (landmark.z * width)))

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

            # Also Plot the Pose landmarks in 3D.
            mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

        # Otherwise
        else:

            # Return the output image and the found landmarks.
            return output_image, landmarks

    def calculateAngle(landmark1, landmark2, landmark3):
        '''
        This function calculates angle between three different landmarks.
        Args:
            landmark1: The first landmark containing the x,y and z coordinates.
            landmark2: The second landmark containing the x,y and z coordinates.
            landmark3: The third landmark containing the x,y and z coordinates.
        Returns:
            angle: The calculated angle between the three landmarks.

        '''

        # Get the required landmarks coordinates.
        x1, y1, _ = landmark1
        x2, y2, _ = landmark2
        x3, y3, _ = landmark3

        # Calculate the angle between the three points
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))

        # Check if the angle is less than zero.
        if angle < 0:
            # Add 360 to the found angle.
            angle += 360

        # Return the calculated angle.
        return angle

    def classifyPose(landmarks, output_image, display=False):
        '''
        This function classifies yoga poses depending upon the angles of various body joints.
        Args:
            landmarks: A list of detected landmarks of the person whose pose needs to be classified.
            output_image: A image of the person with the detected pose landmarks drawn.
            display: A boolean value that is if set to true the function displays the resultant image with the pose label
            written on it and returns nothing.
        Returns:
            output_image: The image with the detected pose landmarks drawn and pose label written.
            label: The classified pose label of the person in the output_image.

        '''

        # Initialize the label of the pose. It is not known at this stage.
        label = 'Unknown Pose'
        font_2 = cv2.FONT_HERSHEY_COMPLEX
        # Specify the color (Red) with which the label will be written on the image.
        color = (0, 0, 255)

        # Calculate the required angles.
        # ----------------------------------------------------------------------------------------------------------------

        # Get the angle between the left shoulder, elbow and wrist points.
        left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])

        # Get the angle between the right shoulder, elbow and wrist points.
        right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])

        # Get the angle between the left elbow, shoulder and hip points.
        left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                             landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])

        # Get the angle between the right hip, shoulder and elbow points.
        right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                              landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])

        # Get the angle between the left hip, knee and ankle points.
        left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])

        # Get the angle between the right hip, knee and ankle points
        right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])

        # ----------------------------------------------------------------------------------------------------------------

        # Check if it is the warrior II pose or the T pose.
        # As for both of them, both arms should be straight and shoulders should be at the specific angle.
        # ----------------------------------------------------------------------------------------------------------------

        # Check if the both arms are straight.
        if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:

            # Check if shoulders are at the required angle.
            if left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:

                # Check if it is the warrior II pose.
                # ----------------------------------------------------------------------------------------------------------------

                # Check if one leg is straight.
                if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

                    # Check if the other leg is bended at the required angle.
                    if left_knee_angle > 90 and left_knee_angle < 120 or right_knee_angle > 90 and right_knee_angle < 120:
                        # Specify the label of the pose that is Warrior II pose.
                        label = 'Warrior II Pose'

                        # ----------------------------------------------------------------------------------------------------------------

                # Check if it is the T pose.
                # ----------------------------------------------------------------------------------------------------------------

                # Check if both legs are straight
                if left_knee_angle > 160 and left_knee_angle < 195 and right_knee_angle > 160 and right_knee_angle < 195:
                    # Specify the label of the pose that is tree pose.
                    label = 'T Pose'

        # ----------------------------------------------------------------------------------------------------------------

        # Check if it is the tree pose.
        # ----------------------------------------------------------------------------------------------------------------

        # Check if one leg is straight
        if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

            # Check if the other leg is bended at the required angle.
            if left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45:
                # Specify the label of the pose that is tree pose.
                label = 'Tree Pose'

        # ----------------------------------------------------------------------------------------------------------------

        # Check if the pose is classified successfully
        if label != 'Unknown Pose':
            # Update the color (to green) with which the label will be written on the image.
            color = (255, 255, 0)

            # Write the label on the output image.
        cv2.putText(output_image, label, (70, 250), font_2, 7.8, color, 7)

        # Check if the resultant image is specified to be displayed.
        if display:

            # Display the resultant image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        else:

            # Return the output image and the classified label.
            return output_image, label

    def calculate_angle(a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def modify_AI_elbow(image, landmarks):

        #####  PARAMETER  ######
        width, height = 2048, 1536  ## setting for Full  HD (3K - Max.)
        font_2 = cv2.FONT_HERSHEY_COMPLEX
        AI_elbow = 'This is an A.I. elbow trainer using webcam'
        #####  PARAMETER  ######

        # Get the angle between the left shoulder, elbow and wrist points.
        Left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        Right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        Left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        Right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

        Left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        Right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        # Calculate elbow angles
        Left_angle = round(calculate_angle(Left_shoulder, Left_elbow, Left_wrist), 2)
        Right_angle = round(calculate_angle(Right_shoulder, Right_elbow, Right_wrist), 2)

        # Visualize elbow angles
        cv2.putText(image, str(Left_angle), tuple(np.multiply(Left_elbow, [width, height]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(image, str(Right_angle), tuple(np.multiply(Right_elbow, [width, height]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 3, cv2.LINE_AA)

        # # Curl counter logic - elbow
        # color = (255, 0, 0)
        # if Left_angle and Right_angle > 160:
        #     stage = "down"
        #     color = (0, 0, 255)
        # if Left_angle and Right_angle < 30 and stage == 'down':
        #     stage = "up"
        #     color = (0, 255, 255)
        #     counter += 1
        #     # print(counter)
        #     speak100(str(counter))

        cv2.putText(image, AI_elbow, (80, 1230), font_2, 2.4, (0, 0, 255), 3, )
        return image, Left_angle, Right_angle

    def modify_AI_shoulder(image, landmarks):

        #####  PARAMETER  ######
        width, height = 2048, 1536  ## setting for Full  HD (3K - Max.)
        font_2 = cv2.FONT_HERSHEY_COMPLEX
        AI_shoulder = 'This is an A.I. shoulder trainer using webcam'
        #####  PARAMETER  ######

        # Get the angle between the  elbow, shoulder and hip points.
        Left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        Right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

        Left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        Right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        Left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        Right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        # Calculate shoulder angles
        Left_angle = round(calculate_angle(Left_elbow, Left_shoulder, Left_hip), 2)
        Right_angle = round(calculate_angle(Right_elbow, Right_shoulder, Right_hip), 2)

        # Visualize shoulder angles
        cv2.putText(image, str(Left_angle), tuple(np.multiply(Left_shoulder, [width, height]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.putText(image, str(Right_angle), tuple(np.multiply(Right_shoulder, [width, height]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3, cv2.LINE_AA)

        # cv2.putText(image, AI_shoulder, (80, 1230), font_2, 2.3, (190, 90, 0), 3, )
        cv2.putText(image, AI_shoulder, (80, 1230), font_2, 2.3, (255, 0, 0), 3, )

        return image, Left_angle, Right_angle

    def modify_AI_knee(image, landmarks):

        #####  PARAMETER  ######
        width, height = 2048, 1536  ## setting for Full  HD (3K - Max.)
        font_2 = cv2.FONT_HERSHEY_COMPLEX
        AI_knee = 'This is an A.I. knee trainer using webcam'
        #####  PARAMETER  ######

        # Get the angle between the left hip, knee and ankle points.
        Left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        Right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        Left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        Right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]

        Left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        Right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate knee angles
        Left_angle = round(calculate_angle(Left_hip, Left_knee, Left_ankle), 2)
        Right_angle = round(calculate_angle(Right_hip, Right_knee, Right_ankle), 2)

        # Visualize knee angles
        cv2.putText(image, str(Left_angle), tuple(np.multiply(Left_knee, [width, height]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(image, str(Right_angle), tuple(np.multiply(Right_knee, [width, height]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3, cv2.LINE_AA)

        # cv2.putText(image, AI_knee, (80, 1230), font_2, 2.3, (190, 90, 0), 3, )
        cv2.putText(image, AI_knee, (80, 1230), font_2, 2.3, (255, 88, 255), 3, )

        return image, Left_angle, Right_angle

    def detectPose_surferGame(image, pose, draw=False, display=False):
        '''
        This function performs the pose detection on the most prominent person in an image.
        Args:
            image:   The input image with a prominent person whose pose landmarks needs to be detected.
            pose:    The pose function required to perform the pose detection.
            draw:    A boolean value that is if set to true the function draw pose landmarks on the output image.
            display: A boolean value that is if set to true the function displays the original input image, and the
                     resultant image and returns nothing.
        Returns:
            output_image: The input image with the detected pose landmarks drawn if it was specified.
            results:      The output of the pose landmarks detection on the input image.
        '''

        # Create a copy of the input image.
        output_image = image.copy()

        # Convert the image from BGR into RGB format.
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform the Pose Detection.
        results = pose.process(imageRGB)

        # Check if any landmarks are detected and are specified to be drawn.
        if results.pose_landmarks and draw:
            # Draw Pose Landmarks on the output image.
            mp_drawing.draw_landmarks(image=output_image,
                                      landmark_list=results.pose_landmarks,
                                      connections=mp_pose.POSE_CONNECTIONS,
                                      landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=5,
                                                                                   circle_radius=8),
                                      # landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),  # It show colorful landmarks.
                                      connection_drawing_spec=mp_drawing.DrawingSpec(color=(49, 125, 237), thickness=5,
                                                                                     circle_radius=2)
                                      )

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

        # Otherwise
        else:

            # Return the output image and the results of pose landmarks detection.
            return output_image, results

    def checkHandsJoined(image, results, draw=False, display=False):
        '''
        This function checks whether the hands of the person are joined or not in an image.
        Args:
            image:   The input image with a prominent person whose hands status (joined or not) needs to be classified.
            results: The output of the pose landmarks detection on the input image.
            draw:    A boolean value that is if set to true the function writes the hands status & distance on the output image.
            display: A boolean value that is if set to true the function displays the resultant image and returns nothing.
        Returns:
            output_image: The same input image but with the classified hands status written, if it was specified.
            hand_status:  The classified status of the hands whether they are joined or not.
        '''

        # Get the height and width of the input image.
        height, width, _ = image.shape

        # Create a copy of the input image to write the hands status label on.
        output_image = image.copy()

        # Get the left wrist landmark x and y coordinates.
        left_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * width,
                               results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)

        # Get the right wrist landmark x and y coordinates.
        right_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * width,
                                results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)

        # Calculate the euclidean distance between the left and right wrist.
        euclidean_distance = int(hypot(left_wrist_landmark[0] - right_wrist_landmark[0],
                                       left_wrist_landmark[1] - right_wrist_landmark[1]))

        # Compare the distance between the wrists with a appropriate threshold to check if both hands are joined.
        if euclidean_distance < 120:

            # Set the hands status to joined.
            hand_status = 'Hands Joined'

            # Set the color value to green.
            color = (255, 255, 0)

        # Otherwise.
        else:

            # Set the hands status to not joined.
            hand_status = 'Hands Not Joined'

            # Set the color value to red.
            color = (255, 0, 255)

        # Check if the Hands Joined status and hands distance are specified to be written on the output image.
        if draw:
            # Write the classified hands status on the image.
            cv2.putText(output_image, hand_status, (70, 100), cv2.FONT_HERSHEY_COMPLEX, 3.0, color, 5)

            # Write the the distance between the wrists on the image.
            cv2.putText(output_image, f'Distance: {euclidean_distance}', (70, 200), cv2.FONT_HERSHEY_COMPLEX, 3.0,
                        color, 5)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10]);
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and the classified hands status indicating whether the hands are joined or not.
            return output_image, hand_status

    def checkLeftRight(image, results, draw=False, display=False):
        '''
        This function finds the horizontal position (left, center, right) of the person in an image.
        Args:
            image:   The input image with a prominent person whose the horizontal position needs to be found.
            results: The output of the pose landmarks detection on the input image.
            draw:    A boolean value that is if set to true the function writes the horizontal position on the output image.
            display: A boolean value that is if set to true the function displays the resultant image and returns nothing.
        Returns:
            output_image:         The same input image but with the horizontal position written, if it was specified.
            horizontal_position:  The horizontal position (left, center, right) of the person in the input image.
        '''

        # Declare a variable to store the horizontal position (left, center, right) of the person.
        horizontal_position = None

        # Get the height and width of the image.
        height, width, _ = image.shape

        # Create a copy of the input image to write the horizontal position on.
        output_image = image.copy()

        # Retreive the x-coordinate of the left shoulder landmark.
        left_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width)

        # Retreive the x-corrdinate of the right shoulder landmark.
        right_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width)

        # Check if the person is at left that is when both shoulder landmarks x-corrdinates
        # are less than or equal to the x-corrdinate of the center of the image.
        if (right_x <= width // 2 and left_x <= width // 2):

            # Set the person's position to left.
            horizontal_position = 'Left'
            # left_sound.play()


        # Check if the person is at right that is when both shoulder landmarks x-corrdinates
        # are greater than or equal to the x-corrdinate of the center of the image.
        elif (right_x >= width // 2 and left_x >= width // 2):

            # Set the person's position to right.
            horizontal_position = 'Right'
            # right_sound.play()

        # Check if the person is at center that is when right shoulder landmark x-corrdinate is greater than or equal to
        # and left shoulder landmark x-corrdinate is less than or equal to the x-corrdinate of the center of the image.
        elif (right_x >= width // 2 and left_x <= width // 2):

            # Set the person's position to center.
            horizontal_position = 'Center'

        # Check if the person's horizontal position and a line at the center of the image is specified to be drawn.
        if draw:
            # Write the horizontal position of the person on the image.
            cv2.putText(output_image, horizontal_position, (25, height - 400), cv2.FONT_HERSHEY_COMPLEX, 4.8,
                        (255, 0, 0), 5)

            # Draw a line at the center of the image.
            cv2.line(output_image, (width // 2, 0), (width // 2, height), (255, 255, 0), 8)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and the person's horizontal position.
            return output_image, horizontal_position

    def checkJumpCrouch(image, results, MID_Y=250, draw=False, display=False):
        '''
        This function checks the posture (Jumping, Crouching or Standing) of the person in an image.
        Args:
            image:   The input image with a prominent person whose the posture needs to be checked.
            results: The output of the pose landmarks detection on the input image.
            MID_Y:   The intial center y-coordinate of both shoulders landmarks of the person recorded during starting
                     the game. This will give the idea of the person's height when he is standing straight.
            draw:    A boolean value that is if set to true the function writes the posture on the output image.
            display: A boolean value that is if set to true the function displays the resultant image and returns nothing.
        Returns:
            output_image: The input image with the person's posture written, if it was specified.
            posture:      The posture (Jumping, Crouching or Standing) of the person in an image.
        '''

        # Get the height and width of the image.
        height, width, _ = image.shape

        # Create a copy of the input image to write the posture label on.
        output_image = image.copy()

        # Retreive the y-coordinate of the left shoulder landmark.
        left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)

        # Retreive the y-coordinate of the right shoulder landmark.
        right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)

        # Calculate the y-coordinate of the mid-point of both shoulders.
        actual_mid_y = (abs(right_y + left_y) // 2) - 90  # different between actual_mid_y & lower_bound = 10 (standing)
        # actual_mid_y = (abs(right_y + left_y) // 2) -100 # different between actual_mid_y & lower_bound = 0
        # actual_mid_y = (abs(right_y + left_y) // 2) -110 # different between actual_mid_y & lower_bound = -10 (jumping)

        # print(str(actual_mid_y))  # answer  varies each time.

        # Calculate the upper and lower bounds of the threshold.
        lower_bound = MID_Y - 100
        upper_bound = MID_Y + 50

        # print(str(lower_bound))  #  height of LB & UB = 150
        # print(str(upper_bound))  #  height of LB & UB = 150

        counter = 0

        # Check if the person has jumped that is when the y-coordinate of the mid-point
        # of both shoulders is less than the lower bound.
        if (actual_mid_y < lower_bound):

            counter = 0

            # Set the posture to jumping.
            posture = 'Jumping'
            counter += 1

        # Check if the person has crouched that is when the y-coordinate of the mid-point
        # of both shoulders is greater than the upper bound.
        elif (actual_mid_y > upper_bound):

            # Set the posture to crouching.
            posture = 'Crouching'
            counter += 2

        # Otherwise the person is standing and the y-coordinate of the mid-point
        # of both shoulders is between the upper and lower bounds.
        else:

            # Set the posture to Standing straight.
            posture = 'Standing'

        # Check if the posture and a horizontal line at the threshold is specified to be drawn.
        if draw:
            # Write the posture of the person on the image.
            cv2.putText(output_image, posture, (25, height - 125), cv2.FONT_HERSHEY_COMPLEX, 4.8, (255, 0, 0), 5)
            # cv2.putText(output_image, str(counter), (790, height - 135), cv2.FONT_HERSHEY_COMPLEX, 4.8, (255, 0, 0), 7)

            # Draw a line at the intial center y-coordinate of the person (threshold).
            cv2.line(output_image, (0, MID_Y), (width, MID_Y), (255, 255, 0), 12)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and posture indicating whether the person is standing straight or has jumped, or crouched.
            return output_image, posture


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