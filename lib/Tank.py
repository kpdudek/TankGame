#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry, Physics, Shell

class Tank(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger, debug_mode, tank_file, name):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode
        self.tank_file = tank_file
        self.name = name
        self.collided_with = []
        self.prev_shot_time = -1.0

        fp = open(f'{self.tanks_path}{tank_file}','r')
        tank_data = json.load(fp)

        self.collision_geometry = Geometry.Polygon(name)
        self.collision_geometry.from_tank_data(tank_data)

        self.visual_geometry = QtGui.QPolygonF()
        self.update_visual_geometry()

        self.mass = float(tank_data['mass'])
        self.max_vel = Geometry.m_to_px(float(tank_data['max_vel']))
        self.fire_rate = 1.0 / (float(tank_data['fire_rate']) / 60.) # seconds per round

        self.logger.log(f'Created tank with params: Mass: {self.mass} Max Vel: {self.max_vel} Fire Rate: {self.fire_rate}')
        self.physics = Physics.Physics2D(self.mass,self.max_vel)
        self.physics.position = self.collision_geometry.sphere.pose

    def update_visual_geometry(self):
        self.visual_geometry = QtGui.QPolygonF()
        r,c = self.collision_geometry.vertices.shape
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)

    def draw_tank(self,painter):
        self.tank_painter(painter,self.forest_green)
        painter.drawPolygon(self.visual_geometry)

        if self.debug_mode:
            x = int(self.collision_geometry.sphere.pose[0])
            y = int(self.collision_geometry.sphere.pose[1])
            r = int(self.collision_geometry.sphere.radius) * 2
            self.tank_debug_painter(painter,self.forest_green)
            painter.drawEllipse(x, y, r, r)

    def update_position(self,forces,delta_t,collision_bodies):
        old_pose = self.physics.position.copy()
        old_vertices = self.collision_geometry.vertices.copy()

        # self.physics.position += self.physics.velocity
        offset = self.physics.accelerate(forces,delta_t)
        self.collision_geometry.translate(offset)

        # collision_geometry is of type Polygon
        self.collided_with = []
        for body in collision_bodies:
            if Geometry.polygon_is_collision(self.collision_geometry,body.collision_geometry):
                self.physics.position = old_pose
                self.collision_geometry.translate(-1*offset)
                self.physics.velocity = numpy.zeros([2,1])
                self.collided_with.append(body.collision_geometry.game_id)
        
        self.update_visual_geometry()

    def fire_shell(self):
        t = time.time()
        if (t-self.prev_shot_time) > self.fire_rate:
            starting_pose = self.collision_geometry.sphere.pose + numpy.array([[50],[-155]])
            self.prev_shot_time = t
            return Shell.Shell(self.logger,'simple.shell','simple1',starting_pose)

        else:
            return None