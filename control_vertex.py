
import math
from PyQt4 import QtCore, QtGui

import shared_qt

SMOOTH 		= 1
SHARP		= 2
SYMMETRIC 	= 3

LEFT_HANDLE 	= 1
RIGHT_HANDLE 	= 3
KNOT 			= 2

HANDLE_SIZE		= 10

SMOOTH_HANDLE_PATH = QtGui.QPainterPath()
SHARP_HANDLE_PATH = QtGui.QPainterPath()
SYMMETRIC_HANDLE_PATH = QtGui.QPainterPath()
KNOT_PATH = QtGui.QPainterPath()

SMOOTH_HANDLE_PATH.addEllipse(-HANDLE_SIZE/2, -HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE)

SHARP_HANDLE_PATH.moveTo(0, HANDLE_SIZE/2)
SHARP_HANDLE_PATH.lineTo(-HANDLE_SIZE/2, HANDLE_SIZE/2)
SHARP_HANDLE_PATH.lineTo(0, -HANDLE_SIZE/2)
SHARP_HANDLE_PATH.lineTo(HANDLE_SIZE/2, HANDLE_SIZE/2)
SHARP_HANDLE_PATH.lineTo(0, HANDLE_SIZE/2)

SYMMETRIC_HANDLE_PATH.moveTo(0, 0)
SYMMETRIC_HANDLE_PATH.arcTo(-HANDLE_SIZE/2, -HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE, 270, 180) 
SYMMETRIC_HANDLE_PATH.lineTo(0, 0)

KNOT_PATH.addRect(-HANDLE_SIZE/2, -HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE)

class controlVertex(object):
	def __init__(self, left=QtCore.QPoint(), knot=QtCore.QPoint(), right=QtCore.QPoint()):
		self.__pressure = 1.0
		self.__behavior = SMOOTH
		self.__handlePos = [0, left, knot, right]
		self.__handleScale = 1
		self.__selected = None

	def setPos(self, pt):
		self.setHandlePos(pt, KNOT)
		
	def getPos(self):
		return self.__handlePos[KNOT]

	pos = property(getPos, setPos)

	def getSelectedHandle(self):
		return self.__selected
		
	def getHandlePos(self, handle):
		return self.__handlePos[handle]
	
	def clearHandlePos(self, handle):
		self.__handlePos[handle] = QtCore.QPoint(0, 0)

	def setHandlePos(self, pt, handle):
		oldLDel = self.__handlePos[LEFT_HANDLE] - self.__handlePos[KNOT]
		oldKnotDel = self.__handlePos[KNOT] - pt
		oldRDel = self.__handlePos[KNOT] - self.__handlePos[RIGHT_HANDLE] 
		llen = math.sqrt(float(oldLDel.x() * oldLDel.x()) + float(oldLDel.y() * oldLDel.y()))
		rlen = math.sqrt(float(oldRDel.x() * oldRDel.x()) + float(oldRDel.y() * oldRDel.y()))
			
		if handle == KNOT:
			if self.__handlePos[LEFT_HANDLE]:
				self.__handlePos[LEFT_HANDLE] -= oldKnotDel
			if self.__handlePos[RIGHT_HANDLE]:
				self.__handlePos[RIGHT_HANDLE] -= oldKnotDel

		elif (self.__behavior == SMOOTH):
			if handle == RIGHT_HANDLE and self.__handlePos[LEFT_HANDLE]:
				if (rlen == 0):
					rlen = 0.00001
		
				lDel = -oldRDel * llen / rlen 
				self.__handlePos[LEFT_HANDLE] = self.__handlePos[KNOT] - lDel
			elif self.__handlePos[RIGHT_HANDLE]:
				if (llen == 0):
					llen = 0.00001

				rDel = -oldLDel * rlen / llen
				self.__handlePos[RIGHT_HANDLE] = self.__handlePos[KNOT] + rDel

		elif (self.__behavior == SYMMETRIC):
			if handle == RIGHT_HANDLE and self.__handlePos[LEFT_HANDLE]:
				self.__handlePos[LEFT_HANDLE] = self.__handlePos[KNOT] + oldRDel
			elif self.__handlePos[RIGHT_HANDLE]:
				self.__handlePos[RIGHT_HANDLE] = self.__handlePos[KNOT] - oldLDel

		self.__handlePos[handle] = pt
	
	def getHandlePosAsList(self):
		knot = (self.__handlePos[KNOT].x(), self.__handlePos[KNOT].y())
		handleList = []

		if self.__handlePos[LEFT_HANDLE]:
			handleList.append((self.__handlePos[LEFT_HANDLE].x(), self.__handlePos[LEFT_HANDLE].y()))

		handleList.append(knot)

		if self.__handlePos[RIGHT_HANDLE]:
			handleList.append((self.__handlePos[RIGHT_HANDLE].x(), self.__handlePos[RIGHT_HANDLE].y()))

		return handleList

	def selectHandle(self, select):
		if (select) and ((select == LEFT_HANDLE) or (select == RIGHT_HANDLE) or (select == KNOT)):
			self.__selected = select
		else:
			self.__selected = None
		
	def selectLeftHandle(self, select=False):
		if (select):
			self.__selected = LEFT_HANDLE
		elif (self.__selected == LEFT_HANDLE):
			self.__selected = None
	
	def selectRightHandle(self, select=False):
		if (select):
			self.__selected = RIGHT_HANDLE
		elif (self.__selected == RIGHT_HANDLE):
			self.__selected = None
	
	def selectKnot(self, select=False):
		if (select):
			self.__selected = KNOT
		elif (self.__selected == KNOT):
			self.__selected = None

	def isRightHandleSelected(self):
		if (self.__selected is not None) and (self.__selected == RIGHT_HANDLE):
			return True
		else:
			return False
	
	def isLeftHandleSelected(self):
		if (self.__selected is not None) and (self.__selected == LEFT_HANDLE):
			return True
		else:
			return False
		
	def isKnotSelected(self):
		if (self.__selected is not None) and (self.__selected == KNOT):
			return True
		else:
			return False

	def setPosOfSelected(self, pt):
		if (self.__selected is None):
			pass
		elif (self.__selected == KNOT):
			self.setPos(pt)
		else:
			self.setHandlePos(pt, self.__selected)
	
	def getPosOfSelected(self):
		if (self.__selected is None):
			return None
		else:
			return self.__handlePos[self.__selected]
		
	selectedHandlePos = property(getPosOfSelected, setPosOfSelected)	
	
	def setBehavior(self, newBehavior):
		self.__behavior = newBehavior
		
		if (self.__behavior == SHARP):
			return
		
		self.setHandlePos(self.__handlePos[self.__selected], self.__selected)
			
	def setBehaviorToSmooth(self):
		self.setBehavior(SMOOTH)
		
	def setBehaviorToSharp(self):
		self.setBehavior(SHARP)
			
	def setBehaviorToSymmetric(self):
		self.setBehavior(SYMMETRIC)
		
	def getBehavior(self):
		return self.__behavior
			
	def draw(self, gc):
		vert = self.__handlePos[KNOT]
		
		gc.setPen(shared_qt.PEN_MD_GRAY)
		
		if (self.__selected is not None):
			if (self.__selected == KNOT):
				gc.setBrush(shared_qt.BRUSH_GREEN_SOLID)
			else:
				gc.setBrush(shared_qt.BRUSH_YELLOW_SOLID)
		else:
			gc.setBrush(shared_qt.BRUSH_MD_GRAY_SOLID)
			
		gc.save()
		gc.translate(vert)
		gc.scale(self.__handleScale, self.__handleScale)
		gc.drawPath(KNOT_PATH)
		gc.restore()
			
		if (self.__behavior == SMOOTH):
			path = QtGui.QPainterPath(SMOOTH_HANDLE_PATH)
		elif (self.__behavior == SHARP):
			path = QtGui.QPainterPath(SHARP_HANDLE_PATH)
		else:	
			path = QtGui.QPainterPath(SYMMETRIC_HANDLE_PATH)
		
		if ((self.__selected is not None) and (self.__selected == LEFT_HANDLE)):
			gc.setBrush(shared_qt.BRUSH_GREEN_SOLID)
		else:
			gc.setBrush(shared_qt.BRUSH_CLEAR)

		vert = self.__handlePos[LEFT_HANDLE]	
		if (vert):
			gc.setPen(shared_qt.PEN_LT_GRAY)
			gc.drawLine(self.__handlePos[KNOT], vert)
			gc.setPen(shared_qt.PEN_LT_GRAY_2)

			gc.save()
			gc.translate(vert)
			gc.scale(self.__handleScale, self.__handleScale)
			gc.drawPath(path)	
			gc.restore()

		if ((self.__selected is not None) and (self.__selected == RIGHT_HANDLE)):
			gc.setBrush(shared_qt.BRUSH_GREEN_SOLID)
		else:
			gc.setBrush(shared_qt.BRUSH_CLEAR)

		vert = self.__handlePos[RIGHT_HANDLE]	
		if (vert):
			gc.setPen(shared_qt.PEN_LT_GRAY)
			gc.drawLine(self.__handlePos[KNOT], vert)
			gc.setPen(shared_qt.PEN_LT_GRAY_2)

			gc.save()
			gc.translate(vert)
			
			gc.scale(-self.__handleScale, self.__handleScale)
			gc.drawPath(path)
			gc.restore()