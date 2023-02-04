#!/usr/bin/env python3

from math import atan2

def edge_angle(V0,V1,V2):
    '''
    The edge angle is found using unit vectors. This function is passed a set of three vertices where V0 is the shared point of the two vectors.
    Args:
        V0 (1x2 numpy array): Shared point of the two vectors
        V1 (1x2 numpy array): Vector 1 endpoint
        V2 (1x2 numpy array): Vector 2 endpoint
    '''
    # This function finds the signed shortest distance between two vectors
    V1[0] = V1[0] - V0[0]
    V1[1] = V1[1] - V0[1]
    V2[0] = V2[0] - V0[0]
    V2[1] = V2[1] - V0[1]

    # Dot product of the vectors
    cosine_theta = V1[0]*V2[0] + V1[1]*V2[1]
    # Cross product of the vectors
    sin_theta = V1[0]*V2[1] - V1[1]*V2[0]
    # find the angle using the relationships sin(theta)== tan(theta) = sin(theta)/cos(theta)
    edge_angle = atan2(sin_theta,cosine_theta)
    return edge_angle