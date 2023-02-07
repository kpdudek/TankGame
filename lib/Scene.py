#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from lib.Utils import initialize_logger, FilePaths
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import QPen, QBrush, QColor
from lib.Entity import Tank, Map, Shell
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

    def initialize_scene(self,num_tanks,max_vel):        
        self.logger.info(f'Initializing scene with {num_tanks} tanks...')
        self.number_of_tanks = num_tanks

        # Remove all items
        items = self.items()
        for item in items:
            self.removeItem(item)
        
        # Clear tank and tank pixmap lists
        self.tanks: List[Tank] = []
        self.tank_pixmaps: List[QGraphicsPixmapItem] = []

        # Clear shells
        self.shells: List[Shell] = []
        self.shell_pixmaps = []
        
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
        step_size = 500.0
        y_offset = 50.0
        x_offset = y_offset
        for i in range(self.number_of_tanks):
            self.spawn_tank(max_vel,np.array([x_offset,y_offset]))
            x_offset += step_size

    def set_debug_mode(self,enabled):
        for tank in self.tanks:
            tank.set_debug_mode(enabled)
        for shell in self.shells:
            shell.set_debug_mode(enabled)
        self.debug_mode = enabled
    
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
        tank.shell_fired_signal.connect(self.shell_fired)
        self.tanks.append(tank)
        self.tank_pixmaps.append(tank.pixmap)
        self.addItem(tank.pixmap)
        self.update_window_text()
    
    def shell_fired(self,tank_name: str,shell: Shell):
        self.logger.info(f"Tank [{tank_name}] fired shell [{shell.type}]")
        shell.set_debug_mode(self.debug_mode)
        self.addItem(shell.pixmap)
        self.shells.append(shell)
        self.shell_pixmaps.append(shell.pixmap)

    def update(self,time):
        self.gravity = np.array([0,50.8])

        # Loop over every shell, update it's position, and check what they collide with
        for idx,shell in enumerate(self.shells):
            force = self.gravity
            shell.update(force,time)
            self.delete = False
            for item in self.collidingItems(shell.pixmap):
                if item in self.tank_pixmaps:
                    idx = self.tank_pixmaps.index(item)
                    self.logger.info(f'Shell [{shell.type}] collided with tank [{self.tanks[idx].name}]')
                    self.tanks[idx].hit_by(shell)
                    self.delete = True
                    if self.tanks[idx].hitpoints_remaining <= 0:
                        self.removeItem(item)
                        self.tanks.pop(idx)
                elif item == self.terrain.pixmap:
                    self.logger.info(f'Shell [{shell.type}] collided with map [{self.terrain.name}]')
                    self.delete = True
            if self.delete:
                self.removeItem(shell.pixmap)
                self.shells.remove(shell)
        
        # Loop over every tank, check what it collides with, and update it's position
        for idx,tank in enumerate(self.tanks):        
            collisions = []
            collision_names = []
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

            # Calculate the ground angle
            angle = self.terrain.get_segment_angle(tank.physics.center_pose[0].copy())
            tank.ground_angle = angle
            
            # If in debug mode, log extra
            if self.debug_mode:
                self.logger.debug(f"Tank {tank.name}:")
                self.logger.debug(f"\tID: {tank.id}")
                self.logger.debug(f'\tOver terrain with angle {angle}')
                self.logger.debug(f"\tPosition: {tank.physics.position}")
                self.logger.debug(f"\tVelocity: {tank.physics.velocity}")
                self.logger.debug(f"\tSteering force: {tank.steering_force}")
                self.logger.debug(f"\tIn collision with: {collision_names}")
            
            # If the tank hit the terrain, apply no forces
            if self.terrain.pixmap in collisions:
                force = np.zeros(2)
            else:
                force = self.gravity
            
            # Update each tank, and set the rotation to the ground angle
            tank.update(force,time)
            tank.rotate(angle)
