#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from lib.Utils import initialize_logger, FilePaths
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import QPen, QBrush, QColor
from lib.Entity import Tank, Map
from PyQt5.QtCore import Qt
from random import randint
from PyQt5 import QtCore
from typing import List
import numpy as np
import uuid

class Scene(QGraphicsScene):
    shutdown_signal = QtCore.pyqtSignal()

    def __init__(self,boundary_size):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()

        self.debug_mode = False
        self.boundary_size = boundary_size

        self.separation_multiplier = 0.0
        self.cohesion_multiplier = 0.0
        self.align_multiplier = 0.0
        self.x_offset = 0
        self.y_offset = 0

        self.setBackgroundBrush(QBrush(QColor('#5ADCEC')))

    def initialize_scene(self,num_tanks=50,max_vel=400.0):        
        self.logger.info(f'Initializing scene with {num_tanks} tanks...')
        self.number_of_tanks = num_tanks

        # Remove all items
        items = self.items()
        for item in items:
            self.removeItem(item)
        
        # Clear tank and tank pixmap lists
        self.tanks: List[Tank] = []
        self.tank_pixmaps: List[QGraphicsPixmapItem] = []
        
        # Create a new terrain object
        self.terrain = Map(self.boundary_size,'map',uuid.uuid4())
        self.addItem(self.terrain.pixmap)

        # Draw the scene rect
        self.setSceneRect(0,0,self.boundary_size[0],self.boundary_size[1])
        self.rect = QGraphicsRectItem(0.0,0.0,self.boundary_size[0],self.boundary_size[1])
        pen = QPen(Qt.black)
        pen.setWidth(3)
        self.rect.setPen(pen)
        self.addItem(self.rect)
        
        # Add the tank count overlay
        self.boid_count_display = QGraphicsTextItem()
        self.update_window_text()
        self.addItem(self.boid_count_display)

        # Spawn starting tanks
        step_size = 200.0
        y_offset = 50.0
        x_offset = y_offset
        for i in range(self.number_of_tanks):
            self.spawn_tank(max_vel,np.array([x_offset,y_offset]))
            x_offset += step_size

    def set_debug_mode(self,enabled):
        if enabled:
            for tank in self.tanks:
                tank.set_debug_mode(True)
                self.debug_mode = True
        else:
            for tank in self.tanks:
                tank.set_debug_mode(False)
                self.debug_mode = False
    
    def update_window_text(self):
        text = f"Tanks: {len(self.tanks)}\n"
        self.boid_count_display.setPlainText(text)

    def spawn_tank(self,max_vel,pose):
        if not isinstance(pose,np.ndarray):
            rand_x = randint(0,self.boundary_size[0])
            rand_y = randint(0,self.boundary_size[1])
            pose = np.array([rand_x,rand_y])
        
        name = 'kurt'
        tank = Tank(self.boundary_size,name,uuid.uuid4(),1.0,max_vel,pose)
        self.tanks.append(tank)
        self.tank_pixmaps.append(tank.pixmap)
        self.addItem(tank.pixmap)
        self.update_window_text()

    def update(self,time):
        # For each tank, find it's nearest neighbors
        # by checking if their position lies within a certain raius
        forces = []
        for idx,tank in enumerate(self.tanks):
            positions = []
            distances = []
            offsets = []
            for neighbor_idx,other_tank in enumerate(self.tanks):
                # Don't skip yourself. You're part of the group.
                distance = np.linalg.norm(tank.physics.center_pose-other_tank.physics.center_pose)
                if distance < tank.config['search_radius']:
                    distances.append(distance)
                    positions.append(other_tank.physics.center_pose.copy())
                    offsets.append(other_tank.physics.position - tank.physics.position)
            
            collisions = []
            collision_names = []
            # touching_ground = False
            tank.touching_ground = False
            for item in self.collidingItems(tank.pixmap):
                if item in self.tank_pixmaps:
                    collisions.append(item)
                    idx = self.tank_pixmaps.index(item)
                    collision_names.append(self.tanks[idx].name)
                elif item == self.terrain.pixmap:
                    collisions.append(item)
                    collision_names.append(self.terrain.name)
                    tank.physics.velocity = np.zeros(2)
                    tank.touching_ground = True
                    # angle = self.terrain.get_segment_angle(tank.physics.position[0])
                    # self.logger.info(f'Tank {tank.name} over terrain with angle {angle}')
                    # touching_ground = True

            angle = self.terrain.get_segment_angle(tank.physics.center_pose[0].copy())
            tank.ground_angle = angle
            if self.debug_mode:
                self.logger.debug(f"Tank {tank.name}:")
                self.logger.debug(f"\tID: {tank.id}")
                self.logger.debug(f'\tOver terrain with angle {angle}')
                self.logger.debug(f"\tPosition: {tank.physics.position}")
                self.logger.debug(f"\tVelocity: {tank.physics.velocity}")
                self.logger.debug(f"\tSteering force: {tank.steering_force}")
                self.logger.debug(f"\tIn collision with: {collision_names}")

            # if touching_ground:
            #     tank.rotate(angle)
            #     return
            if self.terrain.pixmap in collisions:
                force = np.zeros(2)
            else:
                force = np.array([0,50.8])
            forces.append(force)
            tank.update(force,time)
            tank.rotate(angle)

        # for idx,tank in enumerate(self.tanks):
        #     tank.update(forces[idx],time)