#!/usr/bin/env python3

from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem
from lib.Noise import generate_perlin_noise_2d, generate_fractal_noise_2d
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QPoint
from lib.Utils import initialize_logger, FilePaths
from lib.Physics2D import Physics2D
from lib.Geometry import edge_angle
from PyQt5.QtWidgets import QWidget
from random import randint, random
from math import degrees
from PyQt5 import QtGui
import numpy as np
import math, time
import json, uuid

class Map(object):
    def __init__(self,boundary_size,map_type,name,id):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.id = id
        self.name = name
        self.map_type = map_type
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
        self.logger.debug(f'Boundary size for terrain: {self.boundary_size}')
        if self.map_type == 'Perlin':
            self.size = 26
            self.top_mesh = generate_perlin_noise_2d(np.array([1,self.size]),np.array([1,2]))
            self.top_mesh += 1.0
            self.top_mesh = self.top_mesh / 2.0
            self.top_mesh = self.top_mesh * 800.0
            self.top_mesh = self.top_mesh - 100
            self.tank_y_offset = 100
        elif self.map_type == 'Flat':
            self.size = 4
            self.top_mesh = np.zeros([1,self.size])+300
            self.tank_y_offset = 300
        elif self.map_type == 'Peak':
            self.size = 3
            self.top_mesh = np.zeros([1,self.size])+200
            self.top_mesh[0,1] = 500
            self.tank_y_offset = 200
        self.logger.debug(f'Map generated with top mesh heights: {self.top_mesh_str()}')

        self.vertices = np.zeros((2,self.size+2))
        self.vertices[:,0] = np.array([0,self.boundary_size[1]])
        for idx in range(self.size):
            if idx == self.size-1:
                vertex = np.array([self.boundary_size[0],self.boundary_size[1]-self.top_mesh[0,idx]])
                self.vertices[:,idx+1] = vertex
            else:
                vertex = np.array([idx*(self.boundary_size[0]/(self.size-1)),self.boundary_size[1]-self.top_mesh[0,idx]])
                self.vertices[:,idx+1] = vertex
        self.vertices[:,idx+2] = np.array([self.boundary_size[0],self.boundary_size[1]])
        self.logger.debug(f'Map generated vertices: {self.vertices_str()}')
    
        polygon = QtGui.QPolygonF()
        for idx in range(self.size+2):
            point = QPointF(self.vertices[0,idx],self.vertices[1,idx])
            polygon.append(point)
        self.pixmap = QGraphicsPolygonItem(polygon)
        self.pixmap.setBrush(QtGui.QBrush(QtGui.QColor('#78C13B')))

    def get_segment_angle(self,x_pose,current_angle):
        for idx in range(self.size):
            if x_pose >= self.vertices[0,idx] and x_pose < self.vertices[0,idx+1]:
                angle = edge_angle(self.vertices[:,idx].copy(),self.vertices[:,idx+1].copy(),np.array([self.vertices[0,idx]+200,self.vertices[1,idx]]))
                return -1*angle
        return current_angle

class Shell(QWidget):
    def __init__(self,shell_type,id,starting_pose,theta,power,parent_tank):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.shell_type = shell_type
        self.id = id
        self.parent_tank: Tank = parent_tank
        self.config = None
        self.steering_force = np.zeros(2)
        self.ground_angle: float = 0.0 #radians
        self.touching_ground = False
        self.power = power
        self.damage = 0.0
        self.load_config()

        theta = theta + ((random()*2-1)*math.radians(self.max_scatter))
        self.physics:Physics2D = Physics2D(self.mass,self.max_vel,self.center_offset)
        self.teleport(starting_pose)
        x_vel = self.power*math.cos(theta)
        y_vel = self.power*math.sin(theta)
        self.physics.velocity = np.array([x_vel,y_vel])
        self.physics.theta = theta
        self.rotate(-self.physics.theta)
        self.logger.debug(f"Shell {id} spawned at position: {self.physics.position}")

    def __str__(self) -> str:
        entity_str = ''
        entity_str += f'   Angle: {self.physics.theta:.2f}\n'
        entity_str += f'Position: {self.physics.position[0]:.2f} {self.physics.position[1]:.2f}\n'
        entity_str += f'Velocity: {self.physics.velocity[0]:.2f} {self.physics.velocity[1]:.2f}\n'
        return entity_str

    def load_config(self):
        with open(f'{self.file_paths.entity_path}{self.shell_type}.json','r') as fp:
            self.config = json.load(fp)
        
        self.type = self.config['type']
        self.png_file_name = self.config['png_file']
        self.png_scale = self.config['png_scale']
        self.maintain_aspect = self.config['maintain_aspect']
        self.starting_pose = self.config['pose']
        self.mass = self.config['mass']
        self.max_vel = self.config['max_vel']
        self.damage = self.config['damage']
        self.blast_radius = self.config['blast_radius']
        self.armour_penetration = self.config['armour_penetration']
        self.fire_rate = self.config['fire_rate']
        self.capacity = self.config['capacity']
        self.max_scatter = self.config['max_scatter']
        
        if self.type == 'simple_shell':
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
        elif self.type == 'nuke':
            diameter = 12
            radius = diameter/2
            self.pixmap = QGraphicsEllipseItem(-radius,-radius,diameter,diameter)
            black = QtGui.QColor(0,0,0)
            self.pixmap.setPen(black)
            self.pixmap.setBrush(black)
            self.center_offset:np.ndarray = np.array([0,0])
            self.pixmap.setTransformOriginPoint(0,0)
        elif self.type == 'burst':
            diameter = 4
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
        # Blast radius
        self.debug_blast_radius = QGraphicsEllipseItem(-self.blast_radius/2.0,-self.blast_radius/2.0,self.blast_radius,self.blast_radius,self.pixmap)
        self.debug_items.append(self.debug_blast_radius)

    def set_debug_mode(self,enabled):
        if enabled:
            self.debug_line.show()
            self.debug_blast_radius.show()
        else:
            self.debug_line.hide()
            self.debug_blast_radius.hide()

    def teleport(self,pose: np.ndarray):
        offset = pose.copy() - self.center_offset.copy()
        self.physics.position = offset.copy()
        self.physics.center_pose = self.physics.position + self.physics.center_offset
        self.pixmap.setPos(offset[0],offset[1])

    def rotate(self,angle):
        self.physics.theta = angle
        self.pixmap.setRotation(degrees(angle))

    def update(self,force,time):
        resulting_force = self.steering_force + force
        
        self.physics.update(resulting_force,time)            
        pose = self.physics.position.copy()
        self.rotate(self.physics.theta)
        self.pixmap.setPos(pose[0],pose[1])

        self.steering_force = np.zeros(2)

class Tank(QWidget):
    shell_fired_signal = pyqtSignal(Shell)

    def __init__(self,boundary_size,name,id,mass,max_vel,starting_pose,is_ai):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.debug_mode = False
        self.id = id
        self.name = name
        self.is_ai = is_ai
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

        self.shell_type = 'simple_shell'
        self.shell_type_idx = 0
        self.shell_types = ['simple_shell','nuke','burst']
        self.shots_remaining = 0
        self.t_shot_prev = 0.0

        # AI attributes
        self.time_of_flight = -1.0
        self.barrel_setpoint = 0.0
        self.target_locked = False

        self.physics:Physics2D = Physics2D(mass,max_vel,self.center_offset)
        self.teleport(starting_pose)
        self.logger.debug(f"Tank {id} spawned at position: {self.physics.position}")

    def __str__(self) -> str:
        entity_str = ''
        if self.debug_mode:
            entity_str += f'       Angle : {math.degrees(self.physics.theta):.2f}\n'
            entity_str += f'    Position : {self.physics.position[0]:.2f} {self.physics.position[1]:.2f}\n'
            entity_str += f'    Velocity : {self.physics.velocity[0]:.2f} {self.physics.velocity[1]:.2f}\n'
            entity_str += f'Barrel Angle : {self.barrel_angle:.2f}\n'
        entity_str += f'       Power : {self.power:.2f}\n'
        entity_str += f'   Fuel Left : {self.fuel_remaining:.2f}\n'
        entity_str += f' Health Left : {self.hitpoints_remaining:.2f}\n'
        entity_str += f'  Shell Type : {self.shell_type}\n'
        entity_str += f'  Shots Left : {self.shots_remaining}\n'
        return entity_str

    def load_config(self):
        with open(f'{self.file_paths.entity_path}tank.json','r') as fp:
            self.config = json.load(fp)
        
        self.type = self.config['type']
        self.png_file_name = f"{self.file_paths.entity_path}{self.config['png_file']}"
        self.hitpoints_remaining: float = float(self.config['hitpoints'])
        self.fuel_remaining: float = float(self.config['fuel_level'])
        self.armour_rating: float = float(self.config['armour_rating'])
        self.max_initial_speed = 300.0

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
        self.body_width = 50
        height = 20
        self.body = QGraphicsRectItem(-self.body_width/2,0,self.body_width,height,self.pixmap)
        self.body.setPen(black)
        self.body.setBrush(color)

        # Barrel
        self.barrel_len = 25
        self.barrel_offset = -8
        self.barrel_center = 3
        self.barrel = QGraphicsRectItem(0,self.barrel_offset,self.barrel_len,5,self.pixmap)
        self.barrel.setPen(black)
        self.barrel.setBrush(color)
        self.barrel.setTransformOriginPoint(0,self.barrel_offset+self.barrel_center)

        # Name text
        self.name_text = QGraphicsTextItem(self.name,self.pixmap)
        self.name_text.setPos(-self.body_width/2,-75)
        self.name_text.setFont(QtGui.QFont("Arial",12))

        # Health Bar
        self.health_bar = QGraphicsRectItem(self.pixmap)
        self.update_health_bar()

        # Current player display
        self.current_player_stats = QGraphicsTextItem(self.active_stats_str,self.pixmap)
        self.current_player_stats.setPos(-60,30)
        self.current_player_stats.setFont(QtGui.QFont("Arial",12))
        self.set_current_player(False)
        
        self.debug_items = []
        # Angle indicator
        self.debug_line = QGraphicsLineItem(self.body_width/2+10,0,125,0,self.pixmap)
        self.debug_items.append(self.debug_line)
    
    def set_debug_mode(self,enabled):
        self.debug_mode = enabled
        if enabled:
            self.debug_line.show()
        else:
            self.debug_line.hide()
    
    def set_current_player(self,state):
        if state:
            self.reload(self.shell_type)
            self.current_player_stats.show()
        else:
            self.current_player_stats.hide()
        self.is_currrent_player = state

    def teleport(self,pose: np.ndarray):
        offset = pose.copy() - self.center_offset.copy()
        self.physics.position = offset.copy()
        self.physics.center_pose = self.physics.position + self.physics.center_offset
        self.pixmap.setPos(offset[0],offset[1])

    def rotate(self,angle):
        self.physics.theta = angle
        self.pixmap.setRotation(degrees(angle))

    def rotate_barrel(self,direction):
        angle = self.barrel_angle + direction * 0.75
        if angle < -180.0:
            angle = -180.0
        elif angle > 0.0:
            angle = 0.0
        self.barrel.setRotation(angle)
        self.barrel_angle = angle
    
    def set_power(self,direction):
        self.power += direction * .05
        if self.power > 1.0:
            self.power = 1.0
        elif self.power < 0.05:
            self.power = 0.05

    def update_health_bar(self):
        self.health_bar.setRect(-self.body_width/2,-40,self.hitpoints_remaining*.25,4)
        self.health_bar.setBrush(QtGui.QColor(0,255,0))

    def drive(self,direction):
        if self.fuel_remaining <= 0:
            return
        
        if self.touching_ground:
            drive_force = 5000
            drive_x = math.cos(self.ground_angle) * drive_force
            drive_y = math.sin(self.ground_angle) * drive_force
            self.steering_force = direction * np.array([drive_x,drive_y])
            self.fuel_remaining -= 1.0
    
    def reload(self,shell_type):
        self.shell_type = shell_type
        shell = Shell(shell_type,uuid.uuid4(),np.array([0,0]),0,0,self)
        self.shots_remaining = shell.capacity
        self.fire_rate = shell.fire_rate
        self.t_shot_prev = time.time()
        self.shell_type_locked = False
    
    def change_shell_type(self):
        if self.shell_type_locked:
            self.logger.info(f'Request to change shell type for tank {self.name} blocked because a shell has been fired already.')
            return
        
        self.shell_type_idx += 1
        if self.shell_type_idx >= len(self.shell_types):
            self.shell_type_idx = 0

        self.shell_type = self.shell_types[self.shell_type_idx]
        self.reload(self.shell_type)

    def get_global_barrel_angle(self,angle=None):
        if angle:
            theta = self.physics.theta+(math.radians(angle))
        else:
            theta = self.physics.theta+(math.radians(self.barrel_angle))
        return theta
    
    def get_barrel_angle_from_global(self,global_angle):
        theta = math.radians(global_angle) - self.physics.theta
        return math.degrees(theta)
    
    def get_shell_tragectory(self,goal_pose):
        # If the tank is moving, stop the barrel and dont allow firing
        # if np.sum(self.physics.velocity) > 0.1:
        #     self.logger.debug(f'Tank still moving, so skipping ai step.')
        #     self.barrel_setpoint = self.barrel_angle
        #     self.target_locked = False
        #     return
        
        # Given the goal pose, solve for
        #   - shell type (drive closer to minimize spray)
        #   - tank position (get out of blast radius)
        #   - power (power down as you get closer)
        #   - barrel angle (find angle that will hit target)
        
        # Determine which side the goal is on (left or right) and set the global
        # barrel angle to 45 degrees off vertical
        #TODO: make the barrel aim 30 degrees above vector pointing towards goal?
        delta_x = float(goal_pose[0] - self.physics.position[0])
        if delta_x > 0.0:
            self.barrel_setpoint = self.get_barrel_angle_from_global(-55.0)
        elif delta_x < 0.0:
            self.barrel_setpoint = self.get_barrel_angle_from_global(-125.0)
        self.logger.debug(f'Barrel set to {self.barrel_setpoint}')

        # Get the barrel tip pose
        theta = self.get_global_barrel_angle(angle=self.barrel_setpoint)
        x_comp = (self.barrel_len)*math.cos(theta)
        y_comp = (self.barrel_len)*math.sin(theta)
        barrel_tip = np.array([self.physics.position[0] + x_comp, self.physics.position[1]+self.barrel_offset+self.barrel_center + y_comp])

        best_error = 1000
        for power in np.linspace(0.05,1.0,100):
            launch_speed = power*self.max_initial_speed
            t_peak = -launch_speed*math.sin(theta) / 50.8
            y_peak = barrel_tip[1] - abs(launch_speed*math.sin(theta)*t_peak + 0.5*50.8*math.pow(t_peak,2))
            t_descent = math.sqrt(2*abs(goal_pose[1]-y_peak)/50.8)
            t_horizontal = delta_x/(launch_speed*math.cos(theta))
            time_error = t_horizontal - (t_peak+t_descent)
            if abs(time_error) < best_error:
                best_error = time_error
                self.power = power
        
        self.logger.debug(f'Shell time error: {best_error}')
        self.logger.debug(f'Tragectory will hit peak Y {y_peak} in {t_peak} seconds')
        self.logger.debug(f'Descent will take {t_descent} seconds')
        self.logger.debug(f'Horizontal travel will take {t_horizontal} seconds')
        self.target_locked = True
    
    def run_ai_turn(self):
        # Determine if the barrel is at the setpoint or not
        barrel_position_error = self.barrel_setpoint-self.barrel_angle
        aimed = True
        if abs(barrel_position_error) > 1.0:
            aimed = False

        # Move the barrrel towards the setpoint, if it is not within tolerance
        if not aimed:
            direction = (barrel_position_error)/abs(barrel_position_error)
            self.rotate_barrel(direction)
        # Fire a shell if within tolerance of the setpoint, and the target_locked flag is True
        elif aimed and self.target_locked:
            self.fire_shell()
    
    def fire_shell(self):
        t = time.time()
        if self.shots_remaining > 0 and t-self.t_shot_prev > 1.0/self.fire_rate:
            theta = self.get_global_barrel_angle()
            x_comp = (self.barrel_len)*math.cos(theta)
            y_comp = (self.barrel_len)*math.sin(theta)
            barrel_tip = np.array([self.physics.position[0] + x_comp, self.physics.position[1]+self.barrel_offset+self.barrel_center + y_comp])
            launch_speed = self.power*self.max_initial_speed
            shell = Shell(self.shell_type,uuid.uuid4(),barrel_tip,theta,launch_speed,self)
            self.shell_fired_signal.emit(shell)

            self.shots_remaining -= 1
            self.t_shot_prev = t
            self.shell_type_locked = True

    def hit_by(self,shell: Shell, direct_hit=True):
        damage_multiplier = 1.0
        if not direct_hit:
            damage_multiplier = damage_multiplier * 0.5
        damage_multiplier = damage_multiplier / self.armour_rating * shell.armour_penetration

        damage = shell.damage * damage_multiplier
        self.hitpoints_remaining -= damage
        if self.hitpoints_remaining <= 0:
            self.hitpoints_remaining = 0.0
        self.update_health_bar()
        self.physics.update(np.array([-4000.,-4000.]),1.0/60.0)
        self.logger.info(f'{self.name} took {damage} damage from {shell.type}.')
        self.logger.info(f'{self.name} health remaining: {self.hitpoints_remaining}.')

    def update(self,force,time):
        resulting_force = self.steering_force + force
        
        self.physics.update(resulting_force,time)   
        self.physics.theta = self.ground_angle         
        pose = self.physics.position.copy()
        self.pixmap.setPos(pose[0],pose[1])

        self.steering_force = np.zeros(2)
        self.current_player_stats.setPlainText(str(self))
