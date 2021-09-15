
"""
Hand Tracing Module
"""

import cv2
import mediapipe as mp
import os, time
import numpy as np
from colorama import Fore
import matplotlib.pyplot as plt
import subprocess
import pyautogui as pg
import pyglet
import math



# Initialize the mediapipe hands class.
mp_hands = mp.solutions.hands
# Initialize the mediapipe drawing class.
mp_drawing = mp.solutions.drawing_utils
# It show colorful hands landmarks
mp_drawing_styles = mp.solutions.drawing_styles

# Set up the Hands functions for images.
# hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.75) # ## For images only.

# Set up the Hands functions for  videos.
hands_videos = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                              min_detection_confidence=0.75, min_tracking_confidence=0.75)



############ set the size of web cam ########q#####
# width, height = 640, 480  ## setting for default
# width, height = 1280, 720  ## setting for HD
width, height = 1920, 1080  ## setting for Full  HD (2K)
# width, height =3840, 2160  ## setting for 4K
 ############ set the size of web cam ########q#####


class handDetector():

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(imgRGB)
            # print(results.multi_hand_landmarks)

            if self.results.multi_hand_landmarks:
                for handLms in self.results.multi_hand_landmarks:
                    if draw:
                        self.mpDraw.draw_landmarks(img, handLms,self.mpHands.HAND_CONNECTIONS)
            return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                              (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True):

        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    def get_label(self,index, hand, results):
        output = None
        for idx, classification in enumerate(results.multi_handedness):
            if classification.classification[0].index == index:
                label = classification.classification[0].label
                # score = classification.classification[0].score
                text = '{}'.format(label)
                # text = '{} {}'.format(label, round(score, 3))
                coords = tuple(np.multiply(np.array((hand.landmark[mp_hands.HandLandmark.WRIST].x,
                                                     hand.landmark[mp_hands.HandLandmark.WRIST].y)),
                                           [width, height]).astype(int))
                output = text, coords
                return output

    def draw_finger_angles(self,image, results, joint_list):
        # Load sounds
        sound = pyglet.media.load("sound.wav", streaming=False)

        # Loop through hands
        for hand in results.multi_hand_landmarks:

            # Loop through joint sets
            for joint in joint_list:
                a = np.array([hand.landmark[joint[0]].x, hand.landmark[joint[0]].y])  # First coord
                b = np.array([hand.landmark[joint[1]].x, hand.landmark[joint[1]].y])  # Second coord
                c = np.array([hand.landmark[joint[2]].x, hand.landmark[joint[2]].y])  # Third coord

                radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
                angle = np.abs(radians * 180.0 / np.pi)
                if angle > 180.0:
                    angle = 360 - angle
                    cv2.putText(image, str(round(angle, 1)), tuple(np.multiply(b, [width, height]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, (0.5 * 1.8), (255, 200, 200), (1 * 2), cv2.LINE_AA)

                ######### 1. bending thumb --  open the scientific calculator ####################
                if angle < 150.0 and joint==joint_list[0] :
                    sound.play()
                    speak100("let's open the scientific calculator for you sir.")
                    subprocess.Popen('C:/Windows/System32/calc.exe')
                ######### 1. bending thumb -- open the scientific calculator ####################

                ######### 2. bending index finger -- open the video of Bruce Lee ####################
                if angle < 150.0 and joint == joint_list[1]:
                    # speak100("Oops!")
                    sound.play()
                    speak100("the video of Bruce Lee versus Donnie Yen in : a warriors dream ")
                #     os.startfile("https://www.youtube.com/watch?v=Gxtvn23__z4")
                #     # https://www.youtube.com/watch?v=Gxtvn23__z4
                #     time.sleep(5)  ## It can not < 5
                #     pg.click(x=770, y=540, interval=1)
                #     # pg.click(x=1202, y=775, interval=1)
                ######### 2.  bending index finger -- open the video of Bruce Lee ####################

                ########## 3. bending middle finger -- open Sinsuran file  ####################
                if angle < 150.0 and joint == joint_list[2] :
                    sound.play()
                    # speak100("Oops!")
                    speak100("Let's open the LibreOffice calc file of  in Sinsuran, Kota Kinabalu. ")
                    # os.startfile("C:/Users/acer/Desktop/Sinsuran/Sinsuran 2021/Sinsuran - 2 Day payment "
                    #              "- V21- 1Jan2021.ods")
                ######### 3. bending middle finger --  open Sinsuran file  ####################

                ########## 4.  bending ring finger  --  open the The Daily Express newspaper ####################
                if angle < 150.0 and joint == joint_list[3]:
                    sound.play()
                    # speak100("Oops!")
                #     pg.FAILSAFE = True
                    speak100("let's open The Daily Express newspaper for you sir.")
                #     pg.hotkey("winleft")
                #     time.sleep(3)
                #     pg.click(x=833, y=630, interval=1)
                #     # in pyAutoGui the typewrite command the \n means hit enter & not new line.
                #     pg.typewrite('www.dailyexpress.com.my\n', 0.2)
                ######### 4.  bending ring finger  --  open the The Daily Express newspaper ####################

                ######### 5. bending pinky finger --  play the song by Pet Shop Boys & take photos ####################
                if angle < 150.0 and joint == joint_list[4]:
                    sound.play()
                    # speak100("Oops!")
                    speak100("let's play the song by Pet Shop Boys - Domino Dancing. ")
                #     os.startfile('C:/Users/acer/Desktop/songs/Pet Shop Boys - Domino Dancing.mp3')
                # ##  or ##
                # if angle < 150.0 and joint == joint_list[4]:
                    # pg.FAILSAFE = True
                    # speak100("let's open the camera and take picture for you sir.")
                    # pg.hotkey("winleft")
                    # time.sleep(2)
                    # pg.click(x=670, y=460, interval=0.25)  ##click main window
                    # # time.sleep(3)
                    # # pg.click(x=1257, y=(485 + 170), interval=0.25)  ##click camera icon
                    # time.sleep(5)
                    # pg.click(x=1265, y=495, interval=0.25)  ##click start camera button
                    # # pg.click(x=1257, y=485, interval=0.25)
                ######### 5. bending pinky finger --  play the song by Pet Shop Boys  & take photos ####################
            return image

    def make_folder(self, myFolder):
        if not os.path.exists(myFolder):
            os.makedirs(myFolder)
            print('Creating subfolder: Tim_folder')
            print('@============ A new sub-folder created for you, sir! =================@')
        return myFolder

#
    def detectHandsLandmarks(image, hands_videos, draw=True, display=True):
        '''
        This function performs hands landmarks detection on an image.
        Args:
            image:   The input image with prominent hand(s) whose landmarks needs to be detected.
            hands:   The Hands function required to perform the hands landmarks detection.
            draw:    A boolean value that is if set to true the function draws hands landmarks on the output image.
            display: A boolean value that is if set to true the function displays the original input image, and the output
                     image with hands landmarks drawn if it was specified and returns nothing.
        Returns:
            output_image: A copy of input image with the detected hands landmarks drawn if it was specified.
            results:      The output of the hands landmarks detection on the input image.
        '''

        # Create a copy of the input image to draw landmarks on.
        output_image = image.copy()

        # Convert the image from BGR into RGB format.
        imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform the Hands Landmarks Detection.
        results = hands_videos.process(imgRGB)

        # Check if landmarks are found and are specified to be drawn.
        if results.multi_hand_landmarks and draw:

            # Iterate over the found hands.
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks on the copy of the input image.
                mp_drawing.draw_landmarks(image=output_image, landmark_list=hand_landmarks,
                                          connections=mp_hands.HAND_CONNECTIONS,
                                          landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                                          ## Alternative way.
                                          connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style())  ## Alternative way.
                # landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255 ,255 ,255),thickness=5, circle_radius=5),
                # connection_drawing_spec=mp_drawing.DrawingSpec(color=(0 ,255 ,0), thickness=5, circle_radius=7))

        # Check if the original input image and the output image are specified to be displayed.
        if display:

            # Display the original input image and the output image.
            plt.figure(figsize=[15, 15])
            plt.subplot(121) \
                ;
            plt.imshow(image[:, :, ::-1]) \
                ;
            plt.title("Original Image") \
                ;
            plt.axis('off');
            plt.subplot(122) \
                ;
            plt.imshow(output_image[:, :, ::-1]) \
                ;
            plt.title("Output") \
                ;
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and results of hands landmarks detection.
            return output_image, results

        # Now let's test the function **`detectHandsLandmarks()`** created above to perform hands landmarks detection on a sample image and display the results.

    def countFingers(image, results, draw=True, display=True):
        '''
        This function will count the number of fingers up for each hand in the image.
        Args:
            image:   The image of the hands on which the fingers counting is required to be performed.
            results: The output of the hands landmarks detection performed on the image of the hands.
            draw:    A boolean value that is if set to true the function writes the total count of fingers of the hands on the
                     output image.
            display: A boolean value that is if set to true the function displays the resultant image and returns nothing.
        Returns:
            output_image:     A copy of the input image with the fingers count written, if it was specified.
            fingers_statuses: A dictionary containing the status (i.e., open or close) of each finger of both hands.
            count:            A dictionary containing the count of the fingers that are up, of both hands.
        '''

        # Get the height and width of the input image.
        height, width, _ = image.shape

        # Create a copy of the input image to write the count of fingers on.
        output_image = image.copy()

        # Initialize a dictionary to store the count of fingers of both hands.
        count = {'RIGHT': 0, 'LEFT': 0}

        # Store the indexes of the tips landmarks of each finger of a hand in a list.
        fingers_tips_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                            mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]

        # Initialize a dictionary to store the status (i.e., True for open and False for close) of each finger of both hands.
        fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                            'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                            'LEFT_RING': False, 'LEFT_PINKY': False}

        # Iterate over the found hands in the image.
        for hand_index, hand_info in enumerate(results.multi_handedness):

            # Retrieve the label of the found hand.
            hand_label = hand_info.classification[0].label

            # Retrieve the landmarks of the found hand.
            hand_landmarks = results.multi_hand_landmarks[hand_index]

            # Iterate over the indexes of the tips landmarks of each finger of the hand.
            for tip_index in fingers_tips_ids:

                # Retrieve the label (i.e., index, middle, etc.) of the finger on which we are iterating upon.
                finger_name = tip_index.name.split("_")[0]

                # Check if the finger is up by comparing the y-coordinates of the tip and pip landmarks.
                if (hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y):
                    # Update the status of the finger in the dictionary to true.
                    fingers_statuses[hand_label.upper() + "_ " + finger_name] = True

                    # Increment the count of the fingers up of the hand by 1.
                    count[hand_label.upper()] += 1

            # Retrieve the y-coordinates of the tip and mcp landmarks of the thumb of the hand.
            thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
            thumb_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP - 2].x

            # Check if the thumb is up by comparing the hand label and the x-coordinates of the retrieved landmarks.
            if (hand_label == 'Right' and (thumb_tip_x < thumb_mcp_x)) or (hand_label == 'Left'
                                                                           and (thumb_tip_x > thumb_mcp_x)):
                # Update the status of the thumb in the dictionary to true.
                fingers_statuses[hand_label.upper() + "_THUMB"] = True

                # Increment the count of the fingers up of the hand by 1.
                count[hand_label.upper()] += 1

        # Check if the total count of the fingers of both hands are specified to be written on the output image.
        if draw:
            # Write the total count of the fingers of both hands on the output image.
            cv2.putText(output_image, " Total Fingers: ", (450, 68), cv2.FONT_HERSHEY_COMPLEX, 1.5, (20, 255, 155), 3)
            cv2.putText(output_image, str(sum(count.values())), (width // 2 - 100, 125), cv2.FONT_HERSHEY_SIMPLEX,
                        5.0, (20, 255, 155), 12, 10)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image, the status of each finger and the count of the fingers up of both hands.
            return output_image, fingers_statuses, count

    def annotate(image, results, fingers_statuses, count, display=True):
        '''
        This function will draw an appealing visualization of each fingers up of the both hands in the image.
        Args:
            image:            The image of the hands on which the counted fingers are required to be visualized.
            results:          The output of the hands landmarks detection performed on the image of the hands.
            fingers_statuses: A dictionary containing the status (i.e., open or close) of each finger of both hands.
            count:            A dictionary containing the count of the fingers that are up, of both hands.
            display:          A boolean value that is if set to true the function displays the resultant image and
                              returns nothing.
        Returns:
            output_image: A copy of the input image with the visualization of counted fingers.
        '''

        # Get the height and width of the input image.
        height, width, _ = image.shape

        # Create a copy of the input image.
        output_image = image.copy()

        # Select the images of the hands prints that are required to be overlayed.
        ########################################################################################################################

        # Initialize a dictionaty to store the images paths of the both hands.
        # Initially it contains red hands images paths. The red image represents that the hand is not present in the image.
        HANDS_IMGS_PATHS = {'LEFT': ['media/left_hand_not_detected.png'],
                            'RIGHT': ['media/right_hand_not_detected.png']}

        # Check if there is hand(s) in the image.
        if results.multi_hand_landmarks:

            # Iterate over the detected hands in the image.
            for hand_index, hand_info in enumerate(results.multi_handedness):

                # Retrieve the label of the hand.
                hand_label = hand_info.classification[0].label

                # Update the image path of the hand to a green color hand image.
                # This green image represents that the hand is present in the image.
                HANDS_IMGS_PATHS[hand_label.upper()] = ['media/' + hand_label.lower() + '_hand_detected.png']

                # Check if all the fingers of the hand are up/open.
                if count[hand_label.upper()] == 5:

                    # Update the image path of the hand to a hand image with green color palm and orange color fingers image.
                    # The orange color of a finger represents that the finger is up.
                    HANDS_IMGS_PATHS[hand_label.upper()] = ['media/' + hand_label.lower() + '_all_fingers.png']

                # Otherwise if all the fingers of the hand are not up/open.
                else:

                    # Iterate over the fingers statuses of the hands.
                    for finger, status in fingers_statuses.items():

                        # Check if the finger is up and belongs to the hand that we are iterating upon.
                        if status == True and finger.split("_")[0] == hand_label.upper():
                            # Append another image of the hand in the list inside the dictionary.
                            # This image only contains the finger we are iterating upon of the hand in orange color.
                            # As the orange color represents that the finger is up.
                            HANDS_IMGS_PATHS[hand_label.upper()].append('media/' + finger.lower() + '.png')

        ########################################################################################################################

        # Overlay the selected hands prints on the input image.
        ########################################################################################################################

        # Iterate over the left and right hand.
        for hand_index, hand_imgs_paths in enumerate(HANDS_IMGS_PATHS.values()):

            # Iterate over the images paths of the hand.
            for img_path in hand_imgs_paths:
                # Read the image including its alpha channel. The alpha channel (0-255) determine the level of visibility.
                # In alpha channel, 0 represents the transparent area and 255 represents the visible area.
                hand_imageBGRA = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

                # Retrieve all the alpha channel values of the hand image.
                alpha_channel = hand_imageBGRA[:, :, -1]

                # Retrieve all the blue, green, and red channels values of the hand image.
                # As we also need the three-channel version of the hand image.
                hand_imageBGR = hand_imageBGRA[:, :, :-1]

                # Retrieve the height and width of the hand image.
                hand_height, hand_width, _ = hand_imageBGR.shape

                # Retrieve the region of interest of the output image where the handprint image will be placed.
                ROI = output_image[30: 30 + hand_height,
                      (hand_index * width // 2) + width // 12: ((hand_index * width // 2) + width // 12 + hand_width)]

                # Overlay the handprint image by updating the pixel values of the ROI of the output image at the
                # indexes where the alpha channel has the value 255.
                ROI[alpha_channel == 255] = hand_imageBGR[alpha_channel == 255]

                # Update the ROI of the output image with resultant image pixel values after overlaying the handprint.
                output_image[30: 30 + hand_height,
                (hand_index * width // 2) + width // 12: ((hand_index * width // 2) + width // 12 + hand_width)] = ROI

        ########################################################################################################################

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image
            return output_image

    def recognizeGestures(image, fingers_statuses, count, draw=True, display=True):
        '''
        This function will determine the gesture of the left and right hand in the image.
        Args:
            image:            The image of the hands on which the hand gesture recognition is required to be performed.
            fingers_statuses: A dictionary containing the status (i.e., open or close) of each finger of both hands.
            count:            A dictionary containing the count of the fingers that are up, of both hands.
            draw:             A boolean value that is if set to true the function writes the gestures of the hands on the
                              output image, after recognition.
            display:          A boolean value that is if set to true the function displays the resultant image and
                              returns nothing.
        Returns:
            output_image:   A copy of the input image with the left and right hand recognized gestures written if it was
                            specified.
            hands_gestures: A dictionary containing the recognized gestures of the right and left hand.
        '''

        # Create a copy of the input image.
        output_image = image.copy()

        # Store the labels of both hands in a list.
        hands_labels = ['RIGHT', 'LEFT']

        # Initialize a dictionary to store the gestures of both hands in the image.
        hands_gestures = {'RIGHT': "UNKNOWN", 'LEFT': "UNKNOWN"}

        # Iterate over the left and right hand.
        for hand_index, hand_label in enumerate(hands_labels):

            # Initialize a variable to store the color we will use to write the hands gestures on the image.
            # Initially it is red which represents that the gesture is not recognized.
            color = (0, 0, 255)

            ####################################################################################################################
            # 1. Check if the person is making the 'V' gesture with the hand.
            ####################################################################################################################

            # Check if the number of fingers up is 2 and the fingers that are up, are the index and the middle finger.
            if count[hand_label] == 2 and fingers_statuses[hand_label + '_MIDDLE'] and fingers_statuses[
                hand_label + '_INDEX']:

                # Update the gesture value of the hand that we are iterating upon to V SIGN.
                hands_gestures[hand_label] = "V SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ###############################################################################################################
            # 2. Check if the person is making the 'SPIDERMAN' gesture with the hand.
            ##########################################################################################################################################################

            # Check if the number of fingers up is 3 and the fingers that are up, are the thumb, index and the pinky finger.
            elif count[hand_label] == 3 and fingers_statuses[hand_label + '_THUMB'] and fingers_statuses[
                hand_label + '_INDEX'] and fingers_statuses[hand_label + '_PINKY']:

                # Update the gesture value of the hand that we are iterating upon to SPIDERMAN SIGN.
                hands_gestures[hand_label] = "SPIDERMAN SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ###############################################################################################################
            # 3. Check if the person is making the 'HIGH-FIVE' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 5, which means that all the fingers are up.
            elif count[hand_label] == 5:

                # Update the gesture value of the hand that we are iterating upon to HIGH-FIVE SIGN.
                hands_gestures[hand_label] = "HIGH-FIVE SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ####################################################################################################################
            # 4. Check if the person is making the '1' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 1 and the fingers that is up is the index finger.
            elif count[hand_label] == 1 and fingers_statuses[hand_label + '_INDEX']:
                # Update the gesture value of the hand that we are iterating upon to V SIGN.
                hands_gestures[hand_label] = "1 SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ##################################################################################################################
            ####################################################################################################################
            # 5. Check if the person is making the '6' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 3 and the fingers that are up, are the thumband &the pinky finger.
            elif count[hand_label] == 2 and fingers_statuses[hand_label + '_THUMB'] and fingers_statuses[
                hand_label + '_PINKY']:
                # Update the gesture value of the hand that we are iterating upon to V SIGN.
                hands_gestures[hand_label] = "6 SIGN"

                # Update the color value to green.
                color = (0, 255, 0)


            ##################################################################################################################
            ####################################################################################################################
            # 6. Check if the person is making the 'Good' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 1 and the fingers that are up, are the thumband .
            elif count[hand_label] == 1 and fingers_statuses[hand_label + '_THUMB']:

                # Update the gesture value of the hand that we are iterating upon to V SIGN.
                hands_gestures[hand_label] = "Good SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ####################################################################################################################
            # 7. Check if the person is making the 'PINKY FINGER SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 1 and the fingers that are up, are the thumband .
            elif count[hand_label] == 1 and fingers_statuses[hand_label + '_PINKY']:

                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "PINKY FINGER SIGN"

                # Update the color value to green.
                color = (0, 255, 0)
            ####################################################################################################################
            # 8. Check if the person is making the '3 FINGER SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 3 and the fingers that are up, are the thumband .
            elif count[hand_label] == 3 and fingers_statuses[hand_label + '_INDEX'] and fingers_statuses[
                hand_label + '_MIDDLE'] and fingers_statuses[hand_label + '_RING']:
                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "3 FINGER SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ####################################################################################################################
            # 9. Check if the person is making the '4 FINGER SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 4 and the fingers that are up, are the thumband .
            elif count[hand_label] == 4 and fingers_statuses[hand_label + '_INDEX'] and fingers_statuses[
                hand_label + '_MIDDLE'] and fingers_statuses[hand_label + '_RING'] and fingers_statuses[
                hand_label + '_PINKY']:
                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "4 FINGER SIGN"

                # Update the color value to green.
                color = (0, 255, 0)

            ####################################################################################################################
            # 10. Check if the person is making the 'OK SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 4 and the fingers that are up, are the thumband .
            elif count[hand_label] == 4 and fingers_statuses[hand_label + '_THUMB'] and fingers_statuses[
                hand_label + '_MIDDLE'] and fingers_statuses[hand_label + '_RING'] and fingers_statuses[
                hand_label + '_PINKY']:
                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "OK SIGN"

                # Update the color value to green.
                color = (0, 255, 255)

            ####################################################################################################################
            # 11. Check if the person is making the 'GUN SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 3 and the fingers that are up, are the thumband .
            elif count[hand_label] == 3 and fingers_statuses[hand_label + '_THUMB'] and fingers_statuses[
                hand_label + '_INDEX'] and fingers_statuses[hand_label + '_MIDDLE']:

                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "GUN SIGN"

                # Update the color value to green.
                color = (0, 255, 255)

            ####################################################################################################################
            # 12. Check if the person is making the 'SCOUT SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 3 and the fingers that are up, are the thumband .
            elif count[hand_label] == 3 and fingers_statuses[hand_label + '_THUMB'] and fingers_statuses[
                hand_label + '_MIDDLE'] and fingers_statuses[hand_label + '_RING']:

                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "SCOUT SIGN"

                # Update the color value to green.
                color = (0, 255, 255)

            ####################################################################################################################
            # 13. Check if the person is making the 'MONKEY SIGN' gesture with the hand.
            ####################################################################################################################
            # Check if the number of fingers up is 4 and the fingers that are up, are the thumband .
            elif count[hand_label] == 4 and fingers_statuses[hand_label + '_THUMB'] \
                    and fingers_statuses[hand_label + '_INDEX'] and fingers_statuses[
                hand_label + '_MIDDLE'] and fingers_statuses[hand_label + '_RING']:

                # Update the gesture value of the hand that we are iterating upon to PINKY FINGER SIGN.
                hands_gestures[hand_label] = "MONKEY SIGN"

                # Update the color value to green.
                color = (0, 255, 255)
            ##################################################################################################################
            ##################################################################################################################
            ##################################################################################################################

            # Check if the hands gestures are specified to be written.
            if draw:
                # Write the hand gesture on the output image.
                cv2.putText(output_image, hand_label + ': ' + hands_gestures[hand_label], (10, (hand_index + 1) * 60),
                            cv2.FONT_HERSHEY_PLAIN, 4, color, 5)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and the gestures of the both hands.
            return output_image, hands_gestures

    def getHandType(image, results, draw=True, display=True):
        '''
        This function performs hands type (left or right) classification on hands.
        Args:
            image:   The image of the hands that needs to be classified, with the hands landmarks detection already performed.
            results: The output of the hands landmarks detection performed on the image in which hands types needs
                     to be classified.
            draw:    A boolean value that is if set to true the function writes the hand type label on the output image.
            display: A boolean value that is if set to true the function displays the output image and returns nothing.
        Returns:
            output_image: The image of the hands with the classified hand type label written if it was specified.
            hands_status: A dictionary containing classification info of both hands.
        '''

        # Create a copy of the input image to write hand type label on.
        output_image = image.copy()

        # Initialize a dictionary to store the classification info of both hands.
        hands_status = {'Right': False, 'Left': False, 'Right_index': None, 'Left_index': None}

        # Iterate over the found hands in the image.
        for hand_index, hand_info in enumerate(results.multi_handedness):

            # Retrieve the label of the found hand.
            hand_type = hand_info.classification[0].label

            # Update the status of the found hand.
            hands_status[hand_type] = True

            # Update the index of the found hand.
            hands_status[hand_type + '_index'] = hand_index

            # Check if the hand type label is specified to be written.
            if draw:
                # Write the hand type on the output image.
                cv2.putText(output_image, hand_type + ' Hand Detected', (10, (hand_index + 3) * 60),
                            cv2.FONT_HERSHEY_PLAIN,
                            7, (255, 255, 0), 4)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and the hands status dictionary that contains classification info.
            return output_image, hands_status

    def drawBoundingBoxes(image, results, hand_status, padd_amount=10, draw=True, display=True):
        '''
        This function draws bounding boxes around the hands and write their classified types near them.
        Args:
            image:       The image of the hands on which the bounding boxes around the hands needs to be drawn and the
                         classified hands types labels needs to be written.
            results:     The output of the hands landmarks detection performed on the image on which the bounding boxes needs
                         to be drawn.
            hand_status: The dictionary containing the classification info of both hands.
            padd_amount: The value that specifies the space inside the bounding box between the hand and the box's borders.
            draw:        A boolean value that is if set to true the function draws bounding boxes and write their classified
                         types on the output image.
            display:     A boolean value that is if set to true the function displays the output image and returns nothing.
        Returns:
            output_image:     The image of the hands with the bounding boxes drawn and hands classified types written if it
                              was specified.
            output_landmarks: The dictionary that stores both (left and right) hands landmarks as different elements.
        '''

        # Create a copy of the input image to draw bounding boxes on and write hands types labels.
        output_image = image.copy()

        # Initialize a dictionary to store both (left and right) hands landmarks as different elements.
        output_landmarks = {}

        # Get the height and width of the input image.
        height, width, _ = image.shape

        # Iterate over the found hands.
        for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):

            # Initialize a list to store the detected landmarks of the hand.
            landmarks = []

            # Iterate over the detected landmarks of the hand.
            for landmark in hand_landmarks.landmark:
                # Append the landmark into the list.
                landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                  (landmark.z * width)))

            # Get all the x-coordinate values from the found landmarks of the hand.
            x_coordinates = np.array(landmarks)[:, 0]

            # Get all the y-coordinate values from the found landmarks of the hand.
            y_coordinates = np.array(landmarks)[:, 1]

            # Get the bounding box coordinates for the hand with the specified padding.
            x1 = int(np.min(x_coordinates) - padd_amount)
            y1 = int(np.min(y_coordinates) - padd_amount)
            x2 = int(np.max(x_coordinates) + padd_amount)
            y2 = int(np.max(y_coordinates) + padd_amount)

            # Initialize a variable to store the label of the hand.
            label = "Unknown"

            # Check if the hand we are iterating upon is the right one.
            if hand_status['Right_index'] == hand_index:

                # Update the label and store the landmarks of the hand in the dictionary.
                label = 'Right Hand'
                output_landmarks['Right'] = landmarks

            # Check if the hand we are iterating upon is the left one.
            elif hand_status['Left_index'] == hand_index:

                # Update the label and store the landmarks of the hand in the dictionary.
                label = 'Left Hand'
                output_landmarks['Left'] = landmarks

            # Check if the bounding box and the classified label is specified to be written.
            if draw:
                # Draw the bounding box around the hand on the output image.
                cv2.rectangle(output_image, (x1, y1), (x2, y2), (155, 0, 255), 5, cv2.LINE_8)

                # Write the classified label of the hand below the bounding box drawn.
                cv2.putText(output_image, label, (x1 + 15, y2 + 58), cv2.FONT_HERSHEY_COMPLEX, 1.8, (255, 255, 0), 2,
                            cv2.LINE_AA)

        # Check if the output image is specified to be displayed.
        if display:

            # Display the output image.
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1]);
            plt.title("Output Image");
            plt.axis('off');

        # Otherwise
        else:

            # Return the output image and the landmarks dictionary.
            return output_image, output_landmarks

    def customLandmarksAnnotation(image, landmark_dict):
        '''
        This function draws customized landmarks annotation utilizing the z-coordinate (depth) values of the hands.
        Args:
            image:         The image of the hands on which customized landmarks annotation of the hands needs to be drawn.
            landmark_dict: The dictionary that stores the hand(s) landmarks as different elements with keys as hand
                           types(i.e., left and right).
        Returns:
            output_image: The image of the hands with the customized annotation drawn.
            depth:        A dictionary that contains the average depth of all landmarks of the hand(s) in the image.
        '''

        # Create a copy of the input image to draw annotation on.
        output_image = image.copy()

        # Initialize a dictionary to store the average depth of all landmarks of hand(s).
        depth = {}

        # Initialize a list with the arrays of indexes of the landmarks that will make the required
        # line segments to draw on the hand.
        segments = [np.arange(0, 5), np.arange(5, 9), np.arange(9, 13), np.arange(13, 17), np.arange(17, 21),
                    np.arange(5, 18, 4), np.array([0, 5]), np.array([0, 17])]

        # Iterate over the landmarks dictionary.
        for hand_type, hand_landmarks in landmark_dict.items():

            # Get all the z-coordinates (depth) of the landmarks of the hand.
            depth_values = np.array(hand_landmarks)[:, -1]

            # Calculate the average depth of the hand.
            average_depth = int(sum(depth_values) / len(depth_values))

            # Get all the x-coordinates of the landmarks of the hand.
            x_values = np.array(hand_landmarks)[:, 0]

            # Get all the y-coordinates of the landmarks of the hand.
            y_values = np.array(hand_landmarks)[:, 1]

            # Initialize a list to store the arrays of x and y coordinates of the line segments for the hand.
            line_segments = []

            # Iterate over the arrays of indexes of the landmarks that will make the required line segments.
            for segment_indexes in segments:
                # Get an array of a line segment coordinates of the hand.
                line_segment = np.array([[int(x_values[index]), int(y_values[index])] for index in segment_indexes])

                # Append the line segment coordinates into the list.
                line_segments.append(line_segment)

            # Check if the average depth of the hand is less than 0.
            if average_depth < 0:

                # Set the thickness of the line segments of the hand accordingly to the average depth.
                line_thickness = int(np.ceil(0.1 * abs(average_depth))) + 2

                # Set the thickness of the circles of the hand landmarks accordingly to the average depth.
                circle_thickness = int(np.ceil(0.1 * abs(average_depth))) + 3

            # Otherwise.
            else:

                # Set the thickness of the line segments of the hand to 2 (i.e. the minimum thickness we are specifying).
                line_thickness = 2

                # Set the thickness of the circles to 3 (i.e. the minimum thickness)
                circle_thickness = 3

            # Draw the line segments on the hand.
            cv2.polylines(output_image, line_segments, False, (100, 250, 55), line_thickness)

            # Write the average depth of the hand on the output image.
            cv2.putText(output_image, 'Depth (in Z direction): {}'.format(average_depth), (280, 120 + 100 + 300),
                        cv2.FONT_HERSHEY_COMPLEX, 2.8, (255, 25, 0), 3, cv2.LINE_AA)

            # Iterate over the x and y coordinates of the hand landmarks.
            for x, y in zip(x_values, y_values):
                # Draw a circle on the x and y coordinate of the hand.
                cv2.circle(output_image, (int(x), int(y)), circle_thickness, (55, 55, 250), -1)

            # Store the calculated average depth in the dictionary.
            depth[hand_type] = average_depth

        # Return the output image and the average depth dictionary of the hand(s).
        return output_image, depth

#




def main():
        pTime = 0
        cTime = 0
        cap = cv2.VideoCapture(2)
        detector = handDetector()

        while True:
            success, img = cap.read()
            img = detector.findHands(img, draw=True)
            # lmList = detector.findPosition(img, draw=False)
            lmList,bbox = detector.findPosition(img, draw=True)
            if len(lmList) != 0:
                pass
                # print(lmList[8])

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime

            cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 5,(255, 0, 255), 3)
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27 or key == ord('q'):
                break
if __name__ == '__main__':
    main()