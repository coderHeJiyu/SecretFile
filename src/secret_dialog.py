import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDragEnterEvent
from PyQt5.QtWidgets import QDialog,QFileDialog
from ui.ui_secret_dialog import Ui_SecretDialog


class SecretDialog(Ui_SecretDialog,QDialog):
    task_sig = pyqtSignal(str,str,int)
    
    def __init__(self, parent=None, src:str = None, password:str = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.src:str = src
        self.password:str = password
        self.__check_file()
        if self.password:
            self.lineEdit_2.setText(self.password)

    def __button_lock(self):
        """
        锁定“加密”和“解密”按钮
        """
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

    def __check_file(self):
        if self.src:
            self.lineEdit.setText(self.src)
            file_type = os.path.splitext(self.src)[-1]
            if file_type != ".hlx":
                self.pushButton_2.setEnabled(True)
            else:
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)

    def open_file(self):
        """
        “打开”按钮的事件
        """
        # 界面更新
        self.__button_lock()
        # 数据更新(依托于文件选择器)
        self.src, _ = QFileDialog.getOpenFileName(
            None,
            "打开文件",
            "./",
            "全部文件(*.*)"
        )
        # 界面更新(分支处理)
        self.__check_file()

    def encode(self):
        """
        “加密”按钮的事件
        """
        _password = self.lineEdit_2.text()
        self.task_sig.emit(self.src,_password,0)
        self.close()

    def decode(self):
        """
        “解密”按钮的事件
        """
        _password = self.lineEdit_2.text()
        self.task_sig.emit(self.src,_password,1)
        self.close()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        @override 拖入事件
        """
        # 界面更新
        self.__button_lock()
        # 数据更新
        self.src = event.mimeData().urls()[0].toLocalFile()
        # 界面更新(分支处理)
        self.__check_file()

    