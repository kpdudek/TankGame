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
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.zoom = 0
        self.keys_pressed = []
        self.width = -1
        self.height = -1

        self.tanks = []
        self.selected_tank_idx = 0
        self.drive_direction = 0.0
        self.barrel_direction = 0.0

        self.shells = []

        self.map = None

        self.collision_bodies = []

        self.canvas = QtWidgets.QLabel()
        self.layout.addWidget(self.canvas)

        self.pause_menu = PauseMenu.PauseMenu(logger,screen_width,screen_height)

    ##################################################################################
    # Qt Events
    ##################################################################################
    def mousePressEvent(self,e):
        self.logger.log(f'Mouse Press: {e.button()} {e.x()} {e.y()}')
        self.mouse_pose = numpy.array([[e.x()],[e.y()]])
        
        self.collision_bodies = self.tanks + self.shells + [self.map]
        for body in self.collision_bodies:
            selected_entity = Geometry.point_is_collision(body.collision_geometry,self.mouse_pose)
            if selected_entity:
                self.logger.log(f'Mouse collided with: {body.name}')
    
    def mouseMoveEvent(self,e):
        pass

    def mouseReleaseEvent(self,e):
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

        if event.key() == QtCore.Qt.Key_N:
            self.pause_menu.pause_signal.emit()
    
    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            # self.logger.log(f'Key Released: {event.key()}')
            self.keys_pressed.remove(event.key())

    ##################################################################################
    # Class Methods
    ##################################################################################
    def load_map(self,map_file):
        self.logger.log(f'Loading map: {map_file}')
        self.map = Map.Map(self.logger,map_file,self.screen_width,self.screen_height)

    def process_key_presses(self):
        for key in self.keys_pressed:
            if key == QtCore.Qt.Key_D:
                self.drive_direction += 1.0 #rad
            elif key == QtCore.Qt.Key_A:
                self.drive_direction += -1.0 #rad
            elif key == QtCore.Qt.Key_W:
                self.barrel_direction += 1.0
            elif key == QtCore.Qt.Key_S:
                self.barrel_direction += -1.0
            
            elif key == QtCore.Qt.Key_F:
                shell = self.tanks[self.selected_tank_idx].fire_shell()
                if shell:
                    self.shells.append(shell)
                    self.logger.log(f'Tank [{self.tanks[self.selected_tank_idx].name}] fired a [{shell.name}]')

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
        for idx,tank in enumerate(self.tanks):
            forces = tank.gravity_force.copy()
            if idx == self.selected_tank_idx:
                if self.drive_direction:
                    forces[0] += self.drive_direction * tank.drive_force
                if self.barrel_direction:
                    forces[1] += self.barrel_direction * tank.drive_force
            tank.update_position(forces,delta_t,[self.map])
        self.drive_direction = 0.0
        self.barrel_direction = 0.0

        # Update shells movement
        for idx,shell in enumerate(self.shells):
            if not shell.collided_with:
                if not shell.launched:
                    forces = shell.launch_force.copy()
                    shell.launched = True
                else:
                    forces = shell.gravity_force.copy()
                shell.update_position(forces,delta_t,[self.map])

    def update_canvas(self,fps_actual,fps_max):
        self.fps_label = "Current FPS: %.0f\nMax FPS: %.0f"%(fps_actual,fps_max)

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

        self.painter.end()
        self.repaint()
