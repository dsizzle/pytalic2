#!/usr/bin/python
#

from PyQt4 import QtCore, QtGui

from model import guides
import view.paper
import view.widgets_qt

ICON_SIZE = 40
ICON_TEXT_SIZE = 30

class EditInterface(QtGui.QMainWindow):
    def __init__(self, parent, width, height, label):
        QtGui.QMainWindow.__init__(self)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.resize(width, height)
        self.setWindowTitle(label)

        self.message_dialog = QtGui.QMessageBox()
        self.file_open_dialog = QtGui.QFileDialog()
        self.file_save_dialog = QtGui.QFileDialog()
        self.__parent = parent

        self.dwg_area = None
        self.guide_lines = None
        self.preview_area = None
        self.main_widget = QtGui.QWidget()
        self.main_splitter = None
        self.side_splitter = None
        self.main_layout = QtGui.QVBoxLayout()
        self.view_layout = QtGui.QHBoxLayout()
        self.char_selector_layout = QtGui.QHBoxLayout()
        self.char_selector_list = QtGui.QListWidget(self.main_widget)
        self.stroke_selector_list = QtGui.QListWidget(self)
        self.tool_pane = None
        self.bottom_pane = None
        self.char_set_prop_frame = None
        self.char_set_prop_layout = None

        self.main_menu = self.menuBar()
        self.tool_bar = None
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.stroke_menu = None
        self.help_menu = None

    def create_ui(self):
        self.create_menu()

        wid80 = int(self.width()*.75)
        wid20 = self.width() - wid80

        self.main_splitter = view.widgets_qt.DoubleClickSplitter(self.main_widget)
        self.side_splitter = view.widgets_qt.DoubleClickSplitter(self.main_splitter)
        self.side_splitter.setOrientation(QtCore.Qt.Vertical)

        self.char_selector_layout.setMargin(0)
        self.char_selector_layout.setSpacing(0)
        self.char_selector_layout.setContentsMargins(0, 0, 0, 0)

        self.char_selector_list.setFlow(QtGui.QListView.LeftToRight)
        self.char_selector_list.resize(self.width(), ICON_SIZE*1.75)
        self.char_selector_list.setMaximumHeight(ICON_SIZE*1.75)
        self.char_selector_list.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.char_selector_list.currentItemChanged.connect(self.__parent.char_selected_cb)
        self.char_selector_layout.addWidget(self.char_selector_list, 0, QtCore.Qt.AlignTop)

        self.stroke_selector_list.resize(ICON_SIZE*1.5, self.height())
        self.stroke_selector_list.setMaximumWidth(ICON_SIZE*1.5)
        self.stroke_selector_list.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.stroke_selector_list.currentItemChanged.connect(self.__parent.stroke_selected_cb)
        self.view_layout.addWidget(self.stroke_selector_list)

        self.dwg_area = view.paper.DrawingArea(self.main_splitter)
        self.dwg_area.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.dwg_area.setLineWidth(2)

        self.stroke_dwg_area = view.paper.DrawingArea(self)
        self.stroke_dwg_area.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.stroke_dwg_area.setLineWidth(2)
        self.stroke_dwg_area.drawGuidelines = False
        self.stroke_dwg_area.drawNibGuides = False

        self.preview_area = view.paper.LayoutArea(self)
        self.preview_area.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.preview_area.setLineWidth(2)

        self.tool_pane = QtGui.QFrame(self.side_splitter)
        self.tool_pane_layout = QtGui.QVBoxLayout(self.tool_pane)

        self.bottom_pane = QtGui.QFrame(self.side_splitter)
        self.bottom_pane.setFrameStyle(QtGui.QFrame.Panel)
        self.bottom_pane_layout = QtGui.QVBoxLayout(self.bottom_pane)

        self.char_set_prop_frame = QtGui.QFrame(self.tool_pane)
        self.char_set_prop_layout = QtGui.QFormLayout(self.char_set_prop_frame)
        self.main_char_set_prop_label = QtGui.QLabel(self.char_set_prop_frame)
        self.main_char_set_prop_label.setText("Note: All units are nib-widths.")
        self.char_set_prop_layout.addRow(self.main_char_set_prop_label)

        self.base_height_label = QtGui.QLabel(self.char_set_prop_frame)
        self.base_height_label.setText("X-height:")

        self.base_height_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.base_height_spin.setMinimum(1.0)
        self.base_height_spin.setMaximum(10.0)
        self.base_height_spin.setValue(1.0)
        self.base_height_spin.setWrapping(True)
        self.base_height_spin.setDecimals(1)
        self.base_height_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.base_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_base_height_changed_cb)

        self.cap_height_label = QtGui.QLabel(self.char_set_prop_frame)
        self.cap_height_label.setText("Capital height:")

        self.cap_height_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.cap_height_spin.setMinimum(0.5)
        self.cap_height_spin.setMaximum(10)
        self.cap_height_spin.setValue(2.0)
        self.cap_height_spin.setWrapping(True)
        self.cap_height_spin.setDecimals(1)
        self.cap_height_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.cap_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_cap_height_changed_cb)

        self.ascent_height_label = QtGui.QLabel(self.char_set_prop_frame)
        self.ascent_height_label.setText("Ascent height:")

        self.ascent_height_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.ascent_height_spin.setMinimum(1)
        self.ascent_height_spin.setMaximum(10)
        self.ascent_height_spin.setValue(1)
        self.ascent_height_spin.setWrapping(True)
        self.ascent_height_spin.setDecimals(1)
        self.ascent_height_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.ascent_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_ascent_changed_cb)

        self.descent_height_label = QtGui.QLabel(self.char_set_prop_frame)
        self.descent_height_label.setText("Descent height:")

        self.descent_height_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.descent_height_spin.setMinimum(1)
        self.descent_height_spin.setMaximum(10)
        self.descent_height_spin.setValue(1)
        self.descent_height_spin.setWrapping(True)
        self.descent_height_spin.setDecimals(1)
        self.descent_height_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.descent_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_descent_changed_cb)

        self.angle_label = QtGui.QLabel(self.char_set_prop_frame)
        self.angle_label.setText("Guide angle:")

        self.angle_spin = QtGui.QSpinBox(self.char_set_prop_frame)
        self.angle_spin.setMinimum(0)
        self.angle_spin.setMaximum(45)
        self.angle_spin.setValue(0)
        self.angle_spin.setWrapping(True)
        QtCore.QObject.connect(self.angle_spin, \
            QtCore.SIGNAL("valueChanged(int)"), \
            self.__parent.guide_angle_changed_cb)

        self.gap_height_label = QtGui.QLabel(self.char_set_prop_frame)
        self.gap_height_label.setText("Gap distance:")

        self.gap_height_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.gap_height_spin.setMinimum(1)
        self.gap_height_spin.setMaximum(5)
        self.gap_height_spin.setValue(1.5)
        self.gap_height_spin.setWrapping(True)
        self.gap_height_spin.setDecimals(1)
        self.gap_height_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.gap_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_gap_height_changed_cb)

        self.nominal_width_label = QtGui.QLabel(self.char_set_prop_frame)
        self.nominal_width_label.setText("Nominal width:")

        self.nominal_width_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.nominal_width_spin.setMinimum(2)
        self.nominal_width_spin.setMaximum(10)
        self.nominal_width_spin.setValue(4.0)
        self.nominal_width_spin.setWrapping(True)
        self.nominal_width_spin.setDecimals(1)
        self.nominal_width_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.nominal_width_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_nominal_width_changed_cb)

        self.char_set_left_space_label = QtGui.QLabel(self.char_set_prop_frame)
        self.char_set_left_space_label.setText("Left spacing:")

        self.char_set_left_space_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.char_set_left_space_spin.setMinimum(0)
        self.char_set_left_space_spin.setMaximum(3)
        self.char_set_left_space_spin.setValue(1.0)
        self.char_set_left_space_spin.setWrapping(True)
        self.char_set_left_space_spin.setDecimals(1)
        self.char_set_left_space_spin.setSingleStep(0.1)
        QtCore.QObject.connect(self.char_set_left_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_set_left_space_changed_cb)

        self.char_set_right_space_label = QtGui.QLabel(self.char_set_prop_frame)
        self.char_set_right_space_label.setText("Right spacing:")

        self.char_set_right_space_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.char_set_right_space_spin.setMinimum(0)
        self.char_set_right_space_spin.setMaximum(3)
        self.char_set_right_space_spin.setValue(1.0)
        self.char_set_right_space_spin.setWrapping(True)
        self.char_set_right_space_spin.setDecimals(1)
        self.char_set_right_space_spin.setSingleStep(0.1)
        QtCore.QObject.connect(self.char_set_right_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_set_right_space_changed_cb)

        self.guides_color_label = QtGui.QLabel(self.char_set_prop_frame)
        self.guides_color_label.setText("Guideline color:")
        self.guides_color_button = view.widgets_qt.SelectColorButton(self.char_set_prop_frame)
        self.guides_color_button.setColor(QtGui.QColor(200, 195, 180))
        QtCore.QObject.connect(self.guides_color_button, \
            QtCore.SIGNAL("valueChanged(QColor)"), \
            self.__parent.guide_color_changed_cb)

        self.char_set_nib_angle_label = QtGui.QLabel(self.char_set_prop_frame)
        self.char_set_nib_angle_label.setText("Nib Angle:")

        self.char_set_nib_angle_spin = QtGui.QDoubleSpinBox(self.char_set_prop_frame)
        self.char_set_nib_angle_spin.setMinimum(0)
        self.char_set_nib_angle_spin.setMaximum(90)
        self.char_set_nib_angle_spin.setValue(40)
        self.char_set_nib_angle_spin.setWrapping(True)
        self.char_set_nib_angle_spin.setDecimals(0)
        self.char_set_nib_angle_spin.setSingleStep(1.0)
        QtCore.QObject.connect(self.char_set_nib_angle_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_set_nib_angle_changed_cb)

        self.char_set_prop_layout.addRow(self.base_height_label, \
            self.base_height_spin)
        self.char_set_prop_layout.addRow(self.cap_height_label, \
            self.cap_height_spin)
        self.char_set_prop_layout.addRow(self.ascent_height_label, \
            self.ascent_height_spin)
        self.char_set_prop_layout.addRow(self.descent_height_label, \
            self.descent_height_spin)
        self.char_set_prop_layout.addRow(self.angle_label, \
            self.angle_spin)
        self.char_set_prop_layout.addRow(self.gap_height_label, \
            self.gap_height_spin)
        self.char_set_prop_layout.addRow(self.nominal_width_label, \
            self.nominal_width_spin)
        self.char_set_prop_layout.addRow(self.char_set_left_space_label, \
            self.char_set_left_space_spin)
        self.char_set_prop_layout.addRow(self.char_set_right_space_label, \
            self.char_set_right_space_spin)
        self.char_set_prop_layout.addRow(self.guides_color_label, \
            self.guides_color_button)
        self.char_set_prop_layout.addRow(self.char_set_nib_angle_label, \
            self.char_set_nib_angle_spin)

        self.char_prop_frame = QtGui.QFrame(self.tool_pane)
        self.char_prop_layout = QtGui.QFormLayout(self.char_prop_frame)

        self.main_char_prop_label = QtGui.QLabel(self.char_prop_frame)
        self.main_char_prop_label.setText("Note: All units are nib-widths.")

        self.char_width_label = QtGui.QLabel(self.char_prop_frame)
        self.char_width_label.setText("Character width:")

        self.char_width_spin = QtGui.QDoubleSpinBox(self.char_prop_frame)
        self.char_width_spin.setMinimum(2)
        self.char_width_spin.setMaximum(10)
        self.char_width_spin.setValue(4.0)
        self.char_width_spin.setWrapping(True)
        self.char_width_spin.setDecimals(1)
        self.char_width_spin.setSingleStep(0.5)
        QtCore.QObject.connect(self.char_width_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_width_changed_cb)

        self.left_space_label = QtGui.QLabel(self.char_prop_frame)
        self.left_space_label.setText("Left spacing:")

        self.left_space_spin = QtGui.QDoubleSpinBox(self.char_prop_frame)
        self.left_space_spin.setMinimum(0)
        self.left_space_spin.setMaximum(3)
        self.left_space_spin.setValue(1.0)
        self.left_space_spin.setWrapping(True)
        self.left_space_spin.setDecimals(1)
        self.left_space_spin.setSingleStep(0.1)
        QtCore.QObject.connect(self.left_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_left_space_changed_cb)

        self.right_space_label = QtGui.QLabel(self.char_prop_frame)
        self.right_space_label.setText("Right spacing:")

        self.right_space_spin = QtGui.QDoubleSpinBox(self.char_prop_frame)
        self.right_space_spin.setMinimum(0)
        self.right_space_spin.setMaximum(3)
        self.right_space_spin.setValue(1.0)
        self.right_space_spin.setWrapping(True)
        self.right_space_spin.setDecimals(1)
        self.right_space_spin.setSingleStep(0.1)
        QtCore.QObject.connect(self.right_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_right_space_changed_cb)

        self.override_char_set = QtGui.QCheckBox(self.char_prop_frame)
        self.override_char_set.setText("Override Character Set")
        QtCore.QObject.connect(self.override_char_set, \
            QtCore.SIGNAL("stateChanged(int)"), \
            self.__parent.override_char_set_changed_cb)

        self.char_prop_layout.addRow(self.override_char_set)
        self.char_prop_layout.addRow(self.main_char_prop_label)
        self.char_prop_layout.addRow(self.char_width_label, self.char_width_spin)
        self.char_prop_layout.addRow(self.left_space_label, self.left_space_spin)
        self.char_prop_layout.addRow(self.right_space_label, self.right_space_spin)

        self.stroke_prop_frame = QtGui.QFrame(self.tool_pane)
        self.stroke_prop_layout = QtGui.QFormLayout(self.stroke_prop_frame)

        self.position_label = QtGui.QLabel(self.stroke_prop_frame)
        self.position_label.setText("Position")

        self.stroke_prop_layout.addRow(self.position_label)

        self.position_x_label = QtGui.QLabel(self.stroke_prop_frame)
        self.position_x_label.setText("X")

        self.position_x_spin = QtGui.QDoubleSpinBox(self.stroke_prop_frame)
        self.position_x_spin.setValue(0.0)
        self.position_x_spin.setWrapping(False)
        self.position_x_spin.setDecimals(1)
        self.position_x_spin.setSingleStep(1.0)
        self.position_x_spin.setMinimum(-100000)
        self.position_x_spin.setMaximum(100000)
        self.position_x_spin.setKeyboardTracking(False)
        QtCore.QObject.connect(self.position_x_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.position_x_changed_cb)

        self.position_y_label = QtGui.QLabel(self.stroke_prop_frame)
        self.position_y_label.setText("Y")

        self.position_y_spin = QtGui.QDoubleSpinBox(self.stroke_prop_frame)
        self.position_y_spin.setValue(0.0)
        self.position_y_spin.setWrapping(False)
        self.position_y_spin.setDecimals(1)
        self.position_y_spin.setSingleStep(1.0)
        self.position_y_spin.setMinimum(-100000)
        self.position_y_spin.setMaximum(100000)
        self.position_y_spin.setKeyboardTracking(False)
        QtCore.QObject.connect(self.position_y_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.position_y_changed_cb)

        self.stroke_prop_layout.addRow(self.position_x_label, self.position_x_spin)
        self.stroke_prop_layout.addRow(self.position_y_label, self.position_y_spin)

        self.behavior_label = QtGui.QLabel(self.stroke_prop_frame)
        self.behavior_label.setText("Vertex Behavior")

        self.behavior_combo = QtGui.QComboBox(self.stroke_prop_frame)
        self.behavior_combo.addItem("--")
        self.behavior_combo.addItem("Smooth")
        self.behavior_combo.addItem("Sharp")
        self.behavior_combo.addItem("Symmetric")
        self.behavior_combo.setCurrentIndex(0)
        QtCore.QObject.connect(self.behavior_combo, \
            QtCore.SIGNAL("currentIndexChanged(int)"), \
            self.__parent.vert_behavior_combo_changed_cb)

        self.stroke_prop_layout.addRow(self.behavior_label, self.behavior_combo)

        self.stroke_override_nib_angle = QtGui.QCheckBox(self.stroke_prop_frame)
        self.stroke_override_nib_angle.setText("Override Character Set")
        QtCore.QObject.connect(self.stroke_override_nib_angle, \
            QtCore.SIGNAL("stateChanged(int)"), \
            self.__parent.stroke_override_nib_angle_changed_cb)

        self.stroke_prop_layout.addRow(self.stroke_override_nib_angle)

        self.stroke_nib_angle_label = QtGui.QLabel(self.stroke_prop_frame)
        self.stroke_nib_angle_label.setText("Nib Angle:")

        self.stroke_nib_angle_spin = QtGui.QDoubleSpinBox(self.stroke_prop_frame)
        self.stroke_nib_angle_spin.setMinimum(0)
        self.stroke_nib_angle_spin.setMaximum(90)
        self.stroke_nib_angle_spin.setValue(40)
        self.stroke_nib_angle_spin.setWrapping(True)
        self.stroke_nib_angle_spin.setDecimals(0)
        self.stroke_nib_angle_spin.setSingleStep(1.0)
        QtCore.QObject.connect(self.stroke_nib_angle_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.stroke_nib_angle_changed_cb)

        self.stroke_prop_layout.addRow(self.stroke_nib_angle_label, self.stroke_nib_angle_spin)

        self.property_tabs = QtGui.QTabWidget(self.tool_pane)
        self.property_tabs.addTab(self.stroke_prop_frame, "Stroke")
        self.property_tabs.addTab(self.char_prop_frame, "Character")
        self.property_tabs.addTab(self.char_set_prop_frame, "Character Set")

        self.tool_pane_layout.addWidget(self.property_tabs)
        self.tool_pane_layout.setMargin(0)
        self.tool_pane_layout.setSpacing(5)
        self.tool_pane_layout.setContentsMargins(0, 0, 0, 0)

        self.stroke_dwg_area.set_origin_delta(QtCore.QPoint())

        self.main_view_tabs = QtGui.QTabWidget(self.main_widget)
        self.main_view_tabs.addTab(self.dwg_area, "Character")
        self.main_view_tabs.addTab(self.stroke_dwg_area, "Glyph")
        self.main_view_tabs.addTab(self.preview_area, "Preview")
        self.main_view_tabs.setTabEnabled(self.main_view_tabs.indexOf(self.stroke_dwg_area), False)
        self.main_view_tabs.currentChanged.connect(self.__parent.view_tab_changed_cb)

        self.main_splitter.addWidget(self.main_view_tabs)
        self.main_splitter.addWidget(self.side_splitter)

        self.side_splitter.addWidget(self.tool_pane)
        self.side_splitter.addWidget(self.bottom_pane)
        self.side_splitter.setCollapsible(0, False)
        self.side_splitter.setCollapsible(1, True)
        self.side_splitter.setMaxPaneSize(self.height() / 2)
        self.side_splitter.setSizes([self.height(), 0])

        self.main_splitter.setMaxPaneSize(wid20)
        self.main_splitter.setSizes([wid80, wid20])

        self.view_layout.addWidget(self.main_splitter)
        self.view_layout.setMargin(0)
        self.view_layout.setSpacing(5)
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        main_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, \
            QtGui.QSizePolicy.Expanding)
        self.main_splitter.setSizePolicy(main_size_policy)
        self.side_splitter.setSizePolicy(main_size_policy)

        self.dwg_area.setSizePolicy(main_size_policy)
        self.stroke_dwg_area.setSizePolicy(main_size_policy)

        self.main_layout.addLayout(self.char_selector_layout)
        self.main_layout.addLayout(self.view_layout, 2)

        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        self.guide_lines = guides.GuideLines()
        self.guide_lines.nib_width = self.dwg_area.nib.width * 2
        self.dwg_area.set_guidelines(self.guide_lines)
        self.stroke_dwg_area.set_guidelines(self.guide_lines)
        self.preview_area.set_guidelines(self.guide_lines)

    def create_menu(self):
        self.tool_bar = self.addToolBar("main")
        self.tool_bar.resize(self.width(), ICON_SIZE+ICON_TEXT_SIZE)
        self.tool_bar.setFloatable(False)
        self.tool_bar.setMovable(False)
        self.tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.file_menu = self.main_menu.addMenu('&File')
        self.edit_menu = self.main_menu.addMenu('&Edit')
        self.view_menu = self.main_menu.addMenu('&View')
        self.stroke_menu = self.main_menu.addMenu('Stro&ke')
        self.glyph_menu = self.main_menu.addMenu('&Glyph')
        self.help_menu = self.main_menu.addMenu('&Help')

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
        self.stroke_delete.setEnabled(False)
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
        self.stroke_menu.addAction(self.stroke_join)

        self.stroke_flip_x = QtGui.QAction("Flip X", self)
        self.stroke_flip_x.setStatusTip('flip stroke horizontally')
        self.stroke_flip_x.setEnabled(True)
        self.stroke_flip_x.triggered.connect(self.__parent.flip_stroke_x_cb)
        self.stroke_menu.addAction(self.stroke_flip_x)

        self.stroke_flip_y = QtGui.QAction("Flip Y", self)
        self.stroke_flip_y.setStatusTip('flip stroke vertically')
        self.stroke_flip_y.setEnabled(True)
        self.stroke_flip_y.triggered.connect(self.__parent.flip_stroke_y_cb)
        self.stroke_menu.addAction(self.stroke_flip_y)

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

        self.stroke_save = QtGui.QAction("Save Stroke(s) as Glyph", self)
        self.stroke_save.setEnabled(False)
        self.stroke_save.triggered.connect(self.__parent.save_glyph_cb)
        self.glyph_menu.addAction(self.stroke_save)

        self.stroke_load = QtGui.QAction("Paste From Saved", self)
        self.stroke_load.setEnabled(False)
        self.stroke_load.triggered.connect(self.__parent.paste_glyph_from_saved_cb)
        self.glyph_menu.addAction(self.stroke_load)

        self.glyph_delete = QtGui.QAction("Delete Saved", self)
        self.glyph_delete.setEnabled(False)
        self.glyph_delete.triggered.connect(self.__parent.delete_saved_glyph_cb)
        self.glyph_menu.addAction(self.glyph_delete)

        self.help_about = QtGui.QAction("About", self)
        self.help_about.triggered.connect(self.about_cb)
        self.help_menu.addAction(self.help_about)

    def about_cb(self, event):
        reply = QtGui.QMessageBox.information(self, 'About PyTalic Editor', \
            "PyTalic Editor\nby Dale Cieslak\n(c) 2007-2018" + \
            "\n\nhttps://github.com/dsizzle/pytalic2", \
            QtGui.QMessageBox.Ok)

    def mouseMoveEvent(self, event):
        self.__parent.mouse_event(event)

    def mousePressEvent(self, event):
        self.__parent.mouse_event(event)

    def mouseReleaseEvent(self, event):
        self.__parent.mouse_event(event)

    def wheelEvent(self, event):
        self.__parent.wheel_event(event)

    def paintEvent(self, event):
        QtGui.QMainWindow.paintEvent(self, event)

    def closeEvent(self, event):
        close = self.__parent.quit_cb(event)

        if close:
            event.accept()
        else:
            event.ignore()
