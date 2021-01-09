#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy

from lib import Utils, PaintUtils, Game, MainMenu, Canvas, Tank, Shell, GameOver

class Game(QtWidgets.QMainWindow,Utils.FilePaths,PaintUtils.Colors):

    def __init__(self,logger,debug_mode,screen,fps):
        super().__init__()
        self.fps = fps
        self.physics_step_time = 1.0/60.0
        self.logger = logger
        self.fps_actual = -1.0
        self.fps_max = -1.0
        self.is_paused = False
        self.prev_loop_tic = None
        self.debug_mode = debug_mode

        self.time_scale = 1.0

        self.screen_height = screen.size().height()
        self.screen_width = screen.size().width()

        self.welcome_width = 800.
        self.welcome_height = 600.
        self.welcome_offset_x = int((self.screen_width-self.welcome_width)/2.)
        self.welcome_offset_y = int((self.screen_height-self.welcome_height)/2.)

        self.loop_count = 0
        self.keys_pressed = []

        # setting title 
        self.setWindowTitle('Tank Game : Welcome Screen')
        self.setGeometry(self.welcome_offset_x, self.welcome_offset_y, self.welcome_width, self.welcome_height) 

        # Set main widget as main windows central widget
        self.main_menu = MainMenu.MainMenu(logger)
        self.main_menu.start_game_button.clicked.connect(self.start_game)
        self.main_menu.load_game_button.clicked.connect(self.load_game)
        if self.debug_mode:
            self.main_menu.debug_mode_checkbox.setChecked(True)

        self.game_timer = QtCore.QTimer()
        self.game_timer.timeout.connect(self.game_loop)

        # Show main window
        self.setCentralWidget(self.main_menu)
        self.show()

    def start_game(self):
        self.logger.log(f'Starting game: {self.main_menu.game_name_line_edit.text()}')
        self.setWindowTitle('Tank Game : Running')

        self.debug_mode = self.main_menu.debug_mode_checkbox.isChecked()

        self.canvas = Canvas.Canvas(self.logger,self.debug_mode,self.screen_width,self.screen_height)
        self.canvas.pause_menu.quit_signal.connect(self.quit_game)
        self.canvas.pause_menu.pause_signal.connect(self.toggle_pause_state)
        
        tank_colors = [self.forest_green,self.midnight_blue,self.star_gold]
        for tank_idx in range(0,self.main_menu.number_of_tanks_spinbox.value()):
            color = tank_colors[random.randint(0,len(tank_colors)-1)]
            self.canvas.tanks.append(Tank.Tank(self.logger,self.debug_mode,'m1_abrams.tank',str(tank_idx+1),color))
        
        self.canvas.load_map(self.main_menu.map_files_combobox.currentText())

        self.game_over = GameOver.GameOver(self.logger,self.screen_width,self.screen_height)
        self.game_over.quit_signal.connect(self.quit_game)
        self.game_over.return_to_menu_signal.connect(self.show_main_menu)

        self.setCentralWidget(self.canvas)
        self.setFocus(False)
        self.canvas.setFocus(True)
        self.showMaximized()

        if self.debug_mode:
            self.logger.log(f'Starting game in debug mode! Use the "n" key to step through frames')

        self.prev_loop_tic = time.time()
        self.game_timer.start(1000/self.fps)

    def save_game(self):
        pass

    def show_main_menu(self):
        self.canvas.setFocus(False)
        self.setFocus(True)

        self.main_menu = MainMenu.MainMenu(self.logger)
        self.main_menu.start_game_button.clicked.connect(self.start_game)
        self.main_menu.load_game_button.clicked.connect(self.load_game)
        
        self.setCentralWidget(self.main_menu)
        self.setWindowTitle('Tank Game : Welcome Screen')

        try:
            self.game_over.close()
        except:
            pass

        QtGui.QGuiApplication.processEvents()

    def load_game(self):
        save_game_file = self.main_menu.save_files_combobox.currentText()
        self.logger.log(f'Loading game from save file: {save_game_file}')

    def quit_game(self):
        self.logger.log('Shutdown signal received...')
        self.logger.log('Saving game...')
        self.save_game()
        self.canvas.pause_menu.close()
        self.game_over.close()
        self.close()

    def toggle_pause_state(self):
        if self.is_paused:
            self.logger.log('Resuming game...')
            self.is_paused = False
            if not self.debug_mode:
                self.canvas.setEnabled(True)
        else:
            self.logger.log('Pausing game...')
            self.is_paused = True
            if not self.debug_mode:
                self.canvas.setEnabled(False)

    def game_loop(self):
        if len(self.canvas.tanks) > 1:
            # Capture loop start time
            tic = time.time()
            loop_time = tic - self.prev_loop_tic
            physics_loops = int(loop_time/self.physics_step_time)
            
            # Compute game step
            if not self.is_paused:
                self.canvas.set_pixmap()
                self.canvas.update_physics(loop_time * self.time_scale)
                self.canvas.update_canvas(self.fps_actual,self.fps_max)
            toc = time.time()

            # Try to compute the actual fps and max fps. Expect it might try to divide by zero
            try:
                self.fps_actual = 1.0/(tic-self.prev_loop_tic)
                self.fps_max = 1.0/(toc-tic)
            except ZeroDivisionError:
                pass

            # If you're in debug mode, pause at the end of every step
            if self.debug_mode:
                self.is_paused = True

            # Set loop variables
            self.loop_count += 1
            self.prev_loop_tic = tic
        else:
            winning_tank = f'{self.canvas.tanks[0].name} won!'
            self.game_over.winning_tank_label.setText(winning_tank)
            self.game_over.show()
            self.game_timer.stop()
            