#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry, Noise

class MapCreator(QtWidgets.QWidget):
    def __init__(self,logger, debug_mode):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode

        self.scale = 800.
    
    def random_map(self):
        self.length = 3000.
        self.bottom_height = 50

        num_vertices = random.randint(10,20)
        self.logger.log(f'Generating random map with {num_vertices} top vertices...')
        grid = Noise.perlin_noise(num_vertices)
        idx = random.randint(0,num_vertices)

        # top_surface = numpy.average(grid,axis=0) * self.scale * -1.
        top_surface = grid[idx,:] * self.scale * -1.
        x_spacing = numpy.linspace(0,self.length,num=num_vertices)
        vertices = numpy.vstack((x_spacing,top_surface))
        
        bottom_right = numpy.array([[self.length],[self.bottom_height]])
        bottom_left = numpy.array([[0.0],[self.bottom_height]])
        vertices = numpy.hstack((vertices,bottom_right,bottom_left))
        
        # print(vertices)
        return vertices

class Map(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger,debug_mode,screen_width,screen_height):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.map_creator = MapCreator(self.logger,self.debug_mode)

    def read_from_file(self,map_file):
        fp = open(f'{self.maps_path}{map_file}','r')
        map_data = json.load(fp)
        self.name = map_data['name']
        
        self.collision_geometry = Geometry.Polygon(self.name)
        self.collision_geometry.from_map_data(map_data)
        offset = numpy.array([[0.],[self.screen_height]])
        self.collision_geometry.translate(offset)

        r,c = self.collision_geometry.vertices.shape
        self.visual_geometry = QtGui.QPolygonF()
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)

    def random(self):
        self.name ='ground'
        vertices = self.map_creator.random_map()
        
        self.collision_geometry = Geometry.Polygon(self.name)
        self.collision_geometry.custom(vertices)

        offset = numpy.array([[0.],[self.screen_height]])
        self.collision_geometry.translate(offset)

        r,c = self.collision_geometry.vertices.shape
        self.visual_geometry = QtGui.QPolygonF()
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)

    def draw_map(self,painter):
        self.map_painter(painter)
        painter.drawPolygon(self.visual_geometry)

        if self.debug_mode:
            self.point_painter(painter,self.black)
            r,c = self.collision_geometry.vertices.shape
            for idx in range(0,int(c)):
                x = int(self.collision_geometry.vertices[0,idx])
                y = int(self.collision_geometry.vertices[1,idx])
                painter.drawPoint(x,y)
