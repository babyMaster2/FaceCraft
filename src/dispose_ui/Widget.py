from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QToolButton, QMessageBox, QSpinBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimediaWidgets import QVideoWidget
import queue
from PyQt5.QtCore import QUrl, QTimer
import cv2 as cv
import threading
import sys
from src.utils.tools import *
from src.utils.face_detection import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import time
from PyQt5.QtWidgets import QFileDialog, QLCDNumber
from PyQt5.QtWidgets import QProgressBar


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

        # img = img.scaled(self.label.width(), self.label.height())

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

        self.video_path = video_path

        self.ui.show()

        self.run = True
        self.cap = None
        self.timer = None
        self.vfx_thread = None

        self.ui.spinBox = self.ui.findChild(QSpinBox, "spinbox")
        self.ui.toolButton_1.mousePressEvent = self.add_video_vfx
        self.ui.toolButton_2.mousePressEvent = self.video_play_paused
        self.ui.toolButton_3.mousePressEvent = self.video_replay
        self.ui.toolButton_4.mousePressEvent = self.change_video

        self.ui.progressBar = self.ui.findChild(QProgressBar, "progressBar")

        self.ui.comboBox_2.currentIndexChanged.connect(self.hat_choose)
        self.ui.comboBox_3.currentIndexChanged.connect(self.glass_choose)
        self.ui.comboBox_4.currentIndexChanged.connect(self.mask_choose)

        self.label_1 = self.ui.findChild(QLabel, "label")
        self.label_2 = self.ui.findChild(QLabel, "label_2")
        self.label_3 = self.ui.findChild(QLabel, "label_3")

        self.lock = threading.Lock()

    def display_video(self, event):
        video_url = QUrl.fromLocalFile(self.video_path)
        self.media_player.setMedia(QMediaContent(video_url))
        self.media_player.play()

    def add_video_vfx(self, event):
        if self.vfx_thread and self.vfx_thread.isRunning():
            reply = QMessageBox.question(self, 'Message',
                                         "当前有任务在进行，是否终结",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.vfx_thread.quit()  # Use quit instead of terminate
                self.vfx_thread.wait()  # Wait for the thread to finish
            else:
                return
        else:
            current_vfx_hat = self.ui.comboBox_2.currentText()
            current_vfx_glass = self.ui.comboBox_3.currentText()
            current_vfx_mask = self.ui.comboBox_4.currentText()

            vfx_dict = {
                'hats': current_vfx_hat,
                'glasses': current_vfx_glass,
                'masks': current_vfx_mask
            }

            file_dialog = QFileDialog()
            save_path, _ = file_dialog.getSaveFileName(self, '保存视频', '', '视频文件 (*.mp4)')

            self.vfx_thread = VFXThread(self.video_path, vfx_dict, self.ui.spinBox.value(), save_path)
            self.vfx_thread.progress_signal.connect(self.ui.progressBar.setValue)
            self.vfx_thread.finished.connect(self.on_vfx_thread_finished)  # Connect the finished signal to a slot
            self.vfx_thread.start()

            self.ui.comboBox_2.setEnabled(False)
            self.ui.comboBox_3.setEnabled(False)
            self.ui.comboBox_4.setEnabled(False)
            self.ui.spinBox.setEnabled(False)

    def on_vfx_thread_finished(self):
        # Enable comboBoxes when processing finishes
        self.ui.comboBox_2.setEnabled(True)
        self.ui.comboBox_3.setEnabled(True)
        self.ui.comboBox_4.setEnabled(True)
        self.ui.spinBox.setEnabled(True)

    def video_play_paused(self, event):
        with self.lock:
            if self.run:
                self.media_player.pause()
                self.run = False
            else:
                self.media_player.play()
                self.run = True

    def video_replay(self, event):
        self.media_player.setPosition(0)
        self.media_player.play()

    def change_video(self, event):
        file_dialog = QFileDialog()
        video_path = self.video_path
        self.video_path, _ = file_dialog.getOpenFileName(self, '选择视频', '', '视频文件 (*.mp4 *.avi)')
        if self.video_path:
            self.display_video("")
        else:
            self.video_path = video_path

    def hat_choose(self, event):
        path = face_vfx['hats'][self.ui.comboBox_2.currentText()]
        pixmap = QPixmap(f'../../data/icon/hats/{path}')
        pixmap = pixmap.scaled(self.label_1.width(), self.label_1.height())
        self.label_1.setPixmap(pixmap)
        # self.vfx_choose(event, self.ui.comboBox_2, 'hats')

    def glass_choose(self, event):
        path = face_vfx['glasses'][self.ui.comboBox_3.currentText()]
        pixmap = QPixmap(f'../../data/icon/glasses/{path}')
        pixmap = pixmap.scaled(self.label_2.width(), self.label_2.height())
        self.label_2.setPixmap(pixmap)
        # self.vfx_choose(event, self.ui.comboBox_3, 'glasses')

    def mask_choose(self, event):
        path = face_vfx['masks'][self.ui.comboBox_4.currentText()]
        pixmap = QPixmap(f'../../data/icon/masks/{path}')
        pixmap = pixmap.scaled(self.label_3.width(), self.label_3.height())
        self.label_3.setPixmap(pixmap)
        # self.vfx_choose(event, self.ui.comboBox_4, 'masks')

    def closeEvent(self, event):
        if self.vfx_thread and self.vfx_thread.isRunning():
            reply = QMessageBox.question(self, 'Message',
                                         "当前有任务在进行，是否终结",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.vfx_thread.quit()  # Use quit instead of terminate
                self.vfx_thread.wait()  # Wait for the thread to finish
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class VFXThread(QThread):
    progress_signal = pyqtSignal(int)  # Add this line
    finished = pyqtSignal()  # Add this line

    def __init__(self, video_path, vfx_dict, spinBox_value, save_path=None):
        super().__init__()
        self.video_path = video_path
        self.vfx_dict = vfx_dict
        self.save_path = save_path
        self.skip_frames = int(spinBox_value)

    def run(self):
        cap = cv.VideoCapture(self.video_path)

        total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        total_frames = total_frames // self.skip_frames  # Add this line

        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv.CAP_PROP_FPS))

        if not self.save_path:
            return

        fourcc = cv.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
        out = cv.VideoWriter(self.save_path, fourcc, fps, (width, height))

        processed_frames = 0
        frame_counter = 0  # Add this line

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_counter += 1  # Add this line
                if frame_counter % self.skip_frames == 0:  # Add this line
                    for vfx_type, current_option in self.vfx_dict.items():
                        frame = add_vfx(frame, vfx_type, current_option)
                    out.write(frame)

                    processed_frames += 1
                    progress = int((processed_frames / total_frames) * 100)
                    self.progress_signal.emit(progress)
                    print(f'Progress: {progress}%')

            else:
                break
        cap.release()
        out.release()

        self.finished.emit()


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # video = MyVideo('../../data/video/dy.mp4')
    # video.display_video("")
    # sys.exit(app.exec_())

    app = QApplication(sys.argv)
    label = MyImg('../../data/img/555472.jpg')
    label.display_image("")
    sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # label = MyCam()
    # label.display_camera("")
    # sys.exit(app.exec_())
