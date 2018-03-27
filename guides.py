#!/usr/bin/python
#

import math
from PyQt4 import QtCore, QtGui

class guideLines(object):
	def __init__(self):
		# units are nibwidths from baseline
		self.__baseHeightNibs = 5
		self.__widthNibs = 4
		self.__ascentHeightNibs = 3
		self.__descentHeightNibs = 3
		self.__capHeightNibs = 2
		# nibwidths between rows
		self.__gapHeightNibs = 2
		
		# internal-only caching of pixel dimensions
		self.__baseHeightPixels = 0
		self.__baseWidthPixels = 0
		self.__halfBaseWidthPixels= 0
		self.__ascentHeightPixels = 0
		self.__descentHeightPixels = 0
		self.__capHeightPixels = 0
		self.__gapHeightPixels = 0

		# degrees
		self.__angle = 5
		self.__angleDX = math.tan(math.radians(self.__angle))
		
		self.__lineColor = QtGui.QColor(200, 195, 180)
		self.__lineColorLt = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30)
		self.__lineColorAlpha = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30, 128)
		self.__linePenLt = QtGui.QPen(self.__lineColorLt, 1, QtCore.Qt.SolidLine)
		self.__linePen = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.SolidLine)
		self.__linePen2 = QtGui.QPen(self.__lineColor, 2, QtCore.Qt.SolidLine)
		self.__linePenDotted = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.DotLine)
		self.__spacerBrush = QtGui.QBrush(self.__lineColorAlpha, QtCore.Qt.SolidPattern)
		self.__nibWidth = 0
		self.__lastNibWidth = 0
		self.__gridPts = []
	
	def setAngle(self, angle):
		self.__angle = angle
		self.__angleDX = math.tan(math.radians(angle))
		
	def getAngle(self):
		return self.__angle
		
	angle = property(getAngle, setAngle)
	
	def setLineColor(self, linecolor):
		self.__lineColor = linecolor
		self.__lineColorLt = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30)
		self.__lineColorAlpha = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30, 192)
		self.__linePenLt = QtGui.QPen(self.__lineColorLt, 1, QtCore.Qt.SolidLine)
		self.__linePen = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.SolidLine)
		self.__linePen2 = QtGui.QPen(self.__lineColor, 2, QtCore.Qt.SolidLine)
		self.__linePenDotted = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.DotLine)
		self.__spacerBrush = QtGui.QBrush(self.__lineColorAlpha, QtCore.Qt.SolidPattern)
		
	def getLineColor(self):
		return self.__lineColor

	lineColor = property(getLineColor, setLineColor)
	
	def setBaseHeight(self, height):
		self.__baseHeightNibs = height
		self.__baseHeightPixels = height * self.__nibWidth
	
	def getBaseHeight(self):
		return self.__baseHeightNibs
		
	baseHeight = property(getBaseHeight, setBaseHeight)
	
	def setAscent(self, height):
		self.__ascentHeightNibs = height
		self.__ascentHeightPixels = height * self.__nibWidth
		
	def getAscent(self):
		return self.__ascentHeightNibs

	ascentHeight = property(getAscent, setAscent)

	def setCapHeight(self, height):
		self.__capHeightNibs = height
		self.__capHeightPixels = height * self.__nibWidth
		
	def getCapHeight(self):
		return self.__capHeightNibs #-self.__baseHeight

	capHeight = property(getCapHeight, setCapHeight)
	
	def setDescent(self, height):
		self.__descentHeightNibs = height
		self.__descentHeightPixels = height * self.__nibWidth

	def getDescent(self):
		return self.__descentHeightNibs

	descentHeight = property(getDescent, setDescent)
	
	def setGap(self, height):
		self.__gapHeightNibs = height
		self.__gapHeightPixels = height * self.__nibWidth

	def getGap(self):
		return self.__gapHeightNibs

	gapHeight = property(getGap, setGap)

	def setNibWidth(self, newNibWidth):
		self.__nibWidth = newNibWidth
		self.__baseWidthPixels = newNibWidth * self.__widthNibs
		self.__halfBaseWidthPixels = newNibWidth * self.__widthNibs / 2
		self.__baseHeightPixels = newNibWidth * self.__baseHeightNibs
		self.__ascentHeightPixels = newNibWidth * (self.__ascentHeightNibs + self.__baseHeightNibs)
		self.__descentHeightPixels = newNibWidth * self.__descentHeightNibs
		self.__capHeightPixels = newNibWidth * (self.__capHeightNibs + self.__baseHeightNibs)
		self.__gapHeightPixels = newNibWidth * self.__gapHeightNibs
	
	def getNibWidth(self):
		return self.__nibWidth
		
	nibWidth = property(getNibWidth, setNibWidth)

	def snapToAxes(self, strokePos, pos, vertPos, tolerance=10):
		snapPt = QtCore.QPoint(-1, -1)

		delta = pos - vertPos - strokePos

		if abs(delta.y()) < tolerance:
			snapPt = QtCore.QPoint(pos.x(), vertPos.y() + strokePos.y())
		else:
			vecLength = math.sqrt(float(delta.x())*float(delta.x()) + float(delta.y())*float(delta.y()))

			guideAngle = -self.__angle

			if guideAngle > 0:
				delta.setX(-delta.x())

			if delta.x() > 0 and delta.y() < 0:
				guideAngle += 180
			elif not (delta.x() < 0 and delta.y() > 0):
				return snapPt

			newPt = QtCore.QPoint(vecLength * math.sin(math.radians(guideAngle)), \
				vecLength * math.cos(math.radians(guideAngle)))
			newPt = newPt + vertPos + strokePos

			newDelta = pos - newPt

			if abs(newDelta.x()) < tolerance:
				snapPt = newPt

		return snapPt

	def closestGridPoint(self, pt, nibWidth=0, tolerance=10):
		gridPt = QtCore.QPoint(-1, -1)

		if self.nibWidth == 0:
	 		if self.__lastNibWidth == 0:
	 			return gridPt 
	 		else:
	 			self.nibWidth = self.__lastNibWidth

	 	yLines = [self.__baseHeightPixels]
		widthX = self.__halfBaseWidthPixels + self.__baseWidthPixels
	 	
	 	for yLine in yLines:
	 		testY = pt.y() % yLine

	 		print "y", pt, testY, yLine - testY, "<=", tolerance

	 		ysign = 1
	 		if pt.y() < 0:
	 			ysign = -1

	 		if abs(testY) <= tolerance or abs(yLine - testY) <= tolerance:
	 			y = int(float(pt.y() + (ysign * tolerance)) / float(yLine)) * yLine
	 			
	 			print "YMATCH", y

	 			sign = 1
	 			if pt.x() < 0:
	 				sign = -1

	 			dx =  0 - int(y * self.__angleDX) * ysign
	 			testX = (pt.x() - dx) % widthX

	 			print "x", pt, dx, widthX, testX, widthX - testX, tolerance

	 			if abs(testX) <= tolerance or abs(widthX - testX) <= tolerance:
	 				x = int(float(pt.x() + (sign * tolerance)) / float(widthX)) * widthX + (dx * ysign) 

	 				print "XMATCH", x, pt, tolerance, widthX, dx
	 				print int(float(pt.x() + (sign * tolerance)) / float(widthX))
	 				print int(float(pt.x() + (sign * tolerance)) / float(widthX)) * widthX
	 				print "ENDXMATCH"
	 				return QtCore.QPoint(x, y)

	 	return gridPt
	
	def draw(self, gc, size, origin, nib=None):
		nibWidth = 20 #nib.getWidth() << 1

		if not self.__lastNibWidth == nibWidth:
			self.__lastNibWidth = nibWidth
			self.nibWidth = nibWidth

		scale = gc.worldTransform().m11()
		csize = QtCore.QSize(size.width() / scale, size.height() / scale)
		
		coordsRect = QtCore.QRect(-origin.x(), -origin.y(), csize.width(), csize.height())
			
		topX = self.__angleDX * origin.y()
		topY = coordsRect.topLeft().y()
		botX = -(self.__angleDX * (csize.height() - origin.y()))
		botY = coordsRect.bottomRight().y()
		gc.setPen(self.__linePen)
		gc.drawLine(botX, botY, topX, topY)
		
		# horizontal grid	
		dist = self.__halfBaseWidthPixels + self.__baseWidthPixels
		gc.drawLine(botX-dist, botY, topX-dist, topY)
		pos = dist
		gc.setPen(self.__linePenLt)
		while (pos < csize.width()):
		 	gc.drawLine(botX+pos, botY, topX+pos, topY)
		 	pos = pos + dist
		 	gc.drawLine(botX-pos, botY, topX-pos, topY)
		 	
			
		# baseline
		gc.setPen(self.__linePen2)
		gc.drawLine(-origin.x(), 0, coordsRect.bottomRight().x(), 0)
			
		# base height line
		gc.setPen(self.__linePen)
		gc.drawLine(-origin.x(), -self.__baseHeightPixels, coordsRect.bottomRight().x(), -self.__baseHeightPixels)
		
		gc.drawLine(-origin.x(), -self.__ascentHeightPixels, coordsRect.bottomRight().x(), -self.__ascentHeightPixels)
		gc.drawLine(-origin.x(), self.__descentHeightPixels, coordsRect.bottomRight().x(), self.__descentHeightPixels)
		
		gc.setPen(self.__linePenDotted)
		gc.drawLine(-origin.x(), -self.__capHeightPixels, coordsRect.bottomRight().x(), -self.__capHeightPixels)
		
		gc.setBrush(self.__spacerBrush)
		gc.drawRect(-origin.x(), self.__descentHeightPixels, csize.width(), self.__gapHeightPixels)

		vpos = -self.__ascentHeightPixels - self.__gapHeightPixels - self.__descentHeightPixels
		while (vpos+self.__descentHeightPixels > coordsRect.topLeft().y()):
			gc.setPen(self.__linePen2)
			gc.drawLine(-origin.x(), vpos, coordsRect.bottomRight().x(), vpos)

			gc.setPen(self.__linePen)
			gc.drawLine(-origin.x(), vpos-self.__baseHeightPixels, coordsRect.bottomRight().x(), vpos-self.__baseHeightPixels)
		
			gc.drawLine(-origin.x(), vpos-self.__ascentHeightPixels, coordsRect.bottomRight().x(), vpos-self.__ascentHeightPixels)
			gc.drawLine(-origin.x(), vpos+self.__descentHeightPixels, coordsRect.bottomRight().x(), vpos+self.__descentHeightPixels)
		
			gc.setPen(self.__linePenDotted)
			gc.drawLine(-origin.x(), vpos-self.__capHeightPixels, coordsRect.bottomRight().x(), vpos-self.__capHeightPixels)
		
			gc.setBrush(self.__spacerBrush)
			gc.drawRect(-origin.x(), vpos+self.__descentHeightPixels, csize.width(), self.__gapHeightPixels)
			vpos = vpos -self.__ascentHeightPixels - self.__gapHeightPixels - self.__descentHeightPixels

		vpos = self.__ascentHeightPixels + self.__gapHeightPixels + self.__descentHeightPixels
		while (vpos-self.__ascentHeightPixels < coordsRect.bottomRight().y()):
			gc.setPen(self.__linePen2)
			gc.drawLine(-origin.x(), vpos, coordsRect.bottomRight().x(), vpos)

			gc.setPen(self.__linePen)
			gc.drawLine(-origin.x(), vpos-self.__baseHeightPixels, coordsRect.bottomRight().x(), vpos-self.__baseHeightPixels)
		
			gc.drawLine(-origin.x(), vpos-self.__ascentHeightPixels, coordsRect.bottomRight().x(), vpos-self.__ascentHeightPixels)
			gc.drawLine(-origin.x(), vpos+self.__descentHeightPixels, coordsRect.bottomRight().x(), vpos+self.__descentHeightPixels)
		
			gc.setPen(self.__linePenDotted)
			gc.drawLine(-origin.x(), vpos-self.__capHeightPixels, coordsRect.bottomRight().x(), vpos-self.__capHeightPixels)
		
			gc.setBrush(self.__spacerBrush)
			gc.drawRect(-origin.x(), vpos+self.__descentHeightPixels, csize.width(), self.__gapHeightPixels)
			vpos = vpos + self.__ascentHeightPixels + self.__gapHeightPixels + self.__descentHeightPixels


		gc.setPen(self.__linePen)

		
		
