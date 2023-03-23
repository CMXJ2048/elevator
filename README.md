# 基于python实现的电梯调度

# 1 项目说明

## 1.1 项目目的

- 通过实现电梯调度，体会操作系统调度过程

- 学习特定环境下多线程编程方法

- 学习调度算法

## 1.2 开发环境

- **开发语言**：python

- **开发环境**：pycharm

- **开发框架**：pyQt5

## 1.3  基本需求

### 1.3.1 基本任务

某一层楼20层，有五部互联的电梯。基于线程思想，编写一个电梯调度程序。

### 1.3.2 功能描述

- 电梯应有一些按键，如：数字键、关门键、开门键、上行键、下行键、报警键等

- 有数码显示器指示当前电梯状态

- 每层楼、每部电梯门口，有上行、下行按钮、数码显示

- 五部电梯相互联结，即当一个电梯按钮按下去时，其它电梯相应按钮同时点亮，表示也按下去了

### 1.3.3 调度算法

- 所有电梯初始状态都在第一层

- 每个电梯没有相应请求情况下，则应该在原地保持不动

- 电梯调度算法自行设计

## 1.4 操作手册

### 1.4.1 数字键

每部电梯中都设有1-20的数字键，点击数字键，电梯到达指定楼层。如图操作：

![](http://www.writebug.com/myres/static/uploads/2021/10/19/d8d5e5649b66ea048d65d4a72d33e68e.writebug)

### 1.4.2 上下健

每个楼层设有上行和下行键，点击上下行健，所有电梯都会接收到请求，调度算法进行调度，安排电梯到达该楼层，如图操作：

![](http://www.writebug.com/myres/static/uploads/2021/10/19/c0fc6c47b34599d00994067c7a547b53.writebug)

# 2. 设计与实现

## 2.1 算法设计

采用LOOK算法，LOOK算法是扫描算法（SCAN）的一种改进。对LOOK算法而言，电梯同样在最底层和最顶层之间运行。但当LOOK算法发现电梯所移动的方向上不再有请求时立即改变运行方向，而扫描算法则需要移动到最底层或者最顶层时才改变运行方向。

## 2.2 类设计

### 2.2.1 UI类

```python
class Window(QWidget):
```

**方法**

```
def __init__(self):
```

**属性**

```python
self.lift = {} # 电梯图案数组
self.lift_anime = {} # 电梯动画数组
self.floor_digit = {} # 楼层数显数组
self.up_btn = {} # 上行按钮数组
self.down_btn = {} # 下行按钮数组
self.floor_btn = [[] for i in range(6)] #楼层按钮
self.dispatcher = Dispatcher(self) # 电梯调度
```

### 2.2.2 调度算法类

```python
class Dispatcher():
```

**方法**

```python
`def __init__(self, ui):
def listenUpBtn(self, btn_floor):  # 监听上行按钮
def listenDownBtn(self, btn_floor):  # 监听下行按钮
def listenFloorBtn(self, lift_num, btn_floor):
def thread(self, lift_num):  # 为各台电梯创建线程
def upAnime(self, lift_num):  # 上行动画实现
def downAnime(self, lift_num):  # 下行动画实现
def afterUp(self, lift_num):  # 上行后的相关善后
def afterDown(self, lift_num):  # 下行后的相关善后
def dispatch(self, lift_num):  # 循环执行电梯调度`
```

**属性**

```python
self.ui = ui
self.currentFloor = {}  # 电梯所在层数
self.isGoingUp = {}  # 电梯上行标志数组
self.isGoingDown = {}  # 电梯下行标志数组
self.toUp = [[0] * 21 for i in range(6)]  # 尚未处理的上行请求
self.toDown = [[0] * 21 for i in range(6)]  # 尚未处理的下行请求
self.upSeq = [[] for i in range(6)]  # 电梯上行序列
self.downSeq = [[] for i in range(6)]  # 电梯下行序列
```

# 3 测试

## 3.1 上行键测试

- **测试用例**:某楼层按上行键

- **预期结果**:距离最短的电梯响应

- **测试结果**:符合要求

![](http://www.writebug.com/myres/static/uploads/2021/10/19/4d0717c8c5c0b8a94dc011b79edd6331.writebug)

## 3.2 下行键测试

- **测试用例**:某楼层按下行键

- **预期结果**:距离最短的电梯响应

- **测试结果**:符合要求,如图电梯5正在前往

![](http://www.writebug.com/myres/static/uploads/2021/10/19/c386c777ea7bd0717ac97bae3ae3cbe8.writebug)

## 3.3 楼层键

- **测试用例**:某台电梯按下楼层键

- **预期结果**:该电梯响应,前往指定楼层

- **测试结果**:符合要求

![](http://www.writebug.com/myres/static/uploads/2021/10/19/a80fb564fbdf46f5f3a1b0aa85bf32d8.writebug)

![](http://www.writebug.com/myres/static/uploads/2021/10/19/959dc2afc087611dc634b48bf918fa19.writebug)