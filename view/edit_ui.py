#!/usr/bin/python
#

from PyQt4 import QtCore, QtGui, uic

import pytalic2_ui

from model import guides
import view.paper
import view.widgets_qt

ICON_SIZE = 40
ICON_TEXT_SIZE = 30

class EditInterface(QtGui.QMainWindow, pytalic2_ui.Ui_MainWindow):
    def __init__(self, parent, width, height, label):
        QtGui.QMainWindow.__init__(self)
       
        self.message_dialog = QtGui.QMessageBox()
        self.file_open_dialog = QtGui.QFileDialog()
        self.file_save_dialog = QtGui.QFileDialog()
        self.__parent = parent

        self.setupUi(self)

        self.setWindowTitle(label)

        self.setAcceptDrops(True)

    def create_ui(self):
        
        self.char_selector_list.currentItemChanged.connect(self.__parent.char_selected_cb)
        
        self.stroke_selector_list.currentItemChanged.connect(self.__parent.stroke_selected_cb)

        QtCore.QObject.connect(self.base_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_base_height_changed_cb)
        
        QtCore.QObject.connect(self.cap_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_cap_height_changed_cb)

        QtCore.QObject.connect(self.ascent_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_ascent_changed_cb)

        QtCore.QObject.connect(self.descent_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_descent_changed_cb)

        QtCore.QObject.connect(self.angle_spin, \
            QtCore.SIGNAL("valueChanged(int)"), \
            self.__parent.guide_angle_changed_cb)

        QtCore.QObject.connect(self.gap_height_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_gap_height_changed_cb)

        QtCore.QObject.connect(self.nominal_width_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.guide_nominal_width_changed_cb)

        QtCore.QObject.connect(self.char_set_left_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_set_left_space_changed_cb)

        QtCore.QObject.connect(self.char_set_right_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_set_right_space_changed_cb)

        self.guides_color_button.setColor(QtGui.QColor(200, 195, 180))
        QtCore.QObject.connect(self.guides_color_button, \
            QtCore.SIGNAL("valueChanged(QColor)"), \
            self.__parent.guide_color_changed_cb)
        
        QtCore.QObject.connect(self.char_set_nib_angle_spin, \
            QtCore.SIGNAL("valueChanged(int)"), \
            self.__parent.char_set_nib_angle_changed_cb)

        QtCore.QObject.connect(self.char_width_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_width_changed_cb)

        QtCore.QObject.connect(self.left_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_left_space_changed_cb)

        QtCore.QObject.connect(self.right_space_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.char_right_space_changed_cb)

        QtCore.QObject.connect(self.override_char_set, \
            QtCore.SIGNAL("stateChanged(int)"), \
            self.__parent.override_char_set_changed_cb)

        QtCore.QObject.connect(self.position_x_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.position_x_changed_cb)

        QtCore.QObject.connect(self.position_y_spin, \
            QtCore.SIGNAL("valueChanged(double)"), \
            self.__parent.position_y_changed_cb)

        QtCore.QObject.connect(self.behavior_combo, \
            QtCore.SIGNAL("currentIndexChanged(int)"), \
            self.__parent.vert_behavior_combo_changed_cb)

        QtCore.QObject.connect(self.stroke_override_nib_angle, \
            QtCore.SIGNAL("stateChanged(int)"), \
            self.__parent.stroke_override_nib_angle_changed_cb)

        QtCore.QObject.connect(self.stroke_nib_angle_spin, \
            QtCore.SIGNAL("valueChanged(int)"), \
            self.__parent.stroke_nib_angle_changed_cb)

        self.create_menu()

        self.stroke_dwg_area.set_origin_delta(QtCore.QPoint())

        self.main_view_tabs.currentChanged.connect(self.__parent.view_tab_changed_cb)

        self.guide_lines = guides.GuideLines()
        self.guide_lines.nib_width = self.dwg_area.nib.width * 2
        self.dwg_area.set_guidelines(self.guide_lines)
        self.stroke_dwg_area.set_guidelines(self.guide_lines)
        self.preview_area.set_guidelines(self.guide_lines)

    def create_menu(self):
        self.file_new.triggered.connect(self.__parent.file_new_cb)
        self.file_open.triggered.connect(self.__parent.file_open_cb)
        self.file_save.triggered.connect(self.__parent.file_save_cb)
        self.file_save_as.triggered.connect(self.__parent.file_save_as_cb)
        self.file_quit.triggered.connect(self.__parent.quit_cb)
       
        self.edit_undo.triggered.connect(self.__parent.undo_cb)
        self.edit_redo.triggered.connect(self.__parent.redo_cb)
        self.edit_cut.triggered.connect(self.__parent.cut_strokes_cb)
        self.edit_copy.triggered.connect(self.__parent.copy_strokes_cb)
        self.edit_paste.triggered.connect(self.__parent.paste_strokes_cb)
        
        self.view_reset_origin.triggered.connect(self.__parent.view_reset_origin_cb)
        self.view_reset_zoom.triggered.connect(self.__parent.view_reset_zoom_cb)
        self.view_guides.triggered.connect(self.__parent.view_toggle_guidelines_cb)
        self.view_nib_guides.triggered.connect(self.__parent.view_toggle_nib_guides_cb)
        self.view_snap_to_axes.triggered.connect(self.__parent.view_toggle_snap_axially_cb)
        self.view_snap_to_nib_axes.triggered.connect(self.__parent.view_toggle_snap_to_nib_axes_cb)
        self.view_snap_to_grid.triggered.connect(self.__parent.view_toggle_snap_to_grid_cb)
        self.view_snap_to_ctrl_pts.triggered.connect(self.__parent.view_toggle_snap_to_ctrl_pts_cb)
        
        self.stroke_new.triggered.connect(self.__parent.create_new_stroke_cb)
        self.stroke_delete.triggered.connect(self.__parent.delete_strokes_cb)
        self.stroke_straighten.triggered.connect(self.__parent.straighten_stroke_cb)
        self.stroke_join.triggered.connect(self.__parent.join_strokes_cb)
        self.stroke_flip_x.triggered.connect(self.__parent.flip_stroke_x_cb)
        self.stroke_flip_y.triggered.connect(self.__parent.flip_stroke_y_cb)
        self.stroke_align_tangents.triggered.connect(self.__parent.align_tangents_symmetrical_cb)
        self.stroke_smooth_tangents.triggered.connect(self.__parent.align_tangents_cb)
        self.stroke_sharpen_tangents.triggered.connect(self.__parent.break_tangents_cb)
        self.stroke_add_vertex.triggered.connect(self.__parent.add_control_point_cb)
        self.stroke_split_at_point.triggered.connect(self.__parent.split_at_point_cb)

        self.stroke_save.triggered.connect(self.__parent.save_glyph_cb)
        self.stroke_load.triggered.connect(self.__parent.paste_glyph_from_saved_cb)
        self.glyph_delete.triggered.connect(self.__parent.delete_saved_glyph_cb)
        
        self.help_about.triggered.connect(self.about_cb)
        
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()
        
    def dropEvent(self, event):
        if self.dwg_area.rect().contains(event.pos()) and self.dwg_area.underMouse():
            stroke_ctrl = self.__parent.get_stroke_controller()
            stroke_ctrl.paste_glyph_from_saved()
            