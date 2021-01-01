#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

a = numpy.array([[1,2,3],[4,5,6]])
b = numpy.array([[1],[1]])
c = a+b

print(b[0]>0)