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

from PyQt4 import QtCore, QtGui

import control_vertex
#import serif
from view import shared_qt

DEBUG_BBOXES = False

class Stroke(object):
	def __init__(self, dimension=2, fromStroke=None, parent=None):
		if fromStroke is not None:
			self.__startSerif = fromStroke.getStartSerif()
			self.__endSerif = fromStroke.getEndSerif()
			self.__strokeCtrlVerts = fromStroke.getCtrlVertices()
			self.updateCtrlVertices()
			self.__pos = QtCore.QPoint(fromStroke.getPos())
			self.__strokeShape = fromStroke.getStrokeShape()
			self.__curvePath = self.calcCurvePoints()
			self.__boundRect = fromStroke.getBoundRect()
		else:	
			self.__startSerif = None
			self.__endSerif = None
			self.__strokeCtrlVerts = []
			self.__pos = QtCore.QPoint(0, 0)
			self.__strokeShape = None
			self.__curvePath = None
			self.__boundRect = None

		self.__startFlourish = None
		self.__endFlourish = None
		self.__handleSize = 10
		self.__instances = {}
		self.__parent = parent
		
		self.__isSelected = False

		self.seed = time.localtime()

	def __getstate__(self):
		saveDict = self.__dict__.copy()

		saveDict["_Stroke__strokeShape"] = None
		saveDict["_Stroke__curvePath"] = None

		return saveDict

	def __setstate__(self, stateDict):
		self.__dict__ = stateDict

		self.calcCurvePoints()

	def addInstance(self, inst):
		self.__instances[inst] = 1
		
	def removeInstance(self, inst):
		self.__instances.pop(inst, None)

	def getInstances(self):
		return self.__instances.keys()

	def setPos(self, pt):
		self.__pos = pt
		
	def getPos(self):
		return self.__pos

	pos = property(getPos, setPos)
	
	def getHandlePos(self):
		return (int(self.__hx), int(self.__hy))
	
	def straighten(self):
		tempCv = []
		ctrlVerts = self.getCtrlVerticesAsList()
		numVerts = len(ctrlVerts)

		start = ctrlVerts[0]
		end = ctrlVerts[-1]
		
		dX = (end[0]-start[0])/(numVerts-1)
		dY = (end[1]-start[1])/(numVerts-1)
		
		xpos = start[0]
		ypos = start[1]

		for i in range (0, numVerts):
			tempCv.append([xpos, ypos])
			xpos += dX
			ypos += dY
		
		self.setCtrlVerticesFromList(tempCv)
		self.calcCurvePoints()
		
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

	def splitCurve(self, testAngle):
		l = []
		r = []
		newCurves = []
		oppTestAngle = testAngle + 180
		tolerance = 1

		verts = self.getCtrlVerticesAsList()
		curCurve = self.__curvePath

		for i in range(0, 1000):
			pct = float(i) / 1000.0
			try:
				angle = int(curCurve.angleAtPercent(pct))
			except ValueError:
				continue

			if (angle >= testAngle-tolerance and angle <= testAngle+tolerance) or \
				(angle >= oppTestAngle-tolerance and angle <= oppTestAngle+tolerance):
				(l, r) = self.divideCurveAtPoint(verts, pct, 1)
				l.append(r[0])
			
				curCurve = QtGui.QPainterPath()
				curCurve.moveTo(l[0][0], l[0][1])
				curCurve.cubicTo(l[1][0], l[1][1], l[2][0], l[2][1], l[3][0], l[3][1])
				newCurves.append(curCurve)
				verts = r
				curCurve = QtGui.QPainterPath()
				curCurve.moveTo(verts[0][0], verts[0][1])
				curCurve.cubicTo(verts[1][0], verts[1][1], verts[2][0], verts[2][1], verts[3][0], verts[3][1])
				i = 0;

		while (len(verts) > 3):
			curCurve = QtGui.QPainterPath()
			curCurve.moveTo(verts[0][0], verts[0][1])
			curCurve.cubicTo(verts[1][0], verts[1][1], verts[2][0], verts[2][1], verts[3][0], verts[3][1])
			newCurves.append(curCurve)
			verts = verts[3:]

		return newCurves

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
			pts.extend(vert.getHandlePosAsList())
			
		return pts
		
	def setCtrlVerticesFromList(self, pts):
		self.__strokeCtrlVerts = []
		
		tmpPts = pts[:]
		left = QtCore.QPoint()
		
		while (tmpPts):
			pt = tmpPts.pop(0)
			center = QtCore.QPoint(pt[0], pt[1])
			if len(tmpPts):
				pt = tmpPts.pop(0)
				right = QtCore.QPoint(pt[0], pt[1])
			
			self.__strokeCtrlVerts.append(control_vertex.controlVertex(left, center, right))

			right = None
			if len(tmpPts):
				pt = tmpPts.pop(0)
				left = QtCore.QPoint(pt[0], pt[1])

	def generateCtrlVerticesFromPoints(self, pts):	
		tempCv = []

		numPts = len(pts)
		startX, startY = pts[0]
		
		if (2 > numPts):
			# not sure about this one
			return
		if (2 == numPts):
			dX = (pts[1][0]-pts[0][0])/3.
			dY = (pts[1][1]-pts[0][1])/3.
			pts = [pts[0], [pts[0][0]+dX, pts[0][1]+dY], [pts[1][0]-dX, pts[1][1]-dY], pts[1]]
		elif (3 == numPts):
			dX1 = (pts[1][0]-pts[0][0])/4.
			dY1 = (pts[1][1]-pts[0][1])/4.
			
			dX2 = (pts[2][0]-pts[1][0])/4.
			dY2 = (pts[2][1]-pts[1][1])/4.
			
			pts = [pts[0], [pts[1][0]-dX1, pts[1][1]-dY1], [pts[1][0]+dX2, pts[1][1]+dY2], pts[2]]
		else:
			firstPts = [pts[0], pts[1]]
			lastPts = [pts[-2], pts[-1]]
			midPts = []
			
			for i in range(2, numPts-2):
				dxT = (pts[i+1][0]-pts[i-1][0])/2.
				dyT = (pts[i+1][1]-pts[i-1][1])/2.
				
				dxA = (pts[i-1][0]-pts[i][0])
				dyA = (pts[i-1][1]-pts[i][1])
				vLenA = math.sqrt(float(dxA)*float(dxA) + float(dyA)*float(dyA))+0.001
				dxB = (pts[i+1][0]-pts[i][0])
				dyB = (pts[i+1][1]-pts[i][1])
				vLenB = math.sqrt(float(dxB)*float(dxB) + float(dyB)*float(dyB))+0.001

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

		self.setCtrlVerticesFromList(pts)
	
	def setCtrlVertices(self, ctrlVerts):
		self.__strokeCtrlVerts = ctrlVerts[:]
		self.updateCtrlVertices()
		
	def updateCtrlVertices(self):
		pts = self.getCtrlVerticesAsList()
		
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
	
	def divideCurveAtPoint(self, pts, t, index):
		trueIndex = index*3
		
		p3 = pts[trueIndex]
		p2 = pts[trueIndex-1]
		p1 = pts[trueIndex-2]
		p0 = pts[trueIndex-3]
	
		newPts = []
		for i in range (0, 5):
			newPts.append([0,0])
			
		for k in range (0, 2):
			p0_1 = float((1.0-t)*p0[k] + (t * p1[k]))
			p1_2 = float((1.0-t)*p1[k] + (t * p2[k]))
			p2_3 = float((1.0-t)*p2[k] + (t * p3[k]))
 			p01_12 = float((1.0-t)*p0_1 + (t * p1_2))
			p12_23 = float((1.0-t)*p1_2 + (t * p2_3))
			p0112_1223 = float((1.0-t)*p01_12 + (t * p12_23))
		
			newPts[0][k] = p0_1
			newPts[1][k] = p01_12
			newPts[2][k] = p0112_1223
			newPts[3][k] = p12_23
			newPts[4][k] = p2_3
			
		pts[trueIndex-2:trueIndex] = newPts
		
		return (pts[:trueIndex], pts[trueIndex:])

	def addCtrlVertex(self, t, index):
		pts = self.getCtrlVerticesAsList()

		(pts, remainder) = self.divideCurveAtPoint(pts, t, index)
		
		pts.extend(remainder)

		self.setCtrlVerticesFromList(pts)	
		self.calcCurvePoints()

	def splitAtPoint(self, t, index):
		pts = self.getCtrlVerticesAsList()

		(pts, remainder) = self.divideCurveAtPoint(pts, t, index)
		
		pts.append(remainder[0])
		
		self.setCtrlVerticesFromList(pts)	
		self.calcCurvePoints()

		return remainder

	def setParent(self, parent):
		self.__parent = parent

	def getParent(self):
		return self.__parent

	parent = property(getParent, setParent)

	def draw(self, gc, showCtrlVerts=0, nib=None):
		minX = 9999
		minY = 9999
		maxX = 0
		maxY = 0
		
		random.seed(self.seed)
		
		if (nib == None):
			print "ERROR: No nib provided to draw stroke\n"
			return
		
		gc.save()
		gc.translate(self.__pos)		

		gc.setPen(nib.pen)
		gc.setBrush(shared_qt.BRUSH_CLEAR) #nib.brush)
		
		verts = self.getCtrlVerticesAsList()
		if len(verts) > 0:
			self.__strokeShape = QtGui.QPainterPath()
			if self.__curvePath is None:
				self.calcCurvePoints()

			nib.draw(gc, self)
		
			path1 = QtGui.QPainterPath(self.__curvePath)
			path2 = QtGui.QPainterPath(self.__curvePath).toReversed()
			
			distX, distY = nib.getActualWidths()

			path1.translate(distX, -distY)
			path2.translate(-distX, distY)
			
			self.__strokeShape.addPath(path1)
			self.__strokeShape.connectPath(path2)
			self.__strokeShape.closeSubpath()

			#self.__strokeShape.setFillRule(QtCore.Qt.WindingFill)

			#gc.drawPath(self.__strokeShape)
			
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
				gc.setBrush(shared_qt.BRUSH_CLEAR)
				gc.setPen(shared_qt.PEN_MD_GRAY_DOT)
		
				gc.drawRect(self.__boundRect)

		gc.restore()
		
	def insideStroke(self, pt):
		minDist = 10
		testPt = pt - self.__pos
		if self.__strokeShape is not None:
			inside = self.__strokeShape.contains(testPt)
		else:
			inside = False

		if self.__boundRect.contains(testPt):
			if self.__isSelected:
				for i in range(0, self.__curvePath.elementCount()):
					element = self.__curvePath.elementAt(i)
					dist = math.sqrt(
						math.pow(element.x-testPt.x(), 2) +
						math.pow(element.y-testPt.y(), 2)
					)
					if dist < self.__handleSize:
						return (True, i, None)
				
				if inside:
					# get exact point
					hitPoint = None
					testBox = QtCore.QRect(testPt.x()-2, testPt.y()-2, 4, 4)
					for i in range(0, 100):
						pct = float(i) / 100.0
						curvePt = self.__curvePath.pointAtPercent(pct)
						if testBox.contains(int(curvePt.x()), int(curvePt.y())):
							hitPoint = pct
							break
 
					if hitPoint is not None:
						return (True, int(math.ceil((len(self.__strokeCtrlVerts) - 1) * hitPoint)),  hitPoint)
					else:
						return (True, -1, None)

			elif inside:
				return (True, -1, None)

		return (False, -1, None)

	def getBoundRect(self):
		return self.__boundRect

	def setBoundRect(self, newBoundRect):
		if newBoundRect is not None:
			self.__boundRect = newBoundRect
		
	boundRect = property(getBoundRect, setBoundRect)

	def getSelectState(self):
		return self.__isSelected

	def setSelectState(self, newState):
		self.__isSelected = newState

	selected = property(getSelectState, setSelectState)

	def deselectCtrlVerts(self):
		for vert in self.__strokeCtrlVerts:
			vert.selectHandle(None)

	def getStrokeShape(self):
		return self.__strokeShape

	def setStrokeShape(self, newStrokeShape):
		self.__strokeShape = newStrokeShape

	strokeShape = property(getStrokeShape, setStrokeShape)

	def getCurvePath(self):
		return self.__curvePath

	def setCurvePath(self, newCurvePath):
		self.__curvePath = newCurvePath

	curvePath = property(getCurvePath, setCurvePath)


class StrokeInstance(object):
	def __init__(self, parent=None):
		self.__stroke = None
		self.__pos = QtCore.QPoint(0, 0)
		self.__color = QtGui.QColor(128, 128, 192, 90)
		self.__boundRect = None
		self.__parent = parent
		self.__isSelected = False
		
	def __del__(self):
		if self.__stroke:
			self.__stroke.removeInstance(self)

	def setPos(self, pt):
		self.__pos = pt
	
	def getPos(self):
		return self.__pos

	pos = property(getPos, setPos)

	def setStroke(self, stroke):
		if self.__stroke:
			self.__stroke.removeInstance(self)

		self.__stroke = stroke
		
		self.__pos = QtCore.QPoint(stroke.getPos())
		self.__boundRect = stroke.getBoundRect()

		self.__stroke.addInstance(self)

	def getStroke(self):
		return self.__stroke

	stroke = property(getStroke, setStroke)

	def setParent(self, parent):
		self.__parent = parent

	def getParent(self):
		return self.__parent

	parent = property(getParent, setParent)

	def getStartSerif(self):
		return self.__stroke.getStartSerif()

	def getEndSerif(self):
		return self.__stroke.getEndSerif()

	def draw(self, gc, showCtrlVerts=0, nib=None):

		if self.__stroke == None:
			return

		strokeToDraw = Stroke(fromStroke=self.__stroke)

		#
		# perform overrides
		#

		strokePos = self.__stroke.getPos()		
		gc.save()

		gc.translate(-strokePos)
		gc.translate(self.__pos)

		strokeToDraw.draw(gc, 0, nib)
		self.__boundRect = strokeToDraw.boundRect
		gc.restore()

		if self.__isSelected or showCtrlVerts:
			gc.save()

			gc.translate(self.__pos)
			gc.setBrush(shared_qt.BRUSH_CLEAR)
			gc.setPen(shared_qt.PEN_MD_GRAY_DOT_2)
			
			gc.drawRect(self.__boundRect)
			
			gc.restore()


	def getHitPoint(self, idx):
		return self.__stroke.getHitPoint(idx)

	def getBoundRect(self):
		return self.__stroke.getBoundRect()

	def insideStroke(self, pt):
		if self.__stroke is not None:
			strokePos = self.__stroke.getPos()
			testPt = pt + strokePos - self.__pos
			inside = self.__stroke.insideStroke(testPt)
		else:
			inside = (False, -1, None)

		return inside
	
	def getCtrlVertices(self, copy=False):
		return []

	def deselectCtrlVerts(self):
		if self.__stroke:
			self.__stroke.deselectCtrlVerts()

	def getSelectState(self):
		return self.__isSelected

	def setSelectState(self, newState):
		self.__isSelected = newState

	selected = property(getSelectState, setSelectState)

	def calcCurvePoints(self):
		if self.__stroke:
			self.__stroke.calcCurvePoints()