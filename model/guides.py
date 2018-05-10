#!/usr/bin/python
#

import math
from PyQt4 import QtCore, QtGui

class guideLines(object):
	def __init__(self):
		# units are nibwidths from baseline
		self.__baseHeightNibs = 5.0
		self.__widthNibs = 4.0
		self.__ascentHeightNibs = 3.0
		self.__descentHeightNibs = 3.0
		self.__capHeightNibs = 2.0
		# nibwidths between rows
		self.__gapHeightNibs = 1.5
		
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
		
		self.setLineColor(QtGui.QColor(200, 195, 180))

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
		self.__lineColorAlpha = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30, 128)
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
		self.__ascentHeightPixels = (self.__ascentHeightNibs + self.__baseHeightNibs) * self.__nibWidth
		self.__capHeightPixels = (self.__capHeightNibs + self.__baseHeightNibs) * self.__nibWidth
	
	def getBaseHeight(self):
		return self.__baseHeightNibs
		
	baseHeight = property(getBaseHeight, setBaseHeight)
	
	def setAscent(self, height):
		self.__ascentHeightNibs = height
		self.__ascentHeightPixels = (height + self.__baseHeightNibs) * self.__nibWidth
		
	def getAscent(self):
		return self.__ascentHeightNibs

	ascentHeight = property(getAscent, setAscent)

	def setCapHeight(self, height):
		self.__capHeightNibs = height
		self.__capHeightPixels = (height + self.__baseHeightNibs) * self.__nibWidth
		
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

	def setNominalWidth(self, newWidth):
		self.__widthNibs = newWidth
		self.__baseWidthPixels = newWidth * self.__nibWidth
		self.__halfBaseWidthPixels = self.__baseWidthPixels / 2

	def getNominalWidth(self):
		return self.__widthNibs

	nominalWidth = property(getNominalWidth, setNominalWidth)

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

	def closestGridPoint(self, pt, nibWidth=0, tolerance=10):
		gridPt = QtCore.QPoint(-1, -1)

		if self.__nibWidth == 0:
	 		if self.__lastNibWidth == 0:
	 			return gridPt 
	 		else:
	 			self.__nibWidth = self.__lastNibWidth

	 	ascentOnly = self.__ascentHeightNibs * self.__nibWidth
	 	capOnly = ascentOnly - (self.__capHeightNibs * self.__nibWidth)

	 	yLines = [0, 
	 			self.__gapHeightPixels + self.__descentHeightPixels + capOnly,
	 			self.__gapHeightPixels + self.__descentHeightPixels + ascentOnly,
	 			self.__gapHeightPixels + self.__descentHeightPixels,
	 			self.__descentHeightPixels,
	 			 ]
	 	
		widthX = self.__baseWidthPixels
		heightY = self.__ascentHeightPixels + self.__gapHeightPixels + self.__descentHeightPixels

	 	for yLine in yLines:
	 		testY = (pt.y() - yLine) % heightY
	 	
	 		y = -1
	 		if abs(testY) <= tolerance:
	 			y = pt.y() - testY
	 		elif abs(yLine - testY) <= tolerance:
	 			y = pt.y() - testY + heightY
	 		
	 		if y != -1:
				dx =  0-int(y * self.__angleDX)
				testX = (pt.x() - dx) % widthX

				x = -1
 				if abs(testX) <= tolerance:
					x = pt.x() - testX			
				elif abs(widthX - testX) <= tolerance:
					x = pt.x() - testX + widthX

				if x != -1 and (abs(pt.x() - x) <= tolerance*2 and abs(pt.y() - y) <= tolerance*2):
	 				return QtCore.QPoint(x, y)

	 	return gridPt
	
	def draw(self, gc, size, origin, nib=None):
		nibWidth = 20 #nib.getWidth() << 1

		if not self.__lastNibWidth == nibWidth:
			self.__lastNibWidth = nibWidth
			self.nibWidth = nibWidth

		scale = gc.worldTransform().m11()

		csize = QtCore.QSize(size.width() / scale, size.height() / scale)
		
		coordsRect = QtCore.QRect(-origin.x() / scale, -origin.y() / scale, csize.width(), csize.height())
		
		topX = self.__angleDX * origin.y() / scale
		topY = coordsRect.topLeft().y()
		botX = -(self.__angleDX * (csize.height() - origin.y() / scale))
		botY = coordsRect.bottomRight().y()
		gc.setPen(self.__linePen)
		gc.drawLine(botX, botY, topX, topY)
		
		# horizontal grid	
		dist = self.__baseWidthPixels 
		gc.drawLine(botX-dist, botY, topX-dist, topY)
		pos = dist
		gc.setPen(self.__linePenLt)
		while (pos < csize.width()):
		 	gc.drawLine(botX+pos, botY, topX+pos, topY)
		 	pos = pos + dist
		 	gc.drawLine(botX-pos, botY, topX-pos, topY)
			
		# baseline
		gc.setPen(self.__linePen2)
		gc.drawLine(coordsRect.topLeft().x(), 0, coordsRect.bottomRight().x(), 0)
			
		# base height line
		gc.setPen(self.__linePen)
		gc.drawLine(coordsRect.topLeft().x(), -self.__baseHeightPixels, coordsRect.bottomRight().x(), -self.__baseHeightPixels)
		
		gc.drawLine(coordsRect.topLeft().x(), -self.__ascentHeightPixels, coordsRect.bottomRight().x(), -self.__ascentHeightPixels)
		gc.drawLine(coordsRect.topLeft().x(), self.__descentHeightPixels, coordsRect.bottomRight().x(), self.__descentHeightPixels)
		
		gc.setPen(self.__linePenDotted)
		gc.drawLine(coordsRect.topLeft().x(), -self.__capHeightPixels, coordsRect.bottomRight().x(), -self.__capHeightPixels)
		
		gc.setBrush(self.__spacerBrush)
		gc.drawRect(coordsRect.topLeft().x(), self.__descentHeightPixels, csize.width(), self.__gapHeightPixels)

		vpos = -self.__ascentHeightPixels - self.__gapHeightPixels - self.__descentHeightPixels
		while (vpos+self.__descentHeightPixels > coordsRect.topLeft().y()):
			gc.setPen(self.__linePen2)
			gc.drawLine(coordsRect.topLeft().x(), vpos, coordsRect.bottomRight().x(), vpos)

			gc.setPen(self.__linePen)
			gc.drawLine(coordsRect.topLeft().x(), vpos-self.__baseHeightPixels, coordsRect.bottomRight().x(), vpos-self.__baseHeightPixels)
		
			gc.drawLine(coordsRect.topLeft().x(), vpos-self.__ascentHeightPixels, coordsRect.bottomRight().x(), vpos-self.__ascentHeightPixels)
			gc.drawLine(coordsRect.topLeft().x(), vpos+self.__descentHeightPixels, coordsRect.bottomRight().x(), vpos+self.__descentHeightPixels)
		
			gc.setPen(self.__linePenDotted)
			gc.drawLine(coordsRect.topLeft().x(), vpos-self.__capHeightPixels, coordsRect.bottomRight().x(), vpos-self.__capHeightPixels)
		
			gc.setBrush(self.__spacerBrush)
			gc.drawRect(coordsRect.topLeft().x(), vpos+self.__descentHeightPixels, csize.width(), self.__gapHeightPixels)
			vpos = vpos -self.__ascentHeightPixels - self.__gapHeightPixels - self.__descentHeightPixels

		vpos = self.__ascentHeightPixels + self.__gapHeightPixels + self.__descentHeightPixels
		while (vpos-self.__ascentHeightPixels < coordsRect.bottomRight().y()):
			gc.setPen(self.__linePen2)
			gc.drawLine(coordsRect.topLeft().x(), vpos, coordsRect.bottomRight().x(), vpos)

			gc.setPen(self.__linePen)
			gc.drawLine(coordsRect.topLeft().x(), vpos-self.__baseHeightPixels, coordsRect.bottomRight().x(), vpos-self.__baseHeightPixels)
		
			gc.drawLine(coordsRect.topLeft().x(), vpos-self.__ascentHeightPixels, coordsRect.bottomRight().x(), vpos-self.__ascentHeightPixels)
			gc.drawLine(coordsRect.topLeft().x(), vpos+self.__descentHeightPixels, coordsRect.bottomRight().x(), vpos+self.__descentHeightPixels)
		
			gc.setPen(self.__linePenDotted)
			gc.drawLine(coordsRect.topLeft().x(), vpos-self.__capHeightPixels, coordsRect.bottomRight().x(), vpos-self.__capHeightPixels)
		
			gc.setBrush(self.__spacerBrush)
			gc.drawRect(coordsRect.topLeft().x(), vpos+self.__descentHeightPixels, csize.width(), self.__gapHeightPixels)
			vpos = vpos + self.__ascentHeightPixels + self.__gapHeightPixels + self.__descentHeightPixels


		gc.setPen(self.__linePen)

		
		
