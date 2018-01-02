
import math
from PyQt4 import QtCore, QtGui

SMOOTH 		= 1
SHARP		= 2
SYMMETRIC 	= 3

LEFT_HANDLE 	= 1
RIGHT_HANDLE 	= 2
KNOT 		= 3

class controlVertex(object):
	def __init__(self):
		self.__pos = ()
		self.__pressure = 1.0
		self.__behavior = SMOOTH
		self.__leftHandlePos = ()
		self.__rightHandlePos = ()
		self.__handleSize = 10
		self.__grayPen = (200,200,200,QtCore.Qt.SolidLine) #QtGui.QPen(QtGui.QColor(200, 200, 200), 1, wx.SOLID)
		self.__grayBrush = (200,200,200,QtCore.Qt.SolidPattern) #QtGui.QBrush(QtGui.QColor(200,200,200), wx.SOLID)
		self.__dkGrayPen = (128,128,128,QtCore.Qt.SolidLine) #QtGui.QPen(QtGui.QColor(128, 128, 128), 1, wx.SOLID)
		self.__dkGrayBrush = (128,128,128,QtCore.Qt.SolidPattern) #QtGui.QBrush(QtGui.QColor(128,128,128), wx.SOLID)
		self.__clearBrush = (0,0,0,QtCore.Qt.NoBrush) #QtGui.QBrush(QtGui.QColor(0,0,0), wx.TRANSPARENT)
		self.__selected = None
		
	def setPos(self, x, y):
		oldPos = self.__pos
		if (oldPos):
			dx = oldPos[0]-x
			dy = oldPos[1]-y
			
			lPos = self.__leftHandlePos
			if (lPos):
				self.__leftHandlePos = (lPos[0]-dx, lPos[1]-dy)
					
			rPos = self.__rightHandlePos
			if (rPos):
				self.__rightHandlePos = (rPos[0]-dx, rPos[1]-dy)
			
		self.__pos = (x, y)
		
	def getPos(self):
		return self.__pos

	def getSelectedHandle(self):
		return self.__selected
		
	def setLeftHandlePos(self, x, y):
		oldLPos = self.__leftHandlePos
		oldRPos = self.__rightHandlePos
		
		if (self.__behavior == SMOOTH):
			if (self.__leftHandlePos and self.__rightHandlePos and self.__pos):
				oldx = oldLPos[0] - self.__pos[0]
				oldy = oldLPos[1] - self.__pos[1]
				ordx = self.__pos[0] - oldRPos[0]
				ordy = self.__pos[1] - oldRPos[1]
				llen = math.sqrt(float(oldx * oldx) + float(oldy * oldy))
				rlen = math.sqrt(float(ordx * ordx) + float(ordy * ordy))
				if (llen == 0):
					llen = 0.00001
				normldx = oldx / llen
				normldy = oldy / llen
				rdx = (0 - normldx) * rlen
				rdy = (0 - normldy) * rlen
				
				self.__rightHandlePos = (self.__pos[0] + rdx, self.__pos[1] + rdy)
		elif (self.__behavior == SYMMETRIC):
			if (self.__leftHandlePos and self.__rightHandlePos and self.__pos):
				oldx = oldLPos[0] - self.__pos[0]
				oldy = oldLPos[1] - self.__pos[1]
				
				self.__rightHandlePos = (self.__pos[0] - oldx, self.__pos[1] - oldy)
	
		self.__leftHandlePos = (x, y)
		
	def getLeftHandlePos(self):
		return self.__leftHandlePos
	
	def clearLeftHandlePos(self):
		self.__leftHandlePos = ()
		
	def setRightHandlePos(self, x, y):
		oldLPos = self.__leftHandlePos
		oldRPos = self.__rightHandlePos

		if (self.__behavior == SMOOTH):
			if (self.__leftHandlePos and self.__rightHandlePos and self.__pos):
				oldx = oldLPos[0] - self.__pos[0]
				oldy = oldLPos[1] - self.__pos[1]
				ordx = self.__pos[0] - oldRPos[0]
				ordy = self.__pos[1] - oldRPos[1]
				llen = math.sqrt(float(oldx * oldx) + float(oldy * oldy))
				rlen = math.sqrt(float(ordx * ordx) + float(ordy * ordy))
				if (rlen == 0):
					rlen = 0.00001
				normrdx = ordx / rlen
				normrdy = ordy / rlen
				ldx = (0 - normrdx) * llen
				ldy = (0 - normrdy) * llen
				
				self.__leftHandlePos = (self.__pos[0] - ldx, self.__pos[1] - ldy)
		elif (self.__behavior == SYMMETRIC):
			if (self.__leftHandlePos and self.__rightHandlePos and self.__pos):
				ordx = self.__pos[0] - oldRPos[0]
				ordy = self.__pos[1] - oldRPos[1]
				
				self.__leftHandlePos = (self.__pos[0] + ordx, self.__pos[1] + ordy)
				
		self.__rightHandlePos = (x, y)

	def getRightHandlePos(self):
		return self.__rightHandlePos
	
	def clearRightHandlePos(self):
		self.__rightHandlePos = ()
	
	def selectHandle(self, select):
		if (select == LEFT_HANDLE) or (select == RIGHT_HANDLE) or (select == KNOT):
			self.__selected = select
		
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

	def setPosOfSelected(self, x, y):
		if (self.__selected is None):
			pass
		elif (self.__selected == KNOT):
			self.setPos(x,y)
		elif (self.__selected == LEFT_HANDLE):
			self.setLeftHandlePos(x,y)
		elif (self.__selected == RIGHT_HANDLE):
			self.setRightHandlePos(x,y)
	
	def getPosOfSelected(self):
		if (self.__selected is None):
			return None
		elif (self.__selected == KNOT):
			return self.__pos
		elif (self.__selected == LEFT_HANDLE):
			return self.__leftHandlePos
		elif (self.__selected == RIGHT_HANDLE):
			return self.__rightHandlePos
		else:
			return None
	
	def checkForHit(self, x, y, offset):
		pt = self.getLeftHandlePos()
		if (pt) and (self.handleHit(x, y, pt, offset)):
			self.__selected = LEFT_HANDLE
			return 1

		pt = self.getRightHandlePos()
		if (pt) and (self.handleHit(x, y, pt, offset)):
			self.__selected = RIGHT_HANDLE
			return 1
		
		pt = self.getPos()
		if (pt) and (self.handleHit(x, y, pt, offset)):
			self.__selected = KNOT
			return 1

		self.__selected = None
		return 0

	def handleHit(self, x, y, pt, offset):
		vxmin = pt[0]+offset[0]-self.__handleSize/2 
		vxmax = vxmin+self.__handleSize
		vymin = pt[1]+offset[1]-self.__handleSize/2 
		vymax = vymin+self.__handleSize 
		if (x >= vxmin) and (x <= vxmax) and \
			(y >= vymin) and (y <= vymax):	
			return True		
	
	def setBehavior(self, newBehavior):
		self.__behavior = newBehavior
		
		if (self.__behavior == SHARP):
			return
		
		if (self.__selected == LEFT_HANDLE):
			lPos = self.__leftHandlePos
			self.setLeftHandlePos(lPos[0], lPos[1])
		elif (self.__selected == RIGHT_HANDLE):
			rPos = self.__rightHandlePos
			self.setRightHandlePos(rPos[0], rPos[1])
			
	def setBehaviorToSmooth(self):
		self.setBehavior(SMOOTH)
		
	def setBehaviorToSharp(self):
		self.setBehavior(SHARP)
			
	def setBehaviorToSymmetric(self):
		self.setBehavior(SYMMETRIC)
		
	def getBehavior(self):
		return self.__behavior
			
	def draw(self, gc):
		vert = self.__pos
		
		gc.setPen(QtGui.QPen(QtGui.QColor(self.__dkGrayPen[0], self.__dkGrayPen[1], self.__dkGrayPen[2]), 1, self.__dkGrayPen[3]))
		
		if (self.__selected is not None):
			if (self.__selected == KNOT):
				gc.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0), QtCore.Qt.SolidPattern))
			else:
				gc.setBrush(QtGui.QBrush(QtGui.QColor(0, 196, 0), QtCore.Qt.SolidPattern))
		else:
			gc.setBrush(QtGui.QBrush(QtGui.QColor(self.__dkGrayBrush[0], self.__dkGrayBrush[1], self.__dkGrayBrush[2]), self.__dkGrayBrush[3]))
			
		gc.drawRect (vert[0]-self.__handleSize/2,
					vert[1]-self.__handleSize/2,
					self.__handleSize, 
					self.__handleSize)
						
		
		if ((self.__selected is not None) and (self.__selected == LEFT_HANDLE)):
			gc.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0), QtCore.Qt.SolidPattern))
		else:
			gc.setBrush(QtGui.QBrush(QtGui.QColor(self.__clearBrush[0], self.__clearBrush[1], self.__clearBrush[2]), self.__clearBrush[3]))
		
		vert = self.__leftHandlePos	
		if (vert):
			gc.setPen(QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 1, self.__grayPen[3]))
			gc.drawLine(self.__pos[0], self.__pos[1], vert[0], vert[1])
			gc.setPen(QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
			
			if (self.__behavior == SMOOTH):
				path = QtGui.QPainterPath()
				path.addEllipse(vert[0]-self.__handleSize/2, vert[1]-self.__handleSize/2, self.__handleSize, self.__handleSize)
				gc.strokePath(path, QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
			elif (self.__behavior == SHARP):
				path = QtGui.QPainterPath()
				path.moveTo(vert[0], vert[1]+self.__handleSize/2)
				path.lineTo(vert[0]-self.__handleSize/2, vert[1]+self.__handleSize/2)
				path.lineTo(vert[0], vert[1]-self.__handleSize/2)
				path.lineTo(vert[0]+self.__handleSize/2, vert[1]+self.__handleSize/2)
				path.lineTo(vert[0], vert[1]+self.__handleSize/2)
				gc.strokePath(path, QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
			else:	
				path = QtGui.QPainterPath()
				path.moveTo(vert[0], vert[1])
				path.arcTo(vert[0]-self.__handleSize/2, vert[1]-self.__handleSize/2, self.__handleSize, self.__handleSize, 90, 180) #math.pi/2.0, 3.0*math.pi/2.0)
				path.lineTo(vert[0], vert[1])
				gc.strokePath(path, QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
				
					
		if ((self.__selected is not None) and (self.__selected == RIGHT_HANDLE)):
			gc.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0), QtCore.Qt.SolidPattern))
		else:
			gc.setBrush(QtGui.QBrush(QtGui.QColor(self.__clearBrush[0], self.__clearBrush[1], self.__clearBrush[2]), self.__clearBrush[3]))

		vert = self.__rightHandlePos	
		if (vert):
			gc.setPen(QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 1, self.__grayPen[3]))
			gc.drawLine(self.__pos[0], self.__pos[1], vert[0], vert[1])
			gc.setPen(QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
			
			if (self.__behavior == SMOOTH):
				path = QtGui.QPainterPath()
				path.addEllipse(vert[0]-self.__handleSize/2, vert[1]-self.__handleSize/2, self.__handleSize, self.__handleSize)
				gc.strokePath(path, QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
			elif (self.__behavior == SHARP):
				path = QtGui.QPainterPath()
				path.moveTo(vert[0], vert[1]+self.__handleSize/2)
				path.lineTo(vert[0]-self.__handleSize/2, vert[1]+self.__handleSize/2)
				path.lineTo(vert[0], vert[1]-self.__handleSize/2)
				path.lineTo(vert[0]+self.__handleSize/2, vert[1]+self.__handleSize/2)
				path.lineTo(vert[0], vert[1]+self.__handleSize/2)
				gc.strokePath(path, QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
			else:
				path = QtGui.QPainterPath()
				path.moveTo(vert[0], vert[1])
				path.arcTo(vert[0]-self.__handleSize/2, vert[1]-self.__handleSize/2, self.__handleSize, self.__handleSize, 270, 180)
				path.lineTo(vert[0], vert[1])
				gc.strokePath(path, QtGui.QPen(QtGui.QColor(self.__grayPen[0], self.__grayPen[1], self.__grayPen[2]), 2, self.__grayPen[3]))
				
				
		
