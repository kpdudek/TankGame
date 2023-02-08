#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem
from lib.Noise import generate_perlin_noise_2d, generate_fractal_noise_2d
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QPoint
from lib.Utils import initialize_logger, FilePaths
from lib.Physics2D import Physics2D
from lib.Geometry import edge_angle
from PyQt5.QtWidgets import QWidget
from random import randint
from math import degrees
from PyQt5 import QtGui
import numpy as np
import math, time
import json, uuid

class Map(object):
    def __init__(self,boundary_size,name,id):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.id = id
        self.name = name
        self.config = None
        self.boundary_size = boundary_size
        self.top_mesh:np.ndarray = np.zeros(2)
        self.pixmap:QGraphicsPolygonItem = None
        self.load_config()
        self.generate_terrain()

    def top_mesh_str(self)-> str:
        out:str = '['
        for idx in range(len(self.top_mesh[0,:])-1):
            out += f'{self.top_mesh[0,idx]:.2f}, '
        out += f'{self.top_mesh[0,-1]:.2f}]'
        return out
    
    def vertices_str(self)-> str:
        out:str = '['
        for idx in range(len(self.vertices[0,:])-1):
            out += f'[{self.vertices[0,idx]:.2f},{self.vertices[1,idx]:.2f}], '
        out += f'[{self.vertices[0,-1]:.2f},{self.vertices[1,-1]:.2f}]]'
        return out
    
    def load_config(self):
        pass

    def generate_terrain(self):
        self.logger.debug(f'Boundary size: {self.boundary_size}')
        self.size = 20
        self.top_mesh = generate_perlin_noise_2d(np.array([1,self.size]),np.array([1,2]))
        self.top_mesh += 1.0
        self.top_mesh = self.top_mesh / 2.0
        self.top_mesh = self.top_mesh * 800.0
        self.top_mesh = self.top_mesh - 100
        self.logger.debug(f'Map generated with top mesh heights: {self.top_mesh_str()}')

        self.vertices = np.zeros((2,self.size+2))
        self.vertices[:,0] = np.array([0,self.boundary_size[1]])
        for idx in range(self.size):
            if idx == self.size-1:
                vertex = np.array([self.boundary_size[0],self.boundary_size[1]-self.top_mesh[0,idx]])
                self.vertices[:,idx+1] = vertex
            else:
                vertex = np.array([idx*(self.boundary_size[0]/self.size),self.boundary_size[1]-self.top_mesh[0,idx]])
                self.vertices[:,idx+1] = vertex
        self.vertices[:,idx+2] = np.array([self.boundary_size[0],self.boundary_size[1]])
        self.logger.debug(f'Map generated vertices: {self.vertices_str()}')
    
        polygon = QtGui.QPolygonF()
        for idx in range(self.size+2):
            point = QPointF(self.vertices[0,idx],self.vertices[1,idx])
            polygon.append(point)
        self.pixmap = QGraphicsPolygonItem(polygon)
        self.pixmap.setBrush(QtGui.QBrush(QtGui.QColor('#78C13B')))

    def get_segment_angle(self,x_pose):
        for idx in range(self.size-1):
            if x_pose >= self.vertices[0,idx] and x_pose < self.vertices[0,idx+1]:
                angle = edge_angle(self.vertices[:,idx].copy(),self.vertices[:,idx+1].copy(),np.array([self.vertices[0,idx]+200,self.vertices[1,idx]]))
                return angle
        angle = edge_angle(self.vertices[:,idx-1].copy(),self.vertices[:,idx].copy(),np.array([self.vertices[0,idx-1]+200,self.vertices[1,idx-1]]))
        return angle

class Shell(QWidget):
    def __init__(self,id,starting_pose,theta,power,parent_tank):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.id = id
        self.parent_tank: Tank = parent_tank
        self.config = None
        self.steering_force = np.zeros(2)
        self.ground_angle: float = 0.0 #radians
        self.touching_ground = False
        self.power = power
        self.damage = 0.0
        self.load_config()

        self.physics:Physics2D = Physics2D(self.mass,self.max_vel,self.center_offset)
        self.teleport(starting_pose)
        x_vel = self.power*self.launch_force*math.cos(theta)
        y_vel = self.power*self.launch_force*math.sin(theta)
        self.physics.velocity = np.array([x_vel,y_vel])
        self.logger.debug(f"Shell {id} spawned at position: {self.physics.position}")

    def __str__(self) -> str:
        entity_str = ''
        entity_str += f'   Angle: {self.physics.theta:.2f}\n'
        entity_str += f'Position: {self.physics.position[0]:.2f} {self.physics.position[1]:.2f}\n'
        entity_str += f'Velocity: {self.physics.velocity[0]:.2f} {self.physics.velocity[1]:.2f}\n'
        return entity_str

    def load_config(self):
        with open(f'{self.file_paths.entity_path}simple_shell.json','r') as fp:
            self.config = json.load(fp)

        self.type = self.config['type']
        self.mass = self.config['mass']
        self.max_vel = self.config['max_vel']
        self.launch_force = self.config['launch_force']
        self.damage = self.config['damage']
        self.fire_rate = self.config['fire_rate']
        self.capacity = self.config['capacity']
        
        diameter = 6
        radius = diameter/2
        self.pixmap = QGraphicsEllipseItem(-radius,-radius,diameter,diameter)
        r,g,b = randint(0,255), randint(0,255), randint(0,255)
        color = QtGui.QColor(r,g,b)
        black = QtGui.QColor(0,0,0)
        self.pixmap.setPen(black)
        self.pixmap.setBrush(color)
        self.center_offset:np.ndarray = np.array([0,0])
        self.pixmap.setTransformOriginPoint(0,0)

        self.debug_items = []
        # Angle indicator
        self.debug_line = QGraphicsLineItem(20,0,125,0,self.pixmap)
        self.debug_items.append(self.debug_line)

    def set_debug_mode(self,enabled):
        if enabled:
            self.debug_line.show()
        else:
            self.debug_line.hide()

    def teleport(self,pose: np.ndarray):
        offset = pose.copy() - self.center_offset.copy()
        self.physics.position = offset.copy()
        self.physics.center_pose = self.physics.position + self.physics.center_offset
        self.pixmap.setPos(offset[0],offset[1])

    def rotate(self,angle):
        self.physics.theta = angle
        self.pixmap.setRotation(degrees(-angle))

    def update(self,force,time):
        resulting_force = self.steering_force + force
        
        self.physics.update(resulting_force,time)            
        pose = self.physics.position.copy()
        self.pixmap.setRotation(degrees(-self.physics.theta))
        self.pixmap.setPos(pose[0],pose[1])

        self.steering_force = np.zeros(2)

class Tank(QWidget):
    shell_fired_signal = pyqtSignal(Shell)

    def __init__(self,boundary_size,name,id,mass,max_vel,starting_pose):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.id = id
        self.name = name
        self.config = None
        self.active_stats_str = ''
        self.boundary_size = boundary_size
        self.steering_force = np.zeros(2)
        self.ground_angle: float = 0.0 #radians
        self.touching_ground = False
        self.barrel_angle = 0.0
        self.power = 1.0
        self.fuel_remaining = 0.0
        self.hitpoints_remaining = 0.0
        self.load_config()

        self.shell_type = None
        self.shots_remaining = 0
        self.t_shot_prev = 0.0

        self.physics:Physics2D = Physics2D(mass,max_vel,self.center_offset)
        self.teleport(starting_pose)
        self.logger.debug(f"Tank {id} spawned at position: {self.physics.position}")

    def __str__(self) -> str:
        entity_str = ''
        entity_str += f'       Angle: {math.degrees(self.physics.theta):.2f}\n'
        entity_str += f'    Position: {self.physics.position[0]:.2f} {self.physics.position[1]:.2f}\n'
        entity_str += f'    Velocity: {self.physics.velocity[0]:.2f} {self.physics.velocity[1]:.2f}\n'
        entity_str += f'Barrel Angle: {self.barrel_angle:.2f}\n'
        entity_str += f'       Power: {self.power:.2f}\n'
        entity_str += f'   Fuel Left: {self.fuel_remaining:.2f}\n'
        entity_str += f' Health Left: {self.hitpoints_remaining:.2f}\n'
        entity_str += f'  Shots Left: {self.shots_remaining}\n'
        return entity_str

    def load_config(self):
        with open(f'{self.file_paths.entity_path}tank.json','r') as fp:
            self.config = json.load(fp)
        
        # png_file = f"{self.file_paths.entity_path}{self.config['png_file']}"
        self.hitpoints_remaining: float = float(self.config['hitpoints'])
        self.fuel_remaining: float = float(self.config['fuel_level'])

        # Tank color
        r,g,b = randint(0,255), randint(0,255), randint(0,255)
        color = QtGui.QColor(r,g,b)
        black = QtGui.QColor(0,0,0)
        
        # Dome
        d = 24
        r = d/2
        self.pixmap = QGraphicsEllipseItem(-r,-r,d,d)
        self.pixmap.setPen(black)
        self.pixmap.setBrush(color)
        self.center_offset:np.ndarray = np.array([0,0])
        self.pixmap.setTransformOriginPoint(0,0)

        # Body
        width = 50
        height = 20
        self.body = QGraphicsRectItem(-width/2,0,width,height,self.pixmap)
        self.body.setPen(black)
        self.body.setBrush(color)

        # Barrel
        self.barrel_len = 25
        self.barrel_offset = -9
        self.barrel_center = 3
        self.barrel = QGraphicsRectItem(0,self.barrel_offset,self.barrel_len,5,self.pixmap)
        self.barrel.setPen(black)
        self.barrel.setBrush(color)
        self.barrel.setTransformOriginPoint(0,self.barrel_offset+self.barrel_center)

        # Name text
        self.name_text = QGraphicsTextItem(self.name,self.pixmap)
        self.name_text.setPos(10,-75)
        self.name_text.setFont(QtGui.QFont("Arial",12))

        # Health Bar
        self.health_bar = QGraphicsRectItem(self.pixmap)
        self.update_health_bar()

        # Current player display
        self.current_player_stats = QGraphicsTextItem(self.active_stats_str,self.pixmap)
        self.current_player_stats.setPos(-20,30)
        self.current_player_stats.setFont(QtGui.QFont("Arial",12))
        self.set_current_player(False)
        
        self.debug_items = []
        # Angle indicator
        self.debug_line = QGraphicsLineItem(width/2+10,0,125,0,self.pixmap)
        self.debug_items.append(self.debug_line)
    
    def set_debug_mode(self,enabled):
        if enabled:
            self.debug_line.show()
        else:
            self.debug_line.hide()
    
    def set_current_player(self,state):
        if state:
            self.reload('simple_shell')
            self.current_player_stats.show()
        else:
            self.current_player_stats.hide()

    def teleport(self,pose: np.ndarray):
        offset = pose.copy() - self.center_offset.copy()
        self.physics.position = offset.copy()
        self.physics.center_pose = self.physics.position + self.physics.center_offset
        self.pixmap.setPos(offset[0],offset[1])

    def rotate(self,angle):
        self.physics.theta = angle
        self.pixmap.setRotation(degrees(-angle))

    def rotate_barrel(self,direction):
        angle = self.barrel_angle + direction * 0.75
        if angle < -180.0:
            angle = -180.0
        elif angle > 0.0:
            angle = 0.0
        self.barrel.setRotation(angle)
        self.barrel_angle = angle

    def update_health_bar(self):
        self.health_bar.setRect(0,-40,self.hitpoints_remaining*.25,4)
        self.health_bar.setBrush(QtGui.QColor(0,255,0))

    def drive(self,direction):
        if self.fuel_remaining <= 0:
            return
        
        if self.touching_ground:
            drive_force = 5000
            drive_x = math.cos(self.ground_angle) * drive_force
            drive_y = -1 * math.sin(self.ground_angle) * drive_force
            self.steering_force = direction * np.array([drive_x,drive_y])
        else:
            self.steering_force = np.array([100.0*direction,0.0])

        self.fuel_remaining -= 1.0
    
    def reload(self,shell_type):
        self.shell_type = shell_type
        if shell_type == 'simple_shell':
            self.shots_remaining = 5#Shell().capacity
        self.t_shot_prev = time.time()

    def fire_shell(self):
        t = time.time()
        fire_rate = 1.0/2.0
        if self.shots_remaining > 0 and t-self.t_shot_prev > fire_rate:
            theta = 1*(-1*self.physics.theta+math.radians(self.barrel_angle))
            x_comp = self.barrel_len*math.cos(theta)
            y_comp = self.barrel_len*math.sin(theta)
            barrel_tip = np.array([self.physics.position[0] + x_comp, self.physics.position[1]+self.barrel_offset+self.barrel_center + y_comp])
            shell = Shell(uuid.uuid4(),barrel_tip,theta,self.power,self)
            self.shell_fired_signal.emit(shell)

            self.shots_remaining -= 1
            self.t_shot_prev = t

    def hit_by(self,shell: Shell):
        self.hitpoints_remaining -= shell.damage
        if self.hitpoints_remaining <= 0:
            self.hitpoints_remaining = 0.0
        self.update_health_bar()

    def update(self,force,time):
        resulting_force = self.steering_force + force
        
        self.physics.update(resulting_force,time)            
        pose = self.physics.position.copy()
        # self.pixmap.setRotation(degrees(-self.physics.theta))
        self.pixmap.setPos(pose[0],pose[1])

        self.steering_force = np.zeros(2)
        self.current_player_stats.setPlainText(str(self))
