#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class Colors():
    # Game Colors
    brown = '#996633'

    sky_blue = '#1BADDE'
    midnight_blue = '#051962'

    star_gold = '#F7D31E'

    forest_green = '#38690E'
    light_green = '#00FF00'

    white = '#FFFFFF'
    light_gray = '#BDBDBD'
    gray = '#353535'
    black = '#000000'

    red = '#DF0101'
    maroon = '#B40431'

    def get_tank_colors(self):
        tank_colors = [self.brown,self.midnight_blue,self.forest_green,self.white,self.gray,self.black,self.maroon]
        return tank_colors


class PaintBrushes():
    def __init__(self):
        super().__init__()

    def text_painter(self,painter):
        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QColor(self.black))

        brush = QtGui.QBrush()
        brush.setColor(QColor(self.black))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)
    
    def point_painter(self,painter,color):
        pen = QtGui.QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(6)
        pen.setColor(QColor(color))

        brush = QtGui.QBrush()
        brush.setColor(QColor(color))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)

    def background_painter(self,painter):
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QColor(self.sky_blue))

        brush = QtGui.QBrush()
        brush.setColor(QColor(self.sky_blue))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)

    def healthbar_painter(self,painter):
        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QColor(self.light_green))

        brush = QtGui.QBrush()
        brush.setColor(QColor(self.light_green))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)
    
    def tank_painter(self,painter,color):
        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QColor(color))

        brush = QtGui.QBrush()
        brush.setColor(QColor(color))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)

    def tank_debug_painter(self,painter,color):
        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QColor(color))

        brush = QtGui.QBrush()
        brush.setColor(QColor(color))
        brush.setStyle(Qt.NoBrush)

        painter.setPen(pen)
        painter.setBrush(brush)

    def shell_painter(self,painter):
        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QColor(self.gray))

        brush = QtGui.QBrush()
        brush.setColor(QColor(self.gray))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)

    def map_painter(self,painter):
        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QColor(self.brown))

        brush = QtGui.QBrush()
        brush.setColor(QColor(self.brown))
        brush.setStyle(Qt.SolidPattern)

        painter.setPen(pen)
        painter.setBrush(brush)

class DarkColors(Colors):
    def __init__(self):
        super().__init__()
        self.palette = QPalette()
        self.palette.setColor(QPalette.Window, QColor(self.gray))
        self.palette.setColor(QPalette.WindowText, QColor(self.light_gray))#Qt.white)
        self.palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ToolTipBase, QColor(self.light_gray))
        self.palette.setColor(QPalette.ToolTipText, QColor(self.light_gray))
        self.palette.setColor(QPalette.Text, QColor(self.light_gray))
        self.palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ButtonText, QColor(255, 153, 85)) #Qt.white
        self.palette.setColor(QPalette.BrightText, Qt.red)
        self.palette.setColor(QPalette.Link, QColor(255, 153, 85))
        self.palette.setColor(QPalette.Highlight, QColor(255, 153, 85))
        self.palette.setColor(QPalette.HighlightedText, Qt.black)