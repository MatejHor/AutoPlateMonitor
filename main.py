import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from models.capture import Capture
from models.converter import Converter
from models.detector import Detector

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.display_width = 640
        self.display_height = 480

        lay = QtWidgets.QVBoxLayout(central_widget)
        toolbar_lay = QtWidgets.QToolBar("Detect toolbox")
        self.view = QtWidgets.QLabel()
        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_stop = QtWidgets.QPushButton("Stop")

        self.input_search = QtWidgets.QLineEdit()
        self.btn_search = QtWidgets.QPushButton('Search for plate')
        
        self.label_time = QtWidgets.QLabel()
        lay.addWidget(self.view, alignment=QtCore.Qt.AlignCenter)
        lay.addWidget(self.btn_start)
        lay.addWidget(self.btn_stop)

        toolbar_lay.addWidget(self.input_search)
        toolbar_lay.addWidget(self.btn_search)
        lay.addWidget(toolbar_lay)
        
        lay.addWidget(self.label_time, alignment=QtCore.Qt.AlignCenter)
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