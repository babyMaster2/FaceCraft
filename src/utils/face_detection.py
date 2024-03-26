import cv2 as cv
# import dlib
import math
import numpy as np
import mediapipe as mp
import time

from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from src.utils.tools import fix_icon, process_effects, swap_non_effcet, get_landmarks


# 使用Haar Cascade 进行人脸识别
def face_detection_haar(func):
    def wrapper(img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        face_detector = cv.CascadeClassifier('../../data/models/haarcascade_frontalface_default.xml')
        eye_detector = cv.CascadeClassifier('../../data/models/haarcascade_eye.xml')

        faces = face_detector.detectMultiScale(gray, 1.05, 5, flags=cv.CASCADE_SCALE_IMAGE)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            eyes = eye_detector.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                func(img, x, y, w, h, roi_color, eyes)

        return img

    return wrapper


@face_detection_haar
def face_detect_haar(img, x, y, w, h, roi_color, eyes):
    cv.rectangle(img, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
    for (ex, ey, ew, eh) in eyes:
        cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), color=(255, 0, 0), thickness=2)

    return img


@face_detection_haar
def vfx_mianju(img, x, y, w, h, roi_color, eyes):
    overlay_img = cv.imread('../../data/icon/mj.png')
    overlay_img_resized = cv.resize(overlay_img, (w, h))
    # 在Python中，图像数据通常以numpy数组的形式存储，其中第一个维度（y轴）代表高
    # 度，第二个维度（x轴）代表宽度。
    img[y:y + h, x:x + w] = overlay_img_resized


def face_detection_dnn(func):
    def wrapper(img, *args, **kwargs):
        h, w, _ = img.shape

        # Create a YuNet object
        model = cv.FaceDetectorYN.create(
            model='../../data/models/face_detection_yunet_2023mar.onnx',
            config="",
            input_size=(w, h),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=5000,
            backend_id=0,
            target_id=0)

        # Detect faces in the image
        faces = model.detect(img)

        # Draw bounding boxes around the faces
        if faces[1] is not None:
            for face in faces[1]:
                func(img, face, *args, **kwargs)
        return img

    return wrapper


# 使用深度学习的DNN,进行人脸识别
@face_detection_dnn
def face_detect_dnn(img, face):
    landmark_color = [
        (255, 0, 0),  # right eye
        (0, 0, 255),  # left eye
        (0, 255, 0),  # nose tip
        (255, 0, 255),  # right mouth corner
        (0, 255, 255)  # left mouth corner
    ]
    bbox = face[0:4].astype(np.int32)
    cv.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)

    # conf = face[-1]
    cv.putText(img, f"Confidence: {face[-1]:.2f}", (bbox[0], bbox[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9,
               (0, 255, 0), 2)

    landmarks = face[4:14].astype(np.int32).reshape((5, 2))
    for idx, landmark in enumerate(landmarks):
        cv.circle(img, landmark, 2, landmark_color[idx], 2)
    return img


def face_detection_mediapipe(func):
    def wrapper(img, *args, **kwargs):
        """
        :param img: ndarray图像
        :return:人脸关键点列表，如[{0:(x,y),1:{x,y},...},{0:(x,y),1:(x,y)}]
        """
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,  # 静态图片设置为False,视频设置为True
            max_num_faces=3,  # 能检测的最大人脸数
            refine_landmarks=True,  # 是否需要对嘴唇、眼睛、瞳孔的关键点进行定位，
            min_detection_confidence=0.5,  # 人脸检测的置信度
            min_tracking_confidence=0.5)  # 人脸追踪的置信度（检测图像时可以忽略）

        func(img, mp_face_mesh, face_mesh, *args, **kwargs)

        return img  # 返回关键点列表和图像

    return wrapper


@face_detection_mediapipe
def face_detect_mediapipe(img, mp_face_mesh, face_mesh, ):
    results = face_mesh.process(cv.cvtColor(img, cv.COLOR_BGR2RGB))

    # mediapipe提供的绘制模块
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    if results.multi_face_landmarks:  # 如果检测到人脸关键点
        for face_landmarks in results.multi_face_landmarks:  # 遍历每个人脸的关键点
            # 绘制关键点和连接线
            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 0, 255),
                    thickness=2,
                    circle_radius=2),
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
            return img  # 返回关键点列表和图像


@face_detection_mediapipe
def add_vfx(img, mp_face_mesh, face_mesh, vfx_type, current_option):
    landmarks = get_landmarks(img, face_mesh)

    # ROI区域中心关键点
    center = {"hats": 10, "glasses": 168, "masks": 0}

    over_img = face_vfx[vfx_type][current_option]
    over_img_path = f'../../data/icon/{vfx_type}/{over_img}'

    icon_name = vfx_type

    for landmark in landmarks:
        effect, w, h = process_effects(landmark, over_img_path, icon_name)
        p = center[icon_name]
        roi = img[landmark[p][1] - int(h / 2):landmark[p][1] - int(h / 2) + h,
              landmark[p][0] - int(w / 2):landmark[p][0] - int(w / 2) + w]

        if effect.shape[:2] == roi.shape[:2]:
            # 消除特效图像中的白色背景区域

            effect = swap_non_effcet(effect, roi, 240)

            # 将处理好的特效添加到人脸图像上
            img[landmark[p][1] - int(h / 2):landmark[p][1] - int(h / 2) + h,
            landmark[p][0] - int(w / 2):landmark[p][0] - int(w / 2) + w] = effect

    return img


recognize_algorithms = {
    'haar': face_detect_haar,
    'dnn': face_detect_dnn,
    'mediapipe': face_detect_mediapipe
}

face_vfx = {
    'hats': {
        '01': 'hat_1.jpg',
        '02': 'hat_2.jpg',
        '03': 'hat_3.jpg',
        '04': 'hat_4.jpg',
        '05': 'hat_5.jpg',
        '06': 'hat_6.jpg'
    },
    'glasses': {
        '01': 'glass_1.jpg',
        '02': 'glass_2.jpg',
        '03': 'glass_3.jpg',
        '04': 'glass_4.jpg'
    },
    'masks': {
        '01': 'mask_1.jpg',
        '02': 'mask_2.jpg',
        '03': 'mask_3.jpg'
    }
}

if __name__ == '__main__':
    # img = cv.imread('../../data/img/555472.jpg')
    # img = add_vfx(img, vfx_type='hats', current_option='01')
    # img = cv.resize(img, (1280, 960))
    # cv.imshow('img', img)
    #
    # cv.waitKey(0)

    cap = cv.VideoCapture(0)
    while True:
        ret, img = cap.read()
        img = cv.flip(img, 1)

        img = add_vfx(img, vfx_type='masks', current_option='02')

        cv.imshow('img', img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
