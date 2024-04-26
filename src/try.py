import cv2 as cv
import math
import mediapipe as mp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.face_detection import add_vfx


# def face_detection_haar(img):
#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#
#     face_detector = cv.CascadeClassifier('../../data/models/haarcascade_frontalface_default.xml')
#     eye_detector = cv.CascadeClassifier('../../data/models/haarcascade_eye.xml')
#
#     faces = face_detector.detectMultiScale(gray, 1.05, 5, flags=cv.CASCADE_SCALE_IMAGE)
#
#     for (x, y, w, h) in faces:
#         roi_gray = gray[y:y + h, x:x + w]
#         roi_color = img[y:y + h, x:x + w]
#
#         eyes = eye_detector.detectMultiScale(roi_gray)
#         if len(eyes) >= 2:
#             cv.rectangle(img, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
#             for (ex, ey, ew, eh) in eyes:
#                 cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), color=(255, 0, 0), thickness=2)
#
#     return img

# def face_detection_mediapipe(img):
#     mp_face_mesh = mp.solutions.face_mesh
#     face_mesh = mp_face_mesh.FaceMesh(
#         static_image_mode=True,  # 静态图片设置为False,视频设置为True
#         max_num_faces=3,  # 能检测的最大人脸数
#         refine_landmarks=True,  # 是否需要对嘴唇、眼睛、瞳孔的关键点进行定位，
#         min_detection_confidence=0.5,  # 人脸检测的置信度
#         min_tracking_confidence=0.5)  # 人脸追踪的置信度（检测图像时可以忽略）
#
#     results = face_mesh.process(cv.cvtColor(img, cv.COLOR_BGR2RGB))
#
#     # mediapipe提供的绘制模块
#     mp_drawing = mp.solutions.drawing_utils
#     mp_drawing_styles = mp.solutions.drawing_styles
#
#     if results.multi_face_landmarks:  # 如果检测到人脸关键点
#         for face_landmarks in results.multi_face_landmarks:  # 遍历每个人脸的关键点
#             # 绘制关键点和连接线
#             mp_drawing.draw_landmarks(
#                 image=img,
#                 landmark_list=face_landmarks,
#                 connections=mp_face_mesh.FACEMESH_TESSELATION,
#                 landmark_drawing_spec=mp_drawing.DrawingSpec(
#                     color=(0, 0, 255),
#                     thickness=2,
#                     circle_radius=2),
#                 connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
#             return img  # 返回关键点列表和图像


def face_detection_dnn(img):
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




