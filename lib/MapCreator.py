#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry

def Shuffle(self,tab):
    for e in reversed(range(0,len(tab)-1)):
        index = round(random.random()*(e-1))
        temp  = tab[e]
        tab[e] = tab[index]
        tab[index] = temp

def MakePermutation(self):
    P = []
    for i in range(0,256):
        P.append(i)
    Shuffle(P)
    for i in range(0,256):
        P.append(P[i])
    return P

def GetConstantVector(self,v):
    # v is the value from the permutation table
    h = v & 3
    if(h == 0):
        return np.array([[1.0], [1.0]])
    elif(h == 1):
        return np.array([[-1.0], [1.0]])
    elif(h == 2):
        return np.array([[-1.0], [-1.0]])
    else:
        return np.array([[1.0], [-1.0]])

def Fade(self,t):
    return ((6*t - 15)*t + 10)*t*t*t

def Lerp(self,t, a1, a2):
    return a1 + t*(a2-a1)

def Perlin2D(self,x, y, P):
    X = int(x) & 255
    Y = int(y) & 255
    xf = x-int(x)
    yf = y-int(y)

    topRight = np.array([[xf-1.0], [yf-1.0]])
    topLeft = np.array([[xf], [yf-1.0]])
    bottomRight = np.array([[xf-1.0], [yf]])
    bottomLeft = np.array([[xf], [yf]])

    # Select a value in the array for each of the 4 corners
    valueTopRight = P[P[X+1]+Y+1]
    valueTopLeft = P[P[X]+Y+1]
    valueBottomRight = P[P[X+1]+Y]
    valueBottomLeft = P[P[X]+Y]

    dotTopRight = np.sum(topRight*GetConstantVector(valueTopRight))
    dotTopLeft = np.sum(topLeft*GetConstantVector(valueTopLeft))
    dotBottomRight = np.sum(bottomRight*GetConstantVector(valueBottomRight))
    dotBottomLeft = np.sum(bottomLeft*GetConstantVector(valueBottomLeft))

    u = Fade(xf)
    v = Fade(yf)

    return Lerp(u,Lerp(v, dotBottomLeft, dotTopLeft),Lerp(v, dotBottomRight, dotTopRight))

def perlin_noise(self,size,passes=2,cutoff=1.1):
    grid = np.zeros([size,size])
    r,c = grid.shape
    for i in range(0,passes):
        P = MakePermutation()
        for y in range(0,c):
            for x in range(0,r):
                # Noise2D generally returns a value in the range [-1.0, 1.0]
                n = Perlin2D(x*0.1, y*0.1,P)
                
                # Transform the range to [0.0, 1.0], supposing that the range of Noise2D is [-1.0, 1.0]
                n += 1.0
                n /= 2.0
                grid[x][y] += n
    return grid

class MapCreator(QtWidgets.QWidget):
    def __init__(self,logger, debug_mode):
        super().__init__()
        self.logger = logger
        self.debug_mode = debug_mode
    
    def random_map(self):
        pass