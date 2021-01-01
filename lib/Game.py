#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy

from lib import Utils, PaintUtils, Game, WelcomeScreen, Canvas, Tank, Shell

class Game(QtWidgets.QMainWindow,Utils.FilePaths,PaintUtils.Colors):

    def __init__(self,logger,screen,fps=60.0):
        super().__init__()
        self.fps = fps
        self.logger = logger
        self.fps_actual = 0.0
        self.is_paused = False
        self.prev_loop_tic = time.time()

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
        self.welcome_widget = WelcomeScreen.WelcomeScreen(logger)
        self.welcome_widget.start_game_button.clicked.connect(self.start_game)

        self.canvas = Canvas.Canvas(logger,self.screen_width,self.screen_height)
        self.canvas.pause_menu.quit_signal.connect(self.quit_game)
        self.canvas.pause_menu.pause_signal.connect(self.toggle_pause_state)

        self.game_timer = QtCore.QTimer()
        self.game_timer.timeout.connect(self.game_loop)

        # Show main window
        self.setCentralWidget(self.welcome_widget)
        self.show()

    def start_game(self):
        self.logger.log('Creating game!')
        self.setWindowTitle('Tank Game : Running')

        self.setCentralWidget(self.canvas)
        self.setFocus(False)
        self.canvas.setFocus(True)
        self.showMaximized()

        self.canvas.load_map(self.welcome_widget.map_files_combobox.currentText())
        self.canvas.tanks = [Tank.Tank(self.logger,'m1_abrams.tank','Tank1')]
        self.canvas.shells = [Shell.Shell(self.logger,'simple.shell','simple1',numpy.array([[200.],[600.]]))]

        self.game_timer.start(1000/self.fps)

    def quit_game(self):
        self.logger.log('Shutdown signal received...')
        self.canvas.pause_menu.close()
        self.close()

    def toggle_pause_state(self):
        if self.is_paused:
            self.logger.log('Resuming game...')
            self.is_paused = False
            self.canvas.setEnabled(True)
        else:
            self.logger.log('Pausing game...')
            self.is_paused = True
            self.canvas.setEnabled(False)

    def game_loop(self):
        tic = time.time()
        delta_t = tic - self.prev_loop_tic
        
        if not self.is_paused:
            self.loop_count += 1
            self.canvas.set_pixmap()
            self.canvas.update_physics(delta_t)
            self.canvas.update_canvas(self.fps_actual)
        toc = time.time()
        
        try:
            self.fps_actual = 1.0/(toc-tic)
        except ZeroDivisionError:
            pass

        self.prev_loop_tic = tic