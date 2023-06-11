#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from lib.Utils import initialize_logger, FilePaths
from PyQt5.QtWidgets import QGraphicsPixmapItem
from lib.GameOverDialog import GameOverDialog
from PyQt5.QtGui import QPen, QBrush, QColor
from lib.Entity import Tank, Map, Shell
from PyQt5.QtCore import Qt
from random import randint
from PyQt5 import QtCore
from typing import List
import numpy as np
import uuid, math

class SceneData():
    def __init__(self):
        self.tank_count:int = 0
        self.shell_count:int = 0
        self.current_player:str = ''

class Scene(QGraphicsScene):
    shutdown_signal = QtCore.pyqtSignal()
    scene_data_signal = QtCore.pyqtSignal(SceneData)
    new_game_signal = QtCore.pyqtSignal()

    def __init__(self,main_window,boundary_size):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()

        self.debug_mode = False
        self.main_window = main_window
        self.boundary_size = boundary_size
        self.current_player_idx = 0
        self.setBackgroundBrush(QBrush(QColor('#5ADCEC')))
        self.scene_data = SceneData()

    def send_scene_data(self):
        self.scene_data.tank_count = len(self.tanks)
        self.scene_data.shell_count = len(self.shells)
        self.scene_data.current_player = self.tanks[self.current_player_idx].name
        self.scene_data_signal.emit(self.scene_data)

    def initialize_scene(self,map_type,num_tanks,num_ai,max_vel):        
        self.logger.info(f'Initializing {map_type} scene with {num_tanks} tanks...')
        self.number_of_tanks = num_tanks
        self.number_of_ai = num_ai
        self.map_type = map_type
        self.max_vel = max_vel

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
        self.terrain = Map(self.boundary_size,self.map_type,'map',uuid.uuid4())
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
        total_number_of_tanks = self.number_of_tanks+self.number_of_ai
        step_size = self.boundary_size[0]/total_number_of_tanks
        y_offset = self.terrain.tank_y_offset
        x_offset = step_size/2
        for i in range(self.number_of_tanks):
            self.spawn_tank(max_vel,np.array([x_offset,y_offset]))
            x_offset += step_size
        for i in range(self.number_of_ai):
            self.spawn_tank(max_vel,np.array([x_offset,y_offset]),is_ai=True)
            x_offset += step_size

        self.send_scene_data()

    def set_debug_mode(self,enabled):
        for tank in self.tanks:
            tank.set_debug_mode(enabled)
        for shell in self.shells:
            shell.set_debug_mode(enabled)
        self.debug_mode = enabled
    
    def update_window_text(self):
        text = f"Tanks: {len(self.tanks)}\n"
        self.boid_count_display.setPlainText(text)

    def spawn_tank(self,max_vel,pose,is_ai=False):
        if not isinstance(pose,np.ndarray):
            rand_x = randint(0,self.boundary_size[0])
            rand_y = randint(0,self.boundary_size[1])
            pose = np.array([rand_x,rand_y])
        
        name = f'Tank{len(self.tanks)+1}'
        tank = Tank(self.boundary_size,name,uuid.uuid4(),1.0,max_vel,pose,is_ai)
        tank.shell_fired_signal.connect(self.shell_fired)
        self.tanks.append(tank)
        self.tank_pixmaps.append(tank.body)
        self.addItem(tank.pixmap)
        self.update_window_text()
    
    def shell_fired(self,shell: Shell):
        self.logger.info(f"Tank [{shell.parent_tank.name}] fired shell [{shell.type}]")
        shell.set_debug_mode(self.debug_mode)
        self.addItem(shell.pixmap)
        self.shells.append(shell)
        self.shell_pixmaps.append(shell.pixmap)

    def remove_tank(self,tank: Tank):
        self.removeItem(tank.pixmap)
        idx = self.tanks.index(tank)
        self.tanks.pop(idx)
        self.tank_pixmaps.pop(idx)
        if len(self.tanks) == 1:
            self.current_player_idx = 0
        self.boid_count_display.setPlainText(f"Tanks: {len(self.tanks)}")

    def next_player(self):
        self.tanks[self.current_player_idx].set_current_player(False)
        self.current_player_idx += 1
        if self.current_player_idx > len(self.tanks)-1:
            self.current_player_idx = 0
        self.tanks[self.current_player_idx].set_current_player(True)
        self.logger.info(f'Tank {self.tanks[self.current_player_idx].name} is now the current player.')

    def update(self,time):
        self.gravity = np.array([0,50.8])

        if len(self.tanks) == 0:
            self.logger.error('No tanks left!')
            self.shutdown_signal.emit()
        elif len(self.tanks) == 1:
            winning_tank_str = f'{self.tanks[0].name} won!'
            new_game_promt_str = f'Would you like to start a new game?'
            self.logger.info(winning_tank_str)
            game_over_dialog = GameOverDialog(winning_tank_str+'\n'+new_game_promt_str,self.main_window)
            result = game_over_dialog.exec_()
            if result:
                self.new_game_signal.emit()
                return
            self.shutdown_signal.emit()

        # Loop over every shell, update it's position, and check what they collide with
        for shell in self.shells:
            force = self.gravity
            shell.update(force,time)
            self.delete = False
            colliding_items = shell.pixmap.collidingItems()

            if self.terrain.pixmap in colliding_items:
                self.logger.info(f'Shell [{shell.type}] collided with map [{self.terrain.name}]')
                self.delete = True

                blast_impacted = shell.debug_blast_radius.collidingItems()
                for tank in self.tanks:
                    if tank.pixmap in blast_impacted or tank.body in blast_impacted:
                        self.logger.info(f'Shell [{shell.type}] blast radius affected tank [{tank.name}]')
                        tank.hit_by(shell,direct_hit=False)
                        if tank.hitpoints_remaining <= 0:
                            self.remove_tank(tank)
            else:
                for tank in self.tanks:
                    if tank.pixmap in colliding_items or tank.body in colliding_items:
                        self.logger.info(f'Shell [{shell.type}] direct hit with tank [{tank.name}]')
                        tank.hit_by(shell)
                        self.delete = True
                        if tank.hitpoints_remaining <= 0:
                            self.remove_tank(tank)
            if self.delete:
                self.removeItem(shell.pixmap)
                self.shells.remove(shell)
        
        # Loop over every tank, check what it collides with, and update it's position
        self.logger.debug(f"Current player: {self.tanks[self.current_player_idx].name}")
        for idx,tank in enumerate(self.tanks):        
            collisions = []
            collision_names = []
            tank.touching_ground = False
            colliding_items = self.collidingItems(tank.body)

            if self.terrain.pixmap in colliding_items:
                collisions.append(self.terrain.pixmap)
                collision_names.append(self.terrain.name)
                tank.physics.velocity = np.zeros(2)
                tank.touching_ground = True
            for other_tank in self.tanks:
                if other_tank.id == tank.id:
                    pass
                elif other_tank.pixmap in colliding_items:
                    collisions.append(other_tank.pixmap)
                    collision_names.append(other_tank.name)

            # Calculate the ground angle
            angle = self.terrain.get_segment_angle(tank.physics.center_pose[0].copy(),tank.ground_angle)
            tank.ground_angle = angle
            
            # If the tank hit the terrain, apply no forces
            if tank.touching_ground:
                force = np.zeros(2)
            else:
                force = self.gravity
            
            # Update each tank, and set the rotation to the ground angle
            tank.rotate(angle)
            tank.update(force,time)
            # If in debug mode, log extra
            if self.debug_mode:
                self.logger.debug(f"Tank {tank.name}:")
                self.logger.debug(f"\tID: {tank.id}")
                self.logger.debug(f'\tOver terrain with angle: {math.degrees(angle)}')
                self.logger.debug(f"\tPosition: {tank.physics.position}")
                self.logger.debug(f"\tVelocity: {tank.physics.velocity}")
                self.logger.debug(f"\tSteering force: {tank.steering_force}")
                self.logger.debug(f"\tIn collision with: {collision_names}")

            # Apply AI controls
            if tank.is_currrent_player and tank.is_ai:
                goal_idx = idx+1
                if goal_idx >= len(self.tanks):
                    goal_idx = 0
                target_tank_pose = self.tanks[goal_idx].physics.position
                tank.get_shell_tragectory(target_tank_pose)
                tank.run_ai_turn()

                # If the current tank is an ai, and all it's shells have exploded,
                # advance to the next player
                if tank.shots_remaining == 0 and len(self.shells) == 0:
                    self.next_player()

        self.send_scene_data()
