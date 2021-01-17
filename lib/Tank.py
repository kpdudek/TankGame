#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json, ctypes

from lib import Utils, PaintUtils, Geometry, Physics, Shell


class Tank(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):
    turn_over_signal = QtCore.pyqtSignal()

    def __init__(self,logger, debug_mode, tank_file, shell_file, shell_list, name, color):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode
        self.tank_file = tank_file

        self.alive = True
        self.collided_with = []
        self.prev_shot_time = -1.0
        self.shell_type = shell_file
        self.shell_list = shell_list
        self.shell_idx = self.shell_list.index(self.shell_type)
        shell = Shell.Shell(self.logger,self.debug_mode,self,shell_file,f'{0}',numpy.zeros([2,1]),0.0)
        self.shot_limit = shell.capacity 
        self.shots_fired = 0
        self.shots_left = self.shot_limit - self.shots_fired
        self.gas_limit = 500.0
        self.gas_used = 0.0
        self.gas_left = self.gas_limit - self.gas_used
        self.xp = 0.0
        self.turn_over = False    

        self.angle = 0.0

        self.barrel_angle = 0.0
        self.power_scale = 1.0
        self.armour_rating = None

        fp = open(f'{self.tanks_path}{tank_file}','r')
        tank_data = json.load(fp)
        fp.close()

        self.name = f"{tank_data['name']}_{name}"
        self.logger.log(f'Creating tank: {self.name}')

        self.color = color
        self.mass = float(tank_data['mass'])
        self.max_vel = Geometry.m_to_px(float(tank_data['max_vel']))
        self.fire_rate = 1.0 / (float(tank_data['fire_rate']) / 60.) # seconds per round
        self.gravity_force = numpy.array([[0.0],[self.mass * Geometry.m_to_px(9.8)]])
        self.drive_force = float(tank_data['drive_force'])
        self.upper_barrel_limit = math.radians(20.0)
        self.lower_barrel_limit = math.radians(-200.0)
        self.health = float(tank_data['health'])
        self.max_health = float(tank_data['health'])

        self.collision_geometry = Geometry.Polygon(self.name)
        self.collision_geometry.from_tank_data(tank_data,'vertices')

        self.barrel_geometry = Geometry.Polygon(self.name)
        self.barrel_geometry.from_tank_data(tank_data,'barrel')
        x,y = tank_data['barrel_offset']
        self.barrel_offset = numpy.array([[float(x)],[float(y)]])
        self.barrel_geometry.translate(self.barrel_offset)

        self.barrel_length = float(tank_data['barrel_length'])
        x = self.barrel_length * math.cos(self.barrel_angle)
        y = self.barrel_length * math.sin(self.barrel_angle)
        self.barrel_tip = self.barrel_offset + numpy.array([[x],[y]])

        self.armour_rating = float(tank_data['armour_rating'])

        self.visual_geometry = QtGui.QPolygonF()
        self.visual_barrel = QtGui.QPolygonF()
        self.update_visual_geometry()

        self.physics = Physics.Physics2D(self.mass,self.max_vel)
        self.physics.position = self.collision_geometry.sphere.pose.copy()

        # C library for collision checking
        self.c_double_p = ctypes.POINTER(ctypes.c_double)
        self.cc_fun = ctypes.CDLL(f'{self.lib_path}{self.cc_lib_path}') # Or full path to file
        self.cc_fun.polygon_is_collision.argtypes = [self.c_double_p,ctypes.c_int,ctypes.c_int,self.c_double_p,ctypes.c_int,ctypes.c_int] 

    def switch_shell(self):
        if self.shots_left != self.shot_limit:
            return
        self.shell_idx += 1
        if self.shell_idx >= len(self.shell_list):
            self.shell_idx = 0
        self.shell_type = self.shell_list[self.shell_idx]
        shell = Shell.Shell(self.logger,self.debug_mode,self,self.shell_type,f'{0}',numpy.zeros([2,1]),0.0)
        self.shot_limit = shell.capacity 
        self.shots_left = self.shot_limit - self.shots_fired

    def update_visual_geometry(self):
        self.visual_geometry = QtGui.QPolygonF()
        r,c = self.collision_geometry.vertices.shape
        for idx in range(0,c):
            point = QtCore.QPointF(self.collision_geometry.vertices[0,idx],self.collision_geometry.vertices[1,idx])
            self.visual_geometry.append(point)
        
        self.visual_barrel = QtGui.QPolygonF()
        r,c = self.barrel_geometry.vertices.shape
        for idx in range(0,c):
            point = QtCore.QPointF(self.barrel_geometry.vertices[0,idx],self.barrel_geometry.vertices[1,idx])
            self.visual_barrel.append(point)

    def draw_tank(self,painter):
        self.text_painter(painter)
        cp = self.collision_geometry.sphere.pose
        width = 100
        height = 30
        offset = 70
        name_box = QtCore.QRect(QtCore.QPoint(int(cp[0])-(width/2),int(cp[1])-offset),QtCore.QSize(width,height))
        # tank_label = f"{self.xp}\n{self.name}"
        tank_label = f"{self.name}"
        painter.drawText(name_box,QtCore.Qt.TextWordWrap|QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop,tank_label)

        self.healthbar_painter(painter)
        cp = self.collision_geometry.sphere.pose
        width = 60 * (self.health/self.max_health)
        if width < 0.0:
            width = 0.0
        height = 4
        offset = 40
        self.healthbar = QtCore.QRect(QtCore.QPoint(int(cp[0])-(width/2),int(cp[1])-offset),QtCore.QSize(width,height))
        painter.drawRoundedRect(self.healthbar,2,2)

        self.tank_painter(painter,self.color)
        painter.drawPolygon(self.visual_geometry)
        painter.drawPolygon(self.visual_barrel)
        x = int(self.barrel_geometry.vertices[0,0].copy())
        y = int(self.barrel_geometry.vertices[1,0].copy())
        r = 9
        painter.drawEllipse(x-r, y-(r/2), r*2, r*2)

        if self.debug_mode:
            x = int(self.collision_geometry.sphere.pose[0])
            y = int(self.collision_geometry.sphere.pose[1])
            r = int(self.collision_geometry.sphere.radius)
            self.tank_debug_painter(painter,self.red)
            painter.drawEllipse(x-r, y-r, r*2, r*2)
            self.point_painter(painter,self.red)
            painter.drawPoint(x,y)

            painter.drawPoint(int(self.barrel_tip[0]),int(self.barrel_tip[1]))
    
    def teleport(self,pose):
        self.collision_geometry.teleport(pose)
        self.barrel_geometry.teleport(pose+self.barrel_offset)

        x = self.barrel_length * math.cos(self.barrel_angle)
        y = self.barrel_length * math.sin(self.barrel_angle)
        self.barrel_tip = pose+self.barrel_offset + numpy.array([[x],[y]])

        self.physics.position = self.collision_geometry.sphere.pose.copy()
        self.physics.velocity = numpy.zeros([2,1])

    def rotate_barrel(self,sign):
        step_size = 0.01
        step_angle = self.barrel_angle + (sign * step_size)
        if (step_angle > self.upper_barrel_limit) or (step_angle < self.lower_barrel_limit):
            return
        self.barrel_angle = step_angle
        self.barrel_geometry.rotate(sign,step_size)

        x = self.barrel_length * math.cos(self.barrel_angle)
        y = self.barrel_length * math.sin(self.barrel_angle)
        self.barrel_tip = self.collision_geometry.origin + self.barrel_offset + numpy.array([[x],[y]])

    def rotate(self,sign,point=None):
        step_size = 0.01
        self.angle += (step_size * sign)
        
        self.collision_geometry.rotate(sign,step_size,point=point)
        self.collision_geometry.set_bounding_sphere()
        self.physics.position = self.collision_geometry.sphere.pose.copy()
        self.collision_geometry.origin = self.collision_geometry.vertices[:,0].reshape(2,1).copy()

        prev_offset = self.barrel_offset.copy()
        tmp_offset = Geometry.rotate_2d(prev_offset,sign*step_size)
        self.barrel_offset = tmp_offset
        self.barrel_geometry.teleport(self.collision_geometry.origin + self.barrel_offset)

        self.rotate_barrel(sign)

    def update_position(self,forces,delta_t,angle,collision_bodies):
        old_pose = self.physics.position.copy()

        self.rotate(angle,point=self.collision_geometry.sphere.pose)
        offset = self.physics.accelerate(forces,delta_t)
        self.collision_geometry.translate(offset)
        self.barrel_geometry.translate(offset)
        self.barrel_tip += offset

        self.collided_with = []
        for body in collision_bodies:
            data = self.collision_geometry.vertices
            r1,c1 = self.collision_geometry.vertices.shape
            data = data.astype(numpy.double)
            data_p = data.ctypes.data_as(self.c_double_p)

            data2 = body.collision_geometry.vertices
            r2,c2 = body.collision_geometry.vertices.shape
            data2 = data2.astype(numpy.double)
            data_p2 = data2.ctypes.data_as(self.c_double_p)

            # C Function call in python
            if Geometry.sphere_is_collision(self.collision_geometry,body.collision_geometry):
                res = self.cc_fun.polygon_is_collision(data_p,int(r1),int(c1),data_p2,int(r2),int(c2))
                if res:
                    self.rotate(-1.0 * angle,point=self.collision_geometry.sphere.pose)
                    self.physics.position = old_pose
                    self.collision_geometry.translate(-1*offset)
                    self.barrel_geometry.translate(-1*offset)
                    self.barrel_tip -= offset
                    self.physics.velocity = numpy.zeros([2,1])
                    self.collided_with.append(body.name)
                    offset = numpy.zeros([2,1])
        
        self.update_visual_geometry()

    def fire_shell(self):
        t = time.time()
        if (t-self.prev_shot_time) > self.fire_rate:
            if self.shots_fired >= self.shot_limit:
                return None
            starting_pose = self.barrel_tip
            self.prev_shot_time = t
            self.shots_fired += 1
            self.shots_left = self.shot_limit - self.shots_fired

            launch_angle = self.barrel_angle+self.angle
            shell = Shell.Shell(self.logger,self.debug_mode,self,self.shell_type,f'{self.shots_fired}',starting_pose,launch_angle)
            
            self.shot_limit = shell.capacity
            self.logger.log(f'Tank [{self.name}] fired a [{shell.name}]')
            return shell
        else:
            return None

    def hit(self,shell,parent,blast=False):
        if blast:
            self.logger.log(f'{self.name} was hit by a {shell.name} blast radius fired by {parent.name}')
            parent.xp += shell.max_damage * 0.5
            self.health -= shell.max_damage * 0.5
        else:
            self.logger.log(f'{self.name} was hit by a {shell.name} fired by {parent.name}')
            parent.xp += shell.max_damage
            self.health -= shell.max_damage

        if self.health < 0.0:
            self.health = 0.0
        self.logger.log(f'{self.name} health is now: {self.health}')

class TankAI(Tank):
    def __init__(self,logger, debug_mode, tank_file, shell_file, shell_list, name, color):
        super().__init__(logger, debug_mode, tank_file, shell_file, shell_list, name, color)
        
        self.barrel_at_setpoint = False
    
    def set_power(self):
        sols = []
        launch_angle = self.barrel_angle+self.angle
        starting_pose = self.barrel_tip
        shell = Shell.Shell(self.logger,self.debug_mode,self,self.shell_type,f'{self.shots_fired}',starting_pose,launch_angle)

        x_goal = float(self.target[0])
        y_goal = float(self.target[1])
        grav = Geometry.m_to_px(9.8)
        for scale in numpy.linspace(.1,1,num=100):
            vx = scale*shell.max_vel*math.cos(launch_angle)
            vy = scale*shell.max_vel*math.sin(launch_angle)

            # Compute time to travel x distance at this starting velocity and angle
            delta_x = x_goal - float(self.barrel_tip[0])
            tx = delta_x/vx

            # Compute time to travel y distance at this starting velocity and angle
            delta_y_peak = (-1.*math.pow(vy,2)) / (2.*grav)
            t_up = -1.*vy / grav
            
            y_max = self.barrel_tip[1] + delta_y_peak
            delta_y_goal = abs(y_goal - y_max)
            v_max = math.sqrt(2.*grav*delta_y_goal)
            t_down = v_max / grav
            ty = t_up + t_down

            # The times should be equal to satisfy this equation
            if abs(tx-ty) < .3:
                sols.append(scale)
        if len(sols) > 0:
            self.power_scale = sols[0]
        # self.logger.log(f'Sols found: {sols}')

    def set_barrel_angle(self):
        if float(self.target[0]) < float(self.collision_geometry.sphere.pose[0]):
            theta = -math.radians(120)
        else:
            theta = -math.radians(60)

        delta_angle = theta - self.barrel_angle
        if abs(delta_angle) > 0.01:
            sign = 1 * numpy.sign(delta_angle)
            self.rotate_barrel(sign)
            self.barrel_at_setpoint = False
        else:
            self.barrel_at_setpoint = True

    def compute_move(self,forces,delta_t,collision_bodies,target):
        shell = None

        self.target = target
        self.set_barrel_angle()
        if self.barrel_at_setpoint:
            self.set_power()
            shell = self.fire_shell()
            
        self.update_position(forces,delta_t,0.0,collision_bodies)
        
        return shell
