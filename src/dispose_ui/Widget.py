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
from PyQt5.QtWidgets import QFileDialog, QLCDNumber


class MyImg(QWidget):
    def __init__(self, image_path=None):
        super().__init__()
        self.ui = loadUi("../../ui/widget_img.ui", self)
        self.label = self.ui.findChild(QLabel, "label")
        self.ui.toolButton_1.mousePressEvent = self.img_rec
        self.ui.toolButton_2.mousePressEvent = self.img_save
        self.ui.toolButton_3.mousePressEvent = self.display_image
        self.ui.toolButton_4.mousePressEvent = self.change_image

        self.ui.comboBox_1.currentIndexChanged.connect(self.choose_algorithm)
        self.ui.comboBox_2.currentIndexChanged.connect(self.hat_choose)
        self.ui.comboBox_3.currentIndexChanged.connect(self.glass_choose)
        self.ui.comboBox_4.currentIndexChanged.connect(self.mask_choose)

        self.algorith = 'haar'
        self.choose_algorithm("")
        self.image_path = image_path
        self.lcd_value = self.ui.lcdNumber.value()

        self.ui.show()

    def display_image(self, event):
        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(pixmap)

    def img_rec(self, event):
        time_start = time.time()

        qimg = img_recognize(self.image_path, self.algorith)

        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(pixmap)

        time_end = time.time()
        self.lcd_value = time_end - time_start
        self.ui.lcdNumber.display(self.lcd_value)

    def img_save(self, event):
        img = self.label.pixmap().toImage()
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, '保存图片', '', '图片文件 (*.jpg *.png)')
        if save_path:
            img.save(save_path)

    def change_image(self, event):
        file_dialog = QFileDialog()
        img_path = self.image_path
        self.image_path, _ = file_dialog.getOpenFileName(self, '选择图片', '', '图片文件 (*.jpg *.png)')
        if self.image_path:
            self.display_image(event)
        else:
            self.image_path = img_path

    def vfx_choose(self, event, combobox, vfx_type):
        current_option = combobox.currentText()

        img = self.label.pixmap().toImage()
        img = convert_qimage_to_mat(img)

        img = add_vfx(img, vfx_type, current_option)

        qimg = BGR_to_RGB(img)
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(pixmap)

    def hat_choose(self, event):
        self.vfx_choose(event, self.ui.comboBox_2, 'hats')

    def glass_choose(self, event):
        self.vfx_choose(event, self.ui.comboBox_3, 'glasses')

    def mask_choose(self, event):
        self.vfx_choose(event, self.ui.comboBox_4, 'masks')

    def choose_algorithm(self, event):
        current_option = self.ui.comboBox_1.currentText()
        self.algorith = current_option

    def closeEvent(self, a0):
        super().closeEvent(a0)


class MyCam(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("../../ui/widget_camera.ui", self)
        self.display_label = self.ui.findChild(QLabel, "label")

        self.algorith = 'haar'
        self.cap = None
        self.timer = None
        self.face_recognition = False  # Add this line

        self.face_vfx = False
        self.vfx_dict = {}

        self.ui.toolButton_1.mousePressEvent = self.cam_rec
        self.ui.toolButton_2.mousePressEvent = self.change_camera
        self.ui.toolButton_3.mousePressEvent = self.cleared_thing

        self.ui.comboBox_1.currentIndexChanged.connect(self.choose_algorithm)
        self.ui.comboBox_2.currentIndexChanged.connect(self.hat_choose)
        self.ui.comboBox_3.currentIndexChanged.connect(self.glass_choose)
        self.ui.comboBox_4.currentIndexChanged.connect(self.mask_choose)

        self.lcd_value = self.ui.lcdNumber.value()

        self.ui.show()

    def display_camera(self, event):
        # todo  选择摄像头
        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start()  # 24 frames per second

    def update_frame(self):
        tm = cv.TickMeter()  # Create a TickMeter object
        tm.start()  # Start the timer

        ret, frame = self.cap.read()

        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            if self.face_recognition:  # Add this line
                frame = recognize_algorithms[self.algorith](frame)
            if self.face_vfx:
                for vfx_type, current_option in self.vfx_dict.items():
                    frame = add_vfx(frame, vfx_type, current_option)

            img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

            pix = QPixmap.fromImage(img)
            pix = pix.scaled(self.display_label.width(), self.display_label.height())
            self.display_label.setPixmap(pix)

        tm.stop()  # Stop the timer
        fps = 1 / tm.getTimeSec()  # Calculate the FPS
        self.lcd_value = fps
        self.ui.lcdNumber.display(self.lcd_value)

    def cam_rec(self, event):
        self.face_recognition = not self.face_recognition  # Add this line

    def hat_choose(self, event):
        self.vfx_choose(event, self.ui.comboBox_2, 'hats')

    def glass_choose(self, event):
        self.vfx_choose(event, self.ui.comboBox_3, 'glasses')

    def mask_choose(self, event):
        self.vfx_choose(event, self.ui.comboBox_4, 'masks')

    def vfx_choose(self, event, combobox, vfx_type):
        current_option = combobox.currentText()
        self.face_vfx = True
        self.vfx_dict[vfx_type] = current_option

    def choose_algorithm(self, event):
        current_option = self.ui.comboBox_1.currentText()
        self.algorith = current_option

    def change_camera(self, event):
        pass

    def cleared_thing(self, event):
        self.face_recognition = False
        self.face_vfx = False
        self.vfx_dict = {}

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
        self.algorith = 'haar'

        self.ui.toolButton.mousePressEvent = self.video_play_paused
        self.ui.toolButton_2.mousePressEvent = self.video_666
        self.ui.toolButton_3.mousePressEvent = self.video_replay

        self.ui.comboBox_1.currentIndexChanged.connect(self.choose_algorithm)
        self.ui.comboBox_2.currentIndexChanged.connect(self.video_vfx)

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

    def choose_algorithm(self, event):
        current_option = self.ui.comboBox_1.currentText()
        self.algorith = current_option

    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # video = MyVideo('../../data/video/shameless.mp4')
    # video.display_video()
    # sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # label = MyImg('../../data/img/555472.jpg')
    # label.display_image("")
    # sys.exit(app.exec_())

    app = QApplication(sys.argv)
    label = MyCam()
    label.display_camera("")
    sys.exit(app.exec_())
