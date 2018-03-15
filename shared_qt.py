from PyQt4 import QtCore, QtGui

COLOR_LT_GRAY = QtGui.QColor(200, 200, 200)
COLOR_MD_GRAY = QtGui.QColor(128, 128, 128)
COLOR_YELLOW = QtGui.QColor(196, 196, 0)
COLOR_GREEN = QtGui.QColor(0, 255, 0)
COLOR_RED = QtGui.QColor(255, 0, 0)
COLOR_BLUE = QtGui.QColor(0, 0, 255)
COLOR_BLACK = QtGui.QColor(0, 0, 0)

BRUSH_CLEAR = QtCore.Qt.NoBrush

def PEN(color, width=1):
	return QtGui.QPen(color, width, QtCore.Qt.SolidLine) 

def BRUSH(color, pattern=QtCore.Qt.SolidPattern):
	return QtGui.QBrush(color, pattern)

