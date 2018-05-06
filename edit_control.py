import os
import os.path
import math
import pickle
import sys

from PyQt4 import QtGui, QtCore

import character_set
import commands
import edit_ui
import stroke

gICON_SIZE = 40

IDLE = 0
MOVING_PAPER = 1
DRAWING_NEW_STROKE = 2
DRAGGING = 3
ADDING_CTRL_POINT = 4
SPLIT_AT_POINT = 5

SNAP_TO_GRID 		= 0x0001
SNAP_TO_AXES 		= 0x0002
SNAP_TO_NIB_AXES 	= 0x0004
SNAP_TO_CTRL_PTS	= 0x0008
SNAP_TO_STROKES		= 0x0010

class editor_controller(): 
	def __init__(self, w, h, label):
		self.__label = label
		self.__ui = edit_ui.edit_interface(self, w, h, label)

		self.fileOpenDlg = QtGui.QFileDialog() 
		self.fileSaveDlg = QtGui.QFileDialog() 
		self.colorPickerDlg = QtGui.QColorDialog()
		
		self.__color = QtGui.QColor(125, 25, 25)
		
		self.__fileName = None
		self.__dirName = os.getcwd()
		self.__mainNib = None 
		self.__tempChar = None
		self.__clipBoard = []
		self.__cmdStack = commands.commandStack()
		self.__selection = {}
		self.__charSet = None
		self.__curChar = None

		self.__savedMousePosPaper = {}
		self.__moveDelta = QtCore.QPoint(0, 0)
		self.__state = 0
		
		self.__strokePts = []
		self.__tmpStroke = None
		self.__snap = SNAP_TO_AXES

		charList = []
		for i in range(32, 128):
			charList.append(str(unichr(i)))

		self.__ui.createUI()
		self.__ui.charSelectorList.addItems(QtCore.QStringList(charList))

		self.blankPixmap = QtGui.QPixmap(gICON_SIZE, gICON_SIZE)
		self.blankPixmap.fill(QtGui.QColor(240, 240, 240))

		for idx in range(0, self.__ui.charSelectorList.count()):
			self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blankPixmap))
		self.__ui.dwgArea.bitmapSize = gICON_SIZE

		self.__currentViewPane = self.__ui.mainViewTabs.currentWidget()
		self.__selection[self.__currentViewPane] = {}

		self.mainMenu = None
		self.toolBar = None
		self.fileNew_cb(None)

	def activate(self):
		self.__ui.show()
		self.__ui.activateWindow()
		self.__ui.raise_()
	
	def quit_cb(self, event):
		if self.__cmdStack.saveCount == 0: 
			self.__ui.close()
		else:
			reply = self.__ui.messageDialog.question(self.__ui, 'Quit Program', "You have unsaved changes. Are you sure you want to quit?", \
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				self.__ui.close()

	def undo_cb(self, event):
		self.__cmdStack.undo()
		if self.__cmdStack.undoIsEmpty():
			self.__ui.editUndo.setEnabled(False)
		self.__ui.editRedo.setEnabled(True)
		self.__ui.repaint()

	def redo_cb(self, event):
		self.__cmdStack.redo()
		if self.__cmdStack.redoIsEmpty():
			self.__ui.editRedo.setEnabled(False)
		self.__ui.editUndo.setEnabled(True)
		self.__ui.repaint()

	def fileNew_cb(self, event):
		self.__fileName = None
	
		self.__charSet = character_set.character_set()
		self.__ui.baseHeightSpin.setValue(self.__charSet.baseHeight)
		self.__ui.capHeightSpin.setValue(self.__charSet.capHeight)
		self.__ui.capHeightSpin.setMaximum(self.__charSet.ascentHeight)
		self.__ui.ascentHeightSpin.setValue(self.__charSet.ascentHeight)
		self.__ui.descentHeightSpin.setValue(self.__charSet.descentHeight)
		self.__ui.angleSpin.setValue(5)

		self.name = (self.__label + " - Untitled")
		self.__ui.setWindowTitle(self.name)

		self.__ui.strokeSelectorList.clear()

		for idx in range(0, self.__ui.charSelectorList.count()):
			self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blankPixmap))

		self.__ui.charSelectorList.setCurrentRow(0)
		self.__curChar = self.__charSet.getCurrentChar()

		self.__cmdStack = commands.commandStack()
		self.__ui.editUndo.setEnabled(False)
		self.__ui.editRedo.setEnabled(False)
		self.__ui.fileSave.setEnabled(False)

	def fileSaveAs_cb(self, event):
		fileName = self.__ui.fileSaveDialog.getSaveFileName(self.__ui,
		     "Save Character Set", self.__dirName, "Character Set Files (*.cs)")
			
		if (fileName):
			(self.__dirName, self.__fileName) = os.path.split(str(fileName))
			(name, ext) = os.path.splitext(self.__fileName)	

			if (ext != ".cs"):
				self.__fileName += ".cs"

			self.save(self.__fileName)
			self.__ui.setWindowTitle(self.__label + " - " + self.__fileName)
			self.__cmdStack.resetSaveCount()
			self.__ui.fileSave.setEnabled(True)

	def fileSave_cb(self, event):
		if self.__fileName and os.path.isfile(self.__fileName):
			self.save(self.__fileName)
			self.__cmdStack.resetSaveCount()
		else:
			self.fileSaveAs_cb(event)

	def fileOpen_cb(self):
	 	fileName = None
		fileName = self.__ui.fileOpenDialog.getOpenFileName(self.__ui,
		     "Open Character Set", self.__dirName, "Character Set Files (*.cs)")

		if (fileName):
			self.load(fileName)

			self.__ui.baseHeightSpin.setValue(self.__charSet.baseHeight)
			self.__ui.capHeightSpin.setValue(self.__charSet.capHeight)
			self.__ui.capHeightSpin.setMaximum(self.__charSet.ascentHeight)
			self.__ui.ascentHeightSpin.setValue(self.__charSet.ascentHeight)
			self.__ui.descentHeightSpin.setValue(self.__charSet.descentHeight)

			(self.__dirName, self.__fileName) = os.path.split(str(fileName))

			self.__ui.setWindowTitle(self.__label + " - " + self.__fileName)
		
	 		self.__ui.strokeSelectorList.clear()

	 		savedStrokeList = self.__charSet.getSavedStrokes()
	 		if len(savedStrokeList) > 0:
	 			i = 0
	 			self.__ui.strokeLoad.setEnabled(True)
	 			for selStroke in savedStrokeList:
					bitmap = self.__ui.dwgArea.drawIcon(None, [selStroke])
					self.__ui.strokeSelectorList.addItem(str(i))
					curItem = self.__ui.strokeSelectorList.item(i)
					self.__ui.strokeSelectorList.setCurrentRow(i)
					curItem.setIcon(QtGui.QIcon(bitmap))
					i += 1
					
			for idx in range(0, self.__ui.charSelectorList.count()):
				self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blankPixmap))

			idx = 0
			charList = self.__charSet.getCharList()

			for character in charList.keys():
				if len(charList[character].strokes) > 0:
					self.__ui.charSelectorList.setCurrentRow(idx)
					self.__ui.repaint()

				idx += 1

			self.__ui.charSelectorList.setCurrentRow(1)
			self.__ui.charSelectorList.setCurrentRow(0)
			
			self.__selection[self.__currentViewPane] = {}
	 		self.__ui.repaint()
		
			self.__cmdStack.clear()
			self.__cmdStack.resetSaveCount()
			self.__ui.fileSave.setEnabled(True)

	def save(self, fileName):
		try:
			dataFileFd = open(fileName, 'wb')
		except IOError:
			print "ERROR: Couldn't open %s for writing." % (fileName)
			return 1
		
		try:
			dataPickler = pickle.Pickler(dataFileFd)
			dataPickler.dump(self.__charSet)
		except pickle.PicklingError:
			print "ERROR: Couldn't serialize data"
			return 1

		if dataFileFd:
			dataFileFd.close()

	def load(self, fileName):
		try:
			dataFileFd = open(fileName, 'rb')
		except IOError:
			print "ERROR: Couldn't open %s for reading." % (fileName)
			return 1
		
		try:
			dataPickler = pickle.Unpickler(dataFileFd)		
			self.__charSet = dataPickler.load()
		except pickle.UnpicklingError:
			print "ERROR: Couldn't unserialize data"
			return 1
		except:
			print "ERROR: OTHER"
			return 1

		if dataFileFd:
			dataFileFd.close()

	def createNewStroke(self, event):
		if self.__state == DRAWING_NEW_STROKE:
			return

		self.__state = DRAWING_NEW_STROKE
		dwgTab = self.__ui.mainViewTabs.indexOf(self.__ui.dwgArea)

		for idx in range(0, self.__ui.mainViewTabs.count()):
			if idx != dwgTab:
				self.__ui.mainViewTabs.setTabEnabled(idx, False)

		self.__strokePts = []
		self.__tmpStroke = stroke.Stroke()
		self.__ui.dwgArea.strokesSpecial.append(self.__tmpStroke)

	def saveStroke_cb(self, event):
		selectedStrokes = []
		instances = []

		for selStroke in self.__selection[self.__currentViewPane].keys():
			if type(selStroke).__name__ == 'Stroke':
				selectedStrokes.append(selStroke)

				newStrokeInstance = stroke.StrokeInstance()
				instances.append(newStrokeInstance)

		itemNum = self.__ui.strokeSelectorList.count()

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
		
		self.__cmdStack.doCommand(saveStrokeCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

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

		for selStroke in selection:
			self.__charSet.saveStroke(selStroke)
			bitmap = self.__ui.dwgArea.drawIcon(None, [selStroke])
			self.__ui.strokeSelectorList.addItem(str(firstItem+i))
			curItem = self.__ui.strokeSelectorList.item(firstItem+i)
			self.__ui.strokeSelectorList.setCurrentRow(firstItem+i)
			curItem.setIcon(QtGui.QIcon(bitmap))
			curChar = self.__charSet.getCurrentChar()
			deletedStrokes.append(selStroke)
			curChar.deleteStroke({'stroke' : selStroke})
			selStroke = self.__charSet.getSavedStroke(firstItem+i)
			instances[i].setStroke(selStroke)
			curChar.addStrokeInstance(instances[i])
			if not self.__selection[self.__currentViewPane].has_key(selStroke):
				self.__selection[self.__currentViewPane][selStroke] = {}
				selStroke.deselectCtrlVerts()

			selStroke.selected = True
			i += 1
				
		for selStroke in deletedStrokes:
			if self.__selection[self.__currentViewPane].has_key(selStroke):
				del self.__selection[self.__currentViewPane][selStroke]

			selStroke.selected = False	

		self.__ui.strokeLoad.setEnabled(True)
		self.__ui.strokeSavedEdit.setEnabled(True)
		self.setUIStateSelection(True)

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

		instances.reverse()
		for inst in instances:
			selStroke = inst.getStroke()
			self.__ui.strokeSelectorList.takeItem(firstItem+i)
			self.__charSet.removeSavedStroke(selStroke)
			curChar = self.__charSet.getCurrentChar()
			curChar.deleteStroke({'stroke' : inst})
			curChar.addStroke({'stroke' : selStroke, 'copyStroke' : False})
			addedStrokes.append(selStroke)
			i -= 1
			
		for selStroke in addedStrokes:
			if not self.__selection[self.__currentViewPane].has_key(selStroke):
				self.__selection[self.__currentViewPane][selStroke] = {}
				selStroke.deselectCtrlVerts()
			
			selStroke.selected = True

		if self.__ui.strokeSelectorList.count() == 0:
			self.__ui.strokeLoad.setEnabled(False)
			self.__ui.strokeSavedEdit.setEnabled(False)

		self.setUIStateSelection(True)
		
	def addControlPoint_cb(self, event):
		self.__state = ADDING_CTRL_POINT

	def splitAtPoint_cb(self, event):
		self.__state = SPLIT_AT_POINT

	def cutStrokes_cb(self, event):
		cutStrokesCmd = commands.command('cutStrokesCmd')
		charIndex = self.__charSet.getCurrentCharIndex()

		doArgs = {
			'strokes' : self.__selection[self.__currentViewPane].copy(),
			'charIndex' : charIndex,
		}

		undoArgs = {
			'strokes' : self.__selection[self.__currentViewPane].copy(),
			'charIndex' : charIndex,
			'copy' : False,
		}

		cutStrokesCmd.setDoArgs(doArgs)
		cutStrokesCmd.setUndoArgs(undoArgs)
		cutStrokesCmd.setDoFunction(self.cutClipboard)
		cutStrokesCmd.setUndoFunction(self.pasteClipboard)
		
		self.__cmdStack.doCommand(cutStrokesCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def cutClipboard(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokesToCut = args['strokes']
		else:
			return

		self.__ui.charSelectorList.setCurrentRow(charIndex)
		self.__clipBoard = []
		for selStroke in strokesToCut:
			self.__curChar.deleteStroke({'stroke' : selStroke})
			self.__clipBoard.append(selStroke)
			if self.__selection[self.__currentViewPane].has_key(selStroke):
				del self.__selection[self.__currentViewPane][selStroke]
			selStroke.selected = False

		self.__ui.editPaste.setEnabled(True)
		self.__ui.repaint()	

	def copyStrokes_cb(self, event):
		copyStrokesCmd = commands.command('copyStrokesCmd')
		charIndex = self.__charSet.getCurrentCharIndex()

		doArgs = {
			'strokes' : self.__selection[self.__currentViewPane].copy(),
			'charIndex' : charIndex,
		}

		undoArgs = {
			'strokes' : self.__selection[self.__currentViewPane].copy(),
			'charIndex' : charIndex,
		}

		copyStrokesCmd.setDoArgs(doArgs)
		copyStrokesCmd.setUndoArgs(undoArgs)
		copyStrokesCmd.setDoFunction(self.copyClipboard)
		copyStrokesCmd.setUndoFunction(self.pasteClipboard)
		
		self.__cmdStack.doCommand(copyStrokesCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def copyClipboard(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokesToCopy = args['strokes']
		else:
			return

		self.__ui.charSelectorList.setCurrentRow(charIndex)
		self.__clipBoard = []
		for selStroke in strokesToCopy.keys():
			self.__clipBoard.append(selStroke)
			
		self.__ui.editPaste.setEnabled(True)
		self.__ui.repaint()	

	def pasteStrokes_cb(self, event):
		pasteStrokesCmd = commands.command('pasteStrokesCmd')
		charIndex = self.__charSet.getCurrentCharIndex()

		doArgs = {
			'strokes' : self.__clipBoard[:],
			'charIndex' : charIndex,
		}

		undoArgs = {
			'strokes' : self.__clipBoard[:],
			'charIndex' : charIndex,
			'copy' : True,
		}

		pasteStrokesCmd.setDoArgs(doArgs)
		pasteStrokesCmd.setUndoArgs(undoArgs)
		pasteStrokesCmd.setDoFunction(self.pasteClipboard)
		pasteStrokesCmd.setUndoFunction(self.cutClipboard)
		
		self.__cmdStack.doCommand(pasteStrokesCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def pasteClipboard(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokesToPaste = args['strokes']
		else:
			return

		if args.has_key('copy'):
			copyStrokes = args['copy']
		else:
			copyStrokes = True

		self.__ui.charSelectorList.setCurrentRow(charIndex)
		
		for selStroke in self.__selection[self.__currentViewPane].keys():
			selStroke.selected = False

		self.__selection[self.__currentViewPane] = {}

		for selStroke in strokesToPaste:
			if copyStrokes:
				pasteStroke = stroke.Stroke(fromStroke=selStroke)
			else:
				pasteStroke = selStroke

			self.__selection[self.__currentViewPane][pasteStroke] = {}
			pasteStroke.selected = True
			if type(pasteStroke).__name__ == 'Stroke':
				self.__curChar.addStroke({'stroke' : pasteStroke, 'copyStroke' : False})
			else:
				self.__curChar.newStrokeInstance({'stroke' : pasteStroke})

		self.setUIStateSelection(True)
		self.__ui.repaint()	

	def pasteInstanceFromSaved_cb(self, event):
		pasteInstanceSavedCmd = commands.command('pasteInstanceSavedCmd')
		charIndex = self.__charSet.getCurrentCharIndex()
		strokeIndex = self.__ui.strokeSelectorList.currentRow()
		savedStroke = self.__charSet.getSavedStroke(strokeIndex)
		newStrokeInstance = stroke.StrokeInstance()
		newStrokeInstance.setStroke(savedStroke)

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
		
		self.__cmdStack.doCommand(pasteInstanceSavedCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def pasteInstance(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokeInstance = args['strokes']
		else:
			return

		self.__ui.charSelectorList.setCurrentRow(charIndex)

		self.__curChar.addStrokeInstance(strokeInstance)
		self.__selection[self.__currentViewPane][strokeInstance] = {}
		
		self.__ui.dwgArea.repaint()
		self.setIcon()

	def deleteInstance(self, args):
		if args.has_key('charIndex'):
			charIndex = args['charIndex']
		else:
			return

		if args.has_key('strokes'):
			strokeToDel = args['strokes']
		else:
			return

		self.__curChar.deleteStroke({'stroke' : strokeToDel})
		if self.__selection[self.__currentViewPane].has_key(strokeToDel):
			del self.__selection[self.__currentViewPane][strokeToDel]

		self.__ui.dwgArea.repaint()

	def viewToggleSnapAxially_cb(self, event):
		self.__snap ^= SNAP_TO_AXES

	def viewToggleSnapToGrid_cb(self, event):
		self.__snap ^= SNAP_TO_GRID

	def viewToggleSnapToNibAxes_cb(self, event):
		self.__snap ^= SNAP_TO_NIB_AXES

	def viewToggleSnapToCtrlPts_cb(self, event):
		self.__snap ^= SNAP_TO_CTRL_PTS

	def viewToggleGuidelines_cb(self, event):
		self.__currentViewPane.drawGuidelines = not self.__currentViewPane.drawGuidelines
		self.__ui.repaint()

	def viewToggleNibGuides_cb(self, event):
		self.__currentViewPane.drawNibGuides = not self.__currentViewPane.drawNibGuides
		self.__ui.repaint()


	def viewResetOrigin(self, event):
		self.__currentViewPane.originDelta = QtCore.QPoint(0, 0)
		self.__ui.repaint()

	def viewResetZoom(self, event):
		self.__currentViewPane.scale = 1
		self.__ui.repaint()

	def mouseEvent(self, event):
		if self.__currentViewPane.underMouse():
			if event.type() == QtCore.QEvent.MouseButtonPress:
				self.mousePressEventPaper(event)
			elif event.type() == QtCore.QEvent.MouseButtonRelease:
				self.mouseReleaseEventPaper(event)
			else:
				self.mouseMoveEventPaper(event)

			event.accept()

	def wheelEvent(self, event):
		if self.__currentViewPane.underMouse():
			scaleChange = 0
			if event.delta() > 0:
				scaleChange = -0.02
			else:
				scaleChange = 0.02

			self.__currentViewPane.scale += scaleChange
			
			paperPos = event.pos() - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos()
			paperPos.setY(paperPos.y() - self.__ui.mainViewTabs.tabBar().height())
			zoomPos = (paperPos - self.__currentViewPane.getOrigin()) * scaleChange

			self.__currentViewPane.originDelta -= zoomPos
			self.__savedMousePosPaper[self.__currentViewPane] = paperPos

			event.accept()
			self.__ui.repaint()

	def mousePressEventPaper(self, event):
		btn = event.buttons()
		mod = event.modifiers()
		
		cmdDown = mod & QtCore.Qt.ControlModifier
		altDown = mod & QtCore.Qt.AltModifier
		shiftDown = mod & QtCore.Qt.ShiftModifier

		leftDown = btn & QtCore.Qt.LeftButton
		rightDown = btn & QtCore.Qt.RightButton

		paperPos = event.pos() - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos()
		paperPos.setY(paperPos.y() - self.__ui.mainViewTabs.tabBar().height())

	def mouseReleaseEventPaper(self, event):
		btn = event.button()
		mod = event.modifiers()
		
		cmdDown = mod & QtCore.Qt.ControlModifier
		altDown = mod & QtCore.Qt.AltModifier
		shiftDown = mod & QtCore.Qt.ShiftModifier

		leftUp = btn & QtCore.Qt.LeftButton
		rightUp = btn & QtCore.Qt.RightButton

		if self.__state == MOVING_PAPER and leftUp:
			self.__state = IDLE
		else:
			if rightUp:
				self.__onRButtonUpPaper()
			elif leftUp:
				self.__onLButtonUpPaper(event.pos(), shiftDown)
				
		self.__ui.repaint()
		self.setIcon()

	def __onRButtonUpPaper(self):
		if self.__state == DRAWING_NEW_STROKE:
			verts = self.__tmpStroke.getCtrlVerticesAsList()
			if len(verts) == 0:
				self.__state = IDLE
				self.__tmpStroke = None
				return

			self.__state = IDLE
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
			addStrokeCmd.setDoFunction(self.__curChar.addStroke)
			addStrokeCmd.setUndoFunction(self.__curChar.deleteStroke)
			
			self.__cmdStack.doCommand(addStrokeCmd)
			self.__ui.editUndo.setEnabled(True)

			self.__selection[self.__currentViewPane][self.__tmpStroke] = {}
			self.__tmpStroke.selected = True
			self.__currentViewPane.strokesSpecial = []
			self.__tmpStroke = None

			self.setUIStateSelection(True)
			
			for idx in range(0, self.__ui.mainViewTabs.count()):
				self.__ui.mainViewTabs.setTabEnabled(idx, True)
			
			self.__ui.repaint()

	def __onLButtonUpPaper(self, pos, shiftDown):
		adjustedPos = pos - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos()
		adjustedPos.setY(adjustedPos.y() - self.__ui.mainViewTabs.tabBar().height())

		paperPos = self.__currentViewPane.getNormalizedPosition(adjustedPos)
		
		self.__currentViewPane.snapPoints = []
		if self.__state == DRAWING_NEW_STROKE:
			self.__strokePts.append([paperPos.x(), paperPos.y()])
			self.__tmpStroke.generateCtrlVerticesFromPoints(self.__strokePts)
			self.__tmpStroke.updateCtrlVertices()

		elif self.__state == DRAGGING:
			moveCmd = commands.command('moveStrokeCmd')
			selectionCopy = self.__selection[self.__currentViewPane].copy()
			doArgs = {
				'strokes' : selectionCopy, 
				'delta' : self.__moveDelta,
			}

			undoArgs = {
				'strokes' : selectionCopy,
				'delta' : QtCore.QPoint(0, 0) - self.__moveDelta,
			}

			moveCmd.setDoArgs(doArgs)
			moveCmd.setUndoArgs(undoArgs)
			moveCmd.setDoFunction(self.moveSelected)
			moveCmd.setUndoFunction(self.moveSelected)
		
			self.__cmdStack.addToUndo(moveCmd)
			self.__cmdStack.saveCount += 1
			self.__ui.editUndo.setEnabled(True)

			self.__state = IDLE
			self.__moveDelta = QtCore.QPoint(0, 0)
		elif self.__state == ADDING_CTRL_POINT:
			if len(self.__selection[self.__currentViewPane].keys()) > 0:
				for selStroke in self.__selection[self.__currentViewPane].keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
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
						
						self.__cmdStack.addToUndo(addVertexCmd)
						self.__cmdStack.saveCount += 1
						self.__ui.editUndo.setEnabled(True)
						break

			self.__state = IDLE
		elif self.__state == SPLIT_AT_POINT:
			if len(self.__selection[self.__currentViewPane].keys()) > 0:
				for selStroke in self.__selection[self.__currentViewPane].keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
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
						
						self.__cmdStack.doCommand(splitAtCmd)
						self.__ui.editUndo.setEnabled(True)
						break

			self.__state = IDLE
		else:
			if len(self.__selection[self.__currentViewPane].keys()) > 0:
				for selStroke in self.__selection[self.__currentViewPane].keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
						ctrlVertexNum = int((insideInfo[1]+1) / 3)
						ctrlVert = selStroke.getCtrlVertex(ctrlVertexNum)
						
						handleIndex = (insideInfo[1]+1) % 3 +1
						if not shiftDown:
							selStroke.deselectCtrlVerts()
							self.__selection[self.__currentViewPane][selStroke] = {}

						self.__selection[self.__currentViewPane][selStroke][ctrlVert] = handleIndex

						for ctrlVert in self.__selection[self.__currentViewPane][selStroke].keys():
							ctrlVert.selectHandle(self.__selection[self.__currentViewPane][selStroke][ctrlVert])
						
						selStroke.selected = True
						
					else:
						if shiftDown:
							if not self.__selection[self.__currentViewPane].has_key(selStroke):
								self.__selection[self.__currentViewPane][selStroke] = {}
								selStroke.deselectCtrlVerts()

							selStroke.selected = True
						else:
							if self.__selection[self.__currentViewPane].has_key(selStroke):
								del self.__selection[self.__currentViewPane][selStroke]

							selStroke.selected = False
							selStroke.deselectCtrlVerts()

			if len(self.__selection[self.__currentViewPane].keys()) == 0 or shiftDown:
				for selStroke in self.__currentViewPane.strokes:
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[0] == True and (len(self.__selection[self.__currentViewPane].keys()) == 0 or shiftDown):
						if not self.__selection[self.__currentViewPane].has_key(selStroke):
							self.__selection[self.__currentViewPane][selStroke] = {}	
							selStroke.deselectCtrlVerts()

						selStroke.selected = True	
					elif not shiftDown:
						selStroke.selected = False
						selStroke.deselectCtrlVerts()

			if len(self.__selection[self.__currentViewPane].keys()) > 0:
				self.setUIStateSelection(True)
			else:
				self.setUIStateSelection(False)
		
	def setUIStateSelection(self, state):
		self.__ui.strokeAddVertex.setEnabled(state)
		self.__ui.strokeSplitAtPoint.setEnabled(state)
		self.__ui.strokeSave.setEnabled(state)
		self.__ui.editCut.setEnabled(state)
		self.__ui.editCopy.setEnabled(state)
		self.__ui.strokeStraighten.setEnabled(state)
		self.__ui.strokeJoin.setEnabled(state)

	def setStrokeControlVertices(self, args):
		if args.has_key('strokes'):
			selStroke = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVerts = args['ctrlVerts']
		else:
			return

		if len(ctrlVerts) == 0:
			self.__cmdStack.dumpStacks()
			return

		selStroke.setCtrlVerticesFromList(ctrlVerts)
		selStroke.calcCurvePoints()
		self.__ui.repaint()

	def splitStroke(self, args):
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
		
		self.__curChar.addStroke({'stroke': newStroke, 'copyStroke': False})
		self.__ui.repaint()

	def unsplitStroke(self, args):
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
		self.__curChar.deleteStroke({'stroke': delStroke})
		self.__ui.repaint()

	def mouseMoveEventPaper(self, event):
		btn = event.buttons()
		mod = event.modifiers()
		
		leftDown = btn & QtCore.Qt.LeftButton
		rightDown = btn & QtCore.Qt.RightButton

		altDown = mod & QtCore.Qt.AltModifier

		paperPos = event.pos() - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos()
		paperPos.setY(paperPos.y() - self.__ui.mainViewTabs.tabBar().height())
		
		if self.__state == MOVING_PAPER:
			delta = paperPos - self.__savedMousePosPaper[self.__currentViewPane]
			self.__currentViewPane.originDelta += delta
			self.__savedMousePosPaper[self.__currentViewPane] = paperPos
		elif self.__state == DRAGGING:
			normPaperPos = self.__currentViewPane.getNormalizedPosition(paperPos) 
			deltaPos = paperPos - normPaperPos
			
			if self.__snap > 0:
				self.__currentViewPane.snapPoints = self.getSnappedPoints(normPaperPos)
				if len(self.__currentViewPane.snapPoints) > 0 and self.__currentViewPane.snapPoints[0] is not QtCore.QPoint(-1, -1):
					paperPos = self.__currentViewPane.snapPoints[0] + deltaPos
					
			delta = (paperPos - self.__savedMousePosPaper[self.__currentViewPane]) / self.__currentViewPane.scale
			self.__moveDelta += delta
			self.__savedMousePosPaper[self.__currentViewPane] = paperPos
			args = {
				'strokes' : self.__selection[self.__currentViewPane],
				'delta' : delta,
			}
			self.moveSelected(args)
		elif leftDown and altDown and self.__state == IDLE:
			self.__savedMousePosPaper[self.__currentViewPane] = paperPos		
			self.__state = MOVING_PAPER
		elif leftDown and self.__state == IDLE:
			self.__state = DRAGGING
			self.__savedMousePosPaper[self.__currentViewPane] = paperPos
			self.__moveDelta = QtCore.QPoint(0, 0)

		self.__ui.repaint()
		self.setIcon()
	
	def moveSelected(self, args):
		if args.has_key('strokes'):
			selection = args['strokes']
		else:
			return

		if args.has_key('delta'):
			delta = args['delta']
		else:
			return

		for stroke in selection.keys():
			if len(selection[stroke].keys()) > 0:
				for strokePt in selection[stroke].keys():
					strokePt.selectHandle(selection[stroke][strokePt])
					strokePt.selectedHandlePos = strokePt.selectedHandlePos + delta
			else:
				stroke.pos += delta
			
			stroke.calcCurvePoints()

	def getSnappedPoints(self, pos):
		snappedPoints = []

		if len(self.__selection[self.__currentViewPane].keys()) == 1:
			selStroke = self.__selection[self.__currentViewPane].keys()[0]

			if len(self.__selection[self.__currentViewPane][selStroke].keys()) == 1:
				selPoint = self.__selection[self.__currentViewPane][selStroke].keys()[0]
			
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
					snapPoint = self.__ui.guideLines.closestGridPoint(pos)

					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						return snappedPoints

				if self.__snap & SNAP_TO_AXES:
					snapPoint = self.snapToAxes(strokePos, pos, vpos, axisAngles=[0-self.__charSet.angle, -90])

					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						snappedPoints.append(vpos + strokePos)
						return snappedPoints

				if self.__snap & SNAP_TO_NIB_AXES:					
					snapPoint = self.snapToAxes(strokePos, pos, vpos, axisAngles=[40, -40])
					
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
		
		delta = pos - vertPos - strokePos

		vecLength = math.sqrt(float(delta.x())*float(delta.x()) + float(delta.y())*float(delta.y()))

		for angle in axisAngles:

			if delta.x() > 0 and delta.y() < 0:
				angle += 180
			elif delta.x() < 0 and delta.y() < 0:
				angle += 270

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

		for charStroke in self.__curChar.strokes:
			for ctrlVert in charStroke.getCtrlVertices(False):
				if selPoint is not ctrlVert:
					testPoint = ctrlVert.getHandlePos(2)

					if testPoint in testRect:
						snapPt = testPoint
						break

		return snapPt

	def straightenStroke_cb(self, event):
		if len(self.__selection[self.__currentViewPane].keys()) == 1:
			selStroke = self.__selection[self.__currentViewPane].keys()[0]

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
						
			self.__cmdStack.addToUndo(strokeStraightenCmd)
			self.__cmdStack.saveCount += 1
			self.__ui.editUndo.setEnabled(True)

	def joinStrokes_cb(self, event):
		if len(self.__selection[self.__currentViewPane].keys()) > 1:
			strokeJoinCmd = commands.command("strokeJoinCmd")
			selectionCopy = self.__selection[self.__currentViewPane].copy()

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

			self.__cmdStack.addToUndo(strokeJoinCmd)
			self.__cmdStack.saveCount += 1
			self.__ui.editUndo.setEnabled(True)
			self.__ui.repaint()
			
	def joinStrokes(self, strokes):
		strokeList = strokes.keys()
		curStroke = strokeList.pop(0)
		vertList = curStroke.getCtrlVerticesAsList()
		self.__curChar.deleteStroke({'stroke': curStroke})
		if self.__selection[self.__currentViewPane].has_key(curStroke):
			del self.__selection[self.__currentViewPane][curStroke]
			curStroke.selected = False

		while len(strokeList):
			curStroke = strokeList.pop(0)
			curVerts = curStroke.getCtrlVerticesAsList()
			self.__curChar.deleteStroke({'stroke': curStroke})
			if self.__selection[self.__currentViewPane].has_key(curStroke):
				del self.__selection[self.__currentViewPane][curStroke]
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
		self.__curChar.addStroke({'stroke': newStroke, 'copyStroke': False})
		
		self.__selection[self.__currentViewPane][newStroke] = {}
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

		self.__curChar.deleteStroke({'stroke': joinedStroke})
		joinedStroke.selected = False
		if self.__selection[self.__currentViewPane].has_key(joinedStroke):
			del self.__selection[self.__currentViewPane][joinedStroke]

		for selStroke in strokes.keys():
			self.__curChar.addStroke({'stroke': selStroke, 'copyStroke': False})
			self.__selection[self.__currentViewPane][selStroke] = {}
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

		self.__curChar.addStroke({'stroke': joinedStroke, 'copyStroke': False})
		joinedStroke.selected = True
		self.__selection[self.__currentViewPane][joinedStroke] = {}

		for selStroke in strokes.keys():
			self.__curChar.deleteStroke({'stroke': selStroke})
			if self.__selection[self.__currentViewPane].has_key(selStroke):
				del self.__selection[self.__currentViewPane][selStroke]
			selStroke.selected = False

	def charSelected(self, event):
		curCharIdx = self.__ui.charSelectorList.currentRow()
		self.__charSet.setCurrentChar(curCharIdx)
		self.__curChar = self.__charSet.getCurrentChar()
		self.__ui.dwgArea.strokesSpecial = []
		self.__ui.dwgArea.strokes = self.__curChar.strokes
		self.__ui.repaint()
		self.setIcon()

	def strokeSelected(self, event):
		selSavedStroke = self.__charSet.getSavedStroke(self.__ui.strokeSelectorList.currentRow())
		
		self.__ui.strokeDwgArea.strokes = [selSavedStroke]
		self.__ui.repaint()
		self.setIcon()

	def viewTabChanged_cb(self, event):
		self.__currentViewPane = self.__ui.mainViewTabs.currentWidget()

		if self.__currentViewPane == self.__ui.dwgArea:
			self.__ui.strokeNew.setEnabled(True)
		elif self.__currentViewPane == self.__ui.strokeDwgArea:
			self.__ui.strokeNew.setEnabled(False)
	
		if not self.__selection.has_key(self.__currentViewPane):
			self.__selection[self.__currentViewPane] = {}

		self.__ui.viewGuides.setChecked(self.__currentViewPane.drawGuidelines)
		self.__ui.viewNibGuides.setChecked(self.__currentViewPane.drawNibGuides)
		self.__ui.repaint()
		self.setIcon()

	def setIcon(self):
		iconBitmap = self.__currentViewPane.getBitmap()
		if iconBitmap:
			if self.__currentViewPane == self.__ui.dwgArea:
				self.__curChar.bitmapPreview = iconBitmap
				self.__ui.charSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))
			elif self.__currentViewPane == self.__ui.strokeDwgArea:
				if self.__ui.strokeSelectorList.count() > 0:
					self.__ui.strokeSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))

	def guideBaseHeightChanged_cb(self, newValue):
		prevValue = self.__charSet.baseHeight

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'baseHeight',
			'ctrlName' : 'baseHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'baseHeight',
			'ctrlName' : 'baseHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeBaseHeightCmd = commands.command("changeBaseHeightCmd")

		changeBaseHeightCmd.setDoArgs(doArgs)
		changeBaseHeightCmd.setUndoArgs(undoArgs)
		changeBaseHeightCmd.setDoFunction(self.changePropertyControl)
		changeBaseHeightCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeBaseHeightCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def guideCapHeightChanged_cb(self, newValue):
		prevValue = self.__charSet.capHeight

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'capHeight',
			'ctrlName' : 'capHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'capHeight',
			'ctrlName' : 'capHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeCapHeightCmd = commands.command("changeCapHeightCmd")

		changeCapHeightCmd.setDoArgs(doArgs)
		changeCapHeightCmd.setUndoArgs(undoArgs)
		changeCapHeightCmd.setDoFunction(self.changePropertyControl)
		changeCapHeightCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeCapHeightCmd)
		self.__ui.editUndo.setEnabled(True)
		
		self.__ui.repaint()

	def guideAscentChanged_cb(self, newValue):
		prevValue = self.__charSet.ascentHeight

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'ascentHeight',
			'ctrlName' : 'ascentHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'ascentHeight',
			'ctrlName' : 'ascentHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeAscentHeightCmd = commands.command("changeAscentHeightCmd")

		changeAscentHeightCmd.setDoArgs(doArgs)
		changeAscentHeightCmd.setUndoArgs(undoArgs)
		changeAscentHeightCmd.setDoFunction(self.changePropertyControl)
		changeAscentHeightCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeAscentHeightCmd)
		self.__ui.editUndo.setEnabled(True)
		
		self.__ui.repaint()

	def guideDescentChanged_cb(self, newValue):
		prevValue = self.__charSet.descentHeight

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'descentHeight',
			'ctrlName' : 'descentHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'descentHeight',
			'ctrlName' : 'descentHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeDescentHeightCmd = commands.command("changeDescentHeightCmd")

		changeDescentHeightCmd.setDoArgs(doArgs)
		changeDescentHeightCmd.setUndoArgs(undoArgs)
		changeDescentHeightCmd.setDoFunction(self.changePropertyControl)
		changeDescentHeightCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeDescentHeightCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def guideGapHeightChanged_cb(self, newValue):
		prevValue = self.__charSet.gapHeight

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'gapHeight',
			'ctrlName' : 'gapHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'gapHeight',
			'ctrlName' : 'gapHeightSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeGapHeightCmd = commands.command("changeGapHeightCmd")

		changeGapHeightCmd.setDoArgs(doArgs)
		changeGapHeightCmd.setUndoArgs(undoArgs)
		changeGapHeightCmd.setDoFunction(self.changePropertyControl)
		changeGapHeightCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeGapHeightCmd)
		self.__ui.editUndo.setEnabled(True)
		
		self.__ui.repaint()

	def guideAngleChanged_cb(self, newValue):
		prevValue = self.__charSet.angle

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'angle',
			'ctrlName' : 'angleSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'angle',
			'ctrlName' : 'angleSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeAngleCmd = commands.command("changeAngleCmd")

		changeAngleCmd.setDoArgs(doArgs)
		changeAngleCmd.setUndoArgs(undoArgs)
		changeAngleCmd.setDoFunction(self.changePropertyControl)
		changeAngleCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeAngleCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def guideNominalWidthChanged_cb(self, newValue):
		prevValue = self.__charSet.nominalWidth

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'nominalWidth',
			'ctrlName' : 'nominalWidthSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'nominalWidth',
			'ctrlName' : 'nominalWidthSpin',
			'objects' : [self.__charSet, self.__ui.guideLines]
		}

		changeNominalWidthCmd = commands.command("changeNominalWidthCmd")

		changeNominalWidthCmd.setDoArgs(doArgs)
		changeNominalWidthCmd.setUndoArgs(undoArgs)
		changeNominalWidthCmd.setDoFunction(self.changePropertyControl)
		changeNominalWidthCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeNominalWidthCmd)
		self.__ui.editUndo.setEnabled(True)
		
		self.__ui.repaint()
			
	def charWidthChanged_cb(self, newValue):
		prevValue = self.__curChar.width

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'width',
			'ctrlName' : 'charWidthSpin',
			'objects' : [self.__curChar]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'width',
			'ctrlName' : 'charWidthSpin',
			'objects' : [self.__curChar]
		}

		changeWidthCmd = commands.command("changeNominalWidthCmd")

		changeWidthCmd.setDoArgs(doArgs)
		changeWidthCmd.setUndoArgs(undoArgs)
		changeWidthCmd.setDoFunction(self.changePropertyControl)
		changeWidthCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeWidthCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def charLeftSpaceChanged_cb(self, newValue):
		prevValue = self.__curChar.leftSpacing

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'leftSpacing',
			'ctrlName' : 'charLeftSpaceSpin',
			'objects' : [self.__curChar]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'leftSpacing',
			'ctrlName' : 'charLeftSpaceSpin',
			'objects' : [self.__curChar]
		}

		changeLeftSpaceCmd = commands.command("changeLeftSpaceCmd")

		changeLeftSpaceCmd.setDoArgs(doArgs)
		changeLeftSpaceCmd.setUndoArgs(undoArgs)
		changeLeftSpaceCmd.setDoFunction(self.changePropertyControl)
		changeLeftSpaceCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeLeftSpaceCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def charRightSpaceChanged_cb(self, newValue):
		prevValue = self.__curChar.rightSpacing

		if (newValue == prevValue):
			return

		doArgs = {
			'value' : newValue,
			'attrName' : 'rightSpacing',
			'ctrlName' : 'charRightSpaceSpin',
			'objects' : [self.__curChar]
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : 'rightSpacing',
			'ctrlName' : 'charRightSpaceSpin',
			'objects' : [self.__curChar]
		}

		changeRightSpaceCmd = commands.command("changeRightSpaceCmd")

		changeRightSpaceCmd.setDoArgs(doArgs)
		changeRightSpaceCmd.setUndoArgs(undoArgs)
		changeRightSpaceCmd.setDoFunction(self.changePropertyControl)
		changeRightSpaceCmd.setUndoFunction(self.changePropertyControl)

		self.__cmdStack.doCommand(changeRightSpaceCmd)
		self.__ui.editUndo.setEnabled(True)

		self.__ui.repaint()

	def changePropertyControl(self, args):
		if (args.has_key('value')):
			val = args['value']
		else:
			return

		if (args.has_key('attrName')):
			attrName = args['attrName']
		else:
			return

		if (args.has_key('ctrlName')):
			ctrlName = args['ctrlName']
		else:
			return

		if (args.has_key('objects')):
			objectsToSet = args['objects']
		else:
			return

		for objectName in objectsToSet:
			setattr(objectName, attrName, val)
		
		setattr(self.__ui, ctrlName, val)

		self.__ui.repaint()

def distBetweenPts (p0, p1):
	return math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]))