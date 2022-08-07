#!/usr/bin/env python3

import sys, inspect, pathlib
import datetime as dt

class Error(Exception):
    pass

class FilePaths(object):
    if sys.platform == 'win32':
        user_path = str(pathlib.Path().absolute()) + '\\'
        lib_path = user_path + 'lib\\'
        saves_path = user_path + 'saves\\'
        maps_path = user_path + 'maps\\'
        tanks_path = user_path + 'tanks\\'
        shells_path = user_path + 'shells\\'
        cc_lib_path = 'cc_lib.dll'
    elif sys.platform == 'linux':    
        user_path = str(pathlib.Path().absolute()) + '/'
        lib_path = user_path + 'lib/'
        saves_path = user_path + 'saves/'
        maps_path = user_path + 'maps/'
        tanks_path = user_path + 'tanks/'
        shells_path = user_path + 'shells/'
        cc_lib_path = 'cc_lib.so'
    else:
        raise Error('OS not recognized!')

class Logger():
    def __init__(self):
        file_paths = FilePaths()
        self.fp = open('%slogs.txt'%(file_paths.user_path),'a')
        self.first_msg = True
        
    def log(self, text, color=None):
        '''
        Display the text passed and append to the logs.txt file
        parameters:
            text (str): Message to be printed and logged
            color (str): Optional. Color to print the message in. Default is white.
        '''
        RESET = '\033[m' # reset to the default color
        GREEN =  '\033[32m'
        RED = '\033[31m'
        YELLOW = '\033[33m'
        CYAN = '\033[36m'

        BOLD = '\033[1m'
        UNDERLINE = '\033[2m'

        # Prepare log message's time of call and filename that the function is called in
        curr_time = '[%s]'%(str(dt.datetime.now())) # date and time

        frame = inspect.stack()[1]
        filepath = frame[0].f_code.co_filename
        if sys.platform == 'win32':
            filename = ' (%s)'%(filepath.split('\\')[-1].split('.')[0])
        elif sys.platform == 'linux':    
            filename = ' (%s)'%(filepath.split('/')[-1].split('.')[0])
        else:
            filename = ''

        # Form log message
        log_msg = curr_time + filename + ' ' + text

        # Print to terminal in specified color
        if color == 'g' or color == 'G':
            print(GREEN + log_msg + RESET)
        elif color == 'r' or color == 'R':
            print(RED + log_msg + RESET)
        elif color == 'y' or color == 'Y':
            print(YELLOW + log_msg + RESET)
        elif color == 'c' or color == 'C':
            print(CYAN + log_msg + RESET)
        else:
            print(log_msg)
        
        if self.first_msg:
            self.fp.write(f'\n\n{log_msg}\n')
            self.first_msg = False
        else:
            self.fp.write(f'{log_msg}\n')

    def end(self):
        self.fp.close()
