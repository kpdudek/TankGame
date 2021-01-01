#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry

class Physics2D(QtWidgets.QWidget,Utils.FilePaths):
    time_scaling = 1.0

    def __init__(self,mass,max_vel):
        super().__init__()
        self.mass = mass
        self.max_vel = max_vel

        self.position = numpy.array([ [0.] , [0.] ])
        self.velocity = numpy.array([ [0.] , [0.] ])
        self.acceleration = numpy.array([ [0.] , [0.] ])

        self.drag_force = numpy.array([ [0.] , [0.] ])
        self.grav_accel = numpy.array([ [0.] , [9.8] ])

        self.c_d = 0.3
        self.prev_time = time.time()

        self.touching_ground = False

    def accelerate(self,force,time):
        # t = time.time()
        self.force = force
        self.compute_drag()

        self.acceleration = force * time
        self.velocity += self.acceleration

        for count,vel in enumerate(self.velocity):
            if abs(vel) > self.max_vel:
                self.velocity[count] = numpy.sign(vel) * self.max_vel

        # self.prev_time = t

    def compute_drag(self):
        # if self.velocity[0] 
        self.drag_force[0] = self.c_d * (-1.0*self.velocity[0])
        self.force[0] += self.drag_force[0]
