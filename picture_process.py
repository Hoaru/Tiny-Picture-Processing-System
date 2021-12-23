#####################################################################################################################
#####################################################################################################################

#       !!!!!!!!重要提示!!!!!!!!

#        在打开图片时请事先选择一张大小在300k以内的图片，否则可能出现移位、侧斜、变色、条纹化等未知bug

#        使用说明：左上角文件中有【打开】和【另存为】功能，每选中一种效果进行调整后，请点击右边的【确认】按钮用以保存，进而实现叠加效果。

#####################################################################################################################
#####################################################################################################################

import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QLabel
import cv2
import numpy as np


def qimage2numpy(img):

    ptr = img.constBits()
    ptr.setsize(img.byteCount())

    mat = np.array(ptr).reshape(img.height(), img.width(), 4)
    # 格式转换以适配opencv中的一系列操作
    return mat  #返回一个numpy矩阵（opencv）




class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(789, 597)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.sharpenButton = QtWidgets.QPushButton(self.centralwidget)
        self.sharpenButton.setGeometry(QtCore.QRect(100, 510, 101, 31))
        self.sharpenButton.setObjectName("sharpenButton")
        self.brightButton = QtWidgets.QPushButton(self.centralwidget)
        self.brightButton.setGeometry(QtCore.QRect(260, 510, 101, 31))
        self.brightButton.setObjectName("brightButton")
        self.saturationButton = QtWidgets.QPushButton(self.centralwidget)
        self.saturationButton.setGeometry(QtCore.QRect(420, 510, 101, 31))
        self.saturationButton.setObjectName("saturationButton")
        self.blurButton = QtWidgets.QPushButton(self.centralwidget)
        self.blurButton.setGeometry(QtCore.QRect(580, 510, 101, 31))
        self.blurButton.setObjectName("blurButton")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(140, 478, 511, 22))
        self.horizontalSlider.setAutoFillBackground(True)
        self.horizontalSlider.setProperty("value", 49)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(670, 470, 61, 31))
        self.saveButton.setObjectName("saveButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 789, 26))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_load = QtWidgets.QAction(MainWindow)
        self.action_load.setObjectName("action_load")
        self.action_save = QtWidgets.QAction(MainWindow)
        self.action_save.setObjectName("action_save")
        self.menu_file.addAction(self.action_load)
        self.menu_file.addAction(self.action_save)
        self.menubar.addAction(self.menu_file.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "图像处理器"))
        self.sharpenButton.setText(_translate("MainWindow", "锐化"))
        self.brightButton.setText(_translate("MainWindow", "亮度"))
        self.saturationButton.setText(_translate("MainWindow", "饱和度"))
        self.blurButton.setText(_translate("MainWindow", "虚化模糊"))
        self.saveButton.setText(_translate("MainWindow", "确定"))
        self.menu_file.setTitle(_translate("MainWindow", "&文件"))
        self.action_load.setText(_translate("MainWindow", "&载入"))
        self.action_save.setText(_translate("MainWindow", "&另存为"))



class ImageEditor(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(ImageEditor, self).__init__(parent)
        self.setupUi(self)
        self.curr_img = None  # 当前处理的图片
        self.result_img = None  # 每次点击保存后的保存结果
        self.origin_img = None  # 原图
        #之前的版本中，图片的艺术效果无法叠加，为解决该问题为图片设置两个“分身”

        self.pic_height = 440  # qt界面中显示框的高度
        self.pic_width = 730  # qt界面中显示框的宽度
        self.image_label = QLabel(self.centralwidget)  # 显示图片的label 为了涂鸦写了继承了Qlabel的子类
        self.image_label.setGeometry(QtCore.QRect(20, 10, 20 + self.pic_width, 10 + self.pic_height))  # label属性从屏幕上（a,b）位置开始，显示一个c*d的界面
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)  # 设置对齐
        self.action_load.triggered.connect(self.load_file)  # 下面几个是自定义的信号量，就是按钮点击事件
        self.action_save.triggered.connect(self.save_file)
        self.sharpenButton.clicked.connect(self.on_click_sharpen)
        self.blurButton.clicked.connect(self.on_click_blur)
        self.brightButton.clicked.connect(self.on_click_bright)
        self.saturationButton.clicked.connect(self.on_click_saturation)
        self.saveButton.clicked.connect(self.on_click_save)

        self.pix = QPixmap()  # 实例化一个 QPixmap 对象，显示图片用

        self.load_file()  # 构造函数中读入一个图片

    def on_click_save(self):
        self.curr_img = qimage2numpy(self.image_label.pixmap().toImage())  # 从label中提取结果转换成opencv图片

        self.result_img = self.curr_img  # 保存为结果图片

    def on_click_sharpen(self):
        self.sharpen(self.result_img)  # 点击锐化，先进行一次锐化
        self.horizontalSlider.valueChanged.connect(lambda: self.sharpen(self.result_img))  # 将锐化函数与拖动滑动条事件绑定

    def on_click_saturation(self):
        self.saturation(self.result_img)
        self.horizontalSlider.valueChanged.connect(lambda: self.saturation(self.result_img))

    def on_click_blur(self):
        self.blur(self.result_img)
        self.horizontalSlider.valueChanged.connect(lambda: self.blur(self.result_img))

    def on_click_bright(self):
        self.bright(self.result_img)
        self.horizontalSlider.valueChanged.connect(lambda: self.bright(self.result_img))

    def resize_image(self, img):#将img缩放成qt中可以显示的大小


        width = img.shape[1]
        height = img.shape[0]

        scale = self.pic_width / width  # 先算一个比例，根据宽度

        if height * scale > self.pic_height:  # 查看按这个比例缩放高是不是会出界
            scale2 = self.pic_height / (height * scale)  # 是的话再算一次缩放比例
            scale *= scale2

        scale = round(scale, 1)  # 保留一位小数，不然有bug
        out = cv2.resize(img, (0, 0), fx=scale, fy=scale)  # 缩放
        return out

    def load_file(self):
        filename = QFileDialog.getOpenFileName(self, 'open file', filter="JPEG Files(*.jpg);;PNG Files(*.png)")  # 获取路径，filter对文件类型筛选
        img = cv2.imread(filename[0])  # 根据路径读取(filename[0]为路径，filename[1]为类型)
        while img is None:
            QMessageBox.warning(self, "出错了", "读入失败，请重新选择！\n(提示：路径中不能存在中文)", QMessageBox.Yes)
            filename = QFileDialog.getOpenFileName(self, 'open file', filter="JPEG Files(*.jpg);;PNG Files(*.png)")
            img = cv2.imread(filename[0])
        img = self.resize_image(img)  # 缩放成qt可以显示的大小
        self.result_img = img
        self.origin_img = img
        self.show_pic(img)

    def save_file(self):
        filename = QFileDialog.getSaveFileName(self, 'save file', filter="JPEG Files(*.jpg);;PNG Files(*.png)")  # 选择路径
        cv2.imwrite(filename[0], self.result_img)  # 保存

    def sharpen(self, image):
        scale = self.horizontalSlider.value() / 10 + 1  # 卷积核参数1
        scale2 = (scale - 1) / 4 * -1  # 卷积中央数，必须保证卷积核中，最中央的数字是其他所有数字的合乘以-1再加1，这样才能达到锐化效果
        kernel = np.array([[0, scale2, 0], [scale2, scale, scale2], [0, scale2, 0]], np.float32)  # 定义一个核
        self.curr_img = cv2.filter2D(image, -1, kernel=kernel)
        self.show_pic(self.curr_img)

    def blur(self, image):
        scale = (self.horizontalSlider.value()) / 100
        self.curr_img = cv2.GaussianBlur(image, (9, 9), 5 * scale + 0.1)  # 高斯模糊
        self.show_pic(self.curr_img)

    def show_pic(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
        frame = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        self.pix = QPixmap.fromImage(frame)
        self.image_label.setPixmap(self.pix)

    def bright(self, img):
        scale = self.horizontalSlider.value() - 49
        self.curr_img = np.uint8(np.clip((img * 1.0 + scale), 0, 255))  # 用np.clip()函数将数据限定：a<0 => a=0, a>255 => a=255
        self.show_pic(self.curr_img)

    def saturation(self, image):
        scale = (self.horizontalSlider.value()) / 50

        f_img = image.astype(np.float32)
        f_img = f_img / 255.0  # 图像归一化，且转换为浮点型, 颜色空间转换 BGR转为HLS
        # HLS空间，三个通道分别是: 0-Hue色相、1-lightness亮度、2-saturation饱和度
        hls_img = cv2.cvtColor(f_img, cv2.COLOR_BGR2HLS)

        # HLS空间通道2是饱和度，对饱和度进行线性变换，且最大值在255以内，这一归一化了，所以应在1以内
        hls_img[:, :, 2] = scale * hls_img[:, :, 2]
        #hls_img是整张图片的三维矩阵参数，hlsimg[:，:，2]是用切片切出的图像中每个HLS参数中的饱和度S位构成的矩阵
        hls_img[:, :, 2][hls_img[:, :, 2] > 1] = 1
        #图片数组中所有大于1的像素点改为1，因为1为最大值

        # HLS 转BGR 并且变成unit8(8位无符号整数)才可以显示在qt中
        self.curr_img = cv2.cvtColor(hls_img, cv2.COLOR_HLS2BGR)
        self.curr_img = self.curr_img * 255.0  #扩大到原始比例
        self.curr_img = self.curr_img.astype(np.uint8)

        self.show_pic(self.curr_img)# 显示调整后的效果



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = ImageEditor()
    myWin.show()
    sys.exit(app.exec())
