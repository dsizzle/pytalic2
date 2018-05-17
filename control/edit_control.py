import os
import os.path
import math
import pickle
import sys

from PyQt4 import QtGui, QtCore

import mouse_operations
import property_operations
import snap_operations
from model import stroke
import stroke_operations
import vertex_operations

from model import character_set, commands
from view import edit_ui

gICON_SIZE = 40

IDLE = 0
MOVING_PAPER = 1
DRAWING_NEW_STROKE = 2
DRAGGING = 3
ADDING_CTRL_POINT = 4
SPLIT_AT_POINT = 5

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

		self.__state = 0
		
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

		self.__propertyController = property_operations.property_controller(self)
		self.__mouseController = mouse_operations.mouse_controller(self)
		self.__snapController = snap_operations.snap_controller(self)
		self.__strokeController = stroke_operations.stroke_controller(self)
		self.__vertexController = vertex_operations.vertex_controller(self)

		self.mainMenu = None
		self.toolBar = None
		self.fileNew_cb(None)

	def getCommandStack(self):
		return self.__cmdStack

	def getUI(self):
		return self.__ui

	def getCurrentView(self):
		return self.__currentViewPane

	def getSelection(self):
		return self.__selection

	def getCurrentChar(self):
		return self.__curChar

	def getCharacterSet(self):
		return self.__charSet

	def getState(self):
		return self.__state

	def setState(self, newState):
		self.__state = newState

	state = property(getState, setState)

	def getSnapController(self):
		return self.__snapController

	def getStrokeController(self):
		return self.__strokeController

	def activate(self):
		self.__ui.show()
		self.__ui.activateWindow()
		self.__ui.raise_()
	
	def mouseEvent(self, event):
		self.__mouseController.mouseEvent(event)

	def wheelEvent(self, event):
		self.__mouseController.wheelEvent(event)

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

	def createNewStroke_cb(self, event):
		self.__strokeController.createNewStroke()

	def saveStroke_cb(self, event):
		self.__strokeController.saveStroke()
		
	def addControlPoint_cb(self, event):
		self.state = ADDING_CTRL_POINT
		QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

	def splitAtPoint_cb(self, event):
		self.state = SPLIT_AT_POINT
		QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

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
		self.__strokeController.pasteInstanceFromSaved()

	def viewToggleSnapAxially_cb(self, event):
		self.__snapController.toggleSnapAxially()

	def viewToggleSnapToGrid_cb(self, event):
		self.__snapController.toggleSnapToGrid()

	def viewToggleSnapToNibAxes_cb(self, event):
		self.__snapController.toggleSnapToNibAxes()

	def viewToggleSnapToCtrlPts_cb(self, event):
		self.__snapController.toggleSnapToCtrlPts()

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
		
	def setUIStateSelection(self, state):
		self.__ui.strokeAddVertex.setEnabled(state)
		self.__ui.strokeSplitAtPoint.setEnabled(state)
		self.__ui.strokeSave.setEnabled(state)
		self.__ui.editCut.setEnabled(state)
		self.__ui.editCopy.setEnabled(state)
		self.__ui.strokeStraighten.setEnabled(state)
		self.__ui.strokeJoin.setEnabled(state)
		self.__ui.strokeAlignTangents.setEnabled(state)
		self.__ui.strokeSmoothTangents.setEnabled(state)
		self.__ui.strokeSharpenTangents.setEnabled(state)		

	def straightenStroke_cb(self, event):
		self.__strokeController.straightenStroke()

	def joinStrokes_cb(self, event):
		self.__strokeController.joinSelectedStrokes()

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

		self.__propertyController.baseHeightChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		

	def guideCapHeightChanged_cb(self, newValue):
		prevValue = self.__charSet.capHeight
		
		self.__propertyController.capHeightChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		
	def guideAscentChanged_cb(self, newValue):
		prevValue = self.__charSet.ascentHeight
		
		self.__propertyController.ascentChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		
	def guideDescentChanged_cb(self, newValue):
		prevValue = self.__charSet.descentHeight
		
		self.__propertyController.descentChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		
	def guideGapHeightChanged_cb(self, newValue):
		prevValue = self.__charSet.gapHeight

		self.__propertyController.gapHeightChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		
	def guideAngleChanged_cb(self, newValue):
		prevValue = self.__charSet.guideAngle

		self.__propertyController.angleChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		
	def guideNominalWidthChanged_cb(self, newValue):
		prevValue = self.__charSet.nominalWidth

		self.__propertyController.nominalWidthChanged(prevValue, newValue, [self.__charSet, self.__ui.guideLines])
		
	def guideColorChanged_cb(self, newColor):
		self.__ui.guideLines.setLineColor(newColor)
		self.__ui.repaint()

	def charSetNibAngleChanged_cb(self, newValue):
		prevValue = self.__charSet.nibAngle

		self.__propertyController.charSetNibAngleChanged(prevValue, newValue, [self.__charSet, self.__ui.dwgArea.nib])

	def charWidthChanged_cb(self, newValue):
		prevValue = self.__curChar.width

		self.__propertyController.charWidthChanged(prevValue, newValue, [self.__curChar])

	def charLeftSpaceChanged_cb(self, newValue):
		prevValue = self.__curChar.leftSpacing

		self.__propertyController.charLeftSpaceChanged(prevValue, newValue, [self.__curChar])

	def charRightSpaceChanged_cb(self, newValue):
		prevValue = self.__curChar.rightSpacing

		self.__propertyController.charRightSpaceChanged(prevValue, newValue, [self.__curChar])

	def vertBehaviorComboChanged_cb(self, newValue):
		if newValue == 0:
			return

		self.__vertexController.alignTangents(newValue)

	def alignTangentsSymmetrical_cb(self, event):
		self.__vertexController.alignTangentsSymmetrical()

	def alignTangents_cb(self, event):
		self.__vertexController.alignTangents()

	def breakTangents_cb(self, event):
		self.__vertexController.breakTangents()
	
