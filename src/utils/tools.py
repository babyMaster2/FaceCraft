import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap, QMovie
import numpy as np
import math
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QLabel


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


def img_recognize(image_path, algorith):
    from src.utils.face_detection import recognize_algorithms
    """
    识别图片中的人脸和眼睛
    :param image_path: 图片路径
    :param algorith: 选择算法
    :return: 标注了人脸和眼睛的图片
    """
    img = cv.imread(image_path)
    img = recognize_algorithms[algorith](img)
    qimg = BGR_to_RGB(img)
    return qimg


def convert_qimage_to_mat(incoming_image):
    """ Converts a QImage to an opencv MAT format """

    incoming_image = incoming_image.convertToFormat(QImage.Format.Format_RGB888)

    width = incoming_image.width()
    height = incoming_image.height()

    ptr = incoming_image.bits()
    ptr.setsize(incoming_image.byteCount())
    arr = np.array(ptr).reshape(height, width, 3)  # Copies the data
    arr = cv.cvtColor(arr, cv.COLOR_RGB2BGR)
    return arr


def fix_icon(small_img_gray, small_img, icon, kind):
    mask = cv.adaptiveThreshold(small_img_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 15, 2)
    if kind == 'hat':
        kernel = np.ones((10, 10), np.uint8)
    elif kind == 'glass':
        kernel = np.ones((5, 5), np.uint8)
    else:
        kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    mask_inv = cv.bitwise_not(mask)
    glass_bg_1 = cv.bitwise_and(small_img, small_img, mask=mask_inv)
    glass_fg_2 = cv.bitwise_and(icon, icon, mask=mask)
    dst = cv.add(glass_bg_1, glass_fg_2)
    return dst


def swap_non_effcet(effect, roi, threshold=240):
    """
    消除特效图像中的白色背景区域
    :param effect: 特效图像
    :param roi: ROI区域
    :param threshold: 阈值
    :return: 消除背景后的特效图像
    """

    # （1）特效图像灰度化
    effect2gray = cv.cvtColor(effect, cv.COLOR_BGR2GRAY)
    # （2）特效图像二值化
    ret, effect2wb = cv.threshold(effect2gray, threshold, 255, cv.THRESH_BINARY)
    # （3）消除特效的白色背景
    effectwb = cv.bitwise_and(roi, roi, mask=effect2wb)

    # （4）反转二值化后的特效
    effect2wb_ne = cv.bitwise_not(effect2wb)
    # （5）处理彩色特效
    effectcolor = cv.bitwise_and(effect, effect, mask=effect2wb_ne)
    # (6) 组合彩色特效与黑色特效
    effect_final = cv.add(effectcolor, effectwb)

    return effect_final


def process_effects(landmarks, icon_path, icon_name):
    """
    处理特效图像
    :param landmarks: 检测到的人脸关键点列表
    :param icon_path: 特效图像地址
    :param icon_name: 特效名称
    :return:处理好的特效图像、特效宽、特效高
    """
    # 特效关键点，用于调整特效的尺寸
    effect_landmarks = {
        "hats": ((landmarks[132][0], landmarks[5][1]), (landmarks[361][0], landmarks[0][1])),
        "glasses": ((landmarks[127][0], landmarks[151][1]), (landmarks[356][0], landmarks[195][1])),
        "masks": ((landmarks[162][0] - 20, landmarks[10][1] - 20), (landmarks[389][0] + 20, landmarks[195][1] + 20))
    }

    # 读取特效图像
    icon = cv.imread(icon_path)
    # 选择特效关键点
    pt1, pt2 = effect_landmarks[icon_name]
    x, y, x_w, y_h = pt1[0], pt1[1], pt2[0], pt2[1]
    # 调整特效的尺寸
    w, h = x_w - x, y_h - y
    effect = cv.resize(icon, (w, h))

    return effect, w, h


# 获取人脸关键点
def get_landmarks(image, face_mesh):
    """
    :param image: ndarray图像
    :param face_mesh: 人脸检测模型
    :return:人脸关键点列表，如[{0:(x,y),1:{x,y},...},{0:(x,y),1:(x,y)}]
    """
    landmarks = []
    height, width = image.shape[0:2]
    # 人脸关键点检测
    results = face_mesh.process(cv.cvtColor(image, cv.COLOR_BGR2RGB))
    # 解释检测结果
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            i = 0
            points = {}
            # 根据图像的高度和宽度还原关键点位置
            for landmark in face_landmarks.landmark:
                x = math.floor(landmark.x * width)
                y = math.floor(landmark.y * height)
                points[i] = (x, y)
                i += 1
            landmarks.append(points)

    return landmarks
