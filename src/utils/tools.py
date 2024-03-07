import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QLabel
from src.utils.face_detection import *


def BGR_to_RGB(img):
    """
    将opencv的BGR格式（numpy.ndarray）转换成RGB格式
    :param img: numpy.ndarray格式的图片
    :return: QImage格式的图片
    """
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    qimg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return qimg


def img_recognize(image_path):
    """
    识别图片中的人脸和眼睛
    :param image_path: 图片路径
    :return: 标注了人脸和眼睛的图片
    """
    img = cv.imread(image_path)
    img = face_detect(img)
    qimg = BGR_to_RGB(img)
    return qimg







