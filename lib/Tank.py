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
        self.collided_with = []
        self.prev_shot_time = -1.0
        self.shots_fired = 0

        fp = open(f'{self.tanks_path}{tank_file}','r')
        tank_data = json.load(fp)
        self.logger.log(f'Creating tank with params: {tank_data}')

        self.name = f"{tank_data['name']}_{name}"
        self.mass = float(tank_data['mass'])
        self.max_vel = Geometry.m_to_px(float(tank_data['max_vel']))
        self.fire_rate = 1.0 / (float(tank_data['fire_rate']) / 60.) # seconds per round
        self.gravity_force = numpy.array([[0],[self.mass * Geometry.m_to_px(9.8)]])
        self.drive_force = float(tank_data['drive_force'])

        self.collision_geometry = Geometry.Polygon(self.name)
        self.collision_geometry.from_tank_data(tank_data)
        self.collision_geometry.translate(numpy.array([[100.],[500]]))

        self.visual_geometry = QtGui.QPolygonF()
        self.update_visual_geometry()

        self.physics = Physics.Physics2D(self.mass,self.max_vel)
        self.physics.position = self.collision_geometry.sphere.pose.copy()

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
            r = int(self.collision_geometry.sphere.radius)
            self.tank_debug_painter(painter,self.red)
            painter.drawEllipse(x-r, y-r, r*2, r*2)
            self.point_painter(painter,self.red)
            painter.drawPoint(x,y)

    def update_position(self,forces,delta_t,collision_bodies):
        old_pose = self.physics.position.copy()

        offset = self.physics.accelerate(forces,delta_t)
        self.collision_geometry.translate(offset)

        self.collided_with = []
        for body in collision_bodies:
            if Geometry.polygon_is_collision(self.collision_geometry,body.collision_geometry):
                self.physics.position = old_pose
                self.collision_geometry.translate(-1*offset)
                self.physics.velocity = numpy.zeros([2,1])
                self.collided_with.append(body.name)
        
        self.update_visual_geometry()

    def fire_shell(self):
        t = time.time()
        if (t-self.prev_shot_time) > self.fire_rate:
            starting_pose = self.collision_geometry.sphere.pose + numpy.array([[30],[-25]])
            self.prev_shot_time = t
            self.shots_fired += 1
            return Shell.Shell(self.logger,self.debug_mode,'simple.shell',f'{self.shots_fired}',starting_pose)
        else:
            return None