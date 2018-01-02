#!/usr/bin/python
#
# nibs class definitions
#

import math
import random
import time

import shapes.polygon

from PyQt4 import QtCore, QtGui

# move color to stroke
class Nib(object):
	def __init__(self, width=20, angle=40, color=QtGui.QColor(125,25,25)): #FL_BLACK):
		if (angle < 0):
			angle = 180+angle
				
		angle = angle % 180
		self.__width = width
		self.__angle = angle
		self.__angleRads = (self.__angle * math.pi) / 180.0		

		self.__color = color
		self.nibwidth_x = self.width * math.cos(self.angle * 
		                    math.pi / 180.0)
		self.nibwidth_y = self.width * math.sin(self.angle * 
                            math.pi / 180.0)

		self.seed = time.localtime()
		self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 220), QtCore.Qt.SolidPattern)
	
	def fromNib(self, nib):
		self.__width = nib.width
		self.__angle = nib.angle
		self.__color = nib.getColor()

		self.nibwidth_x = self.width * math.cos(self.__angle * 
		                    math.pi / 180.0)
		self.nibwidth_y = self.width * math.sin(self.__angle * 
                            math.pi / 180.0)

		self.seed = time.localtime()
		self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 220), QtCore.Qt.SolidPattern)
	
	def getColor(self):
		return self.__color 

	def setAlpha(self, alpha):
		self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), ((90.0 / 255.0) * alpha)), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), ((220.0 / 255.0) * alpha)), QtCore.Qt.SolidPattern)
		
	def resetAlpha(self):
		self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 220), QtCore.Qt.SolidPattern)
		
	def setColor(self, color):
		self.__color = color
		self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 220), QtCore.Qt.SolidPattern)
		
	def setAngle(self, angle):
		if (angle < 0):
			angle = 180+angle
		
		angle = angle % 180
		
		self.__angle = angle
		self.__angleRads = (self.__angle * math.pi) / 180.0		

		self.nibwidth_x = self.__width * math.cos(self.__angleRads)
		self.nibwidth_y = self.__width * math.sin(self.__angleRads)
	
	def getAngle(self):
	   	return self.__angle
    	
	angle = property(getAngle, setAngle)

   	def setWidth(self, width):
   		self.__width = width
   		self.nibwidth_x = self.__width * math.cos(self.__angleRads)
		self.nibwidth_y = self.__width * math.sin(self.__angleRads)
			
	def getWidth(self):
		return self.__width
           
	width = property(getWidth, setWidth)

	def draw(self, gc, x,y,x2=None,y2=None, seed=None):

		pts = shapes.polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = shapes.polygon.normalizePolyRotation(pts)
		
		poly = QtGui.QPolygon(4)
		poly.setPoint(0, QtCore.QPoint(pts[0][0],pts[0][1]))
		poly.setPoint(1, QtCore.QPoint(pts[1][0],pts[1][1]))
		poly.setPoint(2, QtCore.QPoint(pts[2][0],pts[2][1]))
		poly.setPoint(3, QtCore.QPoint(pts[3][0],pts[3][1]))
		
		pen = self.pen
		nullpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1, QtCore.Qt.SolidLine)
		brush = self.brush
		
		gc.setPen(nullpen)
		gc.setBrush(brush)
		
		gc.setPen(nullpen)
		gc.drawPolygon(poly, QtCore.Qt.WindingFill)
		gc.setPen(pen)
		gc.drawPolyline(poly)
		
		bRect = poly.boundingRect()
		
		newPts = [[bRect.topLeft().x(), bRect.topLeft().y()], 
			[bRect.topRight().x(), bRect.topRight().y()],	
			[bRect.bottomRight().x(), bRect.bottomRight().y()],
			[bRect.bottomLeft().x(), bRect.bottomLeft().y()]]
		
		return newPts

	def vertNibWidthScale (self, dc, x, y, num=2):
		tempAngle = self.__angle
		
		self.__angle = 90
		
		random.seed(self.seed)
		for i in range (0, int(math.ceil(num))):
			ypos = y+self.nibwidth_y*i*2
			xpos = x
			if i % 2 == 0:
				xpos = x+self.__width*2
			
			self.draw(dc, xpos, ypos, xpos+self.__width*2, ypos)
			
		self.__angle = tempAngle
	
	def horzNibWidthScale (self, dc, x, y, num=2):
		tempAngle = self.__angle
			
		self.__angle = 0
		
		random.seed(self.seed)	
		for i in range (0, int(math.ceil(num))):
			xpos = x+self.nibwidth_y*i*2
			ypos = y
			if i % 2 == 0:
				ypos = y+self.width*2
			
			self.draw(dc, xpos, ypos, xpos, ypos+self.__width*2, self.seed)
				
		self.__angle = tempAngle

class PenNib(Nib):
	def draw(self, gc, x,y,x2=None,y2=None, seed=None):
		dx = x2 - x
		dy = y2 - y

		tangent = 0

		try:
			tangent = dx / dy
			angle = math.atan(tangent) * 180.0 / math.pi
		
		except ZeroDivisionError:
			tangent = 0
			angle = 90

		self.setAngle(angle)
		
		pts = shapes.polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = shapes.polygon.normalizePolyRotation(pts)
		
		poly = QtGui.QPolygon(4)
		poly.setPoint(0, QtCore.QPoint(pts[0][0],pts[0][1]))
		poly.setPoint(1, QtCore.QPoint(pts[1][0],pts[1][1]))
		poly.setPoint(2, QtCore.QPoint(pts[2][0],pts[2][1]))
		poly.setPoint(3, QtCore.QPoint(pts[3][0],pts[3][1]))
		
		pen = self.pen
		nullpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1, QtCore.Qt.SolidLine)
		brush = self.brush
		
		gc.setPen(nullpen)
		gc.setBrush(brush)
		
		gc.setPen(nullpen)
		gc.drawPolygon(poly, QtCore.Qt.WindingFill)
		gc.drawEllipse(QtCore.QPoint(x, y), self.width, self.width)
		gc.drawEllipse(QtCore.QPoint(x2, y2), self.width, self.width)
		
		return pts


class ScrollNib(Nib):
	def __init__(self, width=10, angle=40, split=5, color=QtGui.QColor(125,25,25)):
		self.__width = width-split
		self.split = split
		if split>width:
			split = 0
		super(ScrollNib, self).__init__(width, angle, color)
		self.setSplitSize(split)

	def fromNib(self, nib):
		super(ScrollNib, self).fromNib(nib)
		self.setSplitSize(nib.getSplitSize())
		
	def setWidth(self, width):
		super(ScrollNib, self).setWidth(width)
		self.setSplitSize(self.split)

	def setSplitSize(self, splitSize):
		if (splitSize > self.width):
			splitSize = 0
			
		self.split = splitSize

		splitx = (splitSize) * math.cos(self.angle * 
							math.pi / 180.0)
		splity = (splitSize) * math.sin(self.angle * 
							math.pi / 180.0)
	
		self.__rem_x = (self.nibwidth_x - splitx) / 2
		self.__rem_y = (self.nibwidth_y - splity) / 2

		self.__split_x = (splitx + self.__rem_x)
		self.__split_y = (splity + self.__rem_y)


	def getSplitSize(self):
		return self.split
		
	def draw(self, gc, x,y,x2=None,y2=None):
		
		pts = shapes.polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = shapes.polygon.normalizePolyRotation(pts)
		
		lpts = shapes.polygon.calcPoly(x+self.__split_x, y-self.__split_y, 
			self.__rem_x, self.__rem_y, 
			x2+self.__split_x, y2-self.__split_y)
		
		lpoly = QtGui.QPolygon(4)
		lpoly.setPoint(0, QtCore.QPoint(lpts[0][0],lpts[0][1]))
		lpoly.setPoint(1, QtCore.QPoint(lpts[1][0],lpts[1][1]))
		lpoly.setPoint(2, QtCore.QPoint(lpts[2][0],lpts[2][1]))
		lpoly.setPoint(3, QtCore.QPoint(lpts[3][0],lpts[3][1]))
		
		rpts = shapes.polygon.calcPoly(x-self.__split_x, y+self.__split_y, 
			self.__rem_x, self.__rem_y, 
			x2-self.__split_x, y2+self.__split_y)
		
		rpoly = QtGui.QPolygon(4)
		rpoly.setPoint(0, QtCore.QPoint(rpts[0][0],rpts[0][1]))
		rpoly.setPoint(1, QtCore.QPoint(rpts[1][0],rpts[1][1]))
		rpoly.setPoint(2, QtCore.QPoint(rpts[2][0],rpts[2][1]))
		rpoly.setPoint(3, QtCore.QPoint(rpts[3][0],rpts[3][1]))
		
		pen = self.pen
		nullpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1, QtCore.Qt.SolidLine)
		brush = self.brush
		gc.setPen(nullpen)
		gc.setBrush(brush)
		
		gc.setPen(nullpen)
		gc.drawPolygon(lpoly, QtCore.Qt.WindingFill)
		gc.drawPolygon(rpoly, QtCore.Qt.WindingFill)
		
		gc.setPen(pen)
		gc.drawPolyline(lpoly)
		gc.drawPolyline(rpoly)
		
		return pts
		
	def setAngle(self, angle):
		super(ScrollNib, self).setAngle(angle)
		self.setSplitSize(self.split)

# 	 				 		
# 		
# 	
class BrushNib(Nib):
	def __init__(self, width=5, angle=40, color=QtGui.QColor(125,25,25)):
 		
		Nib.__init__(self, width, angle, color)
		self.__slope = float(self.nibwidth_y / self.nibwidth_x)
 		
	def draw(self, dc, x, y, x2=None,y2=None):
			
		pts = shapes.polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = shapes.polygon.normalizePolyRotation(pts)
		
		xp = x - self.nibwidth_x
		xp2 = x + self.nibwidth_x
		yp = y + self.nibwidth_y
		yp2 = y - self.nibwidth_y
		
		if (x2 == None) and (y2 == None):
			x2 = x
			y2 = y
		
		
		xxp = x2 - self.nibwidth_x
		xxp2 = x2 + self.nibwidth_x
		yyp = y2 + self.nibwidth_y
		yyp2 = y2 - self.nibwidth_y
		
		steep = abs(yp2 - yp) > abs(xp2 - xp)
						
		if (steep):
			xp, yp = yp, xp
			xp2, yp2 = yp2, xp2
			xxp, yyp = yyp, xxp
			xxp2, yyp2 = yyp2, xxp2
		if (xp > xp2):
			xp, xp2 = xp2, xp
			yp, yp2 = yp2, yp
			xxp, xxp2 = xxp2, xxp
			yyp, yyp2 = yyp2, yyp
		
		dx = xp2 - xp
		dy = abs(yp2 - yp)
		err = - dx / 2
		yy = yp
		yy2 = yyp
		
		stepsize = 2
		if (yp < yp2):
			ystep = stepsize
		else:
			ystep = -stepsize
		
		xx2 = xxp
		
		looprange = int(dx / (stepsize))
		
		self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), self.__color.blue(), 200), stepsize*3, QtCore.Qt.SolidLine)
		pen = self.pen
		brush = self.brush
		
		dc.setPen(pen)
		dc.setBrush(brush)
		
		xx = xp
		for i in range (0, looprange):	
			xr = random.random()*4.0 - 1.0
			yr = random.random()*4.0 - 1.0
			xr2 = random.random()*4.0 - 1.0
			yr2 = random.random()*4.0 - 1.0
			
			if (i == 0) or (i == looprange-1):
				xr = random.random()*1.5 - 1.0
				yr = random.random()*1.5 - 1.0
				xr2 = random.random()*1.5 - 1.0
				yr2 = random.random()*1.5 - 1.0
				
				
			plotx1 = xx
			ploty1 = yy
			plotx2 = xx2
			ploty2 = yy2
			
			err = err + dy
			if err > 0:
				yy = yy+ystep
				yy2 = yy2+ystep
				err = err - dx
			
			xx = xx+stepsize
			xx2 += stepsize
			
			if steep:
				plotx1, ploty1 = ploty1, plotx1
				plotx2, ploty2 = ploty2, plotx2
	
			dc.drawLine(plotx1+xr, ploty1+yr, plotx2+xr2, ploty2+yr2)
			
		
		return pts
