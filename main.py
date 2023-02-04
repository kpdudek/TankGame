#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
from lib.Utils import initialize_logger
from lib.MainWindow import MainWindow
import sys

def main():
    debug_mode = False
    cl_args = sys.argv[1:]
    if "-d" in cl_args:
        logger = initialize_logger(level="DEBUG")
        debug_mode = True
    else:
        logger = initialize_logger(level="INFO")
    logger.info(f"Simulation starting with options: {cl_args}")
    
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    main_window = MainWindow(screen_resolution,debug_mode)
    try:
        main_window.settings.tank_count_spinbox.setValue(int(cl_args[0]))
    except ValueError:
        logger.warning(f'Invalid optional arguments.')
    except IndexError:
        logger.warning(f'No optional arguments provided.')
    except:
        logger.warning(f'Unhandled exception.')
    main_window.settings.reset_simulation()
    main_window.scene.tanks[0].set_current_player(True)
    
    app.exec_()
    logger.info("Simulation ended.")

if __name__ == '__main__':
    main()
