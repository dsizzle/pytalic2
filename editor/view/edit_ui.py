#!/usr/bin/python
#

from PyQt5 import QtCore, QtGui, uic, QtWidgets

import editor.pytalic2_editor_ui

from editor.model import guides


ICON_SIZE = 40
ICON_TEXT_SIZE = 30

class EditInterface(QtWidgets.QMainWindow, editor.pytalic2_editor_ui.Ui_MainWindow):
    def __init__(self, parent, width, height, label):
        QtWidgets.QMainWindow.__init__(self)
       
        self.message_dialog = QtWidgets.QMessageBox()
        self.file_open_dialog = QtWidgets.QFileDialog()
        self.file_save_dialog = QtWidgets.QFileDialog()
        self.__parent = parent

        self.setupUi(self)
        self.__dwg_context_menu = QtWidgets.QMenu()
        self.__glyph_context_menu = QtWidgets.QMenu()
        self.setWindowTitle(label)

        self.setAcceptDrops(True)

    def create_ui(self):
        
        self.char_selector_list.currentItemChanged.connect(self.__parent.char_selected_cb)
        
        self.stroke_selector_list.currentItemChanged.connect(self.__parent.stroke_selected_cb)

        self.base_height_spin.valueChanged.connect( \
            self.__parent.guide_base_height_changed_cb)
        
        self.cap_height_spin.valueChanged.connect( \
            self.__parent.guide_cap_height_changed_cb)

        self.ascent_height_spin.valueChanged.connect( \
            self.__parent.guide_ascent_changed_cb)

        self.descent_height_spin.valueChanged.connect( \
            self.__parent.guide_descent_changed_cb)

        self.angle_spin.valueChanged.connect( \
            self.__parent.guide_angle_changed_cb)

        self.gap_height_spin.valueChanged.connect( \
            self.__parent.guide_gap_height_changed_cb)

        self.nominal_width_spin.valueChanged.connect( \
            self.__parent.guide_nominal_width_changed_cb)

        self.char_set_left_space_spin.valueChanged.connect( \
            self.__parent.char_set_left_space_changed_cb)

        self.char_set_right_space_spin.valueChanged.connect( \
            self.__parent.char_set_right_space_changed_cb)

        self.guides_color_button.setColor(QtGui.QColor(200, 195, 180))
        self.guides_color_button.colorChanged.connect( \
            self.__parent.guide_color_changed_cb)
        
        self.char_set_nib_angle_spin.valueChanged[int].connect( \
            self.__parent.char_set_nib_angle_changed_cb)

        self.char_width_spin.valueChanged.connect( \
            self.__parent.char_width_changed_cb)

        self.left_space_spin.valueChanged.connect( \
            self.__parent.char_left_space_changed_cb)

        self.right_space_spin.valueChanged.connect( \
            self.__parent.char_right_space_changed_cb)

        self.override_char_set.stateChanged[int].connect( \
            self.__parent.override_char_set_changed_cb)

        self.position_x_spin.valueChanged.connect( \
            self.__parent.position_x_changed_cb)

        self.position_y_spin.valueChanged.connect( \
            self.__parent.position_y_changed_cb)

        self.vertex_x_spin.valueChanged.connect( \
            self.__parent.vertex_x_changed_cb)

        self.vertex_y_spin.valueChanged.connect( \
            self.__parent.vertex_y_changed_cb)

        self.behavior_combo.activated[int].connect( \
            self.__parent.vert_behavior_combo_changed_cb)

        self.stroke_nib_combo.activated[int].connect( \
            self.__parent.stroke_nib_combo_changed_cb)

        self.stroke_override_nib_angle.stateChanged[int].connect( \
            self.__parent.stroke_override_nib_angle_changed_cb)

        self.stroke_nib_angle_spin.valueChanged[int].connect( \
            self.__parent.stroke_nib_angle_changed_cb)

        self.layout_reset_button.clicked.connect( \
            self.__parent.layout_update_cb)

        self.layout_combo.currentIndexChanged[int].connect( \
            self.__parent.layout_changed_cb)

        self.frame_layout_button.clicked.connect( \
            self.__parent.layout_frame_cb)
        
        self.create_menu()

        self.stroke_dwg_area.set_origin_delta(QtCore.QPoint())

        self.main_view_tabs.currentChanged.connect(self.__parent.view_tab_changed_cb)

        self.guide_lines = guides.GuideLines()
        self.guide_lines_fixed = guides.GuideLines()
        self.dwg_area.set_guidelines(self.guide_lines)
        self.stroke_dwg_area.set_guidelines(self.guide_lines)
        self.preview_area.set_guidelines(self.guide_lines_fixed)

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
        self.edit_select_all.triggered.connect(self.__parent.select_all_strokes_cb)
        self.edit_deselect_all.triggered.connect(self.__parent.deselect_all_strokes_cb)
        self.edit_preferences.triggered.connect(self.__parent.preferences_cb)
        
        self.view_reset_origin.triggered.connect(self.__parent.view_reset_origin_cb)
        self.view_reset_zoom.triggered.connect(self.__parent.view_reset_zoom_cb)
        self.view_guides.triggered.connect(self.__parent.view_toggle_guidelines_cb)
        self.view_nib_guides.triggered.connect(self.__parent.view_toggle_nib_guides_cb)
        self.view_snap_to_axes.triggered.connect(self.__parent.view_toggle_snap_axially_cb)
        self.view_snap_to_nib_axes.triggered.connect(self.__parent.view_toggle_snap_to_nib_axes_cb)
        self.view_snap_to_grid.triggered.connect(self.__parent.view_toggle_snap_to_grid_cb)
        self.view_snap_to_ctrl_pts.triggered.connect(self.__parent.view_toggle_snap_to_ctrl_pts_cb)
        self.action_constrain_to_x_axis.triggered.connect(self.__parent.action_toggle_constrain_x_cb)
        self.action_constrain_to_y_axis.triggered.connect(self.__parent.action_toggle_constrain_y_cb)
        
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
        
        self.__dwg_context_menu.addAction(self.edit_cut)
        self.__dwg_context_menu.addAction(self.edit_copy)
        self.__dwg_context_menu.addAction(self.edit_paste)
        self.__dwg_context_menu.addSeparator()
        self.__dwg_context_menu.addAction(self.edit_select_all)
        self.__dwg_context_menu.addAction(self.edit_deselect_all)
        self.__dwg_context_menu.addSeparator()
        self.__dwg_context_menu.addAction(self.stroke_straighten)
        self.__dwg_context_menu.addAction(self.stroke_join)
        self.__dwg_context_menu.addAction(self.stroke_flip_x)
        self.__dwg_context_menu.addAction(self.stroke_flip_y)
        self.__dwg_context_menu.addSeparator()
        self.__dwg_context_menu.addAction(self.stroke_add_vertex)
        self.__dwg_context_menu.addAction(self.stroke_split_at_point)
        self.__dwg_context_menu.addSeparator()
        self.__dwg_context_menu.addAction(self.stroke_save)

        self.__glyph_context_menu.addAction(self.edit_cut)
        self.__glyph_context_menu.addAction(self.edit_copy)
        self.__glyph_context_menu.addAction(self.edit_paste)
        self.__glyph_context_menu.addSeparator()
        self.__glyph_context_menu.addAction(self.edit_select_all)
        self.__glyph_context_menu.addAction(self.edit_deselect_all)
        self.__glyph_context_menu.addSeparator()
        self.__glyph_context_menu.addAction(self.stroke_straighten)
        self.__glyph_context_menu.addAction(self.stroke_join)
        self.__glyph_context_menu.addAction(self.stroke_flip_x)
        self.__glyph_context_menu.addAction(self.stroke_flip_y)
        self.__glyph_context_menu.addSeparator()
        self.__glyph_context_menu.addAction(self.stroke_add_vertex)
        self.__glyph_context_menu.addAction(self.stroke_split_at_point)

    def about_cb(self, event):
        reply = QtWidgets.QMessageBox.information(self, 'About PyTalic Editor', \
            "PyTalic Editor\nby Dale Cieslak\n(c) 2007-2018" + \
            "\n\nhttps://github.com/dsizzle/pytalic2", \
            QtWidgets.QMessageBox.Ok)

    def mouseMoveEvent(self, event):
        self.__parent.mouse_event(event)

    def mousePressEvent(self, event):
        self.__parent.mouse_event(event)

    def mouseReleaseEvent(self, event):
        self.__parent.mouse_event(event)

    def wheelEvent(self, event):
        self.__parent.wheel_event(event)

    def keyReleaseEvent(self, event):
        self.__parent.key_event(event)

    def paintEvent(self, event):
        QtWidgets.QMainWindow.paintEvent(self, event)

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
            
    def contextMenuEvent(self, event):
        if self.__parent.state > 0:
            event.ignore() 
            return

        if self.dwg_area.rect().contains(event.pos()) and self.dwg_area.hasFocus():
            self.__dwg_context_menu.exec_(event.globalPos())
        elif self.stroke_dwg_area.rect().contains(event.pos()) and self.stroke_dwg_area.hasFocus():
            self.__glyph_context_menu.exec_(event.globalPos())
