from PyQt4 import QtCore, QtGui

import math

SNAP_TO_GRID 		= 0x0001
SNAP_TO_AXES 		= 0x0002
SNAP_TO_NIB_AXES 	= 0x0004
SNAP_TO_CTRL_PTS	= 0x0008
SNAP_TO_STROKES		= 0x0010

class SnapController(object):
	def __init__(self, parent):
		self.__mainCtrl = parent
		self.__snap = SNAP_TO_AXES

	def toggleSnapAxially(self):
		self.__snap ^= SNAP_TO_AXES

	def toggleSnapToGrid(self):
		self.__snap ^= SNAP_TO_GRID

	def toggleSnapToNibAxes(self):
		self.__snap ^= SNAP_TO_NIB_AXES

	def toggleSnapToCtrlPts(self):
		self.__snap ^= SNAP_TO_CTRL_PTS

	def getSnap(self):
		return self.__snap

	def getSnappedPoints(self, pos):
		selection = self.__mainCtrl.get_selection()
		currentView = self.__mainCtrl.get_current_view()
		curViewSelection = selection[currentView]
		charSet = self.__mainCtrl.get_character_set()

		snappedPoints = []

		if len(curViewSelection.keys()) == 1:
			selStroke = curViewSelection.keys()[0]

			if len(curViewSelection[selStroke].keys()) == 1:
				selPoint = curViewSelection[selStroke].keys()[0]
			
				ctrlVerts = selStroke.getCtrlVertices(make_copy=False)

				vertIndex = ctrlVerts.index(selPoint)
				
				if selPoint.isKnotSelected():
					if vertIndex == 0:
						vertIndex += 1
					else:
						vertIndex -= 1
				
				vpos = ctrlVerts[vertIndex].getHandlePos(2)
				strokePos = selStroke.getPos()

				if self.__snap & SNAP_TO_GRID:
					snapPoint = self.closestGridPoint(pos)

					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						return snappedPoints

				if self.__snap & SNAP_TO_AXES:
					snapPoint = self.snapToAxes(strokePos, pos, vpos, axisAngles=[0-charSet.guideAngle, 90])

					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						snappedPoints.append(vpos + strokePos)
						return snappedPoints

				if self.__snap & SNAP_TO_NIB_AXES:					
					snapPoint = self.snapToAxes(strokePos, pos, vpos, axisAngles=[charSet.nibAngle, charSet.nibAngle-90])
					
					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						snappedPoints.append(vpos + strokePos)
						return snappedPoints

				if self.__snap & SNAP_TO_CTRL_PTS:
					snapPoint = self.snapToCtrlPoint(strokePos, pos, vpos, selPoint)

					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						return snappedPoints
					
		return snappedPoints

	def snapToAxes(self, strokePos, pos, vertPos, tolerance=10, axisAngles=[]):
		snapPt = QtCore.QPoint(-1, -1)

		if len(axisAngles) == 0:
			return snapPt
		
		delta = pos - vertPos
		vecLength = math.sqrt(float(delta.x())*float(delta.x()) + float(delta.y())*float(delta.y()))

		for angle in axisAngles:

			if delta.y() < 0:
				angle += 180

			newPt = QtCore.QPoint(vecLength * math.sin(math.radians(angle)), \
				vecLength * math.cos(math.radians(angle)))
			newPt = newPt + vertPos + strokePos

			newDelta = pos - newPt

			if abs(newDelta.x()) < tolerance:
				snapPt = newPt

		return snapPt

	def snapToCtrlPoint(self, strokePos, pos, vertPos, selPoint, tolerance=10):
		snapPt = QtCore.QPoint(-1, -1)

		testRect = QtCore.QRect(pos.x()-tolerance/2, pos.y()-tolerance/2, tolerance, tolerance)
		curChar = self.__mainCtrl.get_current_char()

		for charStroke in curChar.strokes:
			for ctrlVert in charStroke.getCtrlVertices(False):
				if selPoint is not ctrlVert:
					testPoint = ctrlVert.getHandlePos(2)

					if testPoint in testRect:
						snapPt = testPoint
						break

		return snapPt

	def closestGridPoint(self, pt, nibWidth=0, tolerance=10):
		gridPt = QtCore.QPoint(-1, -1)

		guides = self.__mainCtrl.get_ui().guideLines
		nibWidth = guides.nibWidth
		angleDX = math.tan(math.radians(guides.guideAngle))

		if nibWidth == 0:
	 		return gridPt 
	 		
	 	ascentHeightNibs = guides.ascentHeight
	 	capHeightNibs = guides.capHeight
	 	
	 	ascentHeightPixels = ascentHeightNibs * nibWidth
	 	descentHeightPixels = guides.descentHeight * nibWidth
	 	gapHeightPixels = guides.gapHeight * nibWidth
	 	
	 	ascentOnly = ascentHeightNibs * nibWidth
	 	capOnly = ascentOnly - (capHeightNibs * nibWidth)

	 	yLines = [0, 
	 			gapHeightPixels + descentHeightPixels + capOnly,
	 			gapHeightPixels + descentHeightPixels + ascentOnly,
	 			gapHeightPixels + descentHeightPixels,
	 			descentHeightPixels,
	 			 ]
	 	
		widthX = guides.nominalWidth * nibWidth
		heightY = ascentHeightPixels + gapHeightPixels + descentHeightPixels

	 	for yLine in yLines:
	 		testY = (pt.y() - yLine) % heightY
	 	
	 		y = -1
	 		if abs(testY) <= tolerance:
	 			y = pt.y() - testY
	 		elif abs(yLine - testY) <= tolerance:
	 			y = pt.y() - testY + heightY
	 		
	 		if y != -1:
				dx =  0-int(y * angleDX)
				testX = (pt.x() - dx) % widthX

				x = -1
 				if abs(testX) <= tolerance:
					x = pt.x() - testX			
				elif abs(widthX - testX) <= tolerance:
					x = pt.x() - testX + widthX

				if x != -1 and (abs(pt.x() - x) <= tolerance*2 and abs(pt.y() - y) <= tolerance*2):
	 				return QtCore.QPoint(x, y)

	 	return gridPt