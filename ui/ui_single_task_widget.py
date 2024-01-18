# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_SingleTaskWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SingleTaskWidget(object):
    def setupUi(self, SingleTaskWidget):
        SingleTaskWidget.setObjectName("SingleTaskWidget")
        SingleTaskWidget.resize(591, 77)
        font = QtGui.QFont()
        font.setFamily("华文行楷")
        font.setPointSize(16)
        SingleTaskWidget.setFont(font)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SingleTaskWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_src = QtWidgets.QLabel(SingleTaskWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_src.sizePolicy().hasHeightForWidth())
        self.label_src.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.label_src.setFont(font)
        self.label_src.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_src.setObjectName("label_src")
        self.verticalLayout.addWidget(self.label_src)
        self.progressBar = QtWidgets.QProgressBar(SingleTaskWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setFormat("")
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.line_2 = QtWidgets.QFrame(SingleTaskWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.label_state = QtWidgets.QLabel(SingleTaskWidget)
        self.label_state.setAlignment(QtCore.Qt.AlignCenter)
        self.label_state.setObjectName("label_state")
        self.horizontalLayout.addWidget(self.label_state)
        self.line_3 = QtWidgets.QFrame(SingleTaskWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout.addWidget(self.line_3)
        self.pushButton = QtWidgets.QPushButton(SingleTaskWidget)
        self.pushButton.setStatusTip("")
        self.pushButton.setText("")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(SingleTaskWidget)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setStatusTip("")
        self.pushButton_2.setText("")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(2, 5)
        self.horizontalLayout.setStretch(4, 1)
        self.horizontalLayout.setStretch(5, 1)

        self.retranslateUi(SingleTaskWidget)
        self.pushButton.clicked.connect(SingleTaskWidget.pause_toggled)
        self.pushButton_2.clicked.connect(SingleTaskWidget.remove)
        QtCore.QMetaObject.connectSlotsByName(SingleTaskWidget)

    def retranslateUi(self, SingleTaskWidget):
        _translate = QtCore.QCoreApplication.translate
        SingleTaskWidget.setWindowTitle(_translate("SingleTaskWidget", "Form"))
        self.label_src.setText(_translate("SingleTaskWidget", "文件名"))
        self.label_state.setText(_translate("SingleTaskWidget", "状态"))
        self.pushButton.setToolTip(_translate("SingleTaskWidget", "暂停任务"))
        self.pushButton_2.setToolTip(_translate("SingleTaskWidget", "结束任务"))
