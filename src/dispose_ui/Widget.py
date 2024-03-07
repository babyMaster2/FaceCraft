from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QToolButton
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer
import cv2 as cv
import threading
import sys
from src.utils.tools import *
from src.utils.face_detection import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt


class MyImg(QWidget):
    def __init__(self, image_path=None):
        super().__init__()
        self.ui = loadUi("../../ui/widget_img.ui", self)
        self.label = self.ui.findChild(QLabel, "label")

        self.ui.show()

        self.image_path = image_path

        self.ui.toolButton.mousePressEvent = self.img_rec

        self.ui.comboBox.currentIndexChanged.connect(self.image_vfx)

    def display_image(self):
        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaled(self.label.width(),self.label.height())
        self.label.setPixmap(pixmap)

    def img_rec(self, event):
        qimg = img_recognize(self.image_path)
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(pixmap)

    def image_vfx(self, event):
        current_option = self.ui.comboBox.currentText()
        if current_option == '面具':
            img = cv.imread(self.image_path)

            img = vfx_mianju(img)
            qimg = BGR_to_RGB(img)

            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(self.label.width(), self.label.height())
            self.label.setPixmap(pixmap)


class MyCam(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("../../ui/widget_camera.ui", self)
        self.display_label = self.ui.findChild(QLabel, "label")
        self.ui.show()
        self.cap = None
        self.timer = None

    def display_camera(self):
        # todo  选择摄像头
        self.cap = cv.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000. / 24))  # 24 frames per second

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the image from OpenCV BGR format to PyQt RGB format
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            pix = pix.scaled(self.display_label.width(), self.display_label.height())
            self.display_label.setPixmap(pix)

    def closeEvent(self, a0):
        self.cap.release()
        self.timer.stop()
        super().closeEvent(a0)


class MyVideo(QVideoWidget):
    def __init__(self, video_path=None):
        super().__init__()

        self.ui = loadUi("../../ui/widget_video.ui", self)
        self.video_widget = self.ui.findChild(QVideoWidget, "videowidget")
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # self.tool = self.ui.findChild(QToolButton, "toolButton")

        self.video_path = video_path

        self.ui.show()

        self.ui.toolButton.mousePressEvent = self.video_play_paused
        self.ui.toolButton_2.mousePressEvent = self.video_666
        self.ui.toolButton_3.mousePressEvent = self.video_replay
        self.ui.comboBox.currentIndexChanged.connect(self.video_vfx)

        self.run = True
        self.lock = threading.Lock()

    def display_video(self):
        video_url = QUrl.fromLocalFile(self.video_path)
        self.media_player.setMedia(QMediaContent(video_url))
        self.media_player.play()

    def video_play_paused(self, event):
        with self.lock:
            if self.run:
                self.media_player.pause()
                self.run = False
            else:
                self.media_player.play()
                self.run = True

    def video_666(self, event):
        pass

    def video_replay(self, event):
        self.media_player.setPosition(0)
        self.media_player.play()

    def video_vfx(self, event):
        current_option = self.ui.comboBox.currentText()
        print(f"Current option is: {current_option}")
        if current_option == '面具':
            pass

    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video = MyVideo('D:/0_PyCode/FaceCraft/data/video/shameless.mp4')
    video.display_video()
    sys.exit(app.exec_())
    # app = QApplication(sys.argv)
    # label = MyImg('D:/0_PyCode/FaceCraft//data/img/lyf_01.png')
    # label.display_image()
    # sys.exit(app.exec_())
