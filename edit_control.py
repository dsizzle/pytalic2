import os
import os.path
import pickle
import sys

from PyQt4 import QtGui, QtCore

import character_set
import commands
import edit_ui
import stroke

gICON_SIZE = 40

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
		self.__undoStack = []
		self.__redoStack = []
		self.__selectedStrokes = []
		self.__charSet = None
		self.__curChar = None

		self.__savedMousePosPaper = None
		self.__movingPaper = None
		self.__drawingNewStroke = False
		
		self.__strokePts = []
		self.__tmpStroke = None

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
		self.__ui.repaint()

	def redo_cb(self, event):
		self.__cmdStack.redo()
		self.__ui.repaint()

	def fileNew_cb(self, event):
		self.__fileName = None
	
		self.__charSet = character_set.character_set()
		
		#self.charSelected()
	 	#self.nibTypeSelected()
		#self.setNibColor({'color': self.__color__})

		self.name = (self.__label + " - Untitled")
		self.__ui.setWindowTitle(self.name)

		self.__ui.strokeSelectorList.clear()

		self.__ui.charSelectorList.setCurrentRow(0)
		self.__curChar = self.__charSet.getCurrentChar()

		self.__cmdStack = commands.commandStack()

	def createNewStroke(self, event):
		self.__drawingNewStroke = True
		self.__strokePts = []
		self.__tmpStroke = stroke.Stroke()
		self.__ui.dwgArea.strokesSpecial.append(self.__tmpStroke)

	def viewToggleGuidelines(self, event):
		self.__ui.dwgArea.drawGuidelines = not self.__ui.dwgArea.drawGuidelines
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
			
		if leftDown and altDown:
			self.__savedMousePosPaper = paperPos
			self.__movingPaper = True

	def mouseReleaseEventPaper(self, event):
		btn = event.button()
		paperPos = self.__ui.dwgArea.getNormalizedPosition(event.pos() - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos())
				
		leftUp = btn & QtCore.Qt.LeftButton
		rightUp = btn & QtCore.Qt.RightButton 

		if self.__movingPaper and leftUp:
			self.__movingPaper = False
		elif self.__drawingNewStroke:
			if rightUp:
				self.__drawingNewStroke = False
				self.__strokePts = []
				# add stroke to char
				self.__curChar.addStroke(self.__tmpStroke)
				self.__ui.dwgArea.strokesSpecial = []
				self.__tmpStroke = None
				self.__ui.repaint()
				iconBitmap = self.__ui.dwgArea.getBitmap()
				if iconBitmap:
					self.__curChar.bitmapPreview = iconBitmap
					self.__ui.charSelectorList.currentItem().setIcon(QtGui.QIcon(self.__curChar.bitmapPreview))

			else:
				self.__strokePts.append([paperPos.x(), paperPos.y()])
				self.__tmpStroke.setCtrlVerticesFromList(self.__strokePts)
				self.__tmpStroke.updateCtrlVertices()

		else:
			if leftUp:
				# if len(self.__selectedStrokes) > 0:
				# 	for stroke in self.__selectedStrokes:
				# 		insideInfo = stroke.insideStroke(paperPos)
				# 		if insideInfo[1] >= 0:
				# 			self.__selectedPoints = 

				for stroke in self.__ui.dwgArea.strokes:
					insideInfo = stroke.insideStroke(paperPos)
					if insideInfo[0] == True:
						stroke.selected = True
						print stroke, stroke.selected
						print insideInfo

					else:
						stroke.selected = False
						print stroke, "unselected"

		self.__ui.repaint()

			
	def mouseMoveEventPaper(self, event):
		paperPos = event.pos() - self.__ui.mainSplitter.pos() - self.__ui.mainWidget.pos()

		if self.__movingPaper:
			delta = paperPos - self.__savedMousePosPaper
			self.__ui.dwgArea.origin += delta
			self.__savedMousePosPaper = paperPos

			self.__ui.repaint()
		elif self.__drawingNewStroke:
			#self.__ui.dwgArea.drawStroke(self.__tmpStroke)
			self.__ui.repaint()
	
	def charSelected(self, event):
		curCharIdx = self.__ui.charSelectorList.currentRow()
		self.__charSet.setCurrentChar(curCharIdx)
		self.__curChar = self.__charSet.getCurrentChar()
		self.__ui.dwgArea.strokesSpecial = []
		self.__ui.dwgArea.strokes = self.__curChar.strokes
		self.__ui.repaint()
