import cv2
import numpy as np


def get_camera_matrix_1(h, w):
    ''' 1强 '''
    x, y = w / 2., h / 2.
    f_x = x / np.tan(60 / 2 * np.pi / 180)
    f_y = f_x
    camera_matrix = np.array(
        [[f_x, 0, x],
         [0, f_y, y],
         [0, 0, 1]], dtype="double"
    )
    return camera_matrix


def get_camera_matrix_2(h, w):
    x, y = w / 2., h / 2.
    camera_matrix = np.array(
        [[w, 0, x],
         [0, w, y],
         [0, 0, 1]], dtype="double"
    )
    return camera_matrix


def calc_euler_angles(landmarks_3D, landmarks_2D, camera_matrix,
                      camera_distortion=np.zeros((4, 1)),
                      ):
    '''
    2d点到3D空间的欧拉角
    :param landmarks_3D:
    :param landmarks_2D:
    :param camera_matrix:
    :param camera_distortion:
    :return:
    '''
    success, rotation_vector, translation_vector = cv2.solvePnP(
        landmarks_3D,  # (num_keypoints,3) 世界坐标 人脸 3D模型坐标
        landmarks_2D,  # (num_keypoints,2) 图像坐标系中点的坐标 xy
        camera_matrix,  # (3,3) 相机内参矩阵  通过标定
        camera_distortion,  # (4,1) 畸变系数  通过标定
        flags=cv2.SOLVEPNP_ITERATIVE)

    rmat, _ = cv2.Rodrigues(rotation_vector)
    pose_mat = cv2.hconcat((rmat, translation_vector))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
    # np -> double (3, 1) -> [3]
    # pitch, yaw, roll = euler_angles.squeeze(-1).tolist()
    pitch, yaw, roll = euler_angles.squeeze(-1)

    return pitch, yaw, roll


if __name__ == '__main__':
    ''' ----------------- 关键对应点 ------------------ '''
    face_68_1 = [17, 21, 22, 26, 36, 39, 42, 45, 31, 35, 48, 54, 57, 8]
    face_98_1 = [33, 38, 50, 46, 60, 64, 68, 72, 55, 59, 76, 82, 85, 16]
    face_68_2 = [30, 8, 36, 45, 48, 54]

    ''' ----------------- 人脸模型1 优 ------------------ '''
    HUMAN_FACE_3D_1 = np.float32([
        [6.825897, 6.760612, 4.402142],  # LEFT_EYEBROW_LEFT,
        [1.330353, 7.122144, 6.903745],  # LEFT_EYEBROW_RIGHT,
        [-1.330353, 7.122144, 6.903745],  # RIGHT_EYEBROW_LEFT,
        [-6.825897, 6.760612, 4.402142],  # RIGHT_EYEBROW_RIGHT,
        [5.311432, 5.485328, 3.987654],  # LEFT_EYE_LEFT,
        [1.789930, 5.393625, 4.413414],  # LEFT_EYE_RIGHT,
        [-1.789930, 5.393625, 4.413414],  # RIGHT_EYE_LEFT,
        [-5.311432, 5.485328, 3.987654],  # RIGHT_EYE_RIGHT,
        [-2.005628, 1.409845, 6.165652],  # NOSE_LEFT,
        [-2.005628, 1.409845, 6.165652],  # NOSE_RIGHT,
        [2.774015, -2.080775, 5.048531],  # MOUTH_LEFT,
        [-2.774015, -2.080775, 5.048531],  # MOUTH_RIGHT,
        [0.000000, -3.116408, 6.097667],  # LOWER_LIP,
        [0.000000, -7.415691, 4.070434],  # CHIN
    ])

    HUMAN_FACE_3D_2 = np.array([
        (0.0, 0.0, 0.0),  # Nose tip 鼻子
        (0.0, -330.0, -65.0),  # Chin 下巴
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne 眼
        (-150.0, -150.0, -125.0),  # Left Mouth corner 嘴
        (150.0, -150.0, -125.0)  # Right mouth corner
    ])

    h, w = [256, 256]
    camera_matrix_1 = get_camera_matrix_1(h, w)
