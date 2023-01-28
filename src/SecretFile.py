import os
from PyQt5 import QtWidgets, QtGui
# from PyQt5.QtWidgets import *
import sys
from Threads import *
from mainWindow import Ui_MainWindow
from PyQt5.QtCore import Qt


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.set_more_ui()
        self.encode_thread = EncodeThread()
        self.decode_thread = DecodeThread()
        self.run_state = False
        self.set_threads()

    def set_more_ui(self):
        '''
        手写部分UI
        '''
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.reset()
        self.statusBar.addPermanentWidget(self.progressBar, stretch=4)
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setMaximumWidth(140)
        self.statusLabel.setMinimumWidth(140)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setText("   等待文件输入...   ")
        self.statusBar.addPermanentWidget(self.statusLabel, stretch=1)
        self.setAcceptDrops(True)

    def set_threads(self):
        """
        设置线程
        """
        self.encode_thread.sig.connect(self.encode_feedback)
        self.encode_thread.progress_sig.connect(self.progress_updata)
        self.encode_thread.length_sig.connect(self.progress_set)
        self.decode_thread.sig.connect(self.decode_feedback)
        self.decode_thread.progress_sig.connect(self.progress_updata)
        self.decode_thread.length_sig.connect(self.progress_set)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        '''
        @override 拖入事件
        '''
        # 防冲突
        if self.run_state:
            return
        # 界面更新
        self.button_lock()
        self.progressBar.reset()
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

    def progress_set(self, value: int):
        '''
        进度条最大值设置
        '''
        self.progressBar.setMaximum(value)

    def progress_updata(self, value: int):
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
        if self.run_state:
            return
        # 界面更新
        self.button_lock()
        self.progressBar.reset()
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

    def is_confirm(self, ope: str):
        """
        文件覆盖确认弹窗
        """
        dic = {
            "encode": ("加密", "已存在同名加密后文件，您确定要覆盖吗？"),
            "decode": ("解密", "已存在同名解密后文件，您确定要覆盖吗？")
        }
        title = dic[ope][0]
        text = dic[ope][1]
        reply = QMessageBox.question(
            self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

    def encode(self):
        '''
        “加密”按钮的事件
        '''
        # 数据更新
        self.dst = self.src[:-3] + "hlx"
        # 检查
        if os.path.exists(self.dst):
            if not self.is_confirm("encode"):
                return
        password = self.lineEdit_2.text()
        # 界面更新
        self.button_lock()
        self.statusLabel.setText("   加密中，请等待...   ")
        # 运行
        self.run_state = True
        self.encode_thread.set_data(self.src, self.dst, password)
        self.encode_thread.start()

    def encode_feedback(self, is_done):
        '''
        加密结果反馈
        '''
        self.run_state = False
        if is_done:
            self.statusLabel.setText("    加密成功 !!!   ")
        else:
            self.statusLabel.setText("    加密失败 !!!   ")

    def decode(self):
        '''
        “解密”按钮的事件
        '''
        # 数据更新
        self.dst = self.src[:-3] + "mp4"
        # 检查
        if os.path.exists(self.dst):
            if not self.is_confirm("decode"):
                return
        password = self.lineEdit_2.text()
        # 界面更新
        self.button_lock()
        self.statusLabel.setText("   解密中，请等待...   ")
        # 运行
        self.run_state = True
        self.decode_thread.set_data(self.src, self.dst, password)
        self.decode_thread.start()

    def decode_feedback(self, is_done):
        '''
        解密结果反馈
        '''
        self.run_state = False
        if is_done:
            self.statusLabel.setText("    解密成功 !!!   ")
        else:
            self.statusLabel.setText("    密码错误 !!!   ")


if __name__ == "__main__":
    # 开始
    app = QtWidgets.QApplication(sys.argv)
    # 窗口
    main_window = MainWindow()
    main_window.show()
    # 结束
    sys.exit(app.exec_())
