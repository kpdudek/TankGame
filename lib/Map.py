#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry

class Map(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger,map_file,screen_width,screen_height):
        super().__init__()

        fp = open(f'{self.maps_path}{map_file}','r')
        map_data = json.load(fp)

        self.collision_geometry = Geometry.Polygon('ground')
        self.collision_geometry.from_map_data(map_data)

        self.visual_geometry = QtGui.QPolygonF()
        for vertex in map_data['vertices']:
            point = QtCore.QPointF(vertex[0],vertex[1])
            self.visual_geometry.append(point)

    def draw_map(self,painter):
        self.map_painter(painter)
        painter.drawPolygon(self.visual_geometry)
