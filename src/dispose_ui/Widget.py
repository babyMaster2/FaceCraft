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
import time

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
        pixmap = pixmap.scaled(self.label.width(), self.label.height())
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
        self.face_recognition = False  # Add this line
        #  跟踪器
        self.tracker = cv.TrackerKCF_create()  # Add this line
        self.tracking = False  # Add this line

        self.ui.toolButton.mousePressEvent = self.cam_rec

    def display_camera(self):
        # todo  选择摄像头
        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000. / 24))  # 24 frames per second

    # def update_frame(self):
    #     ret, frame = self.cap.read()
    #     if ret:
    #         frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    #         if self.face_recognition:  # Add this line
    #             frame = face_detect(frame)
    #         img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
    #         pix = QPixmap.fromImage(img)
    #         pix = pix.scaled(self.display_label.width(), self.display_label.height())
    #         self.display_label.setPixmap(pix)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            if self.face_recognition and not self.tracking:  # Add this line
                face_locations = face_detect(frame)
                if len(face_locations) > 0:
                    # Ensure the bounding box is in the format (x, y, w, h)
                    bbox = tuple(face_locations[0])
                    if len(bbox) == 4:
                        self.tracker.init(frame, bbox)
                        self.tracking = True
            elif self.tracking:  # Add this line
                success, bbox = self.tracker.update(frame)
                if success:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                else:
                    self.tracking = False
            img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            pix = pix.scaled(self.display_label.width(), self.display_label.height())
            self.display_label.setPixmap(pix)

    def cam_rec(self, event):
        self.face_recognition = not self.face_recognition  # Add this line

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
            self.start_time = time.time()
            # Open the video file
            cap = cv.VideoCapture(self.video_path)

            # Get the video's width, height and frames per second (fps)
            width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv.CAP_PROP_FPS)

            # Define the codec and create a VideoWriter object
            fourcc = cv.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
            out = cv.VideoWriter('../../data/video/output/output.mp4', fourcc, fps, (width, height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                # Apply the vfx_mianju function to the frame
                frame = vfx_mianju(frame)

                # Write the frame into the file 'output.mp4'
                out.write(frame)
            out.release()
            cap.release()

            # Check if the video processing is finished
            if not cap.isOpened():
                self.end_time = time.time()
                print(f"Video processing finished in {self.end_time - self.start_time} seconds.")
                print("Video processing finished.")

    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video = MyVideo('../../data/video/shameless.mp4')
    video.display_video()
    sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # label = MyImg('../../data/img/lyf_01.png')
    # label.display_image()
    # sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # label = MyCam()
    # label.display_camera()
    # sys.exit(app.exec_())
