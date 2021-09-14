import cv2
import math
import pyautogui
import numpy as np
import mediapipe as mp
from utilpack.util import PyImageUtil
from utilpack.core import PyAlgorithm
from mediapipe.framework.formats import landmark_pb2


class PyHandMouse(object):

    def __init__(self,video_wh=(640,480)):
        self._click_toggle = False
        self._video_wh = video_wh
        self._screen_wh = pyautogui.size()
        self._mp_hands = mp.solutions.hands
        self._mp_drawing = mp.solutions.drawing_utils
        self.run()

    def _normalized_to_pixel_coordinates(self,normalized_x: float, normalized_y: float, image_width: int,
                                         image_height: int):
        """Converts normalized value pair to pixel coordinates."""

        # Checks if the float value is between 0 and 1.
        def is_valid_normalized_value(value: float) -> bool:
            return (value > 0 or math.isclose(0, value)) and (value < 1 or math.isclose(1, value))

        if not (is_valid_normalized_value(normalized_x) and is_valid_normalized_value(normalized_y)):
            # TODO: Draw coordinates even if it's outside of the image bounds.
            return None
        x_px = min(math.floor(normalized_x * image_width), image_width - 1)
        y_px = min(math.floor(normalized_y * image_height), image_height - 1)
        return x_px, y_px

    def _get_landmarks(self, image: np.ndarray, landmark_list: landmark_pb2.NormalizedLandmarkList,
                       connections=None, PRESENCE_THRESHOLD=0.5, VISIBILITY_THRESHOLD=0.5):
        """Draws the landmarks and the connections on the image.

        Args:
            image: A three channel RGB image represented as numpy ndarray.
            landmark_list: A normalized landmark list proto message to be annotated on
                the image.
            connections: A list of landmark index tuples that specifies how landmarks to
                be connected in the drawing.
            landmark_drawing_spec: A DrawingSpec object that specifies the landmarks'
                drawing settings such as color, line thickness, and circle radius.
            connection_drawing_spec: A DrawingSpec object that specifies the
                connections' drawing settings such as color and line thickness.

        Raises:
            ValueError: If one of the followings:
                a) If the input image is not three channel RGB.
                b) If any connetions contain invalid landmark index.
        """
        if not landmark_list:
            return
        if image.shape[2] != 3:
            raise ValueError('Input image must contain three channel rgb data.')
        image_rows, image_cols, _ = image.shape
        idx_to_coordinates = {}
        for idx, landmark in enumerate(landmark_list.landmark):
            if ((landmark.HasField('visibility') and landmark.visibility < VISIBILITY_THRESHOLD) or (
                    landmark.HasField('presence') and landmark.presence < PRESENCE_THRESHOLD)):
                continue
            landmark_px = self._normalized_to_pixel_coordinates(landmark.x, landmark.y, image_cols, image_rows)

            if landmark_px:
                idx_to_coordinates[idx] = landmark_px

        if connections:
            num_landmarks = len(landmark_list.landmark)
            # Draws the connections if the start and end landmarks are both visible.
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
                if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                    raise ValueError(
                        f'Landmark index is out of range. Invalid connection ' f'from landmark #{start_idx} to landmark #{end_idx}.')

        return idx_to_coordinates

    def _video2screen(self, x, y):
        x = PyAlgorithm.limit_minmax(x, 0, self._video_wh[0])
        y = PyAlgorithm.limit_minmax(y, 0, self._video_wh[1])
        return self._screen_wh[0] / self._video_wh[0] * x, self._screen_wh[1] / self._video_wh[1] * y


    def run(self):

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        cv2.namedWindow('PyHandMouse',cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('PyHandMouse',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty('PyHandMouse',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)

        with self._mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75, max_num_hands=1) as hands:
            while cap.isOpened():
                success, image = cap.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                # Flip the image horizontally for a later selfie-view display, and convert
                # the BGR image to RGB.
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                h, w, _ = image.shape
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                results = hands.process(image)

                # Draw the hand annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    hand_landmark = results.multi_hand_landmarks[0]
                    landmarks = self._get_landmarks(image, hand_landmark, self._mp_hands.HAND_CONNECTIONS)

                    if not all([bool(v in landmarks) for v in [0, 8, 4]]):
                        continue
                    # self._mp_drawing.draw_landmarks(image, hand_landmark, self._mp_hands.HAND_CONNECTIONS)
                    image = cv2.circle(image,landmarks[4],5,(255,0,255),3)
                    image = cv2.circle(image, landmarks[0], 5, (255, 255,0), 3)
                    image = cv2.circle(image, landmarks[8], 5, (0, 255, 0), 3)

                    pyautogui.moveTo(self._video2screen(*landmarks[0]), _pause=False)

                    click_distance = np.linalg.norm(np.subtract(landmarks[4], landmarks[8]))
                    if self._click_toggle == False and click_distance < 20:
                        pyautogui.click(self._video2screen(*landmarks[0]))
                        PyImageUtil.putTextCenter(image, 'Clicked!', (w // 2, h // 2),color = (255,255,255))
                        self._click_toggle = not self._click_toggle
                    if self._click_toggle == True and click_distance > 30:
                        self._click_toggle = not self._click_toggle

                cv2.imshow('PyHandMouse', image)

                if cv2.waitKey(1) & 0xFF == 27:
                    break
        cap.release()

if __name__ == '__main__':
    PyHandMouse()