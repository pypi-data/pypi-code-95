import cv2
import numpy as np
import mediapipe as mp
from threading import Thread
import os
import winsound

class start_session:

    def initiate_mediapipe(self):

        mpFaceMesh = mp.solutions.face_mesh
        faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1)
        mpDraw =mp.solutions.drawing_utils
        drawSpec = mpDraw.DrawingSpec(thickness=1, circle_radius=2)

        mpHands=mp.solutions.hands
        hands = mpHands.Hands()
        return faceMesh, hands

    #creating a function to play alarm
    def play_sound(self):
        frequency = 250  # Set Frequency To 2500 Hertz
        duration = 1000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)

    def start_alert(self):

        faceMesh, hands =self.initiate_mediapipe()

        cap = cv2.VideoCapture(0)
        while True:
            _, frame = cap.read()
            h, w, nc = frame.shape
            # print(h, w)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            imgRGB =cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            ##detecting face landmarks
            face_results = faceMesh.process(imgRGB)

            if face_results.multi_face_landmarks:
                for faceLms in face_results.multi_face_landmarks:
                    for id, lm in enumerate(faceLms.landmark):
                        if id ==0:
                            cx, cy = int(lm.x * w), int(lm.y * h)

                noseX, noseY = cx, cy

            ##detecting hand landmarks
            hand_results=hands.process(imgRGB)
            if hand_results.multi_hand_landmarks:
                for handLms in hand_results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        if id==8:
                            cx, cy = int(lm.x*w), int(lm.y*h)

                ##finding the coordinates for the tip of index finger
                indexTipX, indexTipY = cx, cy


                ##Playing alarm when the distance between nose and indix finger tip is less than 30
                if abs(indexTipX - noseX)< 60 and abs(indexTipY-noseY) < 60:
                    t=Thread(target=self.play_sound())
                    t.daemon=True
                    t.start()

            cv2.imshow("Input", frame)
            c = cv2.waitKey(1)
            if c == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

        # self.alert()