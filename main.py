#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy

from lib import Utils, PaintUtils, Game

def main(logger):
    file_paths = Utils.FilePaths()
    assert(file_paths.cc_lib_path in os.listdir('./lib/')),"cc_lib.so/.dll doesn't exist! Be sure to compile collision_check.c as cc_lib.so/.dll!"

    fps = 100.0
    palette = PaintUtils.DarkColors().palette

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    app.setPalette(palette)

    if '-d' in sys.argv:
        debug_mode = True
    else:
        debug_mode = False
    # Create the instance of our Window 
    game_window = Game.Game(logger,debug_mode,app.primaryScreen(),fps) 

    # Start the app 
    sys.exit(app.exec()) 

if __name__ == '__main__':
    try:
        logger = Utils.Logger()
        logger.log('Launching game...')
        main(logger)
    finally:
        logger.log('Game terminated.')
        logger.end()