import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from trucotrack.processors import csv_gzip_writer as csv_writer

class MediapipePose:
    def __init__(self, args):
        self.args = args

        self.mp_poses = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.poses = self.mp_poses.Pose(
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

        pose_landmarks = results.pose_landmarks.landmark

        if self.args.mp_poses_draw == 'yes':
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())

        records = []
        record = self.organize(pose_landmarks, frame, frame_number)
        records.append(record)

        if hasattr(self, 'writer'):
            for record in records:
                self.writer.write(record)

        return records

    def organize(self, pose_landmarks, frame, frame_number):
        height, width, _ = frame.shape

        record = {
            'frame_number': str(frame_number),
        }

        bone_id = 0
        for pose_landmark in pose_landmarks:
            bone_id += 1

            coordinate_x = 'pose_' + str(bone_id) + '_x'
            record[coordinate_x] = '{:-f}'.format(pose_landmark.x * width)
            coordinate_y = 'pose_' + str(bone_id) + '_y'
            record[coordinate_y] = '{:-f}'.format(pose_landmark.y * height)
            coordinate_z = 'pose_' + str(bone_id) + '_z'
            record[coordinate_z] = '{:-f}'.format(pose_landmark.z * width)

        return record

    def close_writer(self):
        if hasattr(self, 'writer'):
            self.writer.close()
