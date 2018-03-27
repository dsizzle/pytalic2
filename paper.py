from PyQt4 import QtCore, QtGui

import math

import guides
import nibs
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

		self.__guideLines = guides.guideLines()
		self.__drawGuidelines = True
		self.__pointsToDraw = []
		self.__strokesToDraw = []
		self.__strokesToDrawSpecial = []
		self.__snapPoints = []
		self.__nib = nibs.Nib()
		self.__instNib = nibs.Nib(color=QtGui.QColor(25,125,25))
		self.__nibSpecial = nibs.Nib(color=QtGui.QColor(25,25,125))
		self.__bitmap = None
		self.__bitmapSize = 40

	def resizeEvent(self, event):
		if self.__origin is None:
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

	def getDrawGuidelines(self):
		return self.__drawGuidelines

	def setDrawGuidelines(self, value):
		self.__drawGuidelines = value

	drawGuidelines = property(getDrawGuidelines, setDrawGuidelines)

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
		
	def getNormalizedPosition(self, rawPos):
		normPos = rawPos
		normPos = normPos / self.__scale
		normPos = normPos - self.__origin - self.__originDelta

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
		dc.scale(self.__scale, self.__scale)
		dc.translate(self.__origin + self.__originDelta)

		if self.__drawGuidelines:
			self.__guideLines.draw(dc, self.size(), self.__origin + self.__originDelta)

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
				dc.drawEllipse(self.__snapPts[0], 20, 20)

		dc.restore()
		dc.end()
		QtGui.QFrame.paintEvent(self,event)