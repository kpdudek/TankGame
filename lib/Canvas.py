#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry, PauseMenu, Map

class Canvas(QtWidgets.QWidget,Utils.FilePaths,PaintUtils.Colors,PaintUtils.PaintBrushes):

    def __init__(self,logger,debug_mode,screen_width,screen_height):
        super().__init__()
        uic.loadUi(f'{self.user_path}ui/canvas.ui',self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.logger = logger
        self.debug_mode = debug_mode
        
        # Drawing data
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = 0
        self.camera_offset = numpy.array([[0.],[0.]])
        self.width = -1
        self.height = -1
        self.keys_pressed = []

        # Game data
        self.tanks = []
        self.shells = []
        self.map = None
        self.collision_bodies = []
        self.selected_tank_idx = 0
        self.drive_direction = 0.0
        self.barrel_direction = 0.0

        self.canvas = QtWidgets.QLabel()
        self.layout.addWidget(self.canvas)
        self.pause_menu = PauseMenu.PauseMenu(logger,screen_width,screen_height)

    ##################################################################################
    # Qt Events
    ##################################################################################
    def mousePressEvent(self,e):
        self.logger.log(f'Mouse Press: {e.button()} {e.x()} {e.y()}')
        self.mouse_pose = numpy.array([[e.x()],[e.y()]])
        self.prev_mouse_pose = numpy.array([[e.x()],[e.y()]])

        for idx,tank in enumerate(self.tanks):
            clicked = Geometry.point_is_collision(tank.collision_geometry,self.mouse_pose)
            if clicked:
                self.logger.log(f'Mouse collided with: {tank.name}')
                self.drag_tank_idx = idx
                return
        
        self.collision_bodies = self.shells + [self.map]
        for body in self.collision_bodies:
            selected_entity = Geometry.point_is_collision(body.collision_geometry,self.mouse_pose)
            if selected_entity:
                self.logger.log(f'Mouse collided with: {body.name}')
    
    def mouseMoveEvent(self,e):
        try:
            self.mouse_pose = numpy.array([[e.x()],[e.y()]])
            self.drag_vel = self.mouse_pose - self.prev_mouse_pose
            self.tanks[self.drag_tank_idx].teleport(self.mouse_pose)
            self.tanks[self.drag_tank_idx].physics.velocity = numpy.zeros([2,1])
            self.prev_mouse_pose = numpy.array([[e.x()],[e.y()]])
        except:
            pass

    def mouseReleaseEvent(self,e):
        try:
            self.tanks[self.drag_tank_idx].physics.velocity += self.drag_vel * 1000
        except:
            pass

    def wheelEvent(self,e):
        self.zoom += e.angleDelta().y()/120
        # self.logger.log(f'Zoom changed to: {self.zoom}')

    def keyPressEvent(self, event):
        if event.key() not in self.keys_pressed:
            # self.logger.log(f'Key Pressed: {event.key()}')
            self.keys_pressed.append(event.key())

        if event.key() == QtCore.Qt.Key_Escape:
            self.pause_menu.pause_signal.emit()
            self.pause_menu.show()

        if event.key() == QtCore.Qt.Key_I:
            if self.debug_mode:
                self.pause_menu.pause_signal.emit()

        if event.key() == QtCore.Qt.Key_N:
            self.next_turn()
    
    def keyReleaseEvent(self, event):
        try:
            if not event.isAutoRepeat():
                # self.logger.log(f'Key Released: {event.key()}')
                self.keys_pressed.remove(event.key())
        except:
            pass
            
    ##################################################################################
    # Class Methods
    ##################################################################################
    def next_turn(self):
        self.logger.log('Next turn...')
        self.tanks[self.selected_tank_idx].shots_fired = 0
        self.selected_tank_idx += 1
        if (self.selected_tank_idx > len(self.tanks)-1) or (self.selected_tank_idx < 0):
            self.selected_tank_idx = 0
    
    def load_map(self,map_file):
        self.map = Map.Map(self.logger,self.debug_mode)

        if map_file == 'Generate Random':
            self.logger.log(f'Generating random map...')
            self.map.random()
        else:
            self.logger.log(f'Loading map: {map_file}')
            self.map.read_from_file(map_file)
        
        delta = numpy.zeros([2,1])
        for tank in self.tanks:
            tank.teleport(self.map.seed_pose + delta)
            delta[0] += 400

    def process_key_presses(self):
        gas_val = 0
        for key in self.keys_pressed:
            # D - move right
            if key == QtCore.Qt.Key_D:
                self.drive_direction += 1.0 #rad
                gas_val += 1.0
            
            # A - move left
            elif key == QtCore.Qt.Key_A:
                self.drive_direction += -1.0 #rad
                gas_val += 1.0
            
            # W - move up
            elif key == QtCore.Qt.Key_W:
                self.barrel_direction += 1.0
                gas_val += 1.0
            
            # S - move down
            elif key == QtCore.Qt.Key_S:
                self.barrel_direction += -1.0
                gas_val += 1.0
            
            # up arrow - raise tank firing power
            elif key == QtCore.Qt.Key_Up:
                self.tanks[self.selected_tank_idx].power_scale += 0.005
                if self.tanks[self.selected_tank_idx].power_scale > 1.0:
                    self.tanks[self.selected_tank_idx].power_scale = 1.0
            
            # down arrow - lower tank firing power
            elif key == QtCore.Qt.Key_Down:
                self.tanks[self.selected_tank_idx].power_scale -= 0.005
                if self.tanks[self.selected_tank_idx].power_scale < .1:
                    self.tanks[self.selected_tank_idx].power_scale = .1
            
            # left arrow - rotate barrel counter clockwise
            elif key == QtCore.Qt.Key_Left:
                self.tanks[self.selected_tank_idx].rotate_barrel(-1)
            
            # right arrow - rotate barrel clockwise
            elif key == QtCore.Qt.Key_Right:
                self.tanks[self.selected_tank_idx].rotate_barrel(1)
            
            # F - fire shell
            elif key == QtCore.Qt.Key_F:
                shell = self.tanks[self.selected_tank_idx].fire_shell()
                if shell:
                    self.shells.append(shell)
                    self.logger.log(f'Tank [{self.tanks[self.selected_tank_idx].name}] fired a [{shell.name}]')

        self.tanks[self.selected_tank_idx].gas_used += gas_val
        if self.tanks[self.selected_tank_idx].gas_used > self.tanks[self.selected_tank_idx].gas_limit:
            self.tanks[self.selected_tank_idx].gas_used = self.tanks[self.selected_tank_idx].gas_limit
        self.tanks[self.selected_tank_idx].gas_left = self.tanks[self.selected_tank_idx].gas_limit - self.tanks[self.selected_tank_idx].gas_used

    def set_pixmap(self):
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        if (width != self.width) or (height != self.height):
            self.logger.log(f'Creating pixmap with size: {width} {height}')
            self.width = width
            self.height = height
            self.pixmap = QtGui.QPixmap(self.width,self.height)
            self.canvas.setPixmap(self.pixmap)
    
    def update_physics(self,delta_t):
        self.process_key_presses()

        # Update tanks movement
        idx_offset = 0
        for idx in range(0,len(self.tanks)):
            tank = self.tanks[idx+idx_offset]
            if tank.health <= 0:
                if self.selected_tank_idx > idx+idx_offset:
                    self.selected_tank_idx -= 1
                self.tanks.pop(idx+idx_offset)
                idx_offset -= 1
            else:
                forces = tank.gravity_force.copy()
                if (idx+idx_offset) == self.selected_tank_idx:
                    if self.tanks[self.selected_tank_idx].gas_left > 0:
                        if self.drive_direction:
                            forces[0] += self.drive_direction * tank.drive_force
                        if self.barrel_direction:
                            forces[1] += self.barrel_direction * tank.drive_force
                tank.update_position(forces,delta_t,[self.map])
        self.drive_direction = 0.0
        self.barrel_direction = 0.0

        # Update shells movement
        idx_offset = 0
        for idx in range(0,len(self.shells)):
            shell = self.shells[idx+idx_offset]
            if not shell.done:
                if not shell.launched:
                    scale = self.tanks[self.selected_tank_idx].power_scale
                    x = scale*shell.launch_force*math.cos(shell.launch_angle)
                    y = scale*shell.launch_force*math.sin(shell.launch_angle)
                    forces = numpy.array([[x],[y]])
                    shell.launched = True
                else:
                    forces = shell.gravity_force.copy()
                shell.update_position(forces,delta_t,[self.map]+self.tanks)
            else:
                self.shells.pop(idx+idx_offset)
                idx_offset -= 1

    def update_canvas(self,fps_actual,fps_max):
        self.fps_label = "Current FPS: %.0f\nMax FPS: %.0f"%(fps_actual,fps_max)
        try:
            self.aim_label = "Angle: %.2f\nPower: %.2f\nShots Left: %d\nGas Left: %.2f"%(
                    math.degrees(self.tanks[self.selected_tank_idx].barrel_angle),
                    self.tanks[self.selected_tank_idx].power_scale,
                    self.tanks[self.selected_tank_idx].shots_left,
                    self.tanks[self.selected_tank_idx].gas_left)
        except:
            self.aim_label = ''

        self.painter = QtGui.QPainter(self.canvas.pixmap())

        self.background_painter(self.painter)
        self.painter.drawRect(QtCore.QRect(0, 0, self.width, self.height))

        self.map.draw_map(self.painter)

        for tank in self.tanks:
            tank.draw_tank(self.painter)

        for shell in self.shells:
            shell.draw_shell(self.painter)

        self.text_painter(self.painter)
        self.painter.drawText(3,13,200,75,QtCore.Qt.TextWordWrap,self.fps_label)

        cp = self.tanks[self.selected_tank_idx].collision_geometry.sphere.pose
        width = 100
        height = 50
        offset = 40
        aim_rect = QtCore.QRect(QtCore.QPoint(int(cp[0])-(width/2),int(cp[1])+offset),QtCore.QSize(width,height))
        self.painter.drawText(aim_rect,QtCore.Qt.TextWordWrap,self.aim_label)

        self.painter.end()
        self.repaint()
