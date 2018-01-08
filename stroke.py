#!/usr/bin/python
#
# stroke class definitions
#
#

import copy
import math
import math
import time
import random

import shapes.splines
import shapes.polygon
import control_vertex
#import serif

from PyQt4 import QtCore, QtGui

DEBUG_BBOXES = False
DARK_GRAY_PEN = (128,128,128,QtCore.Qt.DotLine) 
CLEAR_BRUSH = (0,0,0,QtCore.Qt.NoBrush) 
RED_BRUSH = (128,0,0,QtCore.Qt.SolidPattern)

class Stroke(shapes.splines.BezierSpline):
	def __init__(self, dimension=2, fromStroke=None, parent=None):
		shapes.splines.BezierSpline.__init__(self, dimension)
		
		if fromStroke is not None:
			self.__startSerif = fromStroke.getStartSerif()
			self.__endSerif = fromStroke.getEndSerif()
			self.__strokeCtrlVerts = fromStroke.getCtrlVertices()
			self.updateCtrlVertices()
			(self.__x, self.__y) = fromStroke.getPos()
		else:	
			self.__startSerif = None
			self.__endSerif = None
			self.__strokeCtrlVerts = []
			self.__x = 0
			self.__y = 0
		
		self.__boundRect = None
		self.__curvePath = None
		self.__strokeShape = None

		self.__startFlourish = None
		self.__endFlourish = None
		self.__handleSize = 10
		self.__instances = {}
		self.__parent = parent
		
		self.__isSelected = False

		self.seed = time.localtime()

	def addInstance(self, inst):
		self.__instances[inst] = 1
		
	def removeInstance(self, inst):
		self.__instances.pop(inst, None)

	def getInstances(self):
		return self.__instances.keys()

	def setPos(self, x, y):
		self.__x = x
		self.__y = y
		
	def getPos(self):
		return (int(self.__x), int(self.__y))

	pos = property(getPos, setPos)
	
	def getHandlePos(self):
		return (int(self.__hx), int(self.__hy))
	
	def straighten(self):
		tempCv = []
		oldCv = shapes.splines.BezierSpline.ctrlVertices(self)
		
		start = self.ctrlVerts[0]
		end = self.ctrlVerts[-1]
		
		dX = (end[0]-start[0])/(self.numVerts-1)
		dY = (end[1]-start[1])/(self.numVerts-1)
		
		for i in range (0, self.numVerts):
			tempCv.append([start[0]+dX*i, start[1]+dY*i])
		
		self.setCtrlVerticesFromList(tempCv)
		self.calcCurvePoints()
		
		return oldCv
		
	def addEndSerif(self, distance):
		self.__endSerif = serif.Flick(serif.END)
		verts = self.getCtrlVerticesAsList()
		self.__endSerif.setCtrlVertices(verts)
		self.__endSerif.setLength(distance)
		# if (self.nib):
		# 	self.__endSerif.setAngle(self.nib.getAngle())
		
	def removeEndSerif(self):
		self.__endSerif = None
	
	def getEndSerif(self):
		return self.__endSerif

	def addStartSerif(self, distance):
		self.__startSerif = serif.Flick(serif.START)
		verts = self.getCtrlVerticesAsList()
		self.__startSerif.setCtrlVertices(verts)
		self.__startSerif.setLength(distance)
		# if (self.nib):
		# 	self.__startSerif.setAngle(self.nib.getAngle())

	def removeStartSerif(self):
		self.__startSerif = None

	def getStartSerif(self):
		return self.__startSerif

	def calcCurvePoints(self):
		verts = self.getCtrlVerticesAsList()
		self.__curvePath = QtGui.QPainterPath()
		self.__curvePath.moveTo(verts[0][0], verts[0][1])
			
		while (len(verts) > 3):
			self.__curvePath.cubicTo(verts[1][0], verts[1][1], verts[2][0], verts[2][1], verts[3][0], verts[3][1])
			verts = verts[3:]
	
	def calcCtrlVertices(self, pts):
		return shapes.splines.BezierSpline.calcCtrlVertices(self, pts)
	
	def getCtrlVertices(self, make_copy=True):
		if make_copy:
			verts = copy.deepcopy(self.__strokeCtrlVerts)
		else:
			verts = self.__strokeCtrlVerts

		return verts

	def getCtrlVertex(self, idx):
		if len(self.__strokeCtrlVerts) > idx:
			return self.__strokeCtrlVerts[idx]

		return None

	def getCtrlVerticesAsList(self):
		pts = []
		for vert in self.__strokeCtrlVerts:
			l = vert.getLeftHandlePos()
			k = vert.getPos()
			r = vert.getRightHandlePos()
			
			if (l):
				pts.append(list(l))
			if (k):
				pts.append(list(k))
			if (r):
				pts.append(list(r))
				
		return list(pts)
		
	def setCtrlVerticesFromList(self, pts):	
		tempCv = []

		numPts = len(pts)
		startX, startY = pts[0]
		
		if (2 > numPts):
			# not sure about this one
			return
		if (2 == numPts):
			dX = (pts[1][0]-pts[0][0])/3.
			dY = (pts[1][1]-pts[0][1])/3.
			cp1 = [pts[0][0]+dX, pts[0][1]+dY]
			cp2 = [pts[1][0]-dX, pts[1][1]-dY]
			pts = [pts[0], cp1, cp2, pts[1]]
		elif (3 == numPts):
			dX = (pts[2][0]-pts[1][0])/4.
			dY = (pts[2][1]-pts[1][1])/4.
			
			pts = [pts[0], [pts[1][0]-dX, pts[1][1]-dY], [pts[1][0]+dX, pts[1][1]+dY], pts[2]]
		else:
			firstPts = [pts[0], pts[1]]
			lastPts = [pts[-2], pts[-1]]
			midPts = []
			
			for i in range(2, numPts-2):
				dxT = (pts[i+1][0]-pts[i-1][0])/2.
				dyT = (pts[i+1][1]-pts[i-1][1])/2.
				
				dxA = (pts[i-1][0]-pts[i][0])
				dyA = (pts[i-1][1]-pts[i][1])
				vLenA = math.sqrt(float(dxA)*float(dxA) + float(dyA)*float(dyA))
				dxB = (pts[i+1][0]-pts[i][0])
				dyB = (pts[i+1][1]-pts[i][1])
				vLenB = math.sqrt(float(dxB)*float(dxB) + float(dyB)*float(dyB))
				
				if (vLenA > vLenB):
					ratio = (vLenA / vLenB) / 2.
					midPts.append([pts[i][0]-dxT*ratio, pts[i][1]-dyT*ratio])
					midPts.append(pts[i])
					midPts.append([pts[i][0]+(dxT/2.), pts[i][1]+(dyT/2.)])
				else:
					ratio = (vLenB / vLenA) / 2.
					midPts.append([pts[i][0]-(dxT/2.), pts[i][1]-(dyT/2.)])
					midPts.append(pts[i])
					midPts.append([pts[i][0]+dxT*ratio, pts[i][1]+dyT*ratio])
			
			pts = firstPts
			pts.extend(midPts)
			pts.extend(lastPts)

		shapes.splines.BezierSpline.setCtrlVertices(self, pts)
		self.__strokeCtrlVerts = []
		
		pos = 1
		newVert = control_vertex.controlVertex()
		
		for pt in pts:
			if (pos == 0):
				newVert = control_vertex.controlVertex()
				lPos = newVert.getLeftHandlePos()
				newVert.setLeftHandlePos(pt[0], pt[1])
				pos = 1
			elif (pos == 1):
				newVert.setPos(pt[0], pt[1])
				pos = 2
			elif (pos == 2):
				newVert.setRightHandlePos(pt[0], pt[1])
				pos = 0
				self.__strokeCtrlVerts.append(newVert)
				newVert = None
		
		if (newVert):
			self.__strokeCtrlVerts.append(newVert)
	
	def setCtrlVertices(self, ctrlVerts):
		self.__strokeCtrlVerts = ctrlVerts[:]
		self.updateCtrlVertices()
		
	def updateCtrlVertices(self):
		pts = self.getCtrlVerticesAsList()
		
		#shapes.splines.BezierSpline.setCtrlVertices(self, pts)	
		if len(pts) > 3:
			self.calcCurvePoints()
		
	def deleteCtrlVertex(self, pt):
		if (pt == 0):
			self.__strokeCtrlVerts[pt+1].clearLeftHandlePos()
		elif (pt == len(self.__strokeCtrlVerts)-1):
			self.__strokeCtrlVerts[pt-1].clearRightHandlePos()
			
		self.__strokeCtrlVerts.remove(self.__strokeCtrlVerts[pt])
		self.updateCtrlVertices()
		self.calcCurvePoints()
	
	def addCtrlVertex(self, t, index):
		pts = self.getCtrlVerticesAsList()
		tmpCtrlVerts = self.getCtrlVertices()
		
		trueIndex = index*3
		
		p3 = pts[trueIndex]
		p2 = pts[trueIndex-1]
		p1 = pts[trueIndex-2]
		p0 = pts[trueIndex-3]
	
		newPts = []
		for i in range (0, 7):
			newPts.append([0,0])
			
		for k in range (0, 2):
			p0_1 = float((1.0-t)*p0[k] + (t * p1[k]))
			p1_2 = float((1.0-t)*p1[k] + (t * p2[k]))
			p2_3 = float((1.0-t)*p2[k] + (t * p3[k]))
 			p01_12 = float((1.0-t)*p0_1 + (t * p1_2))
			p12_23 = float((1.0-t)*p1_2 + (t * p2_3))
			p0112_1223 = float((1.0-t)*p01_12 + (t * p12_23))
		
			newPts[0][k] = p0[k]
			newPts[1][k] = p0_1
			newPts[2][k] = p01_12
			newPts[3][k] = p0112_1223
			newPts[4][k] = p12_23
			newPts[5][k] = p2_3
			newPts[6][k] = p3[k]
		
		pts[trueIndex-3:trueIndex+1] = newPts
		self.setCtrlVerticesFromList(pts)	
			
		self.calcCurvePoints()

	def setParent(self, parent):
		self.__parent = parent

	def getParent(self):
		return self.__parent

	parent = property(getParent, setParent)

	def draw(self, gc, showCtrlVerts=0, nib=None, selectedVert=-1):
		minX = 9999
		minY = 9999
		maxX = 0
		maxY = 0
		
		random.seed(self.seed)
		
		if (nib == None):
			print "ERROR: No nib provided to draw stroke\n"
			return
		
		gc.save()
		gc.translate(self.__x, self.__y)		

		gc.setPen(nib.pen)
		gc.setBrush(nib.brush)

		verts = self.getCtrlVerticesAsList()
		if len(verts) > 0:
			self.__strokeShape = QtGui.QPainterPath()
			if self.__curvePath is None:
				self.calcCurvePoints()

			path1 = QtGui.QPainterPath(self.__curvePath)
			path2 = QtGui.QPainterPath(self.__curvePath).toReversed()
			
			path1.translate(5, -5)
			path2.translate(-5, 5)
			
			self.__strokeShape.addPath(path1)
			self.__strokeShape.connectPath(path2)
			self.__strokeShape.closeSubpath()

			gc.drawPath(self.__strokeShape)

			self.__boundRect = self.__strokeShape.controlPointRect()
		
		if (self.__startSerif):
			verts = self.getCtrlVerticesAsList()
			self.__startSerif.setCtrlVertices(verts)
			self.__startSerif.setAngle(nib.getAngle())
			self.__startSerif.draw(gc, nib)
			
		if (self.__endSerif):
			verts = self.getCtrlVerticesAsList()
			self.__endSerif.setCtrlVertices(verts)
			self.__endSerif.setAngle(nib.getAngle())
			self.__endSerif.draw(gc, nib)
			
		if self.__isSelected or showCtrlVerts:
			for vert in self.__strokeCtrlVerts:
				vert.draw(gc)

			if self.__boundRect is not None:
				gc.setBrush(QtGui.QBrush(QtGui.QColor(CLEAR_BRUSH[0], CLEAR_BRUSH[1], CLEAR_BRUSH[2]), CLEAR_BRUSH[3]))
				gc.setPen(QtGui.QPen(QtGui.QColor(DARK_GRAY_PEN[0], DARK_GRAY_PEN[1], DARK_GRAY_PEN[2],128), 2, DARK_GRAY_PEN[3], QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
		
				gc.drawRect(self.__boundRect)

		gc.restore()
		
	def insideStroke(self, pt):
		minDist = 100

		inside = self.__strokeShape.contains(pt)

		if self.__boundRect.contains(pt):
			if self.__isSelected:
				for i in range(0, self.__curvePath.elementCount()):
					element = self.__curvePath.elementAt(i)
					dist = math.sqrt(
						math.pow(element.x-pt.x(), 2) +
						math.pow(element.y-pt.y(), 2)
					)
					if dist < self.__handleSize:
						return (True, i, None)
				
				if inside:
					# get exact point
					hitPoint = None

					for i in range(0, 100):
						pct = float(i) / 100.0
						curvePt = self.__curvePath.pointAtPercent(pct)
						dist = math.sqrt(
							math.pow(curvePt.x()-pt.x(), 2) + 
							math.pow(curvePt.y()-pt.y(), 2)
						)
						if dist < minDist:
							dist = minDist
							hitPoint = curvePt
						
						if hitPoint is not None:
							break

					return (True, -1, hitPoint)

			elif inside:
				return (True, -1, None)

		return (False, -1, None)

	def getBoundRect(self):
		return self.__boundRect

	def setBoundRect(self, newBoundRect):
		if newBoundRect is not None:
			self.__boundRect = boundRect
		
	boundRect = property(getBoundRect, setBoundRect)

	def getSelectState(self):
		return self.__isSelected

	def setSelectState(self, newState):
		self.__isSelected = newState

	selected = property(getSelectState, setSelectState)

	def deselectCtrlVerts(self):
		for vert in self.__strokeCtrlVerts:
			vert.selectHandle(None)

class StrokeInstance(object):
	def __init__(self, parent=None):
		self.__stroke = None
		self.__x = 0
		self.__y = 0
		self.__instNib = None
		self.__color = QtGui.QColor(128, 128, 192, 90)
		self.__boundRect = None
		self.__parent = parent
		
	def __del__(self):
		if self.__stroke:
			self.__stroke.removeInstance(self)

	def __getstate__(self):
		saveDict = self.__dict__.copy()

		saveDict["_strokeInstance__nib"] = None
		saveDict["_strokeInstance__instNib"] = None
		saveDict["_strokeInstance__parent"] = None

		return saveDict

	def __setstate__(self, d):
		self.__dict__ = d

		self.__instNib = None
		self.__color = QtGui.QColor(128, 128, 192, 90)

	def setPos(self, x, y):
		self.__x = x
		self.__y = y
	
	def getPos(self):
		return (int(self.__x), int(self.__y))

	pos = property(getPos, setPos)

	def setStroke(self, stroke):
		if self.__stroke:
			self.__stroke.removeInstance(self)

		self.__stroke = stroke
		self.__nib = nibs.Nib()
		tmpNib = stroke.getNib()
		
		(self.__x, self.__y) = stroke.getPos()

		if tmpNib:
			self.__nib.fromNib(tmpNib)
			self.__nib.setColor(self.__color)
			
		self.__stroke.addInstance(self)

	def getStroke(self):
		return self.__stroke

	stroke = property(getStroke, setStroke)

	def setParent(self, parent):
		self.__parent = parent

	def getParent(self):
		return self.__parent

	parent = property(getParent, setParent)

	def getNib(self):
		return self.__nib

	def getStartSerif(self):
		return self.__stroke.getStartSerif()

	def getEndSerif(self):
		return self.__stroke.getEndSerif()

	def draw(self, gc, showCtrlVerts=0, nib=None, selectedVert=-1):

		if self.__stroke == None:
			return

		if nib is not None:
			self.__nib = nibs_qt.Nib()
			self.__nib.fromNib(nib)
			self.__nib.setColor(self.__color)

		strokeToDraw = stroke_qt.Stroke(fromStroke=self.__stroke)

		#
		# perform overrides
		#

		(stroke_x, stroke_y) = self.__stroke.getPos()		
		gc.save()

		gc.translate(-stroke_x, -stroke_y)
		gc.translate(self.__x, self.__y)

		strokeToDraw.draw(gc, 0, self.__nib, selectedVert)
		self.__boundRect = strokeToDraw.boundRect
		gc.restore()

		if showCtrlVerts:
			gc.save()

			gc.translate(self.__x, self.__y)
			gc.setBrush(QtGui.QBrush(QtGui.QColor(CLEAR_BRUSH[0], CLEAR_BRUSH[1], CLEAR_BRUSH[2]), CLEAR_BRUSH[3]))
			gc.setPen(QtGui.QPen(QtGui.QColor(DARK_GRAY_PEN[0], DARK_GRAY_PEN[1], DARK_GRAY_PEN[2],128), 2, DARK_GRAY_PEN[3], QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
		
			gc.drawRect(self.__boundRect)
			
			gc.restore()

		self.__boundBoxes = strokeToDraw.getBoundBoxes() #True)

	def getHitPoint(self, idx):
		return self.__stroke.getHitPoint(idx)

	def getBoundRect(self):
		return self.__stroke.getBoundRect()

	def insideStroke(self, pt):
		vertIdx = 0
		origbboxIdx = 0
		idxPerVert = 0.0

		if self.__stroke == None:
			return vertIdx, origbboxIdx, idxPerVert

		if self.__boundRect:
			strokeToTest = stroke_qt.Stroke(fromStroke=self.__stroke)
			strokeToTest.boundRect(self.__boundRect)

			(vertIdx, origbboxIdx, idxPerVert) = strokeToTest.insideStroke(pt)

		return vertIdx, origbboxIdx, idxPerVert

	def getCtrlVertices(self, copy=False):
		return []