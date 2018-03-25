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
		
		self.fileMenu 	= self.mainMenu.addMenu('&File')
		self.editMenu 	= self.mainMenu.addMenu('&Edit')
		self.viewMenu	= self.mainMenu.addMenu('&View')
		
		self.strokeMenu = self.mainMenu.addMenu('Stro&ke')
		self.helpMenu 	= self.mainMenu.addMenu('&Help')

		self.fileNew = QtGui.QAction("&New", self)
		self.fileNew.setShortcut('Ctrl+N')
		self.fileNew.setStatusTip('Create a new self.character set')
		self.fileNew.triggered.connect(self.__parent.fileNew_cb)
		self.fileNew.setIcon(QtGui.QIcon("icons/script_add.png"))
		self.fileNew.setIconText("New")
		self.fileMenu.addAction(self.fileNew)
		self.toolBar.addAction(self.fileNew)
		
		self.fileOpen = QtGui.QAction("&Open", self)
		self.fileOpen.setShortcut('Ctrl+O')
		self.fileOpen.setStatusTip('Open a character set')
		self.fileOpen.setIcon(QtGui.QIcon("icons/script_go.png"))
		self.fileOpen.setIconText("Open")
		self.fileOpen.setEnabled(False)
		#fileOpen.triggered.connect(self.fileOpen_cb)
		self.fileMenu.addAction(self.fileOpen)
		self.toolBar.addAction(self.fileOpen)
		self.fileMenu.addSeparator()
		
		self.fileSave = QtGui.QAction("&Save", self)
		self.fileSave.setShortcut('Ctrl+S')
		self.fileSave.setStatusTip('Save the character set')
		self.fileSave.setIcon(QtGui.QIcon("icons/script_save.png"))
		#fileSave.triggered.connect(self.fileSave_cb)
		self.fileSave.setIconText("Save")
		self.fileSave.setEnabled(False)
		self.fileMenu.addAction(self.fileSave)
		self.toolBar.addAction(self.fileSave)
		
		self.fileSaveAs = QtGui.QAction("&Save As...", self)
		self.fileSaveAs.setStatusTip('Save the character set with a new name')
		self.fileSaveAs.setIcon(QtGui.QIcon("icons/save_as.png"))
		self.fileSaveAs.setIconText("Save As...")
		self.fileSaveAs.setEnabled(False)
		#fileSaveAs.triggered.connect(self.fileSaveAs_cb)
		self.fileMenu.addAction(self.fileSaveAs)
		self.toolBar.addAction(self.fileSaveAs)
		
		self.fileMenu.addSeparator()
		self.fileQuit = QtGui.QAction("Q&uit", self)
		self.fileQuit.setShortcut('Ctrl+Q')
		self.fileQuit.triggered.connect(self.__parent.quit_cb)
		self.fileMenu.addAction(self.fileQuit)

		self.toolBar.addSeparator()
		
		self.editUndo = QtGui.QAction("Undo", self)
		self.editUndo.setShortcut('Ctrl+Z')
		self.editUndo.setIcon(QtGui.QIcon("icons/arrow_undo.png"))
		self.editUndo.setIconText("Undo")
		self.editUndo.setEnabled(False)
		self.editUndo.triggered.connect(self.__parent.undo_cb)
		self.editMenu.addAction(self.editUndo)
		self.toolBar.addAction(self.editUndo)
		
		self.editRedo = QtGui.QAction("Redo", self)
		self.editRedo.setShortcut('Ctrl+Shift+Z')
		self.editRedo.setIcon(QtGui.QIcon("icons/arrow_redo.png"))
		self.editRedo.setIconText("Redo")
		self.editRedo.setEnabled(False)
		self.editRedo.triggered.connect(self.__parent.redo_cb)
		self.editMenu.addAction(self.editRedo)
		self.toolBar.addAction(self.editRedo)
		
		self.editMenu.addSeparator()
		self.toolBar.addSeparator()
		
		self.editCut = QtGui.QAction("Cut", self)
		self.editCut.setShortcut('Ctrl+X')
		self.editCut.setIcon(QtGui.QIcon("icons/cut.png"))
		self.editCut.setIconText("Cut")
		self.editCut.triggered.connect(self.__parent.cutStrokes_cb)
		self.editMenu.addAction(self.editCut)
		self.toolBar.addAction(self.editCut)
		
		self.editCopy = QtGui.QAction("Copy", self)
		self.editCopy.setShortcut('Ctrl+C')
		self.editCopy.setIcon(QtGui.QIcon("icons/page_white_copy.png"))
		self.editCopy.setIconText("Copy")
		self.editCopy.triggered.connect(self.__parent.copyStrokes_cb)
		self.editMenu.addAction(self.editCopy)
		self.toolBar.addAction(self.editCopy)
		
		self.editPaste = QtGui.QAction("Paste", self)
		self.editPaste.setShortcut('Ctrl+V')
		self.editPaste.setIcon(QtGui.QIcon("icons/page_white_paste.png"))
		self.editPaste.setIconText("Paste")
		self.editPaste.triggered.connect(self.__parent.pasteStrokes_cb)
		self.editMenu.addAction(self.editPaste)
		self.toolBar.addAction(self.editPaste)

		self.toolBar.addSeparator()
		
		self.viewResetOrigin = QtGui.QAction("Reset View Origin", self)
		self.viewResetOrigin.setShortcut('Ctrl+.')
		self.viewResetOrigin.setStatusTip('Reset origin of view')
		self.viewResetOrigin.triggered.connect(self.__parent.viewResetOrigin)
		self.viewMenu.addAction(self.viewResetOrigin)

		self.viewResetZoom = QtGui.QAction("Zoom 100%", self)
		self.viewResetZoom.setShortcut('Ctrl+0')
		self.viewResetZoom.setStatusTip('Reset zoom of view')
		self.viewResetZoom.triggered.connect(self.__parent.viewResetZoom)
		self.viewMenu.addAction(self.viewResetZoom)

		self.viewMenu.addSeparator()

		self.viewGuides = QtGui.QAction("Guidelines", self)
		self.viewGuides.setStatusTip('Toggle guidelines on/off')
		self.viewGuides.triggered.connect(self.__parent.viewToggleGuidelines)
		self.viewGuides.setCheckable(True)
		self.viewGuides.setChecked(True)
		self.viewMenu.addAction(self.viewGuides)
		
		self.viewNibGuides = QtGui.QAction("Nib Guides", self)
		self.viewNibGuides.setStatusTip('Toggle nib guides on/off')
		#viewNibGuides.triggered.connect(self.viewToggleNibGuides_cb)
		self.viewNibGuides.setCheckable(True)
		self.viewNibGuides.setChecked(True)
		self.viewNibGuides.setEnabled(False)
		self.viewMenu.addAction(self.viewNibGuides)
			
		self.viewMenu.addSeparator()
		
		self.viewSnapMenu = self.viewMenu.addMenu('&Snap')
	
		self.viewSnapToAxes = QtGui.QAction("To Axes", self)
		self.viewSnapToAxes.setStatusTip('Toggle snapping to axes')
		#viewSnapToAxes.triggered.connect(self.viewToggleSnapAxially_cb)
		self.viewSnapToAxes.setCheckable(True)
		self.viewSnapToAxes.setChecked(True)
		self.viewSnapToAxes.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToAxes)
		
		self.viewSnapToNibAxes = QtGui.QAction("To Nib Axes", self)
		self.viewSnapToNibAxes.setStatusTip('Toggle snapping to nib axes')
		#viewSnapToNibAxes.triggered.connect(self.viewToggleSnapToNibAxes_cb)
		self.viewSnapToNibAxes.setCheckable(True)
		self.viewSnapToNibAxes.setChecked(False)
		self.viewSnapToNibAxes.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToNibAxes)
		
		self.viewSnapToGrid = QtGui.QAction("To Grid", self)
		self.viewSnapToGrid.setStatusTip('Toggle snapping to grid')
		#viewSnapToGrid.triggered.connect(self.viewToggleSnapToGrid_cb)
		self.viewSnapToGrid.setCheckable(True)
		self.viewSnapToGrid.setChecked(False)
		self.viewSnapMenu.addAction(self.viewSnapToGrid)
		
		self.viewSnapToCtrlPts = QtGui.QAction("To Control Points", self)
		self.viewSnapToCtrlPts.setStatusTip('Toggle snapping to control points')
		#viewSnapToCtrlPts.triggered.connect(self.viewToggleSnapToCtrlPts_cb)
		self.viewSnapToCtrlPts.setCheckable(True)
		self.viewSnapToCtrlPts.setChecked(False)
		self.viewSnapToCtrlPts.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToCtrlPts)
		
		self.viewSnapToStroke = QtGui.QAction("To Strokes", self)
		self.viewSnapToStroke.setStatusTip('Toggle snapping to strokes')
		#viewSnapToStroke.triggered.connect(self.viewToggleSnapToStroke_cb)
		self.viewSnapToStroke.setCheckable(True)
		self.viewSnapToStroke.setChecked(False)
		self.viewSnapToStroke.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToStroke)
		
		self.strokeNew = QtGui.QAction("New", self)
		self.strokeNew.setStatusTip('Create a new stroke')
		self.strokeNew.setIcon(QtGui.QIcon("icons/draw_path.png"))
		self.strokeNew.setIconText("Stroke")
		self.strokeNew.triggered.connect(self.__parent.createNewStroke)
		self.strokeMenu.addAction(self.strokeNew)
		self.toolBar.addAction(self.strokeNew)
		
		self.strokeNewFreehand = QtGui.QAction("New Experimental", self)
		self.strokeNewFreehand.setStatusTip('Create a new stroke freehand')
		self.strokeNewFreehand.setIcon(QtGui.QIcon("icons/draw_calligraphic.png"))
		self.strokeNewFreehand.setIconText("Freehand")
		self.strokeNewFreehand.setEnabled(False)
		#strokeNewFreehand.triggered.connect(self.createNewFreehandStroke_cb)
		self.strokeMenu.addAction(self.strokeNewFreehand)
		self.toolBar.addAction(self.strokeNewFreehand)
		
		self.strokeStraighten = QtGui.QAction("Straighten", self)
		self.strokeStraighten.setStatusTip('Make the stroke straight')
		self.strokeStraighten.setEnabled(False)
		#strokeStraighten.triggered.connect(self.straightenStroke_cb)
		self.strokeMenu.addAction(self.strokeStraighten)
		
		self.strokeJoin = QtGui.QAction("Join", self)
		self.strokeJoin.setStatusTip('Join multiple strokes into one')
		self.strokeJoin.setEnabled(False)
		#strokeJoin.triggered.connect(self.joinStrokes_cb)
		self.strokeMenu.addAction(self.strokeJoin)
		
		self.strokeMenu.addSeparator()
		self.strokeAlignTangents = QtGui.QAction("Set Tangent To Symmetric", self)
		self.strokeAlignTangents.setEnabled(False)
		#strokeAlignTangents.triggered.connect(self.alignTangentsSymmetrical_cb)
		self.strokeMenu.addAction(self.strokeAlignTangents)
		
		self.strokeSmoothTangents = QtGui.QAction("Set Tangent To Smooth", self)
		self.strokeSmoothTangents.setEnabled(False)
		#strokeSmoothTangents.triggered.connect(self.alignTangents_cb)
		self.strokeMenu.addAction(self.strokeSmoothTangents)
		
		self.strokeSharpenTangents = QtGui.QAction("Set Tangent To Sharp", self)
		self.strokeSharpenTangents.setEnabled(False)
		#strokeSharpenTangents.triggered.connect(self.breakTangents_cb)
		self.strokeMenu.addAction(self.strokeSharpenTangents)
		self.strokeMenu.addSeparator()
		
		self.strokeAddVertex = QtGui.QAction("Add Control Point", self)
		self.strokeAddVertex.setEnabled(False)
		#strokeAddVertex.triggered.connect(self.addControlPoint_cb)
		self.strokeMenu.addAction(self.strokeAddVertex)
	
		self.strokeMenu.addSeparator()
		self.strokeSave = QtGui.QAction("Save Stroke", self)
		self.strokeSave.triggered.connect(self.__parent.saveStroke_cb)
		self.strokeMenu.addAction(self.strokeSave)

		self.strokeLoad = QtGui.QAction("Paste From Saved", self)
		self.strokeLoad.triggered.connect(self.__parent.pasteInstanceFromSaved_cb)
		self.strokeMenu.addAction(self.strokeLoad)

		self.strokeSavedEdit = QtGui.QAction("Edit Saved", self)
		self.strokeSavedEdit.setEnabled(False)
		#strokeSavedEdit.triggered.connect(self.editSaved_cb)
		self.strokeMenu.addAction(self.strokeSavedEdit)

		self.strokeSavedEditDone = QtGui.QAction("Done Editing Saved", self)
		self.strokeSavedEditDone.setShortcut('Esc')
		self.strokeSavedEditDone.setEnabled(False)
		#strokeSavedEditDone.triggered.connect(self.editSavedDone_cb)
		self.strokeMenu.addAction(self.strokeSavedEditDone)

		self.helpAbout = QtGui.QAction("About", self)
		self.helpAbout.setEnabled(False)
		#helpAbout.triggered.connect(self.about_cb)
		self.helpMenu.addAction(self.helpAbout)

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