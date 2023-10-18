import cv2
import numpy as np
import os
import easyocr
import jaro

from PyQt5 import QtCore

class Detector(QtCore.QObject):
    image_ready = QtCore.pyqtSignal(np.ndarray)
    show_message_box = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(Detector, self).__init__(parent)
        self.m_frame = np.array([])
        self.m_timer = QtCore.QBasicTimer()
        self.m_processAll = True
        self.m_image = None

        self.reader = easyocr.Reader(['en'])
        self.classifier = cv2.CascadeClassifier(
            os.path.join('Resources', 'haarcascade_russian_plate_number.xml')
        )
        self.plate = ''
        self.message = None

    def set_params(self, min_area=200, color=(255, 0, 255), similarity_threshold=0.8):
        self.min_area = min_area
        self.color = color
        self.similarity_threshold = similarity_threshold

    def queue(self, frame):
        self.m_frame = frame
        if not self.m_timer.isActive():
            self.m_timer.start(0, self)

    @QtCore.pyqtSlot()
    def search(self, plate):
        self.plate = plate
        self.message = None

    def process(self, frame):
        if not self.message:
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            number_plates = self.classifier.detectMultiScale(gray_image, 1.1, 10)
            for (x, y, w, h) in number_plates:
                area = w * h
                if area > self.min_area:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, 2)
                    detail_image = frame[y:y + h, x:x + w]
                    text = self.reader.readtext(detail_image)

                    if len(text) == 0:
                            continue

                    ocr_plate = text[0][1]
                    if self.plate != '':
                        similarity = self.get_similarity(self.plate, ocr_plate)
                        if similarity < self.similarity_threshold:
                            continue
                        else:
                            int_similarity = int(similarity*100)
                            self.message = f'Find car with {ocr_plate}, similarity {int_similarity}%'
                            self.show_message_box.emit(self.message)
                            break               

        self.image_ready.emit(frame)

    def get_similarity(self, plate, ocr_plate):
        return jaro.jaro_winkler_metric(plate, ocr_plate)

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

    image = QtCore.pyqtProperty(np.ndarray, fget=image, notify=image_ready, user=True)
    process_all = QtCore.pyqtProperty(bool, fget=process_all, fset=set_process_all)
