import cv2
import numpy as np

from PyQt5 import QtCore, QtGui

class Converter(QtCore.QObject):
    image_ready = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(Converter, self).__init__(parent)
        self.m_frame = np.array([])
        self.m_timer = QtCore.QBasicTimer()
        self.m_processAll = True
        self.m_image = QtGui.QImage()

    def set_size(self, width=640, height=480):
        self.width = width
        self.height = height

    def queue(self, frame):
        self.m_frame = frame
        if not self.m_timer.isActive():
            self.m_timer.start(0, self)

    def process(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.m_image = image.scaled(self.width, self.height, QtCore.Qt.KeepAspectRatio)
        self.image_ready.emit(QtGui.QImage(self.m_image))

    def timerEvent(self, event):
        if event.timerId() != self.m_timer.timerId():
            return
        self.process(self.m_frame)
        self.m_timer.stop()

    def process_all(self):
        return self.m_processAll

    def set_process_all(self, _all):
        self.m_processAll = _all

    def processFrame(self, frame):
        if self.m_processAll:
            self.process(frame)
        else:
            self.queue(frame)

    def image(self):
        return self.m_image

    image = QtCore.pyqtProperty(QtGui.QImage, fget=image, notify=image_ready, user=True)
    process_all = QtCore.pyqtProperty(bool, fget=process_all, fset=set_process_all)
