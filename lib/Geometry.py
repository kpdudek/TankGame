#!/usr/bin/env python3

import os, sys, time, math, copy, random
import datetime as dt
import numpy as np

from threading import Thread
from math import sin,cos,atan2
from multiprocessing import Process, Pool

from lib import Utils

def px_to_m(pixels):
    '''
    Converts pixels to meters using the M1 Abrams as a reference
    '''
    scale = 7.94 / 50.0 # 7.94m / 50px
    return pixels * scale

def m_to_px(meters):
    '''
    Converts pixels to meters using the M1 Abrams as a reference
    '''
    scale = 50.0 / 7.94 # 50px / 7.94m
    return meters * scale

def rotate_2d(vertices,angle):
    rot_mat = np.array([[cos(angle),-sin(angle)],[sin(angle),cos(angle)]])
    r,c = vertices.shape
    for idx in range(0,c):
        res = np.matmul(rot_mat,vertices[:,idx].reshape(2,1))
        vertices[0,idx] = res[0]
        vertices[1,idx] = res[1]
    return vertices

def edge_angle(ang_type,*argv):
    '''
    The edge angle is found using unit vectors. This function can be passed two angles defined positive counter clockwise with 0 being horizontal right, or
    a set of three vertices.

    Args:
        ang_type (string): 'angle' or 'vertices' based on the calculation type
        *argv: either two floats with the angle or three vertices
    '''
    # This function finds the signed shortest distance between two vectors
    if ang_type == 'angle':
        assert(len(argv)==2)

        ang1 = float(argv[0])
        ang2 = float(argv[1])
        vertex0 = [0.0,0.0]
        vertex1 = [cos(ang1),sin(ang1)]
        vertex2 = [cos(ang2),sin(ang2)]
    elif ang_type == 'vertices':
        assert(len(argv)==3)

        vertex0 = argv[0]
        vertex1 = argv[1]
        vertex2 = argv[2]

        vertex1[0] = vertex1[0] - vertex0[0]
        vertex1[1] = vertex1[1] - vertex0[1]

        vertex2[0] = vertex2[0] - vertex0[0]
        vertex2[1] = vertex2[1] - vertex0[1]
    else:
        log('Edge angle type not recognized!',color='r')
        return None

    # Dot product of the vectors
    cosine_theta = vertex1[0]*vertex2[0] + vertex1[1]*vertex2[1]
    
    # Cross product of the vectors
    sin_theta = vertex1[0]*vertex2[1] - vertex1[1]*vertex2[0]
    
    # find the angle using the relationships sin(theta)== tan(theta) = sin(theta)/cos(theta)
    edge_angle = atan2(sin_theta,cosine_theta)
    return edge_angle

def cross_product(p1, p2):
    '''
    calculates the cross product of vector p1 and p2
    if p1 is clockwise from p2 wrt origin then it returns +ve value
    if p2 is anti-clockwise from p2 wrt origin then it returns -ve value
    if p1 p2 and origin are collinear then it returs 0
    source: https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    '''
    return p1[0] * p2[1] - p2[0] * p1[1]


def direction(p1, p2, p3):
    '''
    returns the cross product of vector p1p3 and p1p2
    if p1p3 is clockwise from p1p2 it returns +ve value
    if p1p3 is anti-clockwise from p1p2 it returns -ve value
    if p1 p2 and p3 are collinear it returns 0
    source: https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    '''
    return  cross_product(p3-p1, p2-p1)

def on_segment(p1, p2, p):
    '''
    checks if p lies on the segment p1p2
    source: https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    '''
    return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])

def edge_is_collision(edge1,edge2,endpoint_collision=False):
    '''
    checks if line segment p1p2 and p3p4 intersect
    source: https://algorithmtutor.com/Computational-Geometry/Check-if-two-line-segment-intersect/
    '''
    p1 = edge1[:,0]
    p2 = edge1[:,1]
    p3 = edge2[:,0]
    p4 = edge2[:,1]

    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4)

    if endpoint_collision:
        if d1 == 0 and on_segment(p3, p4, p1):
            return True
        elif d2 == 0 and on_segment(p3, p4, p2):
            return True
        elif d3 == 0 and on_segment(p1, p2, p3):
            return True
        elif d4 == 0 and on_segment(p1, p2, p4):
            return True

    # Overlap collision check
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
        ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    else:
        return False

def point_is_collision(poly,point):
    '''
    Check if the point lies inside a concave or convex polygon
    '''
    row,col = poly.vertices.shape
    vertices = poly.vertices.copy()

    tmp = point.copy()
    tmp[0]+=10000
    ray = np.hstack((point.copy(),tmp))
    
    collisions = 0
    for idx in range(0,col):
        if idx == col-1:
            edge = np.concatenate((vertices[:,idx].reshape(2,1),vertices[:,0].reshape(2,1)),axis=1)
        else:
            edge = np.concatenate((vertices[:,idx].reshape(2,1),vertices[:,idx+1].reshape(2,1)),axis=1)
        if edge_is_collision(ray,edge):
            collisions += 1
    if collisions%2 == 0:
        return False
    else:
        return True

def poly_lies_inside(poly1,poly2):
    '''
    Check if the center of mass of poly1 lies inside poly2
    '''
    if point_is_collision(poly2,poly1.sphere.pose.reshape(2,1)):
        return True
    else:
        return False

def sphere_is_collision(poly1,poly2):
    '''
    This function determines if two spheres are in collision
    positive r --> solid sphere
    negative r --> hollow sphere
    '''
    dist = np.sqrt(np.power(poly1.sphere.pose[0]-poly2.sphere.pose[0],2)+np.power(poly1.sphere.pose[1]-poly2.sphere.pose[1],2))
    if (poly1.sphere.radius < 0) and (poly2.sphere.radius < 0):
        return True
    elif (poly1.sphere.radius < 0) or (poly2.sphere.radius < 0):
        if dist > -1*(poly1.sphere.radius+poly2.sphere.radius):
            return True
        else:
            return False
    else:
        if dist < (poly1.sphere.radius+poly2.sphere.radius):
            return True
        else:
            return False

def polygon_is_collision(poly1,poly2):
    '''
    Assume two sets of vertices are passed representing two polygons
    '''
    collision = False
    if not sphere_is_collision(poly1,poly2):
        return collision
    
    vertices1 = poly1.vertices.copy()
    vertices2 = poly2.vertices.copy()
    for idx1 in range(0,len(vertices1[0,:])):
        for idx2 in range(0,len(vertices2[0,:])):
            r,c = vertices1.shape[0:2]
            if idx1 == c-1:
                edge1 = np.concatenate((vertices1[:,idx1].reshape(2,1),vertices1[:,0].reshape(2,1)),axis=1)
            else:
                edge1 = np.concatenate((vertices1[:,idx1].reshape(2,1),vertices1[:,idx1+1].reshape(2,1)),axis=1)
            
            r,c = vertices2.shape[0:2]
            if idx2 == c-1:
                edge2 = np.concatenate((vertices2[:,idx2].reshape(2,1),vertices2[:,0].reshape(2,1)),axis=1)
            else:
                edge2 = np.concatenate((vertices2[:,idx2].reshape(2,1),vertices2[:,idx2+1].reshape(2,1)),axis=1)
               
            if edge_is_collision(edge1,edge2,endpoint_collision=False):
                collision = True
                break

        if collision:
            break

    return collision

class Sphere(object):
    def __init__(self,x,y,r):
        self.pose = np.array([[x],[y]])
        self.radius = r

class Polygon(object):
    def __init__(self,game_id):
        self.game_id = game_id
        self.vertices = None
        self.sphere = None
        self.origin = np.zeros([2,1])
        self.center_of_mass = None

    def custom(self,vertices):
        self.vertices = vertices
        self.set_bounding_sphere()

    def from_map_data(self,map_data):
        vertices = np.zeros([2,len(map_data['vertices'])])
        for idx,vertex in enumerate(map_data['vertices']):
            vertices[0,idx] = vertex[0]
            vertices[1,idx] = vertex[1]
        self.vertices = vertices
        self.set_bounding_sphere()

    def from_tank_data(self,tank_data,key):
        vertices = np.zeros([2,len(tank_data[key])])
        for idx,vertex in enumerate(tank_data[key]):
            vertices[0,idx] = vertex[0]
            vertices[1,idx] = vertex[1]
        self.vertices = vertices
        self.set_bounding_sphere()
    
    def from_shell_data(self,shell_data):
        vertices = np.zeros([2,len(shell_data['vertices'])])
        for idx,vertex in enumerate(shell_data['vertices']):
            vertices[0,idx] = vertex[0]
            vertices[1,idx] = vertex[1]
        self.vertices = vertices
        self.set_bounding_sphere()

    def set_bounding_sphere(self):
        # Compute centroid    
        r,c = self.vertices.shape
        x_c = np.sum(self.vertices[0,:]) / float(c)
        y_c = np.sum(self.vertices[1,:]) / float(c)

        # Compute radius
        rad = 0.
        centroid = np.array([[x_c],[y_c]])
        for idx in range(0,len(self.vertices[0,:])):
            vert = self.vertices[:,idx]
            ray = np.sqrt(np.power(vert[0]-centroid[0],2)+np.power(vert[1]-centroid[1],2))
            if ray > rad:
                rad = ray 
        self.sphere = Sphere(x_c,y_c,rad)
        self.center_of_mass = centroid

    def translate(self,vec):
        self.origin += vec
        self.center_of_mass += vec
        self.vertices += vec
        self.sphere.pose += vec

    def teleport(self,vec):
        diff = vec - self.origin
        self.translate(diff)

    def rotate(self,sign,step_size,point=None):
        if type(point) != type(None):
            offset = point.copy()
        else:
            offset = self.origin.copy()
        tmp_vertices = self.vertices.copy()
        tmp_vertices -= offset
        tmp_vertices = rotate_2d(tmp_vertices,sign*step_size)
        tmp_vertices += offset
        self.vertices = tmp_vertices
        self.origin = self.vertices[:,0].reshape(2,1).copy()
        self.set_bounding_sphere()
