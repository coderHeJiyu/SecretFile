from PyQt5.QtCore import QThread, pyqtSignal
from Coder import Coder


class EncodeThread(QThread, Coder):
    sig = pyqtSignal(bool)
    progress_sig = pyqtSignal(int)
    status_sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super(EncodeThread, self).__init__(parent)

    # def __del__(self):
    #     self.wait()

    def set_data(self, src, dst, password):
        self.src = src
        self.dst = dst
        self.password = password

    def progress_change(self):
        self.progress_sig.emit(self.progress)

    def count_done(self):
        self.status_sig.emit("   加密中，请等待...   ")


    def run(self):
        self.encode(self.src, self.dst, self.password)
        self.sig.emit(True)


class DecodeThread(QThread, Coder):
    sig = pyqtSignal(bool)
    progress_sig = pyqtSignal(int)
    status_sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DecodeThread, self).__init__(parent)

    # def __del__(self):
    #     self.wait()

    def set_data(self, src, dst, password):
        self.src = src
        self.dst = dst
        self.password = password

    def progress_change(self):
        self.progress_sig.emit(self.progress)

    def count_done(self):
        self.status_sig.emit("   解密中，请等待...   ")

    def run(self):
        if not self.decode(self.src, self.dst, self.password):
            self.sig.emit(False)
        else:
            self.sig.emit(True)
