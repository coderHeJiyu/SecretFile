from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QBasicTimer, pyqtSignal
import sys
import Coder
from mainWindow import Ui_MainWindow


class EncodeThread(QThread):
    sig = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(EncodeThread, self).__init__(parent)

    def __del__(self):
        self.wait()

    def set_data(self, src, dst, password):
        self.src = src
        self.dst = dst
        self.password = password

    def run(self):
        Coder.encode(self.src, self.dst, self.password)
        self.sig.emit(True)


class DecodeThread(QThread):
    sig = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(DecodeThread, self).__init__(parent)

    def __del__(self):
        self.wait()

    def set_data(self, src, dst, password):
        self.src = src
        self.dst = dst
        self.password = password

    def run(self):
        if not Coder.decode(self.src, self.dst, self.password):
            self.sig.emit(False)
        else:
            self.sig.emit(True)


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    time_stop_sig = pyqtSignal()
    progress_bar_sig = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.set_more_ui()

    def set_more_ui(self):
        '''
        手写部分UI
        '''
        self.progress_value = 0
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.statusBar.addPermanentWidget(self.progressBar, stretch=4)
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setText("   等待文件输入...   ")
        self.statusBar.addPermanentWidget(self.statusLabel, stretch=1)
        self.setAcceptDrops(True)

    def timerEvent(self, event):
        '''
        @override 计数器事件
        '''
        if self.progress_value >= 99:
            self.time_stop_sig.emit()
            return
        self.progress_value = self.progress_value + 1
        self.progress_bar_sig.emit(self.progress_value)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        '''
        @override 拖入事件
        '''
        # 防冲突
        if timer.isActive():
            return
        # 界面更新
        self.button_lock()
        self.progress_bar_sig.emit(0)
        # 数据更新
        self.src = event.mimeData().urls()[0].toLocalFile()
        # 界面更新(分支处理)
        if self.src is not None and len(self.src) != 0:
            self.statusLabel.setText("   文件已拽入!!!   ")
            self.lineEdit.setText(self.src)
            if self.src.endswith(".hlx"):
                self.pushButton_3.setEnabled(True)
            elif self.src.endswith(".mp4"):
                self.pushButton_2.setEnabled(True)
            else:
                self.statusLabel.setText("   不支持的文件格式!   ")

    def progress_updata(self, value):
        '''
        进度条更新
        '''
        self.progressBar.setValue(value)

    def button_lock(self):
        '''
        锁定“加密”和“解密”按钮
        '''
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

    def open_file(self):
        '''
        “打开”按钮的事件
        '''
        # 防冲突
        if timer.isActive():
            return
        # 界面更新
        self.button_lock()
        self.progress_bar_sig.emit(0)
        self.statusLabel.setText("   等待文件输入...   ")
        # 数据更新(依托于文件选择器)
        self.src, type = QFileDialog.getOpenFileName(
            None,
            "打开文件",
            "./",
            ".hlx文件(*.hlx);;mp4文件(*.mp4)"
        )
        # 界面更新(分支处理)
        self.lineEdit.setText(self.src)
        if self.src is not None and len(self.src) != 0:
            self.statusLabel.setText("   文件打开成功!!!   ")
            if type == ".hlx文件(*.hlx)":
                self.pushButton_3.setEnabled(True)
            else:
                self.pushButton_2.setEnabled(True)

    def encode(self):
        '''
        “加密”按钮的事件
        '''
        # 界面更新
        self.button_lock()
        self.statusLabel.setText("   加密中，请等待...   ")
        # 数据更新
        self.dst = self.src[:-3] + "hlx"
        password = self.lineEdit_2.text()
        # 运行
        self.progress_value = 0
        timer.start(1000, self)
        encode_thread.set_data(self.src, self.dst, password)
        encode_thread.start()

    def encode_feedback(self, is_done):
        '''
        加密结果反馈
        '''
        self.time_stop_sig.emit()
        self.progressBar.setValue(100)
        if is_done:
            self.statusLabel.setText("    加密成功 !!!   ")
        else:
            self.statusLabel.setText("    加密失败 !!!   ")

    def decode(self):
        '''
        “解密”按钮的事件
        '''
        # 界面更新
        self.button_lock()
        self.statusLabel.setText("   解密中，请等待...   ")
        # 数据更新
        self.dst = self.src[:-3] + "mp4"
        password = self.lineEdit_2.text()
        # 运行
        self.progress_value = 0
        timer.start(1000, self)
        decode_thread.set_data(self.src, self.dst, password)
        decode_thread.start()

    def decode_feedback(self, is_done):
        '''
        解密结果反馈
        '''
        self.time_stop_sig.emit()
        if is_done:
            self.progressBar.setValue(100)
            self.statusLabel.setText("    解密成功 !!!   ")
        else:
            self.statusLabel.setText("    密码错误 !!!   ")


if __name__ == "__main__":
    # 线程
    app = QtWidgets.QApplication(sys.argv)
    encode_thread = EncodeThread()
    decode_thread = DecodeThread()
    timer = QBasicTimer()
    # 窗口
    main_window = MainWindow()
    main_window.show()
    # 信号与槽
    encode_thread.sig.connect(main_window.encode_feedback)
    decode_thread.sig.connect(main_window.decode_feedback)
    main_window.time_stop_sig.connect(timer.stop)
    main_window.progress_bar_sig.connect(main_window.progress_updata)
    # 结束
    sys.exit(app.exec_())
