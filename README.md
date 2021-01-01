# Tank Game

## Installation
To run the game you need python3, pip3, numpy, and PyQt5.

#### Ubuntu 18.04
```
sudo apt-get install git
git clone https://github.com/kpdudek/PyQtGame.git
sudo apt-get install python3-pip
pip3 install PyQt5 
pip3 install numpy
```

#### Windows 10
Download python >3.7 from the Microsoft Store and then use pip3 to install PyQt5 and numpy from PowerShell.
Install git as described [here](https://www.computerhope.com/issues/ch001927.htm#:~:text=How%20to%20install%20and%20use%20Git%20on%20Windows,or%20fetching%20updates%20from%20the%20remote%20repository.%20)
```
git clone https://github.com/kpdudek/PyQtGame.git
pip3 install PyQt5 
pip3 install numpy
```

## Playing the Game
Launch the game by navigating to the Tank Game folder in a terminal and then executing `main.py`
```
user@computer:~/path/to/PyQtGame$ python3 main.py
```

## Developing
If you're developing, install PyQt tools to get Qt Designer for editing the UI files.
```
pip3 install pyqt5-tools
```

### Compiling C library for collision checking
Use the cc compiler for creating the required libraries.
On linux:
```
cc -fPIC -shared -o cc_lib.so collision_check.c
```
On Windows:
```
cc -fPIC -shared -o cc_lib.dll collision_check.c
```
