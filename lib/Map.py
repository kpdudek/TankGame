#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry, Noise

class MapCreator(QtWidgets.QWidget):
    def __init__(self,logger, debug_mode):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode

        self.scale = 400.
    
    def random_map(self):
        self.length = 3000.
        self.bottom_height = 500

        num_vertices = random.randint(10,20)
        self.logger.log(f'Generating random map with {num_vertices} top vertices...')
        grid = Noise.perlin_noise(num_vertices)
        idx = random.randint(0,num_vertices-1)

        top_surface = grid[idx,:] * self.scale * -1.
        x_spacing = numpy.linspace(0,self.length,num=num_vertices)
        vertices = numpy.vstack((x_spacing,top_surface))
        
        bottom_right = numpy.array([[self.length],[self.bottom_height]])
        bottom_left = numpy.array([[0.0],[self.bottom_height]])
        vertices = numpy.hstack((vertices,bottom_right,bottom_left))
        
        return vertices

class Map(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger,debug_mode):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode
        self.map_creator = MapCreator(self.logger,self.debug_mode)

    def set_visual_geometry(self):
        r,c = self.collision_geometry.vertices.shape
        self.visual_geometry = QtGui.QPolygonF()
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)

    def read_from_file(self,map_file):
        fp = open(f'{self.maps_path}{map_file}','r')
        map_data = json.load(fp)
        self.name = map_data['name']
        
        self.collision_geometry = Geometry.Polygon(self.name)
        self.collision_geometry.from_map_data(map_data)
        ox,oy = map_data['offset']
        offset = numpy.array([[ox],[oy]])
        tx,ty = map_data['seed_pose']
        self.seed_pose = numpy.array([[tx],[ty]])
        
        self.collision_geometry.translate(offset)
        self.set_visual_geometry()
        self.set_topology()

    def random(self):
        self.name ='ground'
        vertices = self.map_creator.random_map()
        
        self.collision_geometry = Geometry.Polygon(self.name)
        self.collision_geometry.custom(vertices)

        self.seed_pose = numpy.array([[100.],[300.]])

        offset = numpy.array([[0.],[800]])
        self.collision_geometry.translate(offset)

        self.set_visual_geometry()
        self.set_topology()

    def set_topology(self):
        self.topology = self.collision_geometry.vertices[:,0:-2]
        r,c = self.topology.shape
        self.num_segments = c - 1

    def get_segment_angle(self,point):
        x = point[0]
        r,c = self.topology.shape
        seg = None
        for seg_idx in range(0,c-1):
            if (x > self.topology[0,seg_idx]) and (x < self.topology[0,seg_idx + 1]):
                seg = seg_idx
        if seg:
            dx = self.topology[0,seg+1] - self.topology[0,seg]
            dy = self.topology[1,seg+1] - self.topology[1,seg]
            angle = math.atan(dy/dx)
            return angle
        else:
            return None

    def hit(self,shell,parent,blast=False):
        self.logger.log(f'{self.name} was hit by a {shell.name} fired by {parent.name}')

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
