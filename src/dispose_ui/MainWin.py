import sys

import cv2 as cv
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi

from Widget import MyImg,MyCam, MyVideo
# from src.utils.face_detection import show_single
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QUrl


class MyMainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("../../ui/main_win.ui", self)

        self.ui.show()

        # 添加点击事件处理函数
        self.ui.toolButton.mousePressEvent = self.select_image
        self.ui.toolButton_2.mousePressEvent = self.select_video
        self.ui.toolButton_3.mousePressEvent = self.select_camera
        self.ui.pushButton.clicked.connect(self.process)

        # 初始化文件路径
        self.image_path = False
        self.video_path = False
        self.camera = False

        self.choice_buttons = {
            'image_path': self.ui.toolButton,
            'video_path': self.ui.toolButton_2,
            'camera': self.ui.toolButton_3
        }

    def initialize_choice(self, *args):
        for arg in args:
            setattr(self, arg, False)
            self.choice_buttons[arg].setText('未选择')

    def select_image(self, event):
        self.image_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '', '图片文件 (*.jpg *.png)')
        if self.image_path:
            self.ui.toolButton.setText('已选择')
            self.initialize_choice('video_path', 'camera')
        else:  # 如果用户没有选择文件
            self.ui.toolButton.setText('未选择')

    def select_video(self, event):
        self.video_path, _ = QFileDialog.getOpenFileName(self, '选择视频', '', '视频文件 (*.avi *.mp4)')
        if self.video_path:
            self.ui.toolButton_2.setText('已选择')
            self.initialize_choice('image_path', 'camera')
        else:
            self.ui.toolButton_2.setText('未选择')

    def select_camera(self, event):
        self.camera = True
        self.ui.toolButton_3.setText('已选择')
        self.initialize_choice('image_path', 'video_path')

    def process(self):
        if self.image_path:
            label = MyImg(self.image_path)
            label.display_image("")

        elif self.video_path:
            video = MyVideo(self.video_path)
            video.display_video()

        elif self.camera:
            # cap = cv.VideoCapture(0)
            label = MyCam()
            label.display_camera()
        else:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MyMainWin()
    sys.exit(app.exec_())
