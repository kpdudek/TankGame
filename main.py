#!/usr/bin/env python3

from lib.Utils import initialize_logger, set_logging_level
from PyQt5.QtWidgets import QApplication
from lib.MainWindow import MainWindow
import sys

def main():
    debug_mode = False
    cl_args = sys.argv[1:]
    logger = initialize_logger(level="INFO")
    logger.info(f"Game starting with options: {cl_args}")

    if "-d" in cl_args:
        cl_args.remove("-d")
        set_logging_level("DEBUG")
        debug_mode = True
    else:
        set_logging_level("INFO")
    
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    main_window = MainWindow(screen_resolution,debug_mode)
    try:
        main_window.settings.ui.tank_count_spinbox.setValue(int(cl_args[0]))
    except ValueError:
        logger.warning(f'Invalid optional arguments.')
    except IndexError:
        logger.info(f'No optional arguments provided.')
    except:
        logger.warning(f'Unhandled exception.')
    main_window.settings.reset_simulation()
    
    app.exec_()
    logger.info("Game ended.")

if __name__ == '__main__':
    main()
