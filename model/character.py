from PyQt4 import QtCore, QtGui

import stroke
import thirdparty.dp

import random
import math
import copy

CURVE_RESOLUTION = 10

STROKE = 'stroke'

class Character(object):
	def __init__(self):
		self.__width = 4
		self.__leftSpacing = 1.0
		self.__rightSpacing = 1.0
		
		self.__strokes = []
		self.__bitmapPreview = None
		
		self.__pos = QtCore.QPoint(0, 0)

	def __getstate__(self):
		saveDict = self.__dict__.copy()

		saveDict["_Character__bitmapPreview"] = None

		return saveDict

	def setPos(self, pt):
		self.__pos = pt
		
	def getPos(self):
		return self.__pos

	pos = property(getPos, setPos)

	def newStroke(self, pts, add=True):
		myStroke = stroke.Stroke()
		
		tempCv = []
		
		startX, startY = pts[0]
		
		myStroke.setCtrlVerticesFromList(pts)
		myStroke.setNumCurvePoints(len(tempCv * CURVE_RESOLUTION))
		myStroke.setPos(startX, startY)
		
		myStroke.calcCurvePoints()
		if (2 == numPts):
			myStroke.straighten()
	
		if add:
			self.__strokes.append(myStroke)

		myStroke.setParent(self)

		return myStroke
		
	def newFreehandStroke(self, pts):
		myStroke = stroke.Stroke()
		rawCv = []
		tempCv = []
		
		newPts = thirdparty.dp.simplify_points(pts, 10)
		startX, startY = newPts[0]
		numPts = len(newPts)
		while ((numPts % 4) != 0):
			newPts.append(newPts[-1])
			numPts = numPts + 1
			
		rawCv = myStroke.calcCtrlVertices(newPts)
		for pt in rawCv:
			tempCv.append([pt[0]-startX+1, pt[1]-startY+1])
		
		myStroke.setCtrlVerticesFromList(tempCv)
		myStroke.setNumCurvePoints(len(tempCv * CURVE_RESOLUTION))
		myStroke.setPos(startX, startY)

		myStroke.calcCurvePoints()
		if (2 == numPts):
			myStroke.straighten()

		self.__strokes.append(myStroke)

		myStroke.setParent(self)
		return myStroke
		
	def addStroke (self, args):
		copyStroke = True

		if args.has_key(STROKE):
			strokeToAdd = args[STROKE]
		else:
			return

		if args.has_key('copyStroke'):
			copyStroke=args['copyStroke']

		if copyStroke:
			newStroke = self.copyStroke({STROKE: strokeToAdd})
			newStroke.setParent(self)
		else:
			newStroke = strokeToAdd

		self.__strokes.append(newStroke)
		
		return newStroke

	def newStrokeInstance (self, args):
		if args.has_key(STROKE):
			strokeToAdd = args[STROKE]
		else:
			return

		newStrokeInstance = stroke.StrokeInstance()
		if not isinstance(strokeToAdd, stroke.Stroke):
			strokeToAdd = strokeToAdd.getStroke()

		newStrokeInstance.setStroke(strokeToAdd)
		self.__strokes.append(newStrokeInstance)
		newStrokeInstance.setParent(self)

		return newStrokeInstance

	def addStrokeInstance (self, inst):
		if not isinstance(inst, stroke.Stroke):
			self.__strokes.append(inst)
			inst.setParent(self)

	def copyStroke(self, args):
		if args.has_key(STROKE):
			strokeToCopy = args[STROKE]
		else:
			return

		if isinstance(strokeToCopy, stroke.Stroke):
			copiedStroke = stroke.Stroke(fromStroke=strokeToCopy)
		else:
			copiedStroke = stroke.StrokeInstance()
			realStrokeToCopy = strokeToCopy.getStroke()
			copiedStroke.setStroke(realStrokeToCopy)

		return copiedStroke
		
	def deleteStroke(self, args):
		if args.has_key(STROKE):
			strokeToDelete = args[STROKE]
		else:
			return

		try:
			self.__strokes.remove(strokeToDelete)
		except:
			print "ERROR: stroke to delete doesn't exist!", strokeToDelete
			print self.__strokes
	
	def distBetweenPts (self, x,y,x1,y1):
		return math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))
	
	@property
	def strokes(self):
		return self.__strokes
			
	def getBitmap(self):
		return self.__bitmapPreview
	
	def setBitmap(self, bmap):
		self.__bitmapPreview = bmap
		
	def delBitmap(self):
		del self.__bitmapPreview
	
	bitmapPreview = property(getBitmap, setBitmap, delBitmap, "bitmapPreview property")	

	def getWidth(self):
		return self.__width

	def setWidth(self, newWidth):
		self.__width = newWidth

	width = property(getWidth, setWidth)

	def getLeftSpacing(self):
		return self.__leftSpacing

	def setLeftSpacing(self, newLeftSpacing):
		self.__leftSpacing = newLeftSpacing

	leftSpacing = property(getLeftSpacing, setLeftSpacing)

	def getRightSpacing(self):
		return self.__rightSpacing

	def setRightSpacing(self, newRightSpacing):
		self.__rightSpacing = newRightSpacing

	rightSpacing = property(getRightSpacing, setRightSpacing)

	def draw(self, gc, showCtrlVerts=0, drawHandles=0, nib=None):
		gc.save()
		gc.translate(self.__pos)

		for stroke in self.__strokes:
			stroke.draw(gc, showCtrlVerts, drawHandles, nib)

		gc.restore()