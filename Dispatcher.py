import threading
from functools import partial
import time
from PyQt5 import QtCore


class Dispatcher():
    def __init__(self, ui):
        self.ui = ui
        self.currentFloor = {}  # 电梯所在层数
        for i in range(1, 6):
            self.currentFloor[i] = 1
        self.isGoingUp = {}  # 电梯上行标志数组
        for i in range(1, 6):
            self.isGoingUp[i] = False
        self.isGoingDown = {}  # 电梯下行标志数组
        for i in range(1, 6):
            self.isGoingDown[i] = False
        self.toUp = [[0] * 21 for i in range(6)]  # 尚未处理的上行请求
        self.toDown = [[0] * 21 for i in range(6)]  # 尚未处理的下行请求
        self.upSeq = [[] for i in range(6)]  # 电梯上行序列
        self.downSeq = [[] for i in range(6)]  # 电梯下行序列

        for i in range(1, 20):  # 上行按钮与监听函数绑定
            self.ui.up_btn[i].clicked.connect(partial(self.listenUpBtn, i))
        for i in range(2, 21):  # 下行按钮与监听函数绑定
            self.ui.down_btn[i].clicked.connect(partial(self.listenDownBtn, i))
        for i in range(1, 6):
            for j in range(1, 21):  # 楼层按钮与监听函数绑定
                self.ui.floor_btn[i][j].clicked.connect(partial(self.listenFloorBtn, i, j))
        for i in range(1, 6):  # 加载线程
            self.thread(i)

    def listenUpBtn(self, btn_floor):  # 监听上行按钮
        self.ui.up_btn[btn_floor].setStyleSheet("QPushButton{border-image: url(icon/up_pressed.png)}")
        distance = [100, 100, 100, 100, 100, 100]  # 到达目标楼层的距离
        btn_above = {}  # 请求是否在电梯上方
        for i in range(1, 6):
            btn_above[i] = False
            if btn_floor >= self.currentFloor[i]:
                btn_above[i] = True
        for i in range(1, 6):
            if self.isGoingUp[i] == True and self.isGoingDown[i] == False:  # 上行
                if btn_above[i]:  # 请求在上方
                    distance[i] = abs(btn_floor - self.currentFloor[i])  # 当前位置距请求位置距离
                else:  # 请求在下方
                    # distance[i] = abs(self.floor[i] - self.upSeq[i][len(self.upSeq[i]) - 1]) \
                    distance[i] = abs(self.currentFloor[i] - max(self.upSeq[i])) \
                                  + abs(btn_floor - self.upSeq[i][len(self.upSeq[i]) - 1])
                    # 当前位置距终点距离 + 终点距请求位置距离
            elif self.isGoingUp[i] == False and self.isGoingDown[i] == False:  # 静止
                distance[i] = abs(btn_floor - self.currentFloor[i])  # 当前位置距请求位置距离
            elif self.isGoingUp[i] == False and self.isGoingDown[i] == True:  # 下行
                # distance[i] = abs(self.floor[i] - self.downSeq[i][len(self.downSeq[i]) - 1]) \
                distance[i] = abs(self.currentFloor[i] - min(self.downSeq[i])) \
                              + abs(btn_floor - self.downSeq[i][len(self.downSeq[i]) - 1])
                # 距离为先下行结束再上行两段
        nearest_lift = distance.index(min(distance))  # 找出最近的电梯
        if self.isGoingUp[nearest_lift] == True and self.isGoingDown[nearest_lift] == False:  # 上行状态 #被上面一句选中的一台电梯
            if btn_above[nearest_lift]:  # 请求在上方
                self.upSeq[nearest_lift].append(btn_floor)  # 加入上行序列
                self.upSeq[nearest_lift] = list(set(self.upSeq[nearest_lift]))  # 为list去重
                self.upSeq[nearest_lift].sort()  # 排序
            else:  # 请求在下方
                self.toUp[nearest_lift][btn_floor] = 1  # 尚未处理的上行请求
        elif self.isGoingUp[nearest_lift] == False and self.isGoingDown[nearest_lift] == False:  # 静止
            if btn_above[nearest_lift]:  # 请求在上方
                self.upSeq[nearest_lift].append(btn_floor)  # 加入上行序列
                self.upSeq[nearest_lift] = list(set(self.upSeq[nearest_lift]))  # 为list去重
                self.upSeq[nearest_lift].sort()  # 排序
            else:  # 请求在下方
                self.downSeq[nearest_lift] = list(set(self.downSeq[nearest_lift]))  # 为list去重
                self.downSeq[nearest_lift].sort()  # 排序
                self.downSeq[nearest_lift].reverse()  # 翻转 从大到小排序
                self.toUp[nearest_lift][btn_floor] = 1  # 尚未处理的上行请求
        elif self.isGoingUp[nearest_lift] == False and self.isGoingDown[nearest_lift] == True:  # 下行状态
            self.toUp[nearest_lift][btn_floor] = 1  # 尚未处理的上行请求

    def listenDownBtn(self, btn_floor):
        self.ui.down_btn[btn_floor].setStyleSheet("QPushButton{border-image: url(icon/down_pressed.png)}")
        distance = [100, 100, 100, 100, 100, 100]  # 各台电梯距离请求的距离
        btn_below = {}  # 请求是否在电梯下方
        for i in range(1, 6):  # 初始化
            btn_below[i] = False
            # if (btn_floor - self.currentFloor[i]) <= 0:
            if btn_floor <= self.currentFloor[i]:  # 初始化
                btn_below[i] = True
        for i in range(1, 6):
            if self.isGoingUp[i] == False and self.isGoingDown[i] == True:  # 下行
                if btn_below[i]:  # 请求在下方或本层
                    distance[i] = abs(self.currentFloor[i] - btn_floor)
                else:  # 请求在上方
                    distance[i] = abs(self.currentFloor[i] - self.downSeq[i][len(self.downSeq[i]) - 1]) \
                                  + abs(btn_floor - self.downSeq[i][len(self.downSeq[i]) - 1])
                    # 先上行再下行两段距离
            elif self.isGoingUp[i] == False and self.isGoingDown[i] == False:  # 静止
                distance[i] = abs(self.currentFloor[i] - btn_floor)  # 当前位置距请求位置距离
            elif self.isGoingUp[i] == True and self.isGoingDown[i] == False:  # 上行
                distance[i] = abs(self.currentFloor[i] - self.upSeq[i][len(self.upSeq[i]) - 1]) \
                              + abs(btn_floor - self.upSeq[i][len(self.upSeq[i]) - 1])
        nearest_lift = distance.index(min(distance))  # 距离最小的电梯的序号
        if self.isGoingUp[nearest_lift] == False and self.isGoingDown[nearest_lift] == True:  # 下行
            if btn_below[nearest_lift]:
                self.downSeq[nearest_lift].append(btn_floor)  # 加入下行序列
                self.downSeq[nearest_lift] = list(set(self.downSeq[nearest_lift]))
                self.downSeq[nearest_lift].sort()
                self.downSeq[nearest_lift].reverse()
            else:  # 请求在上方
                self.toDown[nearest_lift][btn_floor] = 1
        elif self.isGoingUp[nearest_lift] == False and self.isGoingDown[nearest_lift] == False:  # 静止状态
            if btn_below[nearest_lift]:  # 请求在下方
                self.downSeq[nearest_lift].append(btn_floor)
                self.downSeq[nearest_lift] = list(set(self.downSeq[nearest_lift]))
                self.downSeq[nearest_lift].sort()
                self.downSeq[nearest_lift].reverse()
            else:  # 请求在上方
                self.upSeq[nearest_lift].append(btn_floor)  # 加入上行序列
                self.upSeq[nearest_lift] = list(set(self.upSeq[nearest_lift]))
                self.upSeq[nearest_lift].sort()
                self.toDown[nearest_lift][btn_floor] = 1
        elif self.isGoingUp[nearest_lift] == True and self.isGoingDown[nearest_lift] == False:  # 上行
            self.toDown[nearest_lift][btn_floor] = 1

    def listenFloorBtn(self, lift_num, btn_floor):
        if self.isGoingUp[lift_num] == False and self.isGoingDown[lift_num] == False:
            if self.currentFloor[lift_num] > btn_floor:
                self.ui.floor_btn[lift_num][btn_floor].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(btn_floor) + "_pressed.png)}")
                self.downSeq[lift_num].append(btn_floor)
                self.downSeq[lift_num] = list(set(self.downSeq[lift_num]))
                self.downSeq[lift_num].sort()
                self.downSeq[lift_num].reverse()
            if self.currentFloor[lift_num] < btn_floor:
                self.ui.floor_btn[lift_num][btn_floor].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(btn_floor) + "_pressed.png)}")
                self.upSeq[lift_num].append(btn_floor)
                self.upSeq[lift_num] = list(set(self.upSeq[lift_num]))
                self.upSeq[lift_num].sort()
        elif self.isGoingUp[lift_num] == True and self.isGoingDown[lift_num] == False:
            if self.currentFloor[lift_num] < btn_floor:
                self.ui.floor_btn[lift_num][btn_floor].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(btn_floor) + "_pressed.png)}")
                self.upSeq[lift_num].append(btn_floor)
                self.upSeq[lift_num] = list(set(self.upSeq[lift_num]))
                self.upSeq[lift_num].sort()
        elif self.isGoingUp[lift_num] == False and self.isGoingDown[lift_num] == True:
            if self.currentFloor[lift_num] > btn_floor:
                self.ui.floor_btn[lift_num][btn_floor].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(btn_floor) + "_pressed.png)}")
                self.downSeq[lift_num].append(btn_floor)
                self.downSeq[lift_num] = list(set(self.downSeq[lift_num]))
                self.downSeq[lift_num].sort()
                self.downSeq[lift_num].reverse()

    def thread(self, lift_num):
        t = threading.Thread(target=partial(self.dispatch, lift_num))
        t.start()

    def upAnime(self, lift_num):
        while len(self.upSeq[lift_num]):  # 上行序列非空时
            self.isGoingUp[lift_num] = True  # 置电梯为上行状态
            up_seq1 = self.upSeq[lift_num][0]
            dist = abs(self.upSeq[lift_num][0] - self.currentFloor[lift_num])
            if dist == 0:
                self.ui.floor_btn[lift_num][up_seq1].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(self.upSeq[lift_num][0]) + "_hover.png)}"
                    "QPushButton:hover{border-image: url(icon/" + str(self.upSeq[lift_num][0]) + ".png)}"
                    "QPushButton:pressed{border-image: url(icon/" + str(self.upSeq[lift_num][0]) + "_pressed.png)}")
            i = 1
            while i <= dist:
                if up_seq1 == self.upSeq[lift_num][0]:  # up_seq1还是移动距离最短的请求
                    time.sleep(0.5)
                    self.currentFloor[lift_num] = self.currentFloor[lift_num] + 1  #
                    self.ui.lift[lift_num].setGeometry(
                        QtCore.QRect(lift_num * 190 - 180, 1000 - 45 * self.currentFloor[lift_num], 40, 40))
                    self.ui.floor_digit[lift_num].display(str(self.currentFloor[lift_num]))
                else:
                    dist = abs(self.upSeq[lift_num][0] - self.currentFloor[lift_num])
                    up_seq1 = self.upSeq[lift_num][0]  # 更新
                    i = 0
                i = i + 1
            time.sleep(0.5)
            if self.upSeq[lift_num][0] < 20:  # 第20层没有上行按钮
                self.ui.up_btn[self.upSeq[lift_num][0]].setStyleSheet(self.ui.up_btn_md)
            self.ui.floor_btn[lift_num][self.upSeq[lift_num][0]].setStyleSheet(
                "QPushButton{border-image: url(icon/" + str(self.upSeq[lift_num][0]) + "_hover.png)}"
                "QPushButton:hover{border-image: url(icon/" + str(self.upSeq[lift_num][0]) + ".png)}"
                "QPushButton:pressed{border-image: url(icon/" + str(self.upSeq[lift_num][0]) + "_pressed.png)}")
            del self.upSeq[lift_num][0]
        self.isGoingUp[lift_num] = False

    def downAnime(self, lift_num):
        while len(self.downSeq[lift_num]):
            self.isGoingDown[lift_num] = True
            down_seq1 = self.downSeq[lift_num][0]
            dist = abs(self.downSeq[lift_num][0] - self.currentFloor[lift_num])
            if dist == 0:
                self.ui.floor_btn[lift_num][self.downSeq[lift_num][0]].setStyleSheet(
                    "QPushButton{border-image: url(icon/" + str(self.downSeq[lift_num][0]) + "_hover.png)}"
                    "QPushButton:hover{border-image: url(icon/" + str(self.downSeq[lift_num][0]) + ".png)}"
                    "QPushButton:pressed{border-image: url(icon/" + str(self.downSeq[lift_num][0]) + "_pressed.png)}")
            i = 1
            while i <= dist:
                if down_seq1 == self.downSeq[lift_num][0]:
                    time.sleep(0.5)
                    self.currentFloor[lift_num] = self.currentFloor[lift_num] - 1
                    self.ui.lift[lift_num].setGeometry(
                        QtCore.QRect(lift_num * 190 - 180, 1000 - 45 * self.currentFloor[lift_num], 40, 40))
                    self.ui.floor_digit[lift_num].display(str(self.currentFloor[lift_num]))
                else:
                    dist = abs(self.downSeq[lift_num][0] - self.currentFloor[lift_num])
                    down_seq1 = self.downSeq[lift_num][0]
                    i = 0
                i = i + 1
            time.sleep(0.5)
            if self.downSeq[lift_num][0] > 1: # 第一层没有下行按钮
                self.ui.down_btn[self.downSeq[lift_num][0]].setStyleSheet(self.ui.down_btn_md)
            self.ui.floor_btn[lift_num][self.downSeq[lift_num][0]].setStyleSheet(
                "QPushButton{border-image: url(icon/" + str(self.downSeq[lift_num][0]) + "_hover.png)}"
                "QPushButton:hover{border-image: url(icon/" + str(self.downSeq[lift_num][0]) + ".png)}"
                "QPushButton:pressed{border-image: url(icon/" + str(self.downSeq[lift_num][0]) + "_pressed.png)}")
            del self.downSeq[lift_num][0]
        self.isGoingDown[lift_num] = False

    def afterUp(self, lift_num):  # 上行之后处理上行时没有处理的请求
        i = 20
        while i >= 1:
            if self.toDown[lift_num][i] == 1:
                if i > self.currentFloor[lift_num]:
                    self.upSeq[lift_num].append(i)
                    self.upSeq[lift_num] = list(set(self.upSeq[lift_num]))
                    self.isGoingUp[lift_num] = True
                    break
                self.toDown[lift_num][i] = 0
                self.downSeq[lift_num].append(i)
                self.downSeq[lift_num] = list(set(self.downSeq[lift_num]))
                self.downSeq[lift_num].sort()
                self.downSeq[lift_num].reverse()
                self.isGoingDown[lift_num] = True
            i = i - 1
        if self.isGoingDown[lift_num] == False and self.isGoingUp[lift_num] == False:
            for i in range(1, 21):
                if self.toUp[lift_num][i] == 1:
                    self.downSeq[lift_num].append(i)
                    self.downSeq[lift_num] = list(set(self.downSeq[lift_num]))
                    self.isGoingDown[lift_num] = True
                    break

    def afterDown(self, lift_num):
        i = 1
        while i <= 20:
            if self.toUp[lift_num][i] == 1:
                if i < self.currentFloor[lift_num]:
                    self.downSeq[lift_num].append(i)
                    self.downSeq[lift_num] = list(set(self.downSeq[lift_num]))
                    self.isGoingDown[lift_num] = True
                    break  # 为什么break 因为只要把这个最下方楼层的上行请求记录下来即可 这样就能到达所有需要上行的楼层
                    # 下方不存在执行动作时产生的但未处理的上行请求
                self.toUp[lift_num][i] = 0
                self.upSeq[lift_num].append(i)
                self.upSeq[lift_num] = list(set(self.upSeq[lift_num]))
                self.upSeq[lift_num].sort()
                self.isGoingUp[lift_num] = True
                # 上面这句说明上行之后可以继续上行的 因为elevator_up_anim这个函数结束的条件是upsequence为空
            i = i + 1
        # 不存在上行请求，处理执行动作时产生的但未处理的下行请求（该请求只可能在上方）
        if self.isGoingUp[lift_num] == False and self.isGoingDown[lift_num] == False:
            i = 20  # 倒序处理
            while i >= 1:
                if self.toDown[lift_num][i] == 1:
                    self.upSeq[lift_num].append(i)  # 将最高楼层的下行请求加入上行序列,开始上行
                    self.upSeq[lift_num] = list(set(self.upSeq[lift_num]))
                    self.isGoingUp[lift_num] = True
                    break
                i = i - 1

    def dispatch(self, lift_num):

        while 1:
            time.sleep(0.1)
            self.upAnime(lift_num)
            time.sleep(0.1)
            self.afterUp(lift_num)
            time.sleep(0.1)
            self.downAnime(lift_num)
            time.sleep(0.1)
            self.afterDown(lift_num)
