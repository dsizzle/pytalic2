"""
shared_qt.py

a place to store some Qt objects that are shared amongst modules
"""
from PyQt4 import QtCore, QtGui

COLOR_LT_GRAY = QtGui.QColor(200, 200, 200)
COLOR_MD_GRAY = QtGui.QColor(128, 128, 128)
COLOR_DK_GRAY = QtGui.QColor(100, 100, 100)
COLOR_YELLOW = QtGui.QColor(196, 196, 0)
COLOR_GREEN = QtGui.QColor(0, 255, 0)
COLOR_RED = QtGui.QColor(255, 0, 0)
COLOR_BLUE = QtGui.QColor(0, 0, 255)
COLOR_BLACK = QtGui.QColor(0, 0, 0)

def PEN(color, width=1, pattern=QtCore.Qt.SolidLine):
    """a wrapper function to generate a QPen"""
    return QtGui.QPen(color, width, pattern)

def BRUSH(color, pattern=QtCore.Qt.SolidPattern):
    """a wrapper function to generate a QBrush"""
    return QtGui.QBrush(color, pattern)

BRUSH_CLEAR = BRUSH(COLOR_BLACK, QtCore.Qt.NoBrush)
BRUSH_MD_GRAY_SOLID = BRUSH(COLOR_MD_GRAY)
BRUSH_GREEN_SOLID = BRUSH(COLOR_GREEN)
BRUSH_YELLOW_SOLID = BRUSH(COLOR_YELLOW)

PEN_LT_GRAY = PEN(COLOR_LT_GRAY)
PEN_LT_GRAY_2 = PEN(COLOR_LT_GRAY, 2)
PEN_MD_GRAY = PEN(COLOR_MD_GRAY)
PEN_MD_GRAY_DOT = PEN(COLOR_MD_GRAY, 1, QtCore.Qt.DotLine)
PEN_MD_GRAY_DOT_2 = PEN(COLOR_MD_GRAY, 2, QtCore.Qt.DotLine)
PEN_DK_GRAY_DASH_2 = PEN(COLOR_DK_GRAY, 2, QtCore.Qt.DashLine)
