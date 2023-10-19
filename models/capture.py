import cv2
import numpy as np
import os

from PyQt5 import QtCore

class Capture(QtCore.QObject):
    started = QtCore.pyqtSignal()
    frameReady = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(Capture, self).__init__(parent)
        self._frame = None
        self.m_timer = QtCore.QBasicTimer()
        self.m_videoCapture = cv2.VideoCapture()
        self.camera = 0
        self.writer = None

    @QtCore.pyqtSlot()
    def start(self):
        if self.m_videoCapture is not None:
            self.m_videoCapture.release()
            self.m_videoCapture = cv2.VideoCapture(self.camera)
        if self.m_videoCapture.isOpened():
            self.m_timer.start(0, self)
            self.started.emit()

    @QtCore.pyqtSlot()
    def stop(self):
        self.m_timer.stop()

    @QtCore.pyqtSlot()
    def store(self, path):
        if not self.writer:
            path = os.path.join(path, 'data', 'output.avi')
            self.width = int(self.m_videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.m_videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
            self.writer = cv2.VideoWriter(path, self.codec, 30.0, (self.width, self.height))
        else:
            self.writer = None

    def set_camera(self, camera):
        self.camera = camera

    def __del__(self):
        self.m_videoCapture.release()

    def frame(self):
        return self.m_frame

    def timerEvent(self, event):
        if event.timerId() != self.m_timer.timerId():
            return

        ret, image = self.m_videoCapture.read()
        if not ret:
            self.m_timer.stop()
            return
        if self.writer:
            self.writer.write(image)

        self.m_frame = image    
        self.frameReady.emit(self.m_frame)

    frame = QtCore.pyqtProperty(np.ndarray, fget=frame, notify=frameReady, user=True)