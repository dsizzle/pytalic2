import os
import os.path
import pickle
import sys

from PyQt4 import QtGui, QtCore

import character_set
import editui
import stroke

class editor_controller(): 
	def __init__(self, w, h, label):
		self.__label = label
		self.__ui = editui.edit_interface(self, w, h, label)

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
		self.__charData = None

		self.__savedMousePosPaper = None
		self.__movingPaper = None
		self.__drawingNewStroke = False
		
		#self.__strokePts = []
		self.__tmpStroke = None

		charList = []
		for i in range(32, 128):
			charList.append(str(unichr(i)))

		self.__ui.createUI()
		self.__ui.charSelectorList.addItems(QtCore.QStringList(charList))
		self.mainMenu = None
		self.toolBar = None
		self.fileNew_cb(None)

	def activate(self):
		self.__ui.show()
		self.__ui.activateWindow()
		self.__ui.raise_()
	
	def quit_cb(self, event):
		reply = QtGui.QMessageBox.question(self.__ui, 'Quit Program', "Are you sure you want to quit?", \
			QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.__ui.close()

	def fileNew_cb(self, event):
		self.__fileName = None
	
		self.__charSet = character_set.character_set()
		#self.__ui.dwgArea.setCharData(self.__charSet.currentChar)
		
		#self.charSelected()
	 	#self.nibTypeSelected()
		#self.setNibColor({'color': self.__color__})

		self.name = (self.__label + " - Untitled")
		self.__ui.setWindowTitle(self.name)

		self.__ui.strokeSelectorList.clear()

		self.__ui.charSelectorList.setCurrentRow(0)

		self.__undoStack[:] = []
		self.__redoStack[:] = []

	def createNewStroke(self, event):
		self.__drawingNewStroke = True
		self.__ui.dwgArea.points = []
		self.__tmpStroke = stroke.Stroke()
		self.__ui.dwgArea.strokes.append(self.__tmpStroke)

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
		else:
			event.ignore()

	def wheelEvent(self, event):
		if self.__ui.dwgArea.underMouse():
			if event.delta() > 0:
				self.__ui.dwgArea.scale -= 0.01
			else:
				self.__ui.dwgArea.scale += 0.01

			event.accept()
			self.__ui.repaint()
		else:
			event.ignore()

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
				self.__ui.dwgArea.points = []
				# add stroke to char
				# self.__curChar.addStroke(tmpStroke)
				self.__tmpStroke = None
			else:
				self.__ui.dwgArea.points.append([paperPos.x(), paperPos.y()])
				self.__tmpStroke.setCtrlVerticesFromList(self.__ui.dwgArea.points)
				self.__tmpStroke.updateCtrlVertices()

		else:
			if leftUp:
				for stroke in self.__ui.dwgArea.strokes:
					if stroke.insideStroke(paperPos)[0] == True:
						stroke.selected = True
						print stroke, stroke.selected
						print stroke, "selected"

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
	


