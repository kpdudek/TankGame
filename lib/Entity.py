#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem
from lib.Noise import generate_perlin_noise_2d, generate_fractal_noise_2d
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from lib.Utils import initialize_logger, FilePaths
from PyQt5.QtCore import Qt, QPointF
from lib.Physics2D import Physics2D
from lib.Geometry import edge_angle
from random import randint
from math import degrees
from PyQt5 import QtGui
import numpy as np
import json

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
        self.top_mesh = self.top_mesh * 1000.0
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

class Tank(object):
    def __init__(self,boundary_size,name,id,mass,max_vel,starting_pose):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.id = id
        self.name = name
        self.config = None
        self.active_stats_str = ''
        self.load_config()

        self.physics:Physics2D = Physics2D(mass,max_vel,self.center_offset)
        self.teleport(starting_pose)
        self.logger.debug(f"Tank {id} spawned at position: {self.physics.position}")

        self.boundary_size = boundary_size
        self.steering_force = np.zeros(2)
        self.ground_angle: float = 0.0 #radians
        self.touching_ground = False
        self.barrell_angle = 0.0
        self.theta_prev = 0.0

    def __str__(self) -> str:
        return f'{self.physics.theta:.2f}\n{self.physics.position}\n{self.physics.velocity}'

    def load_config(self):
        with open(f'{self.file_paths.entity_path}tank.json','r') as fp:
            self.config = json.load(fp)
        
        png_file = f"{self.file_paths.entity_path}{self.config['png_file']}"
        self.hitpoints: int = int(self.config['hitpoints'])
        self.search_radius: int = int(self.config['search_radius'])

        # Scale the pixmap based on the 1x2 array or keep default size if value is null
        pixmap = QtGui.QPixmap(png_file)
        x_size = pixmap.size().width()*self.config['png_scale'][0]
        y_size = pixmap.size().height()*self.config['png_scale'][1]
        if self.config['maintain_aspect']:
            pixmap = pixmap.scaled(x_size, y_size, Qt.KeepAspectRatio)
        else:
            pixmap = pixmap.scaled(x_size, y_size)
        mask = pixmap.createMaskFromColor(QtGui.QColor(0, 0, 0), Qt.MaskOutColor)
        p = QtGui.QPainter(pixmap)
        p.setPen(QtGui.QColor(randint(0,255), randint(0,255), randint(0,255)))
        p.drawPixmap(pixmap.rect(), mask, mask.rect())
        p.end()
        
        self.pixmap = QGraphicsPixmapItem(pixmap)
        x = pixmap.size().width()/2
        y = pixmap.size().height()/2
        self.center_offset:np.ndarray = np.array([pixmap.size().width()/2,pixmap.size().height()/2])
        self.pixmap.setTransformOriginPoint(x,y)

        # Current player display
        self.current_player_stats = QGraphicsTextItem(self.active_stats_str,self.pixmap)
        self.current_player_stats.setPos(20,30)
        self.current_player_stats.setFont(QtGui.QFont("Arial",12))
        self.set_current_player(False)
        
        self.debug_items = []
        # Angle indicator
        self.debug_line = QGraphicsLineItem(x+20,y,x+125,y,self.pixmap)
        self.debug_items.append(self.debug_line)
        # Search radius
        self.debug_search_radius = QGraphicsEllipseItem(x-self.search_radius/2,y-self.search_radius/2,self.search_radius,self.search_radius,self.pixmap)
        self.debug_items.append(self.debug_search_radius)
        # Bounding rectangle
        self.debug_pose = QGraphicsRectItem(0,0,x_size,y_size,self.pixmap)
        self.debug_items.append(self.debug_pose)
        # Title
        self.debug_text = QGraphicsTextItem(str(self.name),self.pixmap)
        self.debug_text.setPos(0,-20)
        self.debug_text.setFont(QtGui.QFont("Arial",12))
        self.debug_items.append(self.debug_text)
    
    def set_debug_mode(self,enabled):
        if enabled:
            self.debug_line.show()
            self.debug_search_radius.show()
            self.debug_pose.show()
            self.debug_text.show()
        else:
            self.debug_line.hide()
            self.debug_search_radius.hide()
            self.debug_pose.hide()
            self.debug_text.hide()
    
    def set_current_player(self,state):
        if state:
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

    def rotate_barrell(self,direction):
        pass

    def drive(self,direction):
        if self.touching_ground:
            self.steering_force = np.array([100.0*direction,-500.0])
        else:
            self.steering_force = np.array([100.0*direction,0.0])

    def update(self,force,time):
        resulting_force = self.steering_force + force
        
        self.physics.update(resulting_force,time)
        self.theta_prev = self.physics.theta

        # Wrap position within the boundary size
        if self.physics.center_pose[0] > self.boundary_size[0]:
            self.teleport(np.array([0.0,self.physics.position[1]]))
        elif self.physics.center_pose[0] < 0.0:
            self.teleport(np.array([self.boundary_size[0],self.physics.position[1]]))
        elif self.physics.center_pose[1] > self.boundary_size[1]:
            self.teleport(np.array([self.physics.position[0],0.0]))
        elif self.physics.center_pose[1] < 0.0:
            self.teleport(np.array([self.physics.position[0],self.boundary_size[1]]))
            
        pose = self.physics.position.copy()
        self.pixmap.setRotation(degrees(-self.physics.theta))
        self.pixmap.setPos(pose[0],pose[1])

        self.steering_force = np.zeros(2)

        self.current_player_stats.setPlainText(str(self))
