import sys
from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow


if __name__ == "__main__":
    # 开始
    app = QApplication(sys.argv)
    # 窗口
    main_window = MainWindow()
    main_window.show()
    # 结束
    sys.exit(app.exec_())