#!/usr/bin/env python3

import os,sys

def main():
    '''
    This script loops over everything in the ui/ folder and converts all
    .ui files to their respective .py class using the pyuic5 converter

    Make sure to run this script from the demo-director folder for correct
    relative paths for the icons.
    '''
    if 'ui' not in os.listdir('.'):
        print('Could not locate the ui/ folder. Are you running the script from the demo-director directory?')
        return
    
    files = os.listdir('./ui')
    for file_name in files:
        if file_name[-3:] == '.ui':
            base,extension = file_name.split('.')
            os.system(f'pyuic5 ./ui/{file_name} -o ./ui/{base}.py')

if __name__ == '__main__':
    main()
