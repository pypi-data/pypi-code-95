import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from ..processors import csv_gzip_writer as csv_writer

mp_poses = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class MediapipePose:
    BONES = [
        'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
        'right_eye_inner', 'right_eye', 'right_eye_outer',
        'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
        'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
        'left_index', 'right_index', 'left_thumb', 'right_thumb',
        'left_hip', 'right_hip', 'left_knee', 'right_knee',
        'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
        'left_foot_index', 'right_foot_index']

    def __init__(self, args):
        self.args = args

        self.poses = mp_poses.Pose(
            static_image_mode=args.mp_poses_static == 'no',
            smooth_landmarks=True)

        if self.args.mp_poses_csv != None:
            self.writer = csv_writer.CsvGzipWriter(self.args.mp_poses_csv, self.args)

    def process(self, dispatched_frame):
        frame = dispatched_frame['frame']
        frame_rgb = dispatched_frame['frame_rgb']
        frame_number = dispatched_frame['frame_number']

        results = self.poses.process(frame_rgb)
        if not results.pose_landmarks:
            return []

        pose_landmarks_message = MessageToDict(results.pose_landmarks)['landmark']

        records = []
        self.draw(frame, results.pose_landmarks)
        record = self.organize(pose_landmarks_message, frame, frame_number)
        records.append(record)

        if hasattr(self, 'writer'):
            for record in records:
                self.writer.write(record)

        return records

    def draw(self, frame, pose_landmarks_message):
        if self.args.mp_poses_draw == 'yes':
            mp_drawing.draw_landmarks(
                frame,
                pose_landmarks_message,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

    def organize(self, pose_landmarks, frame, frame_number):
        height, width, _ = frame.shape

        record = {
            'frame_number': str(frame_number),
        }

        for bone_id, bone in enumerate(self.BONES):
            bone_landmarks = pose_landmarks[bone_id]
            bone_name = self.BONES[bone_id]

            for axe in ('x', 'y', 'z'):
                if axe == 'y':
                    scale = height
                else:
                    scale = width

                bone_landmark = bone_landmarks[axe] * scale
                record[bone_name + '_' + axe] = '{:-f}'.format(bone_landmark)

        return record

    def close_writer(self):
        if hasattr(self, 'writer'):
            self.writer.close()
