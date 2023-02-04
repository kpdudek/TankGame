# Tank Game
A classic 2D tank game developed in python using PyQt5 and Numpy

## Installation
The supported platforms are currently Linux and Windows 10.
To run the simulation you will need to have the following installed:
* python3 (>3.6)
* pip3
* numpy
* PyQt5
* git (reccomended)

If you would prefer not to install git and clone the repo, you can download the files from the [main repository webpage](https://github.com/kpdudek/TankGame) by selecing the green `Code` and then `Download ZIP`.

#### *Ubuntu 20.04:*
```
sudo apt install git python3 python3-pip
git clone https://github.com/kpdudek/TankGame.git
pip3 install PyQt5 numpy
```

#### *Windows 10:*
Download python >3.7 from the Microsoft Store and then use pip3 (included in the Microsoft Store download) to install PyQt5 and numpy.

Install git as described [here](https://www.computerhope.com/issues/ch001927.htm#:~:text=How%20to%20install%20and%20use%20Git%20on%20Windows,or%20fetching%20updates%20from%20the%20remote%20repository.%20)
```
git clone https://github.com/kpdudek/TankGame.git
pip3 install PyQt5 numpy
```

## Running the Simulation
After installation, launch the simulation by navigating to the `TankGame` repo you just cloned (or downloaded) and then executing the `main.py` file as follows:
```
/path/to/TankGame> python3 main.py 
```

## Keyboard Controls
**Exit:** Esc

**Camera Pan:** W/S/A/D

**Zoom:** Z/X

**Center Camera:** C

**Pause/Resume:** P

**Enable Debug Mode:** Space Bar