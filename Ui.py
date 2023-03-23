from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLCDNumber
import sys
from Dispatcher import Dispatcher


class Window(QWidget):

    def __init__(self):
        super().__init__()
        # self.center()
        self.resize(1000, 1000)
        self.move(450, 0)
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(palette1)
        self.setObjectName("window")
        self.setStyleSheet("#window{border-image:url(icon/background.png)}")

        self.lift = {}
        for i in range(1, 6):
            self.lift[i] = QtWidgets.QLabel(self)  # 以window为父控件
            self.lift[i].setPixmap(QtGui.QPixmap("icon/lift.png"))
            self.lift[i].setGeometry(QtCore.QRect(i * 190 - 180, 955, 40, 40))
            self.lift[i].setScaledContents(True)
        self.lift_anime = {}
        for i in range(1, 6):
            self.lift_anime[i] = QtCore.QPropertyAnimation(self.lift[i], b"geometry")

        # 程序框上部的数字显示
        self.floor_digit = {}
        for i in range(1, 6):
            self.floor_digit[i] = QLCDNumber(2, self)
            self.floor_digit[i].setGeometry(QtCore.QRect(i * 190 - 180, 0, 100, 100))
            self.floor_digit[i].resize(100, 100)
            self.floor_digit[i].display('1')

        self.up_btn = {}
        self.down_btn = {}
        self.up_btn_md = "QPushButton{border-image: url(icon/up_hover.png)}" \
                       "QPushButton:hover{border-image: url(icon/up.png)}" \
                       "QPushButton:pressed{border-image: url(icon/up_pressed.png)}"
        self.down_btn_md = "QPushButton{border-image: url(icon/down_hover.png)}" \
                         "QPushButton:hover{border-image: url(icon/down.png)}" \
                         "QPushButton:pressed{border-image: url(icon/down_pressed.png)}"
        for i in range(1, 20):
            self.up_btn[i] = QtWidgets.QPushButton(self)
            self.up_btn[i].setGeometry(QtCore.QRect(900, 1000 - i * 45, 40, 40))
            self.up_btn[i].setStyleSheet(self.up_btn_md)
        for i in range(2, 21):
            self.down_btn[i] = QtWidgets.QPushButton(self)
            self.down_btn[i].setGeometry(QtCore.QRect(950, 1000 - i * 45, 40, 40))
            self.down_btn[i].setStyleSheet(self.down_btn_md)

        self.floor_btn = [[] for i in range(6)]
        for i in range(1, 6):
            self.floor_btn[i].append("Nothing")
            for j in range(1, 21):
                self.floor_btn[i].append(QtWidgets.QPushButton(self))  # 创建一个按钮，并将按钮加入到窗口MainWindow中
                self.floor_btn[i][j].setGeometry(QtCore.QRect(i * 190 - 130, 1000 - j * 45, 40, 40))
                self.floor_btn[i][j].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(j) + "_hover.png)}"
                    "QPushButton:hover{border-image: url(icon/" + str(j) + ".png)}"
                    "QPushButton:pressed{border-image: url(icon/" + str(j) + "_pressed.png)}")
        self.dispatcher = Dispatcher(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
