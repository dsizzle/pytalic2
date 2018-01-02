import stroke
import thirdparty.dp

import random
import math
import copy

CURVE_RESOLUTION = 10

class Character(object):
	def __init__(self):
		self.__strokes = []
		self.__bitmapPreview = None
		
	def __getstate__(self):
		saveDict = self.__dict__.copy()

		saveDict["_Character__bitmapPreview"] = None

		return saveDict

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
		
	def addStroke (self, strokeToAdd, copyStroke=True):
		if copyStroke:
			newStroke = self.copyStroke(strokeToAdd)
			newStroke.setParent(self)
		else:
			newStroke = strokeToAdd

		self.__strokes.append(newStroke)
		
		return newStroke
		
	def addStrokeInstance (self, strokeToAdd):
		newStrokeInstance = stroke.StrokeInstance()
		if not isinstance(strokeToAdd, stroke.Stroke):
			strokeToAdd = strokeToAdd.getStroke()

		newStrokeInstance.setStroke(strokeToAdd)
		self.__strokes.append(newStrokeInstance)
		newStrokeInstance.setParent(self)

		return newStrokeInstance

	def copyStroke(self, strokeToCopy):
		if isinstance(strokeToCopy, stroke.Stroke):
			copiedStroke = stroke.Stroke(fromStroke=strokeToCopy)
		else:
			copiedStroke = stroke.StrokeInstance()
			realStrokeToCopy = strokeToCopy.getStroke()
			copiedStroke.setStroke(realStrokeToCopy)

		return copiedStroke
		
	def deleteStroke(self, strokeToDelete):
		try:
			self.__strokes.remove(strokeToDelete)
		except:
			print "ERROR: stroke to delete doesn't exist!"
	
	def joinStrokes(self, args):
		strokesToJoin = copy.copy(args['strokesToJoin'])
		
		firstStroke = strokesToJoin.pop(0)
		initStroke = self.copyStroke(firstStroke)
		
		while (len(strokesToJoin)):
			
			ptToUse = 0
			curStroke = strokesToJoin.pop(0)
			
			newCtrlPts = initStroke.getCtrlVerticesAsList()
			tempCtrlPts = curStroke.getCtrlVerticesAsList()
			
			(sx,sy) = newCtrlPts[0]
			(ex,ey) = newCtrlPts[-1]
			
			(ix,iy) = initStroke.getPos()
			(cx,cy) = curStroke.getPos()
			
			(csx,csy) = tempCtrlPts[0]
			(cex,cey) = tempCtrlPts[-1]
			sx += ix
			sy += iy
			ex += ix
			ey += iy
			
			csx += cx
			csy += cy
			cex += cx
			cey += cy
			
			dss = self.distBetweenPts(sx,sy,csx,csy)
			dse = self.distBetweenPts(sx,sy,cex,cey)
			des = self.distBetweenPts(ex,ey,csx,csy)
			dee = self.distBetweenPts(ex,ey,cex,cey)
			
			smallest = dss
			if (dse < smallest):
				smallest = dse
				ptToUse = 1
			if (des < smallest):
				smallest = des
				ptToUse = 2
			if (dee < smallest):
				smallest = dee
				ptToUse = 3
			
			if (ptToUse == 0):
				newCtrlPts.reverse()
			elif (ptToUse == 1):
				newCtrlPts.reverse()
				tempCtrlPts.reverse()
			elif (ptToUse == 3):
				tempCtrlPts.reverse()
			
			tempCtrlPts.pop(0)
			for i in range(0, len(tempCtrlPts)):
				tempCtrlPts[i][0] += cx-ix
				tempCtrlPts[i][1] += cy-iy
				
			newCtrlPts.extend(tempCtrlPts)			
			numPts = curStroke.getNumCurvePoints()+initStroke.getNumCurvePoints()
			initStroke.setCtrlVerticesFromList(newCtrlPts)
			initStroke.setNumCurvePoints(numPts)
			
		initStroke.updateCtrlVertices()
		initStroke.calcCurvePoints()
		
		for stroke in args['strokesToJoin']:
			self.deleteStroke(stroke)
		
		self.__strokes.append(initStroke)		
		
		return initStroke
		
	def unjoinStrokes (self, args): 
		joinedStroke = args['joinedStroke']
		strokesToUnjoin = args['strokesToUnjoin']
	
		for stroke in strokesToUnjoin:
			self.__strokes.append(stroke)
		
		self.deleteStroke(joinedStroke)
	
	def rejoinStrokes (self, args): 
		joinedStroke = args['joinedStroke']
		strokesToJoin = args['strokesToJoin']

		for stroke in strokesToJoin:
			self.deleteStroke(stroke)
			
		self.__strokes.append(joinedStroke)
	
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
	
	def draw(self, showCtrlVerts=0, drawHandles=0, nib=None):
		
		for stroke in self.__strokes:
			stroke.draw(showCtrlVerts, drawHandles, nib)
