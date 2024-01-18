from PyQt5.QtWidgets import QApplication,QWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from src.threads import CipherSignals
from ui.ui_single_task_widget import Ui_SingleTaskWidget

state_dict = {
    CipherSignals.ENCODE_PROCESS: "正在加密",
    CipherSignals.DECODE_PROCESS: "正在解密",
    CipherSignals.FINISHED: "完成",
    CipherSignals.PW_ERROR: "密码错误",
    CipherSignals.FILE_EXIST: "文件已存在",
    CipherSignals.FILE_BROKEN: "文件已损坏"
}


class SingleTaskListWidgetItem(QListWidgetItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = SingleTaskWidget()
        self.setSizeHint(self.widget.sizeHint())

    def set_src(self, src: str):
        """
        设置源文件路径
        """
        self.widget.label_src.setText(src)

    def set_progress(self, progress: int):
        """
        设置进度条
        """
        self.widget.progressBar.setValue(progress)

    def set_state(self, state: int):
        """
        设置状态
        """
        self.widget.label_state.setText(state_dict[state])
        if state>1:
            self.widget.pushButton.setEnabled(False)
            self.widget.pushButton_2.setEnabled(True)


class SingleTaskWidget(Ui_SingleTaskWidget, QWidget):
    pause_sig = pyqtSignal()
    remove_sig = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.run_icon=QApplication.style().standardIcon(61)
        self.pause_icon=QApplication.style().standardIcon(63)
        self.remove_ico = QApplication.style().standardIcon(44)
        self.pushButton.setIcon(self.pause_icon)
        self.pushButton_2.setIcon(self.remove_ico)
        self.is_paused = False
        self.row = 0

    def pause_toggled(self):
        """
        暂停/继续
        """
        if self.is_paused:
            self.pushButton.setIcon(self.pause_icon)
            self.pushButton.setToolTip("暂停任务")
            self.is_paused = False
            self.pushButton_2.setEnabled(False)
        else:
            self.pushButton.setIcon(self.run_icon)
            self.pushButton.setToolTip("继续任务")
            self.is_paused = True
            self.pushButton_2.setEnabled(True)
        self.pause_sig.emit()

    def remove(self):
        """
        结束
        """
        self.remove_sig.emit()
        
        