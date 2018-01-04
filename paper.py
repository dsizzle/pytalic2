from PyQt4 import QtCore, QtGui

import guides
import nibs

class drawingArea(QtGui.QFrame):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self, parent)
		self.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.setMouseTracking(True)

		self.__origin = None #QtCore.QPoint(self.size().width()/2, self.size().height()/2)
		self.__scale = 1.0
		self.__bgColor = QtGui.QColor(240, 240, 230)
		self.__bgBrush = QtGui.QBrush(self.__bgColor, QtCore.Qt.SolidPattern) 
		self.__grayPen = QtGui.QPen(QtGui.QColor(200, 200, 200), 1, QtCore.Qt.SolidLine) 
		self.__dkGrayPenDashed = QtGui.QPen(QtGui.QColor(100, 100, 100), 2, QtCore.Qt.DashLine)
		self.__clearBrush = QtGui.QBrush(QtGui.QColor(0,0,0), QtCore.Qt.NoBrush)

		self.__oldViewPos = None
		self.__moveView = False

		self.__guideLines = guides.guideLines()
		self.__drawGuidelines = True
		self.__pointsToDraw = []
		self.__strokesToDraw = []
		self.__strokesToDrawSpecial = []
		self.__nib = nibs.Nib()
		self.__nibSpecial = nibs.Nib(color=QtGui.QColor(25,25,125))

	def resizeEvent(self, event):
		if self.__origin is None:
			self.__origin = QtCore.QPoint(self.size().width()/2, self.size().height()/2)
		self.repaint()

	def getScale(self):
		return self.__scale

	def setScale(self, newScale):
		self.__scale = newScale
		if self.__scale < 0.01:
			self.__scale = 0.01
		elif self.__scale > 10.0:
			self.__scale = 10.0

	scale = property(getScale, setScale)
		
	def getOrigin(self):
		return self.__origin

	def setOrigin(self, newOrigin):
		self.__origin = newOrigin

	origin = property(getOrigin, setOrigin)

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

	def getNormalizedPosition(self, rawPos):
		normPos = rawPos
		normPos = normPos / self.__scale
		normPos = normPos - self.__origin

		return normPos

	def paintEvent(self, event):
		dc = QtGui.QPainter(self)
		dc.setRenderHint(QtGui.QPainter.Antialiasing)

		bgBrush = self.__bgBrush

		dc.setBackground(bgBrush)
		dc.eraseRect(self.frameRect())
		dc.save()
		dc.scale(self.__scale, self.__scale)
		dc.translate(self.__origin)

		if self.__drawGuidelines:
			self.__guideLines.draw(dc, self.size(), self.__origin)

		dc.setPen(self.__grayPen)
		dc.setBrush(self.__clearBrush)
		dc.drawEllipse(QtCore.QPoint(0, 0), 10, 10)		
				
		if len(self.__strokesToDraw) > 0:
			tmpStrokes = self.__strokesToDraw[:]

			while(len(tmpStrokes)):
				stroke = tmpStrokes.pop()
				stroke.draw(dc, False, nib=self.__nib)

		if len(self.__strokesToDrawSpecial) > 0:
			tmpStrokes = self.__strokesToDrawSpecial[:]

			while(len(tmpStrokes)):
				stroke = tmpStrokes.pop()
				stroke.draw(dc, True, nib=self.__nibSpecial)
				
		dc.restore()
		dc.end()
		QtGui.QFrame.paintEvent(self,event)