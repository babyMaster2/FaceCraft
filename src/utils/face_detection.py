import cv2 as cv

import numpy as np
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap


# def show_single(cap):
#     flag, frame = cap.read()
#     if flag:
#         gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#         img = QImage(gray.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
#         return QPixmap.fromImage(img)
#     else:
#         cap.release()
#         return None
def face_eye_detection(func):
    def wrapper(img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        face_detector = cv.CascadeClassifier('../../data/models/haarcascade_frontalface_default.xml')
        eye_detector = cv.CascadeClassifier('../../data/models/haarcascade_eye.xml')

        faces = face_detector.detectMultiScale(gray, 1.05, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            eyes = eye_detector.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                func(img, x, y, w, h, roi_color, eyes)

        return img
    return wrapper


@face_eye_detection
def face_detect(img, x, y, w, h, roi_color, eyes):
    cv.rectangle(img, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
    for (ex, ey, ew, eh) in eyes:
        cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), color=(255, 0, 0), thickness=2)

    return img


@face_eye_detection
def vfx_mianju(img, x, y, w, h, roi_color, eyes):
    overlay_img = cv.imread('../../data/icon/mj.png')
    overlay_img_resized = cv.resize(overlay_img, (w, h))
    # 在Python中，图像数据通常以numpy数组的形式存储，其中第一个维度（y轴）代表高
    # 度，第二个维度（x轴）代表宽度。
    img[y:y + h, x:x + w] = overlay_img_resized
