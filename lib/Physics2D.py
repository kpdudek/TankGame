#!/usr/bin/env python3

from lib.Geometry import edge_angle
import numpy as np

class Physics2D(object):

    def __init__(self,mass,max_vel,center_offset):
        super().__init__()

        self.theta = 0.0
        self.mass = mass
        self.time = None
        self.lock : bool = False
        self.max_velocity = max_vel
        self.center_offset = center_offset
        self.position : np.ndarray = np.zeros(2)
        self.center_pose : np.ndarray = self.position + self.center_offset
        self.velocity : np.ndarray = np.zeros(2)
        self.acceleration : np.ndarray = np.zeros(2)

    def update(self,force,time):
        if self.lock:
            return
        acceleration = force / self.mass
        delta_v = acceleration * time

        self.velocity = self.velocity + delta_v
        self.position = self.position + (self.velocity * time)
        self.center_pose = self.position.copy() + self.center_offset.copy()
        # if sum(self.velocity) > 0.001:
        #     self.theta = edge_angle(np.zeros(2),self.velocity.copy(),np.array([100.0,0.0]))
        
        # If the velocity exceeds the maximum magnitude, scale the velocity vector to match its value
        vel_mag = np.linalg.norm(self.velocity)
        if vel_mag > self.max_velocity:
            scale = self.max_velocity / vel_mag
            self.velocity = self.velocity * scale       
