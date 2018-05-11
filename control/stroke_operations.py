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

		for selStroke in selection:
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
		ui.strokeSavedEdit.setEnabled(True)
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
			curChar = self.__charSet.getCurrentChar()
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
			ui.strokeSavedEdit.setEnabled(False)

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