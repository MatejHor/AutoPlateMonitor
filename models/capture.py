import cv2
import numpy as np

from PyQt5 import QtCore

class Capture(QtCore.QObject):
    started = QtCore.pyqtSignal()
    frameReady = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(Capture, self).__init__(parent)
        self._frame = None
        self.m_timer = QtCore.QBasicTimer()
        self.m_videoCapture = cv2.VideoCapture()

    @QtCore.pyqtSlot()
    def start(self, cam=0):
        if self.m_videoCapture is not None:
            self.m_videoCapture.release()
            self.m_videoCapture = cv2.VideoCapture(cam)
        if self.m_videoCapture.isOpened():
            self.m_timer.start(0, self)
            self.started.emit()

    @QtCore.pyqtSlot()
    def stop(self):
        self.m_timer.stop()

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
        self.m_frame = image    
        self.frameReady.emit(self.m_frame)

    frame = QtCore.pyqtProperty(np.ndarray, fget=frame, notify=frameReady, user=True)