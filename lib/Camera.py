#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsView
from lib.Utils import initialize_logger
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui

class Camera(QGraphicsView):
    keypress_signal = pyqtSignal(QtGui.QKeyEvent)
    keyrelease_signal = pyqtSignal(QtGui.QKeyEvent)
    mousepress_signal = pyqtSignal(QtGui.QMouseEvent)
    mousemove_signal = pyqtSignal(QtGui.QMouseEvent)
    mouserelease_signal = pyqtSignal(QtGui.QMouseEvent)

    def __init__(self):
        super().__init__()        
        self.logger = initialize_logger()

        self.setResizeAnchor(QGraphicsView.NoAnchor)
        # self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        # self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.horizontalScrollBar().disconnect()
        self.verticalScrollBar().disconnect()
       
    def mousePressEvent(self, event):
        self.mousepress_signal.emit(event)
    
    def mouseMoveEvent(self, event):
        self.mousemove_signal.emit(event)
    
    def mouseReleaseEvent(self, event):
        self.mouserelease_signal.emit(event)
    
    def keyPressEvent(self, event):
        self.keypress_signal.emit(event)

    def keyReleaseEvent(self, event):
        self.keyrelease_signal.emit(event)