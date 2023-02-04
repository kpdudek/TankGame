#!/usr/bin/env python3

import numpy as np
import random

def shuffle(tab):
    for e in reversed(range(0,len(tab)-1)):
        index = round(random.random()*(e-1))
        temp  = tab[e]
        tab[e] = tab[index]
        tab[index] = temp

def make_permutation():
    perm = []
    for i in range(0,256):
        perm.append(i)
    shuffle(perm)
    for i in range(0,256):
        perm.append(perm[i])
    return perm

def get_constant_vector(v):
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

def fade(t):
    return ((6*t - 15)*t + 10)*t*t*t

def lerp(t, a1, a2):
    return a1 + t*(a2-a1)

def perlin_2d(x, y, perm):
    X = int(x) & 255
    Y = int(y) & 255
    xf = x-int(x)
    yf = y-int(y)

    topRight = np.array([[xf-1.0], [yf-1.0]])
    topLeft = np.array([[xf], [yf-1.0]])
    bottomRight = np.array([[xf-1.0], [yf]])
    bottomLeft = np.array([[xf], [yf]])

    # Select a value in the array for each of the 4 corners
    valueTopRight = perm[perm[X+1]+Y+1]
    valueTopLeft = perm[perm[X]+Y+1]
    valueBottomRight = perm[perm[X+1]+Y]
    valueBottomLeft = perm[perm[X]+Y]

    dotTopRight = np.sum(topRight*get_constant_vector(valueTopRight))
    dotTopLeft = np.sum(topLeft*get_constant_vector(valueTopLeft))
    dotBottomRight = np.sum(bottomRight*get_constant_vector(valueBottomRight))
    dotBottomLeft = np.sum(bottomLeft*get_constant_vector(valueBottomLeft))

    u = fade(xf)
    v = fade(yf)

    return lerp(u,lerp(v, dotBottomLeft, dotTopLeft),lerp(v, dotBottomRight, dotTopRight))

def generate_perlin_noise(r,c,out_range=(0,1)):
    '''
        Generates a 2D grid using perlin noise.
        Each value is in the range [-1,1] unless otherwise specified in the out_range param.
        
        Params:
            r int: Number of rows.
            c int: Number of columns.
            out_range (int,int): Tuple of ints to specify the range of the noise values.
        Returns:
            grid (numpy.ndarray): rxc numpy array of floats in the specified param out_range.
    '''
    grid = np.zeros((r,c))
    perm = make_permutation()
    for y in range(0,c):
        for x in range(0,r):
            # Noise2D generally returns a value in the range [-1.0, 1.0]
            n = perlin_2d(x*0.1, y*0.1,perm)
            # Transform the range to [0.0, 1.0], supposing that the range of Noise2D is [-1.0, 1.0]
            # n += 1.0
            # n /= 2.0
            grid[x][y] += n
    return grid

def interpolant(t):
    return t*t*t*(t*(t*6 - 15) + 10)

def generate_perlin_noise_2d(shape,res,tileable=(False,False),interpolant=interpolant):
    """Generate a 2D numpy array of perlin noise.
    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multple of res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            res.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).
    Returns:
        A numpy array of shape shape with the generated noise.
    Raises:
        ValueError: If shape is not a multiple of res.
    """
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]]\
             .transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    if tileable[0]:
        gradients[-1,:] = gradients[0,:]
    if tileable[1]:
        gradients[:,-1] = gradients[:,0]
    gradients = gradients.repeat(d[0], 0).repeat(d[1], 1)
    g00 = gradients[    :-d[0],    :-d[1]]
    g10 = gradients[d[0]:     ,    :-d[1]]
    g01 = gradients[    :-d[0],d[1]:     ]
    g11 = gradients[d[0]:     ,d[1]:     ]
    # Ramps
    n00 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]  )) * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]  )) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = interpolant(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)

def generate_fractal_noise_2d(shape,res,octaves=1,persistence=0.5,lacunarity=2,tileable=(False,False),interpolant=interpolant):
    """Generate a 2D numpy array of fractal noise.
    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multiple of lacunarity**(octaves-1)*res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            (lacunarity**(octaves-1)*res).
        octaves: The number of octaves in the noise. Defaults to 1.
        persistence: The scaling factor between two octaves.
        lacunarity: The frequency factor between two octaves.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The, interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).
    Returns:
        A numpy array of fractal noise and of shape shape generated by
        combining several octaves of perlin noise.
    Raises:
        ValueError: If shape is not a multiple of
            (lacunarity**(octaves-1)*res).
    """
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * generate_perlin_noise_2d(
            shape, (frequency*res[0], frequency*res[1]), tileable, interpolant
        )
        frequency *= lacunarity
        amplitude *= persistence
    return noise