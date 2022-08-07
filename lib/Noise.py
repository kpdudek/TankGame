#!/usr/bin/env python3

import random, numpy

def Shuffle(tab):
    for e in reversed(range(0,len(tab)-1)):
        index = round(random.random()*(e-1))
        temp  = tab[e]
        tab[e] = tab[index]
        tab[index] = temp

def MakePermutation():
    P = []
    for i in range(0,256):
        P.append(i)
    Shuffle(P)
    for i in range(0,256):
        P.append(P[i])
    return P

def GetConstantVector(v):
    # v is the value from the permutation table
    h = v & 3
    if(h == 0):
        return numpy.array([[1.0], [1.0]])
    elif(h == 1):
        return numpy.array([[-1.0], [1.0]])
    elif(h == 2):
        return numpy.array([[-1.0], [-1.0]])
    else:
        return numpy.array([[1.0], [-1.0]])

def Fade(t):
    return ((6*t - 15)*t + 10)*t*t*t

def Lerp(t, a1, a2):
    return a1 + t*(a2-a1)

def Perlin2D(x, y, P):
    X = int(x) & 255
    Y = int(y) & 255
    xf = x-int(x)
    yf = y-int(y)

    topRight = numpy.array([[xf-1.0], [yf-1.0]])
    topLeft = numpy.array([[xf], [yf-1.0]])
    bottomRight = numpy.array([[xf-1.0], [yf]])
    bottomLeft = numpy.array([[xf], [yf]])

    # Select a value in the array for each of the 4 corners
    valueTopRight = P[P[X+1]+Y+1]
    valueTopLeft = P[P[X]+Y+1]
    valueBottomRight = P[P[X+1]+Y]
    valueBottomLeft = P[P[X]+Y]

    dotTopRight = numpy.sum(topRight*GetConstantVector(valueTopRight))
    dotTopLeft = numpy.sum(topLeft*GetConstantVector(valueTopLeft))
    dotBottomRight = numpy.sum(bottomRight*GetConstantVector(valueBottomRight))
    dotBottomLeft = numpy.sum(bottomLeft*GetConstantVector(valueBottomLeft))

    u = Fade(xf)
    v = Fade(yf)

    return Lerp(u,Lerp(v, dotBottomLeft, dotTopLeft),Lerp(v, dotBottomRight, dotTopRight))

def perlin_noise(size):
    grid = numpy.zeros([size,size])
    r,c = grid.shape
    
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