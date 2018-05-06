#!/usr/bin/python
#

import math
import os
from PyQt4 import QtCore, QtGui

import guides
import paper
import splitter
import widgets_qt

gICON_SIZE = 40
gICON_TEXT_SIZE = 30

class edit_interface(QtGui.QMainWindow):
	def __init__(self, parent, w, h, label):
		QtGui.QMainWindow.__init__(self)
		self.setMouseTracking(True)
		self.setFocusPolicy(QtCore.Qt.ClickFocus)

		self.resize(w, h)
		self.setWindowTitle(label)
	 	
	 	self.messageDialog = QtGui.QMessageBox()
		self.fileOpenDialog = QtGui.QFileDialog() 
		self.fileSaveDialog = QtGui.QFileDialog() 
		self.__parent = parent
		
		self.dwgArea = None
		self.guideLines = None

	def createUI(self):
		self.createMenu()

		wid80 = int(self.width()*.75)
		wid20 = self.width() - wid80
		hgt = self.height() 

		#return
		self.mainWidget = QtGui.QWidget()
		self.mainSplitter = splitter.MySplitter (self.mainWidget)

		self.mainLayout = QtGui.QVBoxLayout()
		self.viewLayout = QtGui.QHBoxLayout()

		self.charSelectorLayout = QtGui.QHBoxLayout()
		self.charSelectorLayout.setMargin(0)
		self.charSelectorLayout.setSpacing(0)
		self.charSelectorLayout.setContentsMargins(0, 0, 0, 0)

		self.charSelectorList = QtGui.QListWidget(self.mainWidget)
		self.charSelectorList.setFlow(QtGui.QListView.LeftToRight)
		self.charSelectorList.resize(self.width(), gICON_SIZE*1.75)
		self.charSelectorList.setMaximumHeight(gICON_SIZE*1.75)
		self.charSelectorList.setIconSize(QtCore.QSize(gICON_SIZE, gICON_SIZE))
		self.charSelectorList.currentItemChanged.connect(self.__parent.charSelected)
		self.charSelectorLayout.addWidget(self.charSelectorList, 0, QtCore.Qt.AlignTop)

		#self.strokeSelectorLayout = QtGui.QVBoxLayout()
		self.strokeSelectorList = QtGui.QListWidget(self)
		#self.strokeSelectorList.setFlow(QtGui.QListView.LeftToRight)
		self.strokeSelectorList.resize(gICON_SIZE*1.5, self.height())
		self.strokeSelectorList.setMaximumWidth(gICON_SIZE*1.5)
		self.strokeSelectorList.setIconSize(QtCore.QSize(gICON_SIZE, gICON_SIZE))
		self.strokeSelectorList.currentItemChanged.connect(self.__parent.strokeSelected)
		self.viewLayout.addWidget(self.strokeSelectorList)
		#self.strokeSelectorLayout.addWidget(self.strokeSelectorList)
		
		self.dwgArea = paper.drawingArea(self.mainSplitter)
		self.dwgArea.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
		self.dwgArea.setLineWidth(2)

		self.toolPane = QtGui.QFrame(self.mainSplitter)
		self.toolPaneLayout = QtGui.QVBoxLayout(self.toolPane)
		self.toolPaneLayout.addWidget(self.charSelectorList)

		self.strokeDwgArea = paper.drawingArea(self)
		self.strokeDwgArea.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
		self.strokeDwgArea.setLineWidth(2)
		self.strokeDwgArea.drawGuidelines = False
		self.strokeDwgArea.drawNibGuides = False

		self.charSetPropFrame = QtGui.QFrame(self.toolPane);
		self.charSetPropLayout = QtGui.QFormLayout(self.charSetPropFrame)
		self.mainCharSetPropLabel = QtGui.QLabel(self.charSetPropFrame)
		self.mainCharSetPropLabel.setText("Note: All units are nib-widths.")
		self.charSetPropLayout.addRow(self.mainCharSetPropLabel)

		self.baseHeightLabel = QtGui.QLabel(self.charSetPropFrame)
		self.baseHeightLabel.setText("X-height:")
		
		self.baseHeightSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.baseHeightSpin.setMinimum(1.0)
		self.baseHeightSpin.setMaximum(10.0)
		self.baseHeightSpin.setValue(1.0)
		self.baseHeightSpin.setWrapping(True)
		self.baseHeightSpin.setDecimals(1)
		self.baseHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.baseHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.guideBaseHeightChanged_cb)
		
		self.capHeightLabel = QtGui.QLabel(self.charSetPropFrame)
		self.capHeightLabel.setText("Capital height:")
		
		self.capHeightSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.capHeightSpin.setMinimum(0.5)
		self.capHeightSpin.setMaximum(10)
		self.capHeightSpin.setValue(2.0)
		self.capHeightSpin.setWrapping(True)
		self.capHeightSpin.setDecimals(1)
		self.capHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.capHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.guideCapHeightChanged_cb)
		
		self.ascentHeightLabel = QtGui.QLabel(self.charSetPropFrame)
		self.ascentHeightLabel.setText("Ascent height:")
		
		self.ascentHeightSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.ascentHeightSpin.setMinimum(1)
		self.ascentHeightSpin.setMaximum(10)
		self.ascentHeightSpin.setValue(1)
		self.ascentHeightSpin.setWrapping(True)
		self.ascentHeightSpin.setDecimals(1)
		self.ascentHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.ascentHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.guideAscentChanged_cb)
		
		self.descentHeightLabel = QtGui.QLabel(self.charSetPropFrame)
		self.descentHeightLabel.setText("Descent height:")
		
		self.descentHeightSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.descentHeightSpin.setMinimum(1)
		self.descentHeightSpin.setMaximum(10)
		self.descentHeightSpin.setValue(1)
		self.descentHeightSpin.setWrapping(True)
		self.descentHeightSpin.setDecimals(1)
		self.descentHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.descentHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.guideDescentChanged_cb)
				
		self.angleLabel = QtGui.QLabel(self.charSetPropFrame)
		self.angleLabel.setText("Guide angle:")
		
		self.angleSpin = QtGui.QSpinBox(self.charSetPropFrame)
		self.angleSpin.setMinimum(0)
		self.angleSpin.setMaximum(45)
		self.angleSpin.setValue(0)
		self.angleSpin.setWrapping(True)
		QtCore.QObject.connect(self.angleSpin, QtCore.SIGNAL("valueChanged(int)"), self.__parent.guideAngleChanged_cb)
		
		self.gapHeightLabel = QtGui.QLabel(self.charSetPropFrame)
		self.gapHeightLabel.setText("Gap distance:")
		
		self.gapHeightSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.gapHeightSpin.setMinimum(1)
		self.gapHeightSpin.setMaximum(5)
		self.gapHeightSpin.setValue(1.5)
		self.gapHeightSpin.setWrapping(True)
		self.gapHeightSpin.setDecimals(1)
		self.gapHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.gapHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.guideGapHeightChanged_cb)
		
		self.nominalWidthLabel = QtGui.QLabel(self.charSetPropFrame)
		self.nominalWidthLabel.setText("Nominal width:")
		
		self.nominalWidthSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.nominalWidthSpin.setMinimum(2)
		self.nominalWidthSpin.setMaximum(10)
		self.nominalWidthSpin.setValue(4.0)
		self.nominalWidthSpin.setWrapping(True)
		self.nominalWidthSpin.setDecimals(1)
		self.nominalWidthSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.nominalWidthSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.guideNominalWidthChanged_cb)

		self.guidesColorLabel = QtGui.QLabel(self.charSetPropFrame)
		self.guidesColorLabel.setText("Guideline color:")
		self.guidesColorButton = widgets_qt.select_color_button(self.charSetPropFrame)
		self.guidesColorButton.setColor(QtGui.QColor(200, 195, 180))
		QtCore.QObject.connect(self.guidesColorButton, QtCore.SIGNAL("valueChanged(QColor)"), self.__parent.guideColorChanged_cb)

		self.charSetPropLayout.addRow(self.baseHeightLabel, self.baseHeightSpin)
		self.charSetPropLayout.addRow(self.capHeightLabel, self.capHeightSpin)
		self.charSetPropLayout.addRow(self.ascentHeightLabel, self.ascentHeightSpin)
		self.charSetPropLayout.addRow(self.descentHeightLabel, self.descentHeightSpin)
		self.charSetPropLayout.addRow(self.angleLabel, self.angleSpin)
		self.charSetPropLayout.addRow(self.gapHeightLabel, self.gapHeightSpin)
		self.charSetPropLayout.addRow(self.nominalWidthLabel, self.nominalWidthSpin)
		self.charSetPropLayout.addRow(self.guidesColorLabel, self.guidesColorButton)

		self.charPropFrame = QtGui.QFrame(self.toolPane);
		self.charPropLayout = QtGui.QFormLayout(self.charPropFrame)

		self.charWidthLabel = QtGui.QLabel(self.charPropFrame)
		self.charWidthLabel.setText("Character width:")

		self.charWidthSpin = QtGui.QDoubleSpinBox(self.charPropFrame)
		self.charWidthSpin.setMinimum(2)
		self.charWidthSpin.setMaximum(10)
		self.charWidthSpin.setValue(4.0)
		self.charWidthSpin.setWrapping(True)
		self.charWidthSpin.setDecimals(1)
		self.charWidthSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.charWidthSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.charWidthChanged_cb)

		self.leftSpaceLabel = QtGui.QLabel(self.charPropFrame)
		self.leftSpaceLabel.setText("Left spacing:")

		self.leftSpaceSpin = QtGui.QDoubleSpinBox(self.charPropFrame)
		self.leftSpaceSpin.setMinimum(0)
		self.leftSpaceSpin.setMaximum(3)
		self.leftSpaceSpin.setValue(1.0)
		self.leftSpaceSpin.setWrapping(True)
		self.leftSpaceSpin.setDecimals(1)
		self.leftSpaceSpin.setSingleStep(0.1)
		QtCore.QObject.connect(self.leftSpaceSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.charLeftSpaceChanged_cb)

		self.rightSpaceLabel = QtGui.QLabel(self.charPropFrame)
		self.rightSpaceLabel.setText("Right spacing:")

		self.rightSpaceSpin = QtGui.QDoubleSpinBox(self.charPropFrame)
		self.rightSpaceSpin.setMinimum(0)
		self.rightSpaceSpin.setMaximum(3)
		self.rightSpaceSpin.setValue(1.0)
		self.rightSpaceSpin.setWrapping(True)
		self.rightSpaceSpin.setDecimals(1)
		self.rightSpaceSpin.setSingleStep(0.1)
		QtCore.QObject.connect(self.rightSpaceSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.charRightSpaceChanged_cb)

		self.charPropLayout.addRow(self.charWidthLabel, self.charWidthSpin)
		self.charPropLayout.addRow(self.leftSpaceLabel, self.leftSpaceSpin)
		self.charPropLayout.addRow(self.rightSpaceLabel, self.rightSpaceSpin)

		self.propertyTabs = QtGui.QTabWidget(self.toolPane)
		self.propertyTabs.addTab(self.charSetPropFrame, "Character Set");
		self.propertyTabs.addTab(self.charPropFrame, "Character");

		self.toolPaneLayout.addWidget(self.propertyTabs)
		self.toolPaneLayout.setMargin(0)
		self.toolPaneLayout.setSpacing(5)
		self.toolPaneLayout.setContentsMargins(0, 0, 0, 0)

		self.strokeDwgArea.setOriginDelta(QtCore.QPoint())

		self.mainViewTabs = QtGui.QTabWidget(self.mainWidget)
		self.mainViewTabs.addTab(self.dwgArea, "Character")
		self.mainViewTabs.addTab(self.strokeDwgArea, "Stroke")
		self.mainViewTabs.currentChanged.connect(self.__parent.viewTabChanged_cb)

		self.mainSplitter.addWidget(self.mainViewTabs)
		self.mainSplitter.addWidget(self.toolPane)
		self.mainSplitter.setMaxPaneWidth(wid20)
		self.mainSplitter.setSizes([wid80, wid20])
		mainSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.mainSplitter.setSizePolicy(mainSizePolicy)

		self.viewLayout.addWidget(self.mainSplitter)
		self.viewLayout.setMargin(0)
		self.viewLayout.setSpacing(5)
		self.viewLayout.setContentsMargins(0, 0, 0, 0)

		mainSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.mainSplitter.setSizePolicy(mainSizePolicy)
	
		self.dwgArea.setSizePolicy(mainSizePolicy)
		self.strokeDwgArea.setSizePolicy(mainSizePolicy)

		self.mainLayout.addLayout(self.charSelectorLayout)
		self.mainLayout.addLayout(self.viewLayout, 2)
		
		self.mainWidget.setLayout(self.mainLayout)

		self.setCentralWidget(self.mainWidget)

		self.guideLines = guides.guideLines()
		self.dwgArea.setGuidelines(self.guideLines)
		self.strokeDwgArea.setGuidelines(self.guideLines)

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
		self.fileOpen.setEnabled(True)
		self.fileOpen.triggered.connect(self.__parent.fileOpen_cb)
		self.fileMenu.addAction(self.fileOpen)
		self.toolBar.addAction(self.fileOpen)
		self.fileMenu.addSeparator()
		
		self.fileSave = QtGui.QAction("&Save", self)
		self.fileSave.setShortcut('Ctrl+S')
		self.fileSave.setStatusTip('Save the character set')
		self.fileSave.setIcon(QtGui.QIcon("icons/script_save.png"))
		self.fileSave.triggered.connect(self.__parent.fileSave_cb)
		self.fileSave.setIconText("Save")
		self.fileSave.setEnabled(False)
		self.fileMenu.addAction(self.fileSave)
		self.toolBar.addAction(self.fileSave)
		
		self.fileSaveAs = QtGui.QAction("&Save As...", self)
		self.fileSaveAs.setStatusTip('Save the character set with a new name')
		self.fileSaveAs.setIcon(QtGui.QIcon("icons/save_as.png"))
		self.fileSaveAs.setIconText("Save As...")
		self.fileSaveAs.setEnabled(True)
		self.fileSaveAs.triggered.connect(self.__parent.fileSaveAs_cb)
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
		self.editCut.setEnabled(False)
		self.editCut.triggered.connect(self.__parent.cutStrokes_cb)
		self.editMenu.addAction(self.editCut)
		self.toolBar.addAction(self.editCut)
		
		self.editCopy = QtGui.QAction("Copy", self)
		self.editCopy.setShortcut('Ctrl+C')
		self.editCopy.setIcon(QtGui.QIcon("icons/page_white_copy.png"))
		self.editCopy.setIconText("Copy")
		self.editCopy.setEnabled(False)
		self.editCopy.triggered.connect(self.__parent.copyStrokes_cb)
		self.editMenu.addAction(self.editCopy)
		self.toolBar.addAction(self.editCopy)
		
		self.editPaste = QtGui.QAction("Paste", self)
		self.editPaste.setShortcut('Ctrl+V')
		self.editPaste.setIcon(QtGui.QIcon("icons/page_white_paste.png"))
		self.editPaste.setIconText("Paste")
		self.editPaste.setEnabled(False)
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
		self.viewGuides.triggered.connect(self.__parent.viewToggleGuidelines_cb)
		self.viewGuides.setCheckable(True)
		self.viewGuides.setChecked(True)
		self.viewMenu.addAction(self.viewGuides)
		
		self.viewNibGuides = QtGui.QAction("Nib Guides", self)
		self.viewNibGuides.setStatusTip('Toggle nib guides on/off')
		self.viewNibGuides.triggered.connect(self.__parent.viewToggleNibGuides_cb)
		self.viewNibGuides.setCheckable(True)
		self.viewNibGuides.setChecked(True)
		self.viewMenu.addAction(self.viewNibGuides)
			
		self.viewMenu.addSeparator()
		
		self.viewSnapMenu = self.viewMenu.addMenu('&Snap')
	
		self.viewSnapToAxes = QtGui.QAction("To Axes", self)
		self.viewSnapToAxes.setStatusTip('Toggle snapping to axes')
		self.viewSnapToAxes.triggered.connect(self.__parent.viewToggleSnapAxially_cb)
		self.viewSnapToAxes.setCheckable(True)
		self.viewSnapToAxes.setChecked(True)
		#self.viewSnapToAxes.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToAxes)
		
		self.viewSnapToNibAxes = QtGui.QAction("To Nib Axes", self)
		self.viewSnapToNibAxes.setStatusTip('Toggle snapping to nib axes')
		self.viewSnapToNibAxes.triggered.connect(self.__parent.viewToggleSnapToNibAxes_cb)
		self.viewSnapToNibAxes.setCheckable(True)
		self.viewSnapToNibAxes.setChecked(False)
		#self.viewSnapToNibAxes.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToNibAxes)
		
		self.viewSnapToGrid = QtGui.QAction("To Grid", self)
		self.viewSnapToGrid.setStatusTip('Toggle snapping to grid')
		self.viewSnapToGrid.triggered.connect(self.__parent.viewToggleSnapToGrid_cb)
		self.viewSnapToGrid.setCheckable(True)
		self.viewSnapToGrid.setChecked(False)
		self.viewSnapToGrid.setEnabled(False)
		self.viewSnapMenu.addAction(self.viewSnapToGrid)
		
		self.viewSnapToCtrlPts = QtGui.QAction("To Control Points", self)
		self.viewSnapToCtrlPts.setStatusTip('Toggle snapping to control points')
		self.viewSnapToCtrlPts.triggered.connect(self.__parent.viewToggleSnapToCtrlPts_cb)
		self.viewSnapToCtrlPts.setCheckable(True)
		self.viewSnapToCtrlPts.setChecked(False)
		#self.viewSnapToCtrlPts.setEnabled(False)
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
		self.strokeStraighten.triggered.connect(self.__parent.straightenStroke_cb)
		self.strokeMenu.addAction(self.strokeStraighten)
		
		self.strokeJoin = QtGui.QAction("Join", self)
		self.strokeJoin.setStatusTip('Join multiple strokes into one')
		self.strokeJoin.setEnabled(False)
		self.strokeJoin.triggered.connect(self.__parent.joinStrokes_cb)
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
		self.strokeAddVertex.triggered.connect(self.__parent.addControlPoint_cb)
		self.strokeMenu.addAction(self.strokeAddVertex)

		self.strokeSplitAtPoint = QtGui.QAction("Split At Point", self)
		self.strokeSplitAtPoint.setEnabled(False)
		self.strokeSplitAtPoint.triggered.connect(self.__parent.splitAtPoint_cb)
		self.strokeMenu.addAction(self.strokeSplitAtPoint)
	
		self.strokeMenu.addSeparator()
		self.strokeSave = QtGui.QAction("Save Stroke", self)
		self.strokeSave.setEnabled(False)
		self.strokeSave.triggered.connect(self.__parent.saveStroke_cb)
		self.strokeMenu.addAction(self.strokeSave)

		self.strokeLoad = QtGui.QAction("Paste From Saved", self)
		self.strokeLoad.setEnabled(False)
		self.strokeLoad.triggered.connect(self.__parent.pasteInstanceFromSaved_cb)
		self.strokeMenu.addAction(self.strokeLoad)

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