#!/usr/bin/python
#

import math
import os
from PyQt4 import QtCore, QtGui

from model import guides
import paper
import splitter
import widgets_qt

gICON_SIZE = 40
gICON_TEXT_SIZE = 30

class EditInterface(QtGui.QMainWindow):
	def __init__(self, parent, w, h, label):
		QtGui.QMainWindow.__init__(self)
		self.setMouseTracking(True)
		self.setFocusPolicy(QtCore.Qt.ClickFocus)

		self.resize(w, h)
		self.setWindowTitle(label)
	 	
	 	self.message_dialog = QtGui.QMessageBox()
		self.file_open_dialog = QtGui.QFileDialog() 
		self.file_save_dialog = QtGui.QFileDialog() 
		self.__parent = parent
		
		self.dwg_area = None
		self.guide_lines = None

	def create_ui(self):
		self.create_menu()

		wid80 = int(self.width()*.75)
		wid20 = self.width() - wid80
		hgt = self.height() 

		#return
		self.mainWidget = QtGui.QWidget()
		self.mainSplitter = splitter.MySplitter (self.mainWidget)
		self.sideSplitter = QtGui.QSplitter(self.mainSplitter)
		self.sideSplitter.setOrientation(2)

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
		
		self.dwg_area = paper.drawingArea(self.mainSplitter)
		self.dwg_area.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
		self.dwg_area.setLineWidth(2)

		self.stroke_dwg_area = paper.drawingArea(self)
		self.stroke_dwg_area.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
		self.stroke_dwg_area.setLineWidth(2)
		self.stroke_dwg_area.drawGuidelines = False
		self.stroke_dwg_area.drawNibGuides = False

		self.preview_area = paper.layoutArea(self)
		self.preview_area.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
		self.preview_area.setLineWidth(2)

		self.toolPane = QtGui.QFrame(self.sideSplitter)
		self.toolPaneLayout = QtGui.QVBoxLayout(self.toolPane)
		
		self.bottomPane = QtGui.QFrame(self.sideSplitter)
		self.bottomPane.setFrameStyle(QtGui.QFrame.Panel)
		self.bottomPaneLayout = QtGui.QVBoxLayout(self.bottomPane)

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

		self.charSetNibAngleLabel = QtGui.QLabel(self.charSetPropFrame)
		self.charSetNibAngleLabel.setText("Nib Angle:")

		self.charSetNibAngleSpin = QtGui.QDoubleSpinBox(self.charSetPropFrame)
		self.charSetNibAngleSpin.setMinimum(0)
		self.charSetNibAngleSpin.setMaximum(90)
		self.charSetNibAngleSpin.setValue(40)
		self.charSetNibAngleSpin.setWrapping(True)
		self.charSetNibAngleSpin.setDecimals(0)
		self.charSetNibAngleSpin.setSingleStep(1.0)
		QtCore.QObject.connect(self.charSetNibAngleSpin, QtCore.SIGNAL("valueChanged(double)"), self.__parent.charSetNibAngleChanged_cb)

		self.charSetPropLayout.addRow(self.baseHeightLabel, self.baseHeightSpin)
		self.charSetPropLayout.addRow(self.capHeightLabel, self.capHeightSpin)
		self.charSetPropLayout.addRow(self.ascentHeightLabel, self.ascentHeightSpin)
		self.charSetPropLayout.addRow(self.descentHeightLabel, self.descentHeightSpin)
		self.charSetPropLayout.addRow(self.angleLabel, self.angleSpin)
		self.charSetPropLayout.addRow(self.gapHeightLabel, self.gapHeightSpin)
		self.charSetPropLayout.addRow(self.nominalWidthLabel, self.nominalWidthSpin)
		self.charSetPropLayout.addRow(self.guidesColorLabel, self.guidesColorButton)
		self.charSetPropLayout.addRow(self.charSetNibAngleLabel, self.charSetNibAngleSpin)
		
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

		self.strokePropFrame = QtGui.QFrame(self.toolPane);
		self.strokePropLayout = QtGui.QFormLayout(self.strokePropFrame)

		self.behaviorLabel = QtGui.QLabel(self.strokePropFrame)
		self.behaviorLabel.setText("Vertex Behavior")

		self.behaviorCombo = QtGui.QComboBox(self.strokePropFrame)
		self.behaviorCombo.addItem("--")
		self.behaviorCombo.addItem("Smooth")
		self.behaviorCombo.addItem("Sharp")
		self.behaviorCombo.addItem("Symmetric")
		self.behaviorCombo.setCurrentIndex(0)
		QtCore.QObject.connect(self.behaviorCombo, QtCore.SIGNAL("currentIndexChanged(int)"), self.__parent.vertBehaviorComboChanged_cb)

		self.strokePropLayout.addRow(self.behaviorLabel, self.behaviorCombo)

		self.propertyTabs = QtGui.QTabWidget(self.toolPane)
		self.propertyTabs.addTab(self.strokePropFrame, "Stroke");
		self.propertyTabs.addTab(self.charPropFrame, "Character");
		self.propertyTabs.addTab(self.charSetPropFrame, "Character Set");

		self.toolPaneLayout.addWidget(self.propertyTabs)
		self.toolPaneLayout.setMargin(0)
		self.toolPaneLayout.setSpacing(5)
		self.toolPaneLayout.setContentsMargins(0, 0, 0, 0)

		self.stroke_dwg_area.setOriginDelta(QtCore.QPoint())

		self.mainViewTabs = QtGui.QTabWidget(self.mainWidget)
		self.mainViewTabs.addTab(self.dwg_area, "Character")
		self.mainViewTabs.addTab(self.stroke_dwg_area, "Stroke")
		self.mainViewTabs.addTab(self.preview_area, "Preview")
		self.mainViewTabs.currentChanged.connect(self.__parent.viewTabChanged_cb)

		self.mainSplitter.addWidget(self.mainViewTabs)
		self.mainSplitter.addWidget(self.sideSplitter)
		self.sideSplitter.addWidget(self.toolPane)
		self.sideSplitter.addWidget(self.bottomPane)
		self.sideSplitter.setSizes([self.height(), 0])

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
	
		self.dwg_area.setSizePolicy(mainSizePolicy)
		self.stroke_dwg_area.setSizePolicy(mainSizePolicy)

		self.mainLayout.addLayout(self.charSelectorLayout)
		self.mainLayout.addLayout(self.viewLayout, 2)
		
		self.mainWidget.setLayout(self.mainLayout)

		self.setCentralWidget(self.mainWidget)

		self.guide_lines = guides.guideLines()
		self.dwg_area.setGuidelines(self.guide_lines)
		self.stroke_dwg_area.setGuidelines(self.guide_lines)

	def create_menu(self):
		self.main_menu = self.menuBar()
		self.tool_bar = self.addToolBar("main") 
		self.tool_bar.resize(self.width(), gICON_SIZE+gICON_TEXT_SIZE)
		self.tool_bar.setFloatable(False)
		self.tool_bar.setMovable(False)
		self.tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		
		self.file_menu 	= self.main_menu.addMenu('&File')
		self.edit_menu 	= self.main_menu.addMenu('&Edit')
		self.view_menu	= self.main_menu.addMenu('&View')
		
		self.stroke_menu = self.main_menu.addMenu('Stro&ke')
		self.help_menu 	= self.main_menu.addMenu('&Help')

		self.file_new = QtGui.QAction("&New", self)
		self.file_new.setShortcut('Ctrl+N')
		self.file_new.setStatusTip('Create a new self.character set')
		self.file_new.triggered.connect(self.__parent.file_new_cb)
		self.file_new.setIcon(QtGui.QIcon("icons/script_add.png"))
		self.file_new.setIconText("New")
		self.file_menu.addAction(self.file_new)
		self.tool_bar.addAction(self.file_new)
		
		self.file_open = QtGui.QAction("&Open", self)
		self.file_open.setShortcut('Ctrl+O')
		self.file_open.setStatusTip('Open a character set')
		self.file_open.setIcon(QtGui.QIcon("icons/script_go.png"))
		self.file_open.setIconText("Open")
		self.file_open.setEnabled(True)
		self.file_open.triggered.connect(self.__parent.file_open_cb)
		self.file_menu.addAction(self.file_open)
		self.tool_bar.addAction(self.file_open)
		self.file_menu.addSeparator()
		
		self.file_save = QtGui.QAction("&Save", self)
		self.file_save.setShortcut('Ctrl+S')
		self.file_save.setStatusTip('Save the character set')
		self.file_save.setIcon(QtGui.QIcon("icons/script_save.png"))
		self.file_save.triggered.connect(self.__parent.file_save_cb)
		self.file_save.setIconText("Save")
		self.file_save.setEnabled(False)
		self.file_menu.addAction(self.file_save)
		self.tool_bar.addAction(self.file_save)
		
		self.file_save_as = QtGui.QAction("&Save As...", self)
		self.file_save_as.setShortcut('Ctrl+Shift+S')
		self.file_save_as.setStatusTip('Save the character set with a new name')
		self.file_save_as.setIcon(QtGui.QIcon("icons/save_as.png"))
		self.file_save_as.setIconText("Save As...")
		self.file_save_as.setEnabled(True)
		self.file_save_as.triggered.connect(self.__parent.file_save_as_cb)
		self.file_menu.addAction(self.file_save_as)
		self.tool_bar.addAction(self.file_save_as)
		
		self.file_menu.addSeparator()
		self.file_quit = QtGui.QAction("Q&uit", self)
		self.file_quit.setShortcut('Ctrl+Q')
		self.file_quit.triggered.connect(self.__parent.quit_cb)
		self.file_menu.addAction(self.file_quit)

		self.tool_bar.addSeparator()
		
		self.edit_undo = QtGui.QAction("Undo", self)
		self.edit_undo.setShortcut('Ctrl+Z')
		self.edit_undo.setIcon(QtGui.QIcon("icons/arrow_undo.png"))
		self.edit_undo.setIconText("Undo")
		self.edit_undo.setEnabled(False)
		self.edit_undo.triggered.connect(self.__parent.undo_cb)
		self.edit_menu.addAction(self.edit_undo)
		self.tool_bar.addAction(self.edit_undo)
		
		self.edit_redo = QtGui.QAction("Redo", self)
		self.edit_redo.setShortcut('Ctrl+Shift+Z')
		self.edit_redo.setIcon(QtGui.QIcon("icons/arrow_redo.png"))
		self.edit_redo.setIconText("Redo")
		self.edit_redo.setEnabled(False)
		self.edit_redo.triggered.connect(self.__parent.redo_cb)
		self.edit_menu.addAction(self.edit_redo)
		self.tool_bar.addAction(self.edit_redo)
		
		self.edit_menu.addSeparator()
		self.tool_bar.addSeparator()
		
		self.edit_cut = QtGui.QAction("Cut", self)
		self.edit_cut.setShortcut('Ctrl+X')
		self.edit_cut.setIcon(QtGui.QIcon("icons/cut.png"))
		self.edit_cut.setIconText("Cut")
		self.edit_cut.setEnabled(False)
		self.edit_cut.triggered.connect(self.__parent.cut_strokes_cb)
		self.edit_menu.addAction(self.edit_cut)
		self.tool_bar.addAction(self.edit_cut)
		
		self.edit_copy = QtGui.QAction("Copy", self)
		self.edit_copy.setShortcut('Ctrl+C')
		self.edit_copy.setIcon(QtGui.QIcon("icons/page_white_copy.png"))
		self.edit_copy.setIconText("Copy")
		self.edit_copy.setEnabled(False)
		self.edit_copy.triggered.connect(self.__parent.copy_strokes_cb)
		self.edit_menu.addAction(self.edit_copy)
		self.tool_bar.addAction(self.edit_copy)
		
		self.edit_paste = QtGui.QAction("Paste", self)
		self.edit_paste.setShortcut('Ctrl+V')
		self.edit_paste.setIcon(QtGui.QIcon("icons/page_white_paste.png"))
		self.edit_paste.setIconText("Paste")
		self.edit_paste.setEnabled(False)
		self.edit_paste.triggered.connect(self.__parent.paste_strokes_cb)
		self.edit_menu.addAction(self.edit_paste)
		self.tool_bar.addAction(self.edit_paste)

		self.tool_bar.addSeparator()
		
		self.view_reset_origin = QtGui.QAction("Reset View Origin", self)
		self.view_reset_origin.setShortcut('Ctrl+.')
		self.view_reset_origin.setStatusTip('Reset origin of view')
		self.view_reset_origin.triggered.connect(self.__parent.view_reset_origin_cb)
		self.view_menu.addAction(self.view_reset_origin)

		self.view_reset_zoom = QtGui.QAction("Zoom 100%", self)
		self.view_reset_zoom.setShortcut('Ctrl+0')
		self.view_reset_zoom.setStatusTip('Reset zoom of view')
		self.view_reset_zoom.triggered.connect(self.__parent.view_reset_zoom_cb)
		self.view_menu.addAction(self.view_reset_zoom)

		self.view_menu.addSeparator()

		self.view_guides = QtGui.QAction("Guidelines", self)
		self.view_guides.setStatusTip('Toggle guidelines on/off')
		self.view_guides.triggered.connect(self.__parent.view_toggle_guidelines_cb)
		self.view_guides.setCheckable(True)
		self.view_guides.setChecked(True)
		self.view_menu.addAction(self.view_guides)
		
		self.view_nib_guides = QtGui.QAction("Nib Guides", self)
		self.view_nib_guides.setStatusTip('Toggle nib guides on/off')
		self.view_nib_guides.triggered.connect(self.__parent.view_toggle_nib_guides_cb)
		self.view_nib_guides.setCheckable(True)
		self.view_nib_guides.setChecked(True)
		self.view_menu.addAction(self.view_nib_guides)
			
		self.view_menu.addSeparator()
		
		self.view_snap_menu = self.view_menu.addMenu('&Snap')
	
		self.view_snap_to_axes = QtGui.QAction("To Axes", self)
		self.view_snap_to_axes.setStatusTip('Toggle snapping to axes')
		self.view_snap_to_axes.triggered.connect(self.__parent.view_toggle_snap_axially_cb)
		self.view_snap_to_axes.setCheckable(True)
		self.view_snap_to_axes.setChecked(True)
		#self.view_snap_to_axes.setEnabled(False)
		self.view_snap_menu.addAction(self.view_snap_to_axes)
		
		self.view_snap_to_nib_axes = QtGui.QAction("To Nib Axes", self)
		self.view_snap_to_nib_axes.setStatusTip('Toggle snapping to nib axes')
		self.view_snap_to_nib_axes.triggered.connect(self.__parent.view_toggle_snap_to_nib_axes_cb)
		self.view_snap_to_nib_axes.setCheckable(True)
		self.view_snap_to_nib_axes.setChecked(False)
		#self.view_snap_to_nib_axes.setEnabled(False)
		self.view_snap_menu.addAction(self.view_snap_to_nib_axes)
		
		self.view_snap_to_grid = QtGui.QAction("To Grid", self)
		self.view_snap_to_grid.setStatusTip('Toggle snapping to grid')
		self.view_snap_to_grid.triggered.connect(self.__parent.view_toggle_snap_to_grid_cb)
		self.view_snap_to_grid.setCheckable(True)
		self.view_snap_to_grid.setChecked(False)
		#self.view_snap_to_grid.setEnabled(False)
		self.view_snap_menu.addAction(self.view_snap_to_grid)
		
		self.view_snap_to_ctrl_pts = QtGui.QAction("To Control Points", self)
		self.view_snap_to_ctrl_pts.setStatusTip('Toggle snapping to control points')
		self.view_snap_to_ctrl_pts.triggered.connect(self.__parent.view_toggle_snap_to_ctrl_pts_cb)
		self.view_snap_to_ctrl_pts.setCheckable(True)
		self.view_snap_to_ctrl_pts.setChecked(False)
		#self.view_snap_to_ctrl_pts.setEnabled(False)
		self.view_snap_menu.addAction(self.view_snap_to_ctrl_pts)
		
		self.view_snap_to_stroke = QtGui.QAction("To Strokes", self)
		self.view_snap_to_stroke.setStatusTip('Toggle snapping to strokes')
		#view_snap_to_stroke.triggered.connect(self.__parent.view_toggle_snap_to_stroke_cb)
		self.view_snap_to_stroke.setCheckable(True)
		self.view_snap_to_stroke.setChecked(False)
		self.view_snap_to_stroke.setEnabled(False)
		self.view_snap_menu.addAction(self.view_snap_to_stroke)
		
		self.stroke_new = QtGui.QAction("New", self)
		self.stroke_new.setStatusTip('Create a new stroke')
		self.stroke_new.setShortcut('Shift+N')
		self.stroke_new.setIcon(QtGui.QIcon("icons/draw_path.png"))
		self.stroke_new.setIconText("Stroke")
		self.stroke_new.triggered.connect(self.__parent.create_new_stroke_cb)
		self.stroke_menu.addAction(self.stroke_new)
		self.tool_bar.addAction(self.stroke_new)
		
		self.stroke_new_freehand = QtGui.QAction("New Experimental", self)
		self.stroke_new_freehand.setStatusTip('Create a new stroke freehand')
		self.stroke_new_freehand.setIcon(QtGui.QIcon("icons/draw_calligraphic.png"))
		self.stroke_new_freehand.setIconText("Freehand")
		self.stroke_new_freehand.setEnabled(False)
		#stroke_new_freehand.triggered.connect(self.createNewFreehandStroke_cb)
		self.stroke_menu.addAction(self.stroke_new_freehand)
		self.tool_bar.addAction(self.stroke_new_freehand)
		
		self.stroke_delete = QtGui.QAction("Delete", self)
		self.stroke_delete.setStatusTip('Delete selected stroke(s)')
		self.stroke_delete.setShortcut('Backspace')
		self.stroke_delete.setIcon(QtGui.QIcon("icons/delete.png"))
		self.stroke_delete.setIconText("Delete")
		self.stroke_delete.triggered.connect(self.__parent.delete_strokes_cb)
		self.stroke_menu.addAction(self.stroke_delete)
		self.tool_bar.addAction(self.stroke_delete)

		self.stroke_straighten = QtGui.QAction("Straighten", self)
		self.stroke_straighten.setStatusTip('Make the stroke straight')
		self.stroke_straighten.setEnabled(False)
		self.stroke_straighten.triggered.connect(self.__parent.straighten_stroke_cb)
		self.stroke_menu.addAction(self.stroke_straighten)
		
		self.stroke_join = QtGui.QAction("Join", self)
		self.stroke_join.setStatusTip('Join multiple strokes into one')
		self.stroke_join.setEnabled(False)
		self.stroke_join.triggered.connect(self.__parent.join_strokes_cb)
		self.stroke_menu.addAction(self.strokeJoin)
		
		self.stroke_menu.addSeparator()
		self.stroke_align_tangents = QtGui.QAction("Set Tangent To Symmetric", self)
		self.stroke_align_tangents.setEnabled(False)
		self.stroke_align_tangents.triggered.connect(self.__parent.align_tangents_symmetrical_cb)
		self.stroke_menu.addAction(self.stroke_align_tangents)
		
		self.stroke_smooth_tangents = QtGui.QAction("Set Tangent To Smooth", self)
		self.stroke_smooth_tangents.setEnabled(False)
		self.stroke_smooth_tangents.triggered.connect(self.__parent.align_tangents_cb)
		self.stroke_menu.addAction(self.stroke_smooth_tangents)
		
		self.stroke_sharpen_tangents = QtGui.QAction("Set Tangent To Sharp", self)
		self.stroke_sharpen_tangents.setEnabled(False)
		self.stroke_sharpen_tangents.triggered.connect(self.__parent.break_tangents_cb)
		self.stroke_menu.addAction(self.stroke_sharpen_tangents)
		self.stroke_menu.addSeparator()
		
		self.stroke_add_vertex = QtGui.QAction("Add Control Point", self)
		self.stroke_add_vertex.setEnabled(False)
		self.stroke_add_vertex.triggered.connect(self.__parent.add_control_point_cb)
		self.stroke_menu.addAction(self.stroke_add_vertex)

		self.stroke_split_at_point = QtGui.QAction("Split At Point", self)
		self.stroke_split_at_point.setEnabled(False)
		self.stroke_split_at_point.triggered.connect(self.__parent.split_at_point_cb)
		self.stroke_menu.addAction(self.stroke_split_at_point)
	
		self.stroke_menu.addSeparator()
		self.stroke_save = QtGui.QAction("Save Stroke", self)
		self.stroke_save.setEnabled(False)
		self.stroke_save.triggered.connect(self.__parent.save_stroke_cb)
		self.stroke_menu.addAction(self.stroke_save)

		self.stroke_load = QtGui.QAction("Paste From Saved", self)
		self.stroke_load.setEnabled(False)
		self.stroke_load.triggered.connect(self.__parent.paste_instance_from_saved_cb)
		self.stroke_menu.addAction(self.stroke_load)

		self.help_about = QtGui.QAction("About", self)
		self.help_about.triggered.connect(self.about_cb)
		self.help_menu.addAction(self.help_about)

	def about_cb(self, event):
		reply = QtGui.QMessageBox.information(self, 'About PyTalic Editor', \
			"PyTalic Editor\nby Dale Cieslak\n(c) 2007-2018\n\nhttps://github.com/dsizzle/pytalic2", \
			QtGui.QMessageBox.Ok )

	def mouseMoveEvent(self, event):
		self.__parent.mouse_event(event)

	def mousePressEvent(self, event):
		self.__parent.mouse_event(event)

	def mouseReleaseEvent(self, event):
		self.__parent.mouse_event(event)

	def wheelEvent(self, event):
		self.__parent.wheel_event(event)

	def paintEvent(self, event):
		QtGui.QMainWindow.paintEvent(self,event)

	def closeEvent(self, event):
		self.__parent.quit_cb(event)