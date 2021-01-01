#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry, Physics

class Shell(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger, shell_file, name,starting_pose):
        super().__init__()
        self.logger = logger
        self.shell_file = shell_file
        self.name = name
        self.collided_with = []
        self.launched = False

        fp = open(f'{self.shells_path}{shell_file}','r')
        shell_data = json.load(fp)

        self.collision_geometry = Geometry.Polygon(name)
        self.collision_geometry.from_shell_data(shell_data)
        self.collision_geometry.teleport(starting_pose)

        self.visual_geometry = QtGui.QPolygonF()
        self.update_visual_geometry()

        self.physics = Physics.Physics2D(10,100.0)
        self.physics.position = self.collision_geometry.sphere.pose

    def update_visual_geometry(self):
        self.visual_geometry = QtGui.QPolygonF()
        r,c = self.collision_geometry.vertices.shape
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)

    def draw_shell(self,painter):
        self.shell_painter(painter)
        painter.drawPolygon(self.visual_geometry)

    def update_position(self,collision_bodies):
        old_pose = self.physics.position.copy()
        old_vertices = self.collision_geometry.vertices.copy()

        self.physics.position += self.physics.velocity
        self.collision_geometry.translate(self.physics.velocity)

        # collision_geometry is of type Polygon
        self.collided_with = []
        for body in collision_bodies:
            if Geometry.polygon_is_collision(self.collision_geometry,body.collision_geometry):
                self.physics.position = old_pose
                self.collision_geometry.translate(-1*self.physics.velocity)
                self.physics.velocity = numpy.zeros([2,1])
                self.collided_with.append(body.collision_geometry.game_id)
        
        self.update_visual_geometry()