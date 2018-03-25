#!/usr/bin/python
#

import math
import os
from PyQt4 import QtCore, QtGui

import paper
import splitter

gICON_SIZE = 40
gICON_TEXT_SIZE = 30

class edit_interface(QtGui.QMainWindow):
	def __init__(self, parent, w, h, label):
		QtGui.QMainWindow.__init__(self)
		self.setMouseTracking(True)

		self.resize(w, h)
		self.setWindowTitle(label)
	 	
	 	self.messageDialog = QtGui.QMessageBox()
		self.fileOpenDialog = QtGui.QFileDialog() 
		self.fileSaveDialog = QtGui.QFileDialog() 
		self.__parent = parent
		
		self.dwgArea = None

	def createUI(self):
		self.createMenu()

		wid80 = int(self.width()*.75)
		wid20 = self.width() - wid80
		hgt = self.height() 

		#return
		self.mainWidget = QtGui.QWidget()
		
		self.mainLayout = QtGui.QVBoxLayout()
		self.viewLayout = QtGui.QVBoxLayout()

		self.charSelectorLayout = QtGui.QHBoxLayout()
		self.charSelectorLayout.setMargin(0)
		self.charSelectorLayout.setSpacing(0)
		self.charSelectorLayout.setContentsMargins(0, 0, 0, 0)

		self.charSelectorList = QtGui.QListWidget(self)
		self.charSelectorList.setFlow(QtGui.QListView.LeftToRight)
		self.charSelectorList.resize(self.width(), gICON_SIZE*2)
		self.charSelectorList.setMaximumHeight(gICON_SIZE*2)
		self.charSelectorList.setIconSize(QtCore.QSize(gICON_SIZE, gICON_SIZE))
		self.charSelectorList.currentItemChanged.connect(self.__parent.charSelected)

		self.charSelectorLayout.addWidget(self.charSelectorList, 0, QtCore.Qt.AlignTop)

		self.strokeSelectorLayout = QtGui.QHBoxLayout()
		self.strokeSelectorList = QtGui.QListWidget(self)
		self.strokeSelectorList.setFlow(QtGui.QListView.LeftToRight)
		self.strokeSelectorList.resize(self.width(), gICON_SIZE)
		self.strokeSelectorList.setMaximumHeight(gICON_SIZE*2)
		self.strokeSelectorList.setIconSize(QtCore.QSize(gICON_SIZE, gICON_SIZE))
		self.strokeSelectorLayout.addWidget(self.strokeSelectorList)

		self.mainSplitter = splitter.MySplitter (self.mainWidget)
		self.dwgArea = paper.drawingArea(self.mainSplitter)
		self.dwgArea.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken); 
		self.dwgArea.setLineWidth(2)

		self.toolPane = QtGui.QFrame(self.mainSplitter)
		self.toolPaneLayout = QtGui.QVBoxLayout(self.toolPane)

		self.mainSplitter.addWidget(self.dwgArea)
		self.mainSplitter.addWidget(self.toolPane)
		self.mainSplitter.setMaxPaneWidth(wid20)
		self.mainSplitter.setSizes([wid80, wid20])
		mainSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.mainSplitter.setSizePolicy(mainSizePolicy)

		self.viewLayout.addWidget(self.mainSplitter)
		self.viewLayout.setMargin(0)
		self.viewLayout.setSpacing(0)
		self.viewLayout.setContentsMargins(0, 0, 0, 0)

		mainSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.mainSplitter.setSizePolicy(mainSizePolicy)
	
		self.dwgArea.setSizePolicy(mainSizePolicy)

		self.mainLayout.addLayout(self.charSelectorLayout)
		self.mainLayout.addLayout(self.strokeSelectorLayout)
		self.mainLayout.addLayout(self.viewLayout, 2)

		self.mainWidget.setLayout(self.mainLayout)

		self.setCentralWidget(self.mainWidget)

	def createMenu(self):
		self.mainMenu = self.menuBar()
		self.toolBar = self.addToolBar("main") 
		self.toolBar.resize(self.width(), gICON_SIZE+gICON_TEXT_SIZE)
		self.toolBar.setFloatable(False)
		self.toolBar.setMovable(False)
		self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		
		fileMenu 	= self.mainMenu.addMenu('&File')
		editMenu 	= self.mainMenu.addMenu('&Edit')
		viewMenu	= self.mainMenu.addMenu('&View')
		
		strokeMenu 	= self.mainMenu.addMenu('Stro&ke')
		helpMenu 	= self.mainMenu.addMenu('&Help')

		fileNew = QtGui.QAction("&New", self)
		fileNew.setShortcut('Ctrl+N')
		fileNew.setStatusTip('Create a new character set')
		fileNew.triggered.connect(self.__parent.fileNew_cb)
		fileNew.setIcon(QtGui.QIcon("icons/script_add.png"))
		fileNew.setIconText("New")
		fileMenu.addAction(fileNew)
		self.toolBar.addAction(fileNew)
		
		fileOpen = QtGui.QAction("&Open", self)
		fileOpen.setShortcut('Ctrl+O')
		fileOpen.setStatusTip('Open a character set')
		fileOpen.setIcon(QtGui.QIcon("icons/script_go.png"))
		fileOpen.setIconText("Open")
		#fileOpen.triggered.connect(self.fileOpen_cb)
		fileMenu.addAction(fileOpen)
		self.toolBar.addAction(fileOpen)
		fileMenu.addSeparator()
		
		fileSave = QtGui.QAction("&Save", self)
		fileSave.setShortcut('Ctrl+S')
		fileSave.setStatusTip('Save the character set')
		fileSave.setIcon(QtGui.QIcon("icons/script_save.png"))
		#fileSave.triggered.connect(self.fileSave_cb)
		fileSave.setIconText("Save")
		fileMenu.addAction(fileSave)
		self.toolBar.addAction(fileSave)
		
		fileSaveAs = QtGui.QAction("&Save As...", self)
		fileSaveAs.setStatusTip('Save the character set with a new name')
		fileSaveAs.setIcon(QtGui.QIcon("icons/save_as.png"))
		fileSaveAs.setIconText("Save As...")
		#fileSaveAs.triggered.connect(self.fileSaveAs_cb)
		fileMenu.addAction(fileSaveAs)
		self.toolBar.addAction(fileSaveAs)
		
		fileMenu.addSeparator()
		fileQuit = QtGui.QAction("Q&uit", self)
		fileQuit.setShortcut('Ctrl+Q')
		fileQuit.triggered.connect(self.__parent.quit_cb)
		fileMenu.addAction(fileQuit)

		self.toolBar.addSeparator()
		
		editUndo = QtGui.QAction("Undo", self)
		editUndo.setShortcut('Ctrl+Z')
		editUndo.setIcon(QtGui.QIcon("icons/arrow_undo.png"))
		editUndo.setIconText("Undo")
		editUndo.triggered.connect(self.__parent.undo_cb)
		editMenu.addAction(editUndo)
		self.toolBar.addAction(editUndo)
		
		editRedo = QtGui.QAction("Redo", self)
		editRedo.setShortcut('Ctrl+Shift+Z')
		editRedo.setIcon(QtGui.QIcon("icons/arrow_redo.png"))
		editRedo.setIconText("Redo")
		editRedo.triggered.connect(self.__parent.redo_cb)
		editMenu.addAction(editRedo)
		self.toolBar.addAction(editRedo)
		
		editMenu.addSeparator()
		self.toolBar.addSeparator()
		
		editCut = QtGui.QAction("Cut", self)
		editCut.setShortcut('Ctrl+X')
		editCut.setIcon(QtGui.QIcon("icons/cut.png"))
		editCut.setIconText("Cut")
		editCut.triggered.connect(self.__parent.cutStrokes_cb)
		editMenu.addAction(editCut)
		self.toolBar.addAction(editCut)
		
		editCopy = QtGui.QAction("Copy", self)
		editCopy.setShortcut('Ctrl+C')
		editCopy.setIcon(QtGui.QIcon("icons/page_white_copy.png"))
		editCopy.setIconText("Copy")
		editCopy.triggered.connect(self.__parent.copyStrokes_cb)
		editMenu.addAction(editCopy)
		self.toolBar.addAction(editCopy)
		
		editPaste = QtGui.QAction("Paste", self)
		editPaste.setShortcut('Ctrl+V')
		editPaste.setIcon(QtGui.QIcon("icons/page_white_paste.png"))
		editPaste.setIconText("Paste")
		editPaste.triggered.connect(self.__parent.pasteStrokes_cb)
		editMenu.addAction(editPaste)
		self.toolBar.addAction(editPaste)

		self.toolBar.addSeparator()
		
		viewResetOrigin = QtGui.QAction("Reset View Origin", self)
		viewResetOrigin.setShortcut('Ctrl+.')
		viewResetOrigin.setStatusTip('Reset origin of view')
		viewResetOrigin.triggered.connect(self.__parent.viewResetOrigin)
		viewMenu.addAction(viewResetOrigin)

		viewResetZoom = QtGui.QAction("Zoom 100%", self)
		viewResetZoom.setShortcut('Ctrl+0')
		viewResetZoom.setStatusTip('Reset zoom of view')
		viewResetZoom.triggered.connect(self.__parent.viewResetZoom)
		viewMenu.addAction(viewResetZoom)

		viewMenu.addSeparator()

		viewGuides = QtGui.QAction("Guidelines", self)
		viewGuides.setStatusTip('Toggle guidelines on/off')
		viewGuides.triggered.connect(self.__parent.viewToggleGuidelines)
		viewGuides.setCheckable(True)
		viewGuides.setChecked(True)
		viewMenu.addAction(viewGuides)
		
		viewNibGuides = QtGui.QAction("Nib Guides", self)
		viewNibGuides.setStatusTip('Toggle nib guides on/off')
		#viewNibGuides.triggered.connect(self.viewToggleNibGuides_cb)
		viewNibGuides.setCheckable(True)
		viewNibGuides.setChecked(True)
		viewMenu.addAction(viewNibGuides)
			
		viewMenu.addSeparator()
		
		viewSnapMenu = viewMenu.addMenu('&Snap')
	
		viewSnapToAxes = QtGui.QAction("To Axes", self)
		viewSnapToAxes.setStatusTip('Toggle snapping to axes')
		#viewSnapToAxes.triggered.connect(self.viewToggleSnapAxially_cb)
		viewSnapToAxes.setCheckable(True)
		viewSnapToAxes.setChecked(True)
		viewSnapMenu.addAction(viewSnapToAxes)
		
		viewSnapToNibAxes = QtGui.QAction("To Nib Axes", self)
		viewSnapToNibAxes.setStatusTip('Toggle snapping to nib axes')
		#viewSnapToNibAxes.triggered.connect(self.viewToggleSnapToNibAxes_cb)
		viewSnapToNibAxes.setCheckable(True)
		viewSnapToNibAxes.setChecked(False)
		viewSnapMenu.addAction(viewSnapToNibAxes)
		
		viewSnapToGrid = QtGui.QAction("To Grid", self)
		viewSnapToGrid.setStatusTip('Toggle snapping to grid')
		#viewSnapToGrid.triggered.connect(self.viewToggleSnapToGrid_cb)
		viewSnapToGrid.setCheckable(True)
		viewSnapToGrid.setChecked(False)
		viewSnapMenu.addAction(viewSnapToGrid)
		
		viewSnapToCtrlPts = QtGui.QAction("To Control Points", self)
		viewSnapToCtrlPts.setStatusTip('Toggle snapping to control points')
		#viewSnapToCtrlPts.triggered.connect(self.viewToggleSnapToCtrlPts_cb)
		viewSnapToCtrlPts.setCheckable(True)
		viewSnapToCtrlPts.setChecked(False)
		viewSnapMenu.addAction(viewSnapToCtrlPts)
		
		viewSnapToStroke = QtGui.QAction("To Strokes", self)
		viewSnapToStroke.setStatusTip('Toggle snapping to strokes')
		#viewSnapToStroke.triggered.connect(self.viewToggleSnapToStroke_cb)
		viewSnapToStroke.setCheckable(True)
		viewSnapToStroke.setChecked(False)
		viewSnapMenu.addAction(viewSnapToStroke)
		
		strokeNew = QtGui.QAction("New", self)
		strokeNew.setStatusTip('Create a new stroke')
		strokeNew.setIcon(QtGui.QIcon("icons/draw_path.png"))
		strokeNew.setIconText("Stroke")
		strokeNew.triggered.connect(self.__parent.createNewStroke)
		strokeMenu.addAction(strokeNew)
		self.toolBar.addAction(strokeNew)
		
		strokeNewFreehand = QtGui.QAction("New Experimental", self)
		strokeNewFreehand.setStatusTip('Create a new stroke freehand')
		strokeNewFreehand.setIcon(QtGui.QIcon("icons/draw_calligraphic.png"))
		strokeNewFreehand.setIconText("Freehand")
		#strokeNewFreehand.triggered.connect(self.createNewFreehandStroke_cb)
		strokeMenu.addAction(strokeNewFreehand)
		self.toolBar.addAction(strokeNewFreehand)
		
		strokeStraighten = QtGui.QAction("Straighten", self)
		strokeStraighten.setStatusTip('Make the stroke straight')
		#strokeStraighten.triggered.connect(self.straightenStroke_cb)
		strokeMenu.addAction(strokeStraighten)
		
		strokeJoin = QtGui.QAction("Join", self)
		strokeJoin.setStatusTip('Join multiple strokes into one')
		#strokeJoin.triggered.connect(self.joinStrokes_cb)
		strokeMenu.addAction(strokeJoin)
		
		strokeMenu.addSeparator()
		strokeAlignTangents = QtGui.QAction("Set Tangent To Symmetric", self)
		#strokeAlignTangents.triggered.connect(self.alignTangentsSymmetrical_cb)
		strokeMenu.addAction(strokeAlignTangents)
		
		strokeSmoothTangents = QtGui.QAction("Set Tangent To Smooth", self)
		#strokeSmoothTangents.triggered.connect(self.alignTangents_cb)
		strokeMenu.addAction(strokeSmoothTangents)
		
		strokeSharpenTangents = QtGui.QAction("Set Tangent To Sharp", self)
		#strokeSharpenTangents.triggered.connect(self.breakTangents_cb)
		strokeMenu.addAction(strokeSharpenTangents)
		strokeMenu.addSeparator()
		
		strokeAddVertex = QtGui.QAction("Add Control Point", self)
		#strokeAddVertex.triggered.connect(self.addControlPoint_cb)
		strokeMenu.addAction(strokeAddVertex)
	
		strokeMenu.addSeparator()
		strokeSave = QtGui.QAction("Save Stroke", self)
		strokeSave.triggered.connect(self.__parent.saveStroke_cb)
		strokeMenu.addAction(strokeSave)

		strokeLoad = QtGui.QAction("Paste From Saved", self)
		strokeLoad.triggered.connect(self.__parent.pasteInstanceFromSaved_cb)
		strokeMenu.addAction(strokeLoad)

		strokeSavedEdit = QtGui.QAction("Edit Saved", self)
		#strokeSavedEdit.triggered.connect(self.editSaved_cb)
		strokeMenu.addAction(strokeSavedEdit)

		strokeSavedEditDone = QtGui.QAction("Done Editing Saved", self)
		strokeSavedEditDone.setShortcut('Esc')
		#strokeSavedEditDone.triggered.connect(self.editSavedDone_cb)
		strokeMenu.addAction(strokeSavedEditDone)

		helpAbout = QtGui.QAction("About", self)
		#helpAbout.triggered.connect(self.about_cb)
		helpMenu.addAction(helpAbout)

	def mouseMoveEvent(self, event):
		self.__parent.mouseEvent(event)

	def mousePressEvent(self, event):
		self.__parent.mouseEvent(event)

	def mouseReleaseEvent(self, event):
		self.__parent.mouseEvent(event)

	def wheelEvent(self, event):
		self.__parent.wheelEvent(event)

	def paintEvent(self, event):
		QtGui.QMainWindow.paintEvent(self,event)

	def closeEvent(self, event):
		self.__parent.quit_cb(event)