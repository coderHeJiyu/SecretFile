import os
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QMainWindow, QApplication
from src.threads import EncodeThread, DecodeThread
from src.secret_dialog import SecretDialog
from src.single_task_widget import SingleTaskListWidgetItem
from ui.ui_main_window import Ui_MainWindow


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.threadpool = QThreadPool()
        self.pushButton.setIcon(QApplication.style().standardIcon(56))

    def add_task(self, src: str = None):
        """
        唤起任务框
        """
        secret_dialog = SecretDialog(self, src=src)
        secret_dialog.task_sig.connect(self.start_task)
        secret_dialog.exec()
        secret_dialog.close()

    def start_task(self, src: str, password: str, mode: int):
        """
        开始任务
        """
        item = SingleTaskListWidgetItem(self.listWidget)
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, item.widget)
        item.set_src(os.path.basename(src))
        item.set_progress(0)
        if mode == 0:
            _task = EncodeThread(src, password)
        else:
            _task = DecodeThread(src, password)
        _task.signals.status_sig.connect(item.set_state)
        _task.signals.process_sig.connect(item.set_progress)
        item.widget.pause_sig.connect(_task.pause_trigger)
        item.widget.remove_sig.connect(_task.quit)
        item.widget.remove_sig.connect(
            lambda: self.listWidget.takeItem(self.listWidget.row(item)))
        self.threadpool.start(_task)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        @override 拖入事件,不接受文件夹
        """
        if event.mimeData().hasUrls():
            for _file in event.mimeData().urls():
                if os.path.isfile(_file.toLocalFile()):
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        @override 放下事件
        """
        _file_list = event.mimeData().urls()
        for _file in _file_list:
            if os.path.isfile(_file.toLocalFile()):
                self.add_task(_file.toLocalFile())
