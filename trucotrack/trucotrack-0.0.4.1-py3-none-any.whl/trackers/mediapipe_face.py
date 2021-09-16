import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from ..processors import csv_gzip_writer as csv_writer

mp_faces = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class MediapipeFace:
    def __init__(self, args):
        self.args = args

        self.faces = mp_faces.FaceMesh(
            static_image_mode=args.mp_faces_static == 'no',
            max_num_faces=args.mp_faces_max)

        if self.args.mp_faces_csv != None:
            self.writer = csv_writer.CsvGzipWriter(self.args.mp_faces_csv, self.args)

    def process(self, dispatched):
        results = self.faces.process(dispatched['frame_rgb'])
        if not results.multi_face_landmarks:
            return []

        records = []
        for face_index, face_landmarks_message in enumerate(results.multi_face_landmarks):
            face_landmarks = MessageToDict(face_landmarks_message)['landmark']

            if self.args.mp_faces_draw == 'yes':
                self.draw(dispatched['frame'], face_landmarks_message)

            record = self.organize(
                face_index,
                face_landmarks,
                dispatched['frame'],
                dispatched['frame_number'])

            records.append(record)

        if hasattr(self, 'writer'):
            for record in records:
                self.writer.write(record)

        return records

    def draw(self, frame, face_landmarks_message):
        mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks_message,
            connections=mp_faces.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

        mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks_message,
            connections=mp_faces.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())

    def organize(self, face_index, face_landmarks, frame, frame_number):
        height, width, _ = frame.shape

        record = {
            'face_index': str(face_index),
            'frame_number': str(frame_number),
        }

        bone_id = 0
        for face_landmark in face_landmarks:
            bone_id += 1

            for axe in face_landmark:
                if axe == 'y':
                    scale = height
                else:
                    scale = width

                coordinate_name = 'face_' + str(bone_id) + '_' + axe
                record[coordinate_name] = '{:-f}'.format(face_landmark[axe] * scale)

        return record

    def close_writer(self):
        if hasattr(self, 'writer'):
            self.writer.close()
