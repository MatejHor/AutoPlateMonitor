import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia

from models.capture import Capture
from models.converter import Converter
from models.detector import Detector

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        central_widget = QtWidgets.QWidget()
        icon = os.path.join('resources', 'car_plate.ico')
        self.setWindowIcon(QtGui.QIcon(icon))
        self.setCentralWidget(central_widget)
        self.setWindowTitle('AutoPlateMonitor')

        self.display_width = 640
        self.display_height = 480

        lay = QtWidgets.QGridLayout(central_widget)

        self.view = QtWidgets.QLabel()
        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_stop = QtWidgets.QPushButton("Stop")
        lay.addWidget(self.view, 0, 0, 1, 2)
        lay.addWidget(self.btn_start, 1, 0, 1, 2)
        lay.addWidget(self.btn_stop, 2, 0, 1, 2)

        self.input_search = QtWidgets.QLineEdit()
        self.btn_search = QtWidgets.QPushButton('Search for plate')
        lay.addWidget(self.input_search, 3, 0)
        lay.addWidget(self.btn_search, 3, 1)

        self.select_camera = self.list_cameras()
        self.action_store = QtWidgets.QPushButton("Store")
        lay.addWidget(self.select_camera, 4, 0)
        lay.addWidget(self.action_store, 4, 1)

        self.view.setFixedSize(640, 400)
        self.show()
        self.init_camera()

    def init_camera(self):
        self.capture = Capture()
        self.detector = Detector()
        self.converter = Converter()
        self.detector.set_params(similarity_threshold=0.9)
        self.detector.set_process_all(False)
        self.converter.set_size(self.display_width, self.display_height)
        self.converter.set_process_all(False)

        capture_thread = QtCore.QThread(self)
        detector_thread = QtCore.QThread(self)
        converter_thread = QtCore.QThread(self)
        
        capture_thread.start()
        detector_thread.start()
        converter_thread.start()

        self.capture.moveToThread(capture_thread)
        self.detector.moveToThread(detector_thread)
        self.converter.moveToThread(converter_thread)

        self.capture.frameReady.connect(self.detector.processFrame)
        self.detector.image_ready.connect(self.converter.processFrame)
        self.converter.image_ready.connect(self.setImage)
        self.detector.show_message_box.connect(self.on_show_message_box)

        self.btn_start.clicked.connect(self.capture.start)
        self.btn_stop.clicked.connect(self.capture.stop)
        self.btn_search.clicked.connect(lambda: self.detector.search(self.input_search.text()))
        self.select_camera.currentIndexChanged.connect(self.change_camera)
        self.action_store.clicked.connect(self.store_video)

    def list_cameras(self):
        camera_selector = QtWidgets.QComboBox()
        self.available_cameras = QtMultimedia.QCameraInfo.availableCameras()

        camera_selector.setStatusTip("Choose camera to take pictures")
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        camera_selector.addItems([camera.description() for camera in self.available_cameras])
        return camera_selector
    
    def change_camera(self, index):
        camera_position = self.available_cameras[index].position()
        self.capture.set_camera(camera_position)

    def store_video(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Picture Location", "")

        if path:
            self.capture.store(path)

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        self.view.setPixmap(QtGui.QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.capture.stop()
        super(MainWindow, self).closeEvent(event)

    def on_show_message_box(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setWindowModality(False)
        msg.setText(message)
        msg.exec()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())