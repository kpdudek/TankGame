#!/usr/bin/env python3

from lib.Utils import FilePaths, initialize_logger
from ui.MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from lib.Physics2D import edge_angle
from PyQt5.QtCore import Qt, QTimer
from lib.Settings import Settings
from PyQt5.QtGui import QIcon
from lib.Camera import Camera
from lib.Entity import Tank
from lib.Scene import Scene
from PyQt5 import QtGui
from typing import List
import numpy as np
import time

class MainWindow(QMainWindow):

    def __init__(self,screen_resolution,debug_mode):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Tank Game')
        
        self.boundary_size = np.array([1600.0,700.0]) #[1500,800]
        window_size = np.array([1850.0,950.0])
        self.screen_width, self.screen_height = screen_resolution.width(), screen_resolution.height()
        offset_x = int((self.screen_width-window_size[0])/2)
        offset_y = int((self.screen_height-window_size[1])/2)
        self.setGeometry(offset_x,offset_y,window_size[0],window_size[1])
        
        self.selected_offset: np.ndarray = np.zeros(2)
        self.selected_tanks: List[Tank] = []
        self.debug_mode = debug_mode
        self.keys_pressed = []
        self.loop_fps = 60.0
        self.paused = False
        self.delta_t = 0.0
        self.button = None
        self.fps = 60.0

        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)

        self.fps_log_timer = QTimer()
        self.fps_log_timer.timeout.connect(self.fps_log)

        self.scene = Scene(self.boundary_size)

        self.camera = Camera()
        self.camera.setScene(self.scene)
        self.camera.keypress_signal.connect(self.keyPressEvent)
        self.camera.keyrelease_signal.connect(self.keyReleaseEvent)
        self.camera.mousepress_signal.connect(self.mousePressEvent)
        self.camera.mousemove_signal.connect(self.mouseMoveEvent)
        self.camera.mouserelease_signal.connect(self.mouseReleaseEvent)

        self.settings = Settings(self.scene,self.camera,debug_mode)
        self.settings.set_debug_mode_signal.connect(self.set_debug_mode)
        self.settings.toggle_fps_log_signal.connect(self.toggle_fps_log)
        self.settings.reset_simulation_signal.connect(self.reset_simulation)
        self.settings_visible = True
        self.settings.ui.expand_collapse_settings_button.clicked.connect(self.expand_collapse_settings)

        self.scene.scene_data_signal.connect(self.settings.update_scene_data)

        self.ui.layout.addWidget(self.camera)
        self.ui.layout.addWidget(self.settings)
        self.show()
        
        self.loop_count = 0
        self.frame_idx = 0
        self.game_timer.start(1000/self.fps)

    def reset_simulation(self):
        self.frame_idx = 0

    def toggle_fps_log(self,enabled):
        if enabled:
            self.fps_log_timer.start(1000)
        else:
            self.fps_log_timer.stop()

    def mousePressEvent(self, e:QtGui.QMouseEvent):
        self.button = e.button()
        pose = np.array([e.x(),e.y()])
        pose_scene = self.camera.mapToScene(pose[0],pose[1])
        pose_scene = np.array([pose_scene.x(),pose_scene.y()])
        self.logger.info(f'Mouse press ({self.button}) at screen: [{pose[0]},{pose[1]}], scene: [{int(pose_scene[0])},{int(pose_scene[1])}]')
        self.mouse_press = pose_scene.copy()

        if self.button == 1: # Left click
            for tank in self.scene.tanks:
                if tank.pixmap.isUnderMouse():
                    self.selected_tanks.append(tank)
                    self.selected_offset = tank.physics.center_pose - pose_scene
                    tank.teleport(pose_scene+self.selected_offset)
                    tank.physics.lock = True
            if len(self.selected_tanks) > 0:
                return
            # pose_scene = self.camera.mapToScene(pose[0],pose[1])
            # pose_scene = np.array([pose_scene.x(),pose_scene.y()])
            max_vel = self.settings.ui.max_speed_spinbox.value()
            self.scene.spawn_tank(max_vel,pose_scene)
            self.scene.tanks[-1].set_debug_mode(self.debug_mode)
            self.scene.tanks[-1].physics.lock = True
        elif self.button == 2: # Right click
            for tank in self.scene.tanks:
                if tank.pixmap.isUnderMouse():
                    self.scene.remove_tank(tank)
        elif self.button == 4: # Wheel click
            pass

    def mouseMoveEvent(self, e:QtGui.QMouseEvent):
        pose = np.array([e.x(),e.y()])
        pose_scene = self.camera.mapToScene(pose[0],pose[1])
        pose_scene = np.array([pose_scene.x(),pose_scene.y()])

        if self.button == 1: # Left click
            if len(self.selected_tanks) > 0:
                for tank in self.selected_tanks:
                    tank.teleport(pose_scene+self.selected_offset)
                return
            # theta = edge_angle(np.zeros(2),pose_scene-self.mouse_press,np.array([100.0,0.0]))
        elif self.button == 2: # Right click
           pass
        elif self.button == 4: # Wheel click
            pass
    
    def mouseReleaseEvent(self, e:QtGui.QMouseEvent):
        pose = np.array([e.x(),e.y()])
        pose_scene = self.camera.mapToScene(pose[0],pose[1])
        pose_scene = np.array([pose_scene.x(),pose_scene.y()])

        if self.button == 1: # Left click
            if len(self.selected_tanks) > 0:
                for tank in self.selected_tanks:
                    tank.teleport(pose_scene+self.selected_offset)
                    tank.physics.lock = False
                self.selected_tanks = []
                return
            velocity = pose_scene-self.mouse_press
            self.scene.tanks[-1].physics.velocity = velocity
            self.scene.tanks[-1].physics.lock = False
        elif self.button == 2: # Right click
            pass
        elif self.button == 4: # Wheel click
            pass
        self.button = None
        self.selected_tanks: List[Tank] = []
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == Qt.Key_Escape:
            self.shutdown()
        elif key == Qt.Key_C:
            self.scene.boid_count_display.setPos(0,0)
            self.camera.resetTransform()
        elif key == Qt.Key_P:
            if self.paused:
                self.logger.info('Resuming...')
                self.paused = False
            else:
                self.logger.info('Pausing...')
                self.paused = True
        elif key == Qt.Key_Space:
            if self.debug_mode:
                self.settings.ui.debug_mode_checkbox.setChecked(False)
            else:
                self.settings.ui.debug_mode_checkbox.setChecked(True)
        elif key == Qt.Key_V:
            self.frame_idx += 1
        elif key == Qt.Key_N:
            if len(self.scene.tanks) <= 0:
                return
            self.scene.tanks[self.scene.current_player_idx].set_current_player(False)
            self.scene.current_player_idx += 1
            if self.scene.current_player_idx > len(self.scene.tanks)-1:
                self.scene.current_player_idx = 0
            self.scene.tanks[self.scene.current_player_idx].set_current_player(True)
        elif not event.isAutoRepeat():
            self.keys_pressed.append(key)
    
    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        if not event.isAutoRepeat() and event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())

    def shutdown(self):
        self.logger.info('Shutdown called...')
        self.game_timer.stop()
        self.fps_log_timer.stop()
        self.close()
    
    def expand_collapse_settings(self):
        if self.settings_visible:
            self.settings.ui.settings_frame.hide()
            self.settings_visible = False
            self.settings.ui.expand_collapse_settings_button.setIcon(QIcon(f'{self.file_paths.user_path}ui/icons/expand_right.png'))
        else:
            self.settings.ui.settings_frame.show()
            self.settings_visible = True
            self.settings.ui.expand_collapse_settings_button.setIcon(QIcon(f'{self.file_paths.user_path}ui/icons/expand_down.png'))

        self.camera.setFocus(True)

    def fps_log(self):
        self.logger.info(f'Max FPS: {self.loop_fps}')
        if self.loop_fps<self.fps:
            self.logger.warn("FPS has dropped below the set value.")

    def process_keys(self):
        cam_speed = 6.0
        zoom_speed = 0.008
        scale_x = self.camera.transform().m11()
        scale_y = self.camera.transform().m22()
        camera_x = self.camera.geometry().width()
        camera_y = self.camera.geometry().height()
        scene_x = self.scene.sceneRect().width()
        scene_y = self.scene.sceneRect().height()
        
        for key in self.keys_pressed:
            if key == Qt.Key_W:
                if camera_y > scene_y*scale_y:
                    return
                self.camera.translate(0,cam_speed)
            elif key == Qt.Key_S:
                if camera_y > scene_y*scale_y:
                    return
                self.camera.translate(0,-cam_speed)
            elif key == Qt.Key_A:
                if camera_x > scene_x*scale_x:
                    return
                self.camera.translate(cam_speed,0)
            elif key == Qt.Key_D:
                if camera_x > scene_x*scale_x:
                    return
                self.camera.translate(-cam_speed,0)
            elif key == Qt.Key_Z:
                self.camera.scale(1.0-zoom_speed,1.0-zoom_speed)
            elif key == Qt.Key_X:
                self.camera.scale(1.0+zoom_speed,1.0+zoom_speed)
            elif key == Qt.Key_Up:
                if len(self.scene.tanks) <= 0:
                    return
                self.scene.tanks[self.scene.current_player_idx].rotate_barrel(-1)
            elif key == Qt.Key_Down:
                if len(self.scene.tanks) <= 0:
                    return
                self.scene.tanks[self.scene.current_player_idx].rotate_barrel(1)
            elif key == Qt.Key_Left:
                if len(self.scene.tanks) <= 0:
                    return
                self.scene.tanks[self.scene.current_player_idx].drive(-1)
            elif key == Qt.Key_Right:
                if len(self.scene.tanks) <= 0:
                    return
                self.scene.tanks[self.scene.current_player_idx].drive(1)
            elif key == Qt.Key_F:
                if len(self.scene.tanks) <= 0:
                    return
                self.scene.tanks[self.scene.current_player_idx].fire_shell()
    
    def set_debug_mode(self,enabled):
        self.scene.set_debug_mode(enabled)
        self.debug_mode = enabled
        self.frame_idx = self.loop_count

    def game_loop(self):
        if self.paused:
            self.process_keys()
            return
        elif self.debug_mode and self.loop_count >= self.frame_idx:
            self.process_keys()
            return
        
        self.loop_count += 1
        if self.debug_mode:
            self.logger.debug(f"Loop number: {self.loop_count}")            
        
        tic = time.time()
        self.process_keys()        
        t = 1.0 / self.fps
        self.scene.update(t)
        toc = time.time()

        # Calculate max FPS
        self.delta_t = toc-tic
        if self.delta_t > 0.0:
            split_fps = 1.0/(toc-tic)
            self.loop_fps = split_fps
