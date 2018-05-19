from PyQt4 import QtCore, QtGui

import math

import edit_control
from model import commands, stroke

class stroke_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent
		self.__tmpStroke = None
		self.__strokePts = []

	def getTmpStroke(self):
		return self.__tmpStroke

	def setTmpStroke(self, newTmpStroke):
		self.__tmpStroke = newTmpStroke

	tmpStroke = property(getTmpStroke, setTmpStroke)

	def getStrokePts(self):
		return self.__strokePts

	def setStrokePts(self, newStrokePts):
		self.__strokePts = newStrokePts

	strokePts = property(getStrokePts, setStrokePts)

	def createNewStroke(self):
		if self.__mainCtrl.state == edit_control.DRAWING_NEW_STROKE:
			return
		
		ui = self.__mainCtrl.getUI()

		self.__mainCtrl.state = edit_control.DRAWING_NEW_STROKE
		QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

		dwgTab = ui.mainViewTabs.indexOf(ui.dwgArea)

		for idx in range(0, ui.mainViewTabs.count()):
			if idx != dwgTab:
				ui.mainViewTabs.setTabEnabled(idx, False)

		self.__strokePts = []
		self.__tmpStroke = stroke.Stroke()
		ui.dwgArea.strokesSpecial.append(self.__tmpStroke)

	def saveStroke(self):
		selectedStrokes = []
		instances = []
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()
		cmdStack = self.__mainCtrl.getCommandStack()

		for selStroke in curViewSelection.keys():
			if type(selStroke).__name__ == 'Stroke':
				selectedStrokes.append(selStroke)

				newStrokeInstance = stroke.StrokeInstance()
				instances.append(newStrokeInstance)

		itemNum = ui.strokeSelectorList.count()

		saveStrokeCmd = commands.command('saveStrokeCmd')
		
		doArgs = {
			'strokes' : selectedStrokes,
			'instances' : instances,
			'firstItem' : itemNum,
		}

		undoArgs = {
			'instances' : instances,
			'firstItem' : itemNum,
		}

		saveStrokeCmd.setDoArgs(doArgs)
		saveStrokeCmd.setUndoArgs(undoArgs)
		saveStrokeCmd.setDoFunction(self.saveStrokes)
		saveStrokeCmd.setUndoFunction(self.unsaveStrokes)
		
		cmdStack.doCommand(saveStrokeCmd)
		ui.editUndo.setEnabled(True)

		ui.repaint()

	def saveStrokes(self, args):
		deletedStrokes = []
		i = 0

		if args.has_key('strokes'):
			selection = args['strokes']
		else:
			return

		if args.has_key('instances'):
			instances = args['instances']
		else:
			return

		if args.has_key('firstItem'):
			firstItem = args['firstItem']
		else:
			return

		charSet = self.__mainCtrl.getCharacterSet()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()

		for selStroke in curViewSelection:
			charSet.saveStroke(selStroke)
			bitmap = ui.dwgArea.drawIcon(None, [selStroke])
			ui.strokeSelectorList.addItem(str(firstItem+i))
			curItem = ui.strokeSelectorList.item(firstItem+i)
			ui.strokeSelectorList.setCurrentRow(firstItem+i)
			curItem.setIcon(QtGui.QIcon(bitmap))
			curChar = charSet.getCurrentChar()
			deletedStrokes.append(selStroke)
			curChar.deleteStroke({'stroke' : selStroke})
			selStroke = charSet.getSavedStroke(firstItem+i)
			instances[i].setStroke(selStroke)
			curChar.addStrokeInstance(instances[i])
			if not curViewSelection.has_key(selStroke):
				curViewSelection = {}
				selStroke.deselectCtrlVerts()

			selStroke.selected = True
			i += 1
				
		for selStroke in deletedStrokes:
			if curViewSelection.has_key(selStroke):
				del curViewSelection[selStroke]

			selStroke.selected = False	

		ui.strokeLoad.setEnabled(True)
		self.__mainCtrl.setUIStateSelection(True)

	def unsaveStrokes(self, args):
		addedStrokes = []
		i = 0

		if args.has_key('instances'):
			instances = args['instances']
			i = len(instances)-1
		else:
			return

		if args.has_key('firstItem'):
			firstItem = args['firstItem']
		else:
			return

		charSet = self.__mainCtrl.getCharacterSet()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()

		instances.reverse()
		for inst in instances:
			selStroke = inst.getStroke()
			ui.strokeSelectorList.takeItem(firstItem+i)
			charSet.removeSavedStroke(selStroke)
			curChar = charSet.getCurrentChar()
			curChar.deleteStroke({'stroke' : inst})
			curChar.addStroke({'stroke' : selStroke, 'copyStroke' : False})
			addedStrokes.append(selStroke)
			i -= 1
			
		for selStroke in addedStrokes:
			if not curViewSelection.has_key(selStroke):
				curViewSelection[selStroke] = {}
				selStroke.deselectCtrlVerts()
			
			selStroke.selected = True

		if ui.strokeSelectorList.count() == 0:
			ui.strokeLoad.setEnabled(False)
			
		self.__mainCtrl.setUIStateSelection(True)
		
	def pasteInstanceFromSaved(self):
		cmdStack = self.__mainCtrl.getCommandStack()
		charSet = self.__mainCtrl.getCharacterSet()
		ui = self.__mainCtrl.getUI()

		charIndex = charSet.getCurrentCharIndex()
		strokeIndex = ui.strokeSelectorList.currentRow()
		savedStroke = charSet.getSavedStroke(strokeIndex)
		newStrokeInstance = stroke.StrokeInstance()
		newStrokeInstance.setStroke(savedStroke)

		pasteInstanceSavedCmd = commands.command('pasteInstanceSavedCmd')
		
		doArgs = {
			'strokes' : newStrokeInstance,
			'charIndex' : charIndex,
		}

		undoArgs = {
			'strokes' : newStrokeInstance,
			'charIndex' : charIndex,
		}

		pasteInstanceSavedCmd.setDoArgs(doArgs)
		pasteInstanceSavedCmd.setUndoArgs(undoArgs)
		pasteInstanceSavedCmd.setDoFunction(self.pasteInstance)
		pasteInstanceSavedCmd.setUndoFunction(self.deleteInstance)
		
		cmdStack.doCommand(pasteInstanceSavedCmd)
		ui.editUndo.setEnabled(True)

		ui.repaint()

	def pasteInstance(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokeInstance = args['strokes']
		else:
			return

		curChar = self.__mainCtrl.getCurrentChar()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()

		ui.charSelectorList.setCurrentRow(charIndex)

		curChar.addStrokeInstance(strokeInstance)
		curViewSelection[strokeInstance] = {}
		
		ui.dwgArea.repaint()
		self.__mainCtrl.setIcon()

	def deleteInstance(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokeToDel = args['strokes']
		else:
			return

		curChar = self.__mainCtrl.getCurrentChar()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()

		curChar.deleteStroke({'stroke' : strokeToDel})
		if curViewSelection.has_key(strokeToDel):
			del curViewSelection[strokeToDel]

		ui.dwgArea.repaint()

	def straightenStroke(self):
		cmdStack = self.__mainCtrl.getCommandStack()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()

		if len(curViewSelection.keys()) == 1:
			selStroke = curViewSelection.keys()[0]

			vertsBefore = selStroke.getCtrlVerticesAsList()

			strokeStraightenCmd = commands.command("strokeStraightenCmd")

			undoArgs = {
				'strokes' : selStroke,
				'ctrlVerts' : vertsBefore
			}

			selStroke.straighten()

			doArgs = {
				'strokes' : selStroke,
				'ctrlVerts' : selStroke.getCtrlVerticesAsList()
			}

			strokeStraightenCmd.setDoArgs(doArgs)
			strokeStraightenCmd.setUndoArgs(undoArgs)
			strokeStraightenCmd.setDoFunction(self.setStrokeControlVertices)
			strokeStraightenCmd.setUndoFunction(self.setStrokeControlVertices)
						
			cmdStack.addToUndo(strokeStraightenCmd)
			cmdStack.saveCount += 1
			ui.editUndo.setEnabled(True)

	def joinSelectedStrokes(self):
		cmdStack = self.__mainCtrl.getCommandStack()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()

		if len(curViewSelection.keys()) > 1:
			strokeJoinCmd = commands.command("strokeJoinCmd")
			selectionCopy = curViewSelection.copy()

			newStroke = self.joinStrokes(selectionCopy)

			doArgs = {
				'strokes' : selectionCopy,
				'joinedStroke' : newStroke
			}

			undoArgs = {
				'strokes' : selectionCopy.copy(),
				'joinedStroke' : newStroke
			}
			
			strokeJoinCmd.setDoArgs(doArgs)
			strokeJoinCmd.setUndoArgs(undoArgs)
			strokeJoinCmd.setDoFunction(self.joinAllStrokes)
			strokeJoinCmd.setUndoFunction(self.unjoinAllStrokes)

			cmdStack.addToUndo(strokeJoinCmd)
			cmdStack.saveCount += 1
			ui.editUndo.setEnabled(True)
			ui.repaint()
			
	def joinStrokes(self, strokes):
		curChar = self.__mainCtrl.getCurrentChar()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		
		strokeList = strokes.keys()
		curStroke = strokeList.pop(0)
		vertList = curStroke.getCtrlVerticesAsList()
		curChar.deleteStroke({'stroke': curStroke})
		if curViewSelection.has_key(curStroke):
			del curViewSelection[curStroke]
			curStroke.selected = False

		while len(strokeList):
			curStroke = strokeList.pop(0)
			curVerts = curStroke.getCtrlVerticesAsList()
			curChar.deleteStroke({'stroke': curStroke})
			if curViewSelection.has_key(curStroke):
				del curViewSelection[curStroke]
				curStroke.selected = False

			d1 = distBetweenPts(curVerts[0], vertList[0])
			d2 = distBetweenPts(curVerts[-1], vertList[0])
			d3 = distBetweenPts(curVerts[0], vertList[-1])
			d4 = distBetweenPts(curVerts[-1], vertList[-1])

			ptList = [d1, d2, d3, d4]
			ptList.sort()

			smallest = ptList[0]

			if smallest == d1:
				curVerts.reverse()

			if smallest == d1 or smallest == d4:
				vertList.reverse()

			if smallest == d2:
				(curVerts, vertList) = (vertList, curVerts)

			vertList.extend(curVerts[1:])

		newStroke = stroke.Stroke()
		newStroke.setCtrlVerticesFromList(vertList)
		newStroke.calcCurvePoints()
		curChar.addStroke({'stroke': newStroke, 'copyStroke': False})
		
		curViewSelection[newStroke] = {}
		newStroke.selected = True

		return newStroke

	def unjoinAllStrokes(self, args):
		if args.has_key('strokes'):
			strokes = args['strokes']
		else:
			return

		if args.has_key('joinedStroke'):
			joinedStroke = args['joinedStroke']
		else:
			return

		curChar = self.__mainCtrl.getCurrentChar()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		
		curChar.deleteStroke({'stroke': joinedStroke})
		joinedStroke.selected = False
		if curViewSelection.has_key(joinedStroke):
			del curViewSelection[joinedStroke]

		for selStroke in strokes.keys():
			curChar.addStroke({'stroke': selStroke, 'copyStroke': False})
			curViewSelection[selStroke] = {}
			selStroke.selected = True

	def joinAllStrokes(self, args):
		if args.has_key('strokes'):
			strokes = args['strokes']
		else:
			return

		if args.has_key('joinedStroke'):
			joinedStroke = args['joinedStroke']
		else:
			return

		curChar = self.__mainCtrl.getCurrentChar()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]

		curChar.addStroke({'stroke': joinedStroke, 'copyStroke': False})
		joinedStroke.selected = True
		curViewSelection[joinedStroke] = {}

		for selStroke in strokes.keys():
			curChar.deleteStroke({'stroke': selStroke})
			if curViewSelection.has_key(selStroke):
				del curViewSelection[selStroke]
			selStroke.selected = False

	def setStrokeControlVertices(self, args):
		ui = self.__mainCtrl.getUI()

		if args.has_key('strokes'):
			selStroke = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVerts = args['ctrlVerts']
		else:
			return

		if len(ctrlVerts) == 0:
			return

		selStroke.setCtrlVerticesFromList(ctrlVerts)
		selStroke.calcCurvePoints()
		ui.repaint()

	def splitStroke(self, args):
		ui = self.__mainCtrl.getUI()
		curChar = self.__mainCtrl.getCurrentChar()

		if args.has_key('strokes'):
			selStroke = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVerts = args['ctrlVerts']
		else:
			return

		if args.has_key('newStroke'):
			newStroke = args['newStroke']
		else:
			return

		selStroke.setCtrlVerticesFromList(ctrlVerts)
		selStroke.calcCurvePoints()
		
		curChar.addStroke({'stroke': newStroke, 'copyStroke': False})
		ui.repaint()

	def unsplitStroke(self, args):
		ui = self.__mainCtrl.getUI()
		curChar = self.__mainCtrl.getCurrentChar()

		if args.has_key('strokes'):
			selStroke = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVerts = args['ctrlVerts']
		else:
			return

		if args.has_key('strokeToDelete'):
			delStroke = args['strokeToDelete']
		else:
			return

		selStroke.setCtrlVerticesFromList(ctrlVerts)
		selStroke.calcCurvePoints()
		curChar.deleteStroke({'stroke': delStroke})
		ui.repaint()

	def addControlPoint(self, selStroke, insideInfo):
		ui = self.__mainCtrl.getUI()
		cmdStack = self.__mainCtrl.getCommandStack()

		addVertexCmd = commands.command('addVertexCmd')
						
		undoArgs = {
			'strokes' : selStroke,
			'ctrlVerts' : selStroke.getCtrlVerticesAsList()
		}

		selStroke.addCtrlVertex(insideInfo[2], insideInfo[1])
		
		doArgs = {
			'strokes' : selStroke,
			'ctrlVerts' : selStroke.getCtrlVerticesAsList()
		}

		addVertexCmd.setDoArgs(doArgs)
		addVertexCmd.setUndoArgs(undoArgs)
		addVertexCmd.setDoFunction(self.setStrokeControlVertices)
		addVertexCmd.setUndoFunction(self.setStrokeControlVertices)
		
		cmdStack.addToUndo(addVertexCmd)
		cmdStack.saveCount += 1
		ui.editUndo.setEnabled(True)

	def splitStrokeAtPoint(self, selStroke, insideInfo):
		ui = self.__mainCtrl.getUI()
		cmdStack = self.__mainCtrl.getCommandStack()

		splitAtCmd = commands.command('splitAtCmd')
		vertsBefore = selStroke.getCtrlVerticesAsList()

		newVerts = selStroke.splitAtPoint(insideInfo[2], insideInfo[1])
		vertsAfter = selStroke.getCtrlVerticesAsList()

		newStroke = stroke.Stroke()
		newStroke.setCtrlVerticesFromList(newVerts)

		undoArgs = {
			'strokes' : selStroke,
			'ctrlVerts' : vertsBefore,
			'strokeToDelete' : newStroke,
		}

		doArgs = {
			'strokes' : selStroke,
			'newStroke' : newStroke,
			'ctrlVerts' : vertsAfter,
		}

		splitAtCmd.setDoArgs(doArgs)
		splitAtCmd.setUndoArgs(undoArgs)
		splitAtCmd.setDoFunction(self.splitStroke)
		splitAtCmd.setUndoFunction(self.unsplitStroke)
		
		cmdStack.doCommand(splitAtCmd)
		ui.editUndo.setEnabled(True)

	def addNewStroke(self):
		curChar = self.__mainCtrl.getCurrentChar()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()
		cmdStack = self.__mainCtrl.getCommandStack()

		verts = self.__tmpStroke.getCtrlVerticesAsList()
		if len(verts) < 2:
			self.__mainCtrl.state = edit_control.IDLE
			self.__tmpStroke = None
			self.__strokePts = []
			currentView.strokesSpecial = []
			ui.repaint()
			return

		self.__mainCtrl.state = edit_control.IDLE
		self.__strokePts = []
		
		addStrokeCmd = commands.command('addStrokeCmd')
		doArgs = {
			'stroke' : self.__tmpStroke,
			'copyStroke' : False,
		}

		undoArgs = {
			'stroke' : self.__tmpStroke,
		}

		addStrokeCmd.setDoArgs(doArgs)
		addStrokeCmd.setUndoArgs(undoArgs)
		addStrokeCmd.setDoFunction(curChar.addStroke)
		addStrokeCmd.setUndoFunction(curChar.deleteStroke)
		
		cmdStack.doCommand(addStrokeCmd)
		ui.editUndo.setEnabled(True)

		curViewSelection[self.__tmpStroke] = {}
		self.__tmpStroke.selected = True
		currentView.strokesSpecial = []
		self.__tmpStroke = None

		self.__mainCtrl.setUIStateSelection(True)
		
		for idx in range(0, ui.mainViewTabs.count()):
			ui.mainViewTabs.setTabEnabled(idx, True)
		
		ui.repaint()

	def moveSelected(self, args):
		if args.has_key('strokes'):
			selection = args['strokes']
		else:
			return

		if args.has_key('delta'):
			delta = args['delta']
		else:
			return

		snapPoint = None
		if args.has_key('snapPoint'):
			snapPoint = args['snapPoint']
		
		for stroke in selection.keys():
			if len(selection[stroke].keys()) > 0:
				for strokePt in selection[stroke].keys():
					strokePt.selectHandle(selection[stroke][strokePt])
					if snapPoint:
						strokePt.selectedHandlePos = snapPoint-stroke.pos
					else:
						strokePt.selectedHandlePos = strokePt.selectedHandlePos + delta
			else:
				stroke.pos += delta
			
			stroke.calcCurvePoints()

def distBetweenPts (p0, p1):
	return math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]))