#!/usr/bin/env python3

from logging.handlers import RotatingFileHandler
import sys, pathlib, logging
 
class FilePaths(object):
    if sys.platform == 'win32':
        user_path = str(pathlib.Path().absolute()) + '\\'
        lib_path = user_path + 'lib\\'
        ui_path = user_path + 'ui\\'
        entity_path = user_path + 'entities\\'
    elif sys.platform == 'linux':    
        user_path = str(pathlib.Path().absolute()) + '/'
        lib_path = user_path + 'lib/'
        ui_path = user_path + 'ui/'
        entity_path = user_path + 'entities/'
    else:
        raise Error('OS not recognized!')

def set_logging_level(level):
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(level)

def initialize_logger(level=None) -> logging.Logger:
    file_paths = FilePaths()
    logger = logging.getLogger("Rotating Log")

    if level:
        logger.setLevel(level)

    if not logger.hasHandlers():
        max_size = 1024*1024*100 # 10Mb
        path = f'{file_paths.user_path}TankGame.log'
        formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] (%(filename)s:%(lineno)d) %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

        file_handler = RotatingFileHandler(path, maxBytes=max_size, backupCount=5)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.info(f"Console and File loggers initialized.")
    
    return logger
