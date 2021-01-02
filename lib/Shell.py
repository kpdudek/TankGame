#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json, ctypes

from lib import Utils, PaintUtils, Geometry, Physics

class Shell(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger, debug_mode, parent, shell_file, name,starting_pose):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode
        self.parent = parent
        self.shell_file = shell_file
        self.collided_with = []
        self.launched = False

        fp = open(f'{self.shells_path}{shell_file}','r')
        shell_data = json.load(fp)

        self.collision_geometry = Geometry.Polygon(name)
        self.collision_geometry.from_shell_data(shell_data)
        self.collision_geometry.teleport(starting_pose)

        self.visual_geometry = QtGui.QPolygonF()
        self.update_visual_geometry()

        self.name = f"{shell_data['name']}_{name}"
        self.mass = float(shell_data['mass'])
        self.max_vel = float(shell_data['max_vel'])
        self.gravity_force = numpy.array([[0],[self.mass * Geometry.m_to_px(9.8)]])
        fx,fy = shell_data['launch_force']
        self.launch_force = numpy.array([[float(fx)],[float(fy)]])

        self.physics = Physics.Physics2D(self.mass,self.max_vel)
        self.physics.position = self.collision_geometry.sphere.pose.copy()

        # C library for collision checking
        self.c_double_p = ctypes.POINTER(ctypes.c_double)
        self.cc_fun = ctypes.CDLL(f'{self.lib_path}{self.cc_lib_path}') # Or full path to file
        self.cc_fun.polygon_is_collision.argtypes = [self.c_double_p,ctypes.c_int,ctypes.c_int,self.c_double_p,ctypes.c_int,ctypes.c_int] 

    def update_visual_geometry(self):
        self.visual_geometry = QtGui.QPolygonF()
        r,c = self.collision_geometry.vertices.shape
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)

    def draw_shell(self,painter):
        self.shell_painter(painter)
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

        for body in collision_bodies:            
            data = self.collision_geometry.vertices
            r1,c1 = self.collision_geometry.vertices.shape
            data = data.astype(numpy.double)
            data_p = data.ctypes.data_as(self.c_double_p)

            data2 = body.collision_geometry.vertices
            r2,c2 = body.collision_geometry.vertices.shape
            data2 = data2.astype(numpy.double)
            data_p2 = data2.ctypes.data_as(self.c_double_p)

            # # C Function call in python
            if Geometry.sphere_is_collision(self.collision_geometry,body.collision_geometry):
                res = self.cc_fun.polygon_is_collision(data_p,int(r1),int(c1),data_p2,int(r2),int(c2))
                if res or Geometry.poly_lies_inside(self.collision_geometry,body.collision_geometry):
                    self.physics.position = old_pose
                    self.collision_geometry.translate(-1*offset)
                    self.physics.velocity = numpy.zeros([2,1])
                    self.collided_with.append(body.name)
                    self.logger.log(f'Shell fired by [{self.parent}] hit {self.collided_with}')
        
        self.update_visual_geometry()