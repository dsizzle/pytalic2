from PyQt4 import QtCore, QtGui

import math

from model import nibs
import shared_qt

class drawingArea(QtGui.QFrame):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self, parent)
		self.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.setMouseTracking(True)

		self.__origin = None
		self.__originDelta = QtCore.QPoint(0, 0)
		self.__scale = 1.0
		self.__bgColor = QtGui.QColor(240, 240, 230)
		self.__bgBrush = QtGui.QBrush(self.__bgColor, QtCore.Qt.SolidPattern) 
		
		self.__oldViewPos = None
		self.__moveView = False

		self.__guideLines = None 
		self.__drawGuidelines = True
		self.__drawNibGuides = True
		self.__pointsToDraw = []
		self.__strokesToDraw = []
		self.__strokesToDrawSpecial = []
		self.__snapPoints = []
		self.__nib = nibs.Nib(color=QtGui.QColor(125,25,25))
		self.__instNib = nibs.Nib(color=QtGui.QColor(25,125,25))
		self.__nibSpecial = nibs.Nib(color=QtGui.QColor(25,25,125))
		self.__bitmap = None
		self.__bitmapSize = 40

	def resizeEvent(self, event):
		self.__origin = QtCore.QPoint(self.size().width()/2, self.size().height()/2)
		self.repaint()

	def getBitmap(self):
		return self.__bitmap

	def getBitmapSize(self):
		return self.__bitmapSize

	def setBitmapSize(self, newBitmapSize):
		self.__bitmapSize = newBitmapSize

	bitmapSize = property(getBitmapSize, setBitmapSize)

	def getScale(self):
		return self.__scale

	def setScale(self, newScale):
		self.__scale = newScale
		if self.__scale < 0.01:
			self.__scale = 0.01
		elif self.__scale > 10.0:
			self.__scale = 10.0

	scale = property(getScale, setScale)
		
	def getOriginDelta(self):
		return self.__originDelta

	def setOriginDelta(self, newOriginDelta):
		self.__originDelta = newOriginDelta

	originDelta = property(getOriginDelta, setOriginDelta)

	def getOrigin(self):
		return self.__origin

	def getDrawGuidelines(self):
		return self.__drawGuidelines

	def setDrawGuidelines(self, value):
		self.__drawGuidelines = value

	drawGuidelines = property(getDrawGuidelines, setDrawGuidelines)

	def getDrawNibGuides(self):
		return self.__drawNibGuides

	def setDrawNibGuides(self, value):
		self.__drawNibGuides = value

 	drawNibGuides = property(getDrawNibGuides, setDrawNibGuides)

	def setDrawStrokesSpecial(self, strokes):
		self.__strokesToDrawSpecial = strokes

	def getDrawStrokesSpecial(self):
		return self.__strokesToDrawSpecial

	strokesSpecial = property(getDrawStrokesSpecial, setDrawStrokesSpecial)

	def setDrawStrokes(self, strokes):
		self.__strokesToDraw = strokes

	def getDrawStrokes(self):
		return self.__strokesToDraw

	strokes = property(getDrawStrokes, setDrawStrokes)

	def setSnapPoints(self, points):
		self.__snapPoints = points

	def getSnapPoints(self):
		return self.__snapPoints

	snapPoints = property(getSnapPoints, setSnapPoints)

	def getGuidelines(self):
		return self.__guideLines

	def setGuidelines(self, newGuides):
		self.__guideLines = newGuides
	
	def getNib(self):
		return self.__nib

	def setNib(self, newNib):
		self.__nib = newNib

	nib = property(getNib, setNib)

	def getInstNib(self):
		return self.__instNib

	def setInstNib(self, newNib):
		self.__instNib = newNib

	instNib = property(getInstNib, setInstNib)

	def getNormalizedPosition(self, rawPos):
		normPos = rawPos
		normPos = normPos - self.__origin - self.__originDelta
		normPos = normPos / self.__scale
		
		return normPos

	def drawIcon(self, dc, strokesToDraw):
		pixMap = QtGui.QPixmap(self.width(), self.height())
		
		if dc is None:
			dc = QtGui.QPainter()

		dc.begin(pixMap)
 		dc.setRenderHint(QtGui.QPainter.Antialiasing)
		
 		dc.setBackground(self.__bgBrush)
 		dc.eraseRect(self.frameRect())
 		# for icon only translate to origin, not actual view position

 		dc.translate(self.__origin)
 		if len(strokesToDraw) > 0:
			tmpStrokes = strokesToDraw[:]

			while(len(tmpStrokes)):
				stroke = tmpStrokes.pop()
				stroke.draw(dc, False, nib=self.__nibSpecial) 

 		dc.end()
 		
 		return pixMap.scaled(self.__bitmapSize, self.__bitmapSize, QtCore.Qt.KeepAspectRatioByExpanding, 1)

	def paintEvent(self, event):
		nibPixmap = QtGui.QPixmap(20, 2)

		dc = QtGui.QPainter()

		nibBrush = shared_qt.BRUSH_GREEN_SOLID 
		dc.begin(nibPixmap)
		dc.setRenderHint(QtGui.QPainter.Antialiasing)
		dc.setBrush(nibBrush)
		dc.eraseRect(self.frameRect())
		dc.fillRect(self.frameRect(), QtGui.QColor(128, 0, 0, 180))
		dc.end()
		
		self.__bitmap = self.drawIcon(dc, self.__strokesToDraw)

		dc.begin(self)
		dc.setRenderHint(QtGui.QPainter.Antialiasing)

		dc.setBackground(self.__bgBrush)
		dc.eraseRect(self.frameRect())
		dc.save()
		dc.translate(self.__origin + self.__originDelta)
		dc.scale(self.__scale, self.__scale)

		if self.__drawGuidelines:
			self.__guideLines.draw(dc, self.size(), self.__origin + self.__originDelta)

		if self.__drawNibGuides:
			nibGuideWidth = self.__guideLines.getNominalWidth()
			nibGuideBasePosX = 0-(nibGuideWidth * 2 * self.__nib.width) - self.__nib.width * 2
			nibGuideBasePosY = 0
			nibGuideBaseHeight = self.__guideLines.getBaseHeight()
			nibGuideAscentPosY = nibGuideBasePosY - nibGuideBaseHeight * self.__nib.width * 2
			nibGuideAscent = self.__guideLines.getAscent()
			nibGuideDescent = self.__guideLines.getDescent()
			nibGuideDescentPosY = nibGuideBasePosY + nibGuideDescent * self.__nib.width * 2
			

			self.__nib.vertNibWidthScale(dc, nibGuideBasePosX, nibGuideBasePosY, nibGuideBaseHeight)
			self.__nib.vertNibWidthScale(dc, nibGuideBasePosX-self.__nib.width*2, nibGuideAscentPosY, nibGuideAscent)
			self.__nib.vertNibWidthScale(dc, nibGuideBasePosX-self.__nib.width*2, nibGuideDescentPosY, nibGuideDescent)
			self.__nib.horzNibWidthScale(dc, nibGuideBasePosX, nibGuideBasePosY+self.__nib.width*2, nibGuideWidth)

		dc.setPen(shared_qt.PEN_LT_GRAY)
		dc.setBrush(shared_qt.BRUSH_CLEAR)
		dc.drawEllipse(QtCore.QPoint(0, 0), 10, 10)		
				
		if len(self.__strokesToDraw) > 0:
			tmpStrokes = self.__strokesToDraw[:]

			while(len(tmpStrokes)):
				strk = tmpStrokes.pop()
				if type(strk).__name__ == 'Stroke':
					strk.draw(dc, False, nib=self.__nib)
				else:
					strk.draw(dc, False, nib=self.__instNib)

		if len(self.__strokesToDrawSpecial) > 0:
			tmpStrokes = self.__strokesToDrawSpecial[:]

			while(len(tmpStrokes)):
				strk = tmpStrokes.pop()
				strk.draw(dc, True, nib=self.__nibSpecial)
				

		if len(self.__snapPoints) > 0:
			dc.setPen(shared_qt.PEN_DK_GRAY_DASH_2)
			dc.setBrush(shared_qt.BRUSH_CLEAR)
			
			if len(self.__snapPoints) > 1:
				delta = self.__snapPoints[0] - self.__snapPoints[1]
				 
				vecLen = math.sqrt(delta.x() * delta.x() + delta.y() * delta.y())

				if vecLen != 0:
					delta = delta * 50 / vecLen
				else:
					delta = QtCore.QPoint(0, 0)
					
				dc.drawLine(self.__snapPoints[0], self.__snapPoints[0] + delta)
				dc.drawLine(self.__snapPoints[1], self.__snapPoints[1] - delta)
			else:
				dc.drawEllipse(self.__snapPoints[0], 20, 20)

		dc.restore()
		dc.end()
		QtGui.QFrame.paintEvent(self,event)