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

		self.__savedMousePosPaper = None
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
		blankPixmap = QtGui.QPixmap(gICON_SIZE, gICON_SIZE)
		blankPixmap.fill(QtGui.QColor(240, 240, 240))
		for idx in range(0, self.__ui.charSelectorList.count()):
			self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(blankPixmap))
		self.__ui.dwgArea.bitmapSize = gICON_SIZE

		self.mainMenu = None
		self.toolBar = None
		self.fileNew_cb(None)

	def activate(self):
		self.__ui.show()
		self.__ui.activateWindow()
		self.__ui.raise_()
	
	def quit_cb(self, event):
		if self.__cmdStack.undoIsEmpty():
			self.__ui.close()
		else:
			reply = self.__ui.messageDialog.question(self.__ui, 'Quit Program', "Are you sure you want to quit?", \
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
		
		self.name = (self.__label + " - Untitled")
		self.__ui.setWindowTitle(self.name)

		self.__ui.strokeSelectorList.clear()

		self.__ui.charSelectorList.setCurrentRow(0)
		self.__curChar = self.__charSet.getCurrentChar()

		self.__cmdStack = commands.commandStack()
		self.__ui.editUndo.setEnabled(False)
		self.__ui.editRedo.setEnabled(False)

	def fileSaveAs_cb(self, event):
		fileName = self.__ui.fileSaveDialog.getSaveFileName(self.__ui,
		     "Save Character Set", self.__dirName, "Character Set Files (*.cs)")
			
		if (fileName):
			(self.__dirName, self.__fileName) = os.path.split(str(fileName))
				
			self.save(self.__fileName)
			self.__ui.setWindowTitle(self.__label + " - " + self.__fileName)

	def fileSave_cb(self, event):
		if self.__fileName and os.path.isfile(self.__fileName):
			self.save(self.__fileName)
		else:
			self.fileSaveAs_cb(event)

	def fileOpen_cb(self):
	 	fileName = None
		fileName = self.__ui.fileOpenDialog.getOpenFileName(self.__ui,
		     "Open Character Set", self.__dirName, "Character Set Files (*.cs)")

		if (fileName):
			self.load(fileName)

			(self.__dirName, self.__fileName) = os.path.split(str(fileName))

			self.__ui.setWindowTitle(self.__label + " - " + self.__fileName)
		
	 		self.__ui.strokeSelectorList.clear()

			self.__ui.charSelectorList.setCurrentRow(0)
			
			self.__selection = {}
	 		self.__ui.repaint()
		
			self.__cmdStack.clear()

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
		self.__strokePts = []
		self.__tmpStroke = stroke.Stroke()
		self.__ui.dwgArea.strokesSpecial.append(self.__tmpStroke)

	def saveStroke_cb(self, event):
		selectedStrokes = []
		instances = []

		for selStroke in self.__selection.keys():
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
			bitmap = self.__ui.dwgArea.drawIcon(None, [selStroke])
			self.__ui.strokeSelectorList.addItem(str(firstItem+i))
			curItem = self.__ui.strokeSelectorList.item(firstItem+i)
			self.__ui.strokeSelectorList.setCurrentRow(firstItem+i)
			curItem.setIcon(QtGui.QIcon(bitmap))
			self.__charSet.saveStroke(selStroke)
			curChar = self.__charSet.getCurrentChar()
			deletedStrokes.append(selStroke)
			curChar.deleteStroke({'stroke' : selStroke})
			selStroke = self.__charSet.getSavedStroke(firstItem+i)
			instances[i].setStroke(selStroke)
			curChar.addStrokeInstance(instances[i])
			if not self.__selection.has_key(selStroke):
				self.__selection[selStroke] = {}
				selStroke.deselectCtrlVerts()

			selStroke.selected = True
			i += 1
				
		for selStroke in deletedStrokes:
			if self.__selection.has_key(selStroke):
				del self.__selection[selStroke]

			selStroke.selected = False	

		self.__ui.strokeLoad.setEnabled(True)
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
			if not self.__selection.has_key(selStroke):
				self.__selection[selStroke] = {}
				selStroke.deselectCtrlVerts()
			
			selStroke.selected = True

		if self.__ui.strokeSelectorList.count() == 0:
			self.__ui.strokeLoad.setEnabled(False)

		self.setUIStateSelection(True)
		
	def addControlPoint_cb(self, event):
		self.__state = ADDING_CTRL_POINT

	def splitAtPoint_cb(self, event):
		self.__state = SPLIT_AT_POINT

	def cutStrokes_cb(self, event):
		cutStrokesCmd = commands.command('cutStrokesCmd')
		charIndex = self.__charSet.getCurrentCharIndex()

		doArgs = {
			'strokes' : self.__selection.copy(),
			'charIndex' : charIndex,
		}

		undoArgs = {
			'strokes' : self.__selection.copy(),
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
			if self.__selection.has_key(selStroke):
				del self.__selection[selStroke]
			selStroke.selected = False

		self.__ui.editPaste.setEnabled(True)
		self.__ui.repaint()	

	def copyStrokes_cb(self, event):
		copyStrokesCmd = commands.command('copyStrokesCmd')
		charIndex = self.__charSet.getCurrentCharIndex()

		doArgs = {
			'strokes' : self.__selection.copy(),
			'charIndex' : charIndex,
		}

		undoArgs = {
			'strokes' : self.__selection.copy(),
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
		
		for selStroke in self.__selection.keys():
			selStroke.selected = False

		self.__selection = {}

		for selStroke in strokesToPaste:
			if copyStrokes:
				pasteStroke = stroke.Stroke(fromStroke=selStroke)
			else:
				pasteStroke = selStroke

			self.__selection[pasteStroke] = {}
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
		self.__selection[strokeInstance] = {}
		
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
		if self.__selection.has_key(strokeToDel):
			del self.__selection[strokeToDel]

		self.__ui.dwgArea.repaint()

	def viewToggleSnapAxially_cb(self, event):
		self.__snap |= SNAP_TO_AXES

	def viewToggleSnapToGrid_cb(self, event):
		self.__snap |= SNAP_TO_GRID

	def viewToggleGuidelines(self, event):
		self.__ui.dwgArea.drawGuidelines = not self.__ui.dwgArea.drawGuidelines
		self.__ui.repaint()

	def viewResetOrigin(self, event):
		self.__ui.dwgArea.originDelta = QtCore.QPoint(0, 0)
		self.__ui.repaint()

	def viewResetZoom(self, event):
		self.__ui.dwgArea.scale = 1
		self.__ui.repaint()

	def mouseEvent(self, event):
		if self.__ui.dwgArea.underMouse():
			if event.type() == QtCore.QEvent.MouseButtonPress:
				self.mousePressEventPaper(event)
			elif event.type() == QtCore.QEvent.MouseButtonRelease:
				self.mouseReleaseEventPaper(event)
			else:
				self.mouseMoveEventPaper(event)

			event.accept()

	def wheelEvent(self, event):
		if self.__ui.dwgArea.underMouse():
			if event.delta() > 0:
				self.__ui.dwgArea.scale -= 0.01
			else:
				self.__ui.dwgArea.scale += 0.01

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

			self.__selection[self.__tmpStroke] = {}
			self.__tmpStroke.selected = True
			self.__ui.dwgArea.strokesSpecial = []
			self.__tmpStroke = None

			self.setUIStateSelection(True)
			self.__ui.repaint()

	def __onLButtonUpPaper(self, pos, shiftDown):
		paperPos = self.__ui.dwgArea.getNormalizedPosition(pos - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos())

		self.__ui.dwgArea.snapPoints = []
		if self.__state == DRAWING_NEW_STROKE:
			self.__strokePts.append([paperPos.x(), paperPos.y()])
			self.__tmpStroke.generateCtrlVerticesFromPoints(self.__strokePts)
			self.__tmpStroke.updateCtrlVertices()

		elif self.__state == DRAGGING:
			moveCmd = commands.command('moveStrokeCmd')
			selectionCopy = self.__selection.copy()
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
			self.__ui.editUndo.setEnabled(True)

			self.__state = IDLE
			self.__moveDelta = QtCore.QPoint(0, 0)
		elif self.__state == ADDING_CTRL_POINT:
			if len(self.__selection.keys()) > 0:
				for selStroke in self.__selection.keys():
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
						self.__ui.editUndo.setEnabled(True)
						break

			self.__state = IDLE
		elif self.__state == SPLIT_AT_POINT:
			if len(self.__selection.keys()) > 0:
				for selStroke in self.__selection.keys():
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
			if len(self.__selection.keys()) > 0:
				for selStroke in self.__selection.keys():
					insideInfo = selStroke.insideStroke(paperPos)
					
					if insideInfo[1] >= 0:
						ctrlVertexNum = int((insideInfo[1]+1) / 3)
						ctrlVert = selStroke.getCtrlVertex(ctrlVertexNum)
						
						handleIndex = (insideInfo[1]+1) % 3 +1
						if not shiftDown:
							selStroke.deselectCtrlVerts()
							self.__selection[selStroke] = {}

						self.__selection[selStroke][ctrlVert] = handleIndex

						for ctrlVert in self.__selection[selStroke].keys():
							ctrlVert.selectHandle(self.__selection[selStroke][ctrlVert])
						
						selStroke.selected = True
						
					else:
						if shiftDown:
							if not self.__selection.has_key(selStroke):
								self.__selection[selStroke] = {}
								selStroke.deselectCtrlVerts()

							selStroke.selected = True
						else:
							if self.__selection.has_key(selStroke):
								del self.__selection[selStroke]

							selStroke.selected = False
							selStroke.deselectCtrlVerts()

			if len(self.__selection.keys()) == 0 or shiftDown:
				for selStroke in self.__ui.dwgArea.strokes:
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[0] == True and (len(self.__selection.keys()) == 0 or shiftDown):
						if not self.__selection.has_key(selStroke):
							self.__selection[selStroke] = {}	
							selStroke.deselectCtrlVerts()

						selStroke.selected = True	
					elif not shiftDown:
						selStroke.selected = False
						selStroke.deselectCtrlVerts()

			if len(self.__selection.keys()) > 0:
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
			
		if self.__state == MOVING_PAPER:
			delta = paperPos - self.__savedMousePosPaper
			self.__ui.dwgArea.originDelta += delta
			self.__savedMousePosPaper = paperPos
		elif self.__state == DRAGGING:
			normPaperPos = self.__ui.dwgArea.getNormalizedPosition(paperPos)
			deltaPos = paperPos - normPaperPos
			
			if self.__snap > 0:
				self.__ui.dwgArea.snapPoints = self.getSnappedPoints(normPaperPos)
				if len(self.__ui.dwgArea.snapPoints) > 0 and self.__ui.dwgArea.snapPoints[0] is not QtCore.QPoint(-1, -1):
					paperPos = self.__ui.dwgArea.snapPoints[0] + deltaPos
					
			delta = paperPos - self.__savedMousePosPaper
			self.__moveDelta += delta
			self.__savedMousePosPaper = paperPos
			args = {
				'strokes' : self.__selection,
				'delta' : delta,
			}
			self.moveSelected(args)
		elif leftDown and altDown and self.__state == IDLE:
			self.__savedMousePosPaper = paperPos		
			self.__state = MOVING_PAPER
		elif leftDown and self.__state == IDLE:
			self.__state = DRAGGING
			self.__savedMousePosPaper = paperPos
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

		if len(self.__selection.keys()) == 1:
			selStroke = self.__selection.keys()[0]

			if len(self.__selection[selStroke].keys()) == 1:
				selPoint = self.__selection[selStroke].keys()[0]
			
				if self.__snap & SNAP_TO_GRID:
					snapPoint = self.__ui.dwgArea.getGuidelines().closestGridPoint(pos)

					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)

				elif self.__snap & SNAP_TO_AXES:
					ctrlVerts = selStroke.getCtrlVertices(make_copy=False)

					vertIndex = ctrlVerts.index(selPoint)
					
					if selPoint.isKnotSelected():
						if vertIndex == 0:
							vertIndex += 1
						else:
							vertIndex -= 1
					
					vpos = ctrlVerts[vertIndex].getHandlePos(2)
					
					snapPoint = self.__ui.dwgArea.getGuidelines().snapToAxes(selStroke.getPos(), pos, vpos)
					
					if snapPoint != QtCore.QPoint(-1, -1):
						snappedPoints.append(snapPoint)
						snappedPoints.append(vpos + selStroke.getPos())
					
		return snappedPoints

	def straightenStroke_cb(self, event):
		if len(self.__selection.keys()) == 1:
			selStroke = self.__selection.keys()[0]

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
			self.__ui.editUndo.setEnabled(True)

	def joinStrokes_cb(self, event):
		if len(self.__selection.keys()) > 1:
			strokeJoinCmd = commands.command("strokeJoinCmd")
			selectionCopy = self.__selection.copy()

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
			self.__ui.editUndo.setEnabled(True)
			self.__ui.repaint()
			
	def joinStrokes(self, strokes):
		strokeList = strokes.keys()
		curStroke = strokeList.pop(0)
		vertList = curStroke.getCtrlVerticesAsList()
		self.__curChar.deleteStroke({'stroke': curStroke})
		if self.__selection.has_key(curStroke):
			del self.__selection[curStroke]
			curStroke.selected = False

		while len(strokeList):
			curStroke = strokeList.pop(0)
			curVerts = curStroke.getCtrlVerticesAsList()
			self.__curChar.deleteStroke({'stroke': curStroke})
			if self.__selection.has_key(curStroke):
				del self.__selection[curStroke]
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
		
		self.__selection[newStroke] = {}
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
		if self.__selection.has_key(joinedStroke):
			del self.__selection[joinedStroke]

		for selStroke in strokes.keys():
			self.__curChar.addStroke({'stroke': selStroke, 'copyStroke': False})
			self.__selection[selStroke] = {}
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
		self.__selection[joinedStroke] = {}

		for selStroke in strokes.keys():
			self.__curChar.deleteStroke({'stroke': selStroke})
			if self.__selection.has_key(selStroke):
				del self.__selection[selStroke]
			selStroke.selected = False

	def charSelected(self, event):
		curCharIdx = self.__ui.charSelectorList.currentRow()
		self.__charSet.setCurrentChar(curCharIdx)
		self.__curChar = self.__charSet.getCurrentChar()
		self.__ui.dwgArea.strokesSpecial = []
		self.__ui.dwgArea.strokes = self.__curChar.strokes
		self.__ui.repaint()
		self.setIcon()

	def setIcon(self):
		iconBitmap = self.__ui.dwgArea.getBitmap()
		if iconBitmap:
			self.__curChar.bitmapPreview = iconBitmap
			self.__ui.charSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))

def distBetweenPts (p0, p1):
	return math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]))