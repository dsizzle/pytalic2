"""
edit_control.py

The main controller module for pyTalic Editor.

Contains EditorController class.
"""

from PyQt4 import QtGui, QtCore

import control.clipboard_operations
import control.file_operations
import control.mouse_operations
import control.property_operations
import control.snap_operations
import control.stroke_operations
import control.vertex_operations
from model import character_set, character, commands, instance, layout, stroke
from view import edit_ui
import view.shared_qt

IDLE = 0
MOVING_PAPER = 1
DRAWING_NEW_STROKE = 2
DRAGGING = 3
ADDING_CTRL_POINT = 4
SPLIT_AT_POINT = 5

START_CHAR_CODE = 32
END_CHAR_CODE = 128

class EditorController(object):
    """
    EditorController is the main Controller for pyTalic Editor
    """
    def __init__(self, w, h, label):
        self.__label = label
        self.__ui = edit_ui.EditInterface(self, w, h, label)

        self.__color = QtGui.QColor(125, 25, 25)

        self.__cmd_stack = commands.CommandStack()
        self.__selection = {}
        self.__char_set = None
        self.__cur_char = None

        self.__state = 0

        char_list = []
        for i in range(START_CHAR_CODE, END_CHAR_CODE):
            char_list.append(str(unichr(i)))

        self.__ui.create_ui()
        self.__ui.char_selector_list.addItems(QtCore.QStringList(char_list))

        self.__ui.dwg_area.bitmap_size = view.shared_qt.ICON_SIZE

        self.__current_view_pane = self.__ui.main_view_tabs.currentWidget()
        self.__selection[self.__current_view_pane] = {}

        self.__clipboard_controller = control.clipboard_operations.ClipboardController(self)
        self.__file_controller = control.file_operations.FileController(self)
        self.__property_controller = control.property_operations.PropertyController(self)
        self.__mouse_controller = control.mouse_operations.MouseController(self)
        self.__snap_controller = control.snap_operations.SnapController(self)
        self.__stroke_controller = control.stroke_operations.StrokeController(self)
        self.__vertex_controller = control.vertex_operations.VertexController(self)

        self.file_new_cb(None)
        
        self.__layout_abc = layout.Layout()
        self.__layout_abc.init_with_string("TEST", self.__char_set, \
            nib_width=self.__ui.dwg_area.nib.width * 2)

        self.__ui.preview_area.layout = self.__layout_abc

    def get_command_stack(self):
        return self.__cmd_stack

    def get_ui(self):
        return self.__ui

    def get_current_view(self):
        return self.__current_view_pane

    def get_selection(self):
        return self.__selection

    def get_current_char(self):
        return self.__cur_char

    def get_character_set(self):
        return self.__char_set

    def set_character_set(self, new_char_set):
        self.__char_set = new_char_set

    def get_state(self):
        return self.__state

    def set_state(self, new_state):
        self.__state = new_state

    state = property(get_state, set_state)

    def get_snap_controller(self):
        return self.__snap_controller

    def get_stroke_controller(self):
        return self.__stroke_controller

    def activate(self):
        self.__ui.show()
        self.__ui.activateWindow()
        self.__ui.raise_()

    def mouse_event(self, event):
        self.__mouse_controller.mouse_event(event)

    def wheel_event(self, event):
        self.__mouse_controller.wheel_event(event)

    def quit_cb(self, event):
        close = False
        if self.__cmd_stack.save_count == 0:
            self.__ui.close()
            close = True
        else:
            reply = self.__ui.message_dialog.question(self.__ui, \
                'Quit Program', \
                "You have unsaved changes. Are you sure you want to quit?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
                QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                self.__ui.close()
                close = True

        return close

    def undo_cb(self, event):
        self.__cmd_stack.undo()
        if self.__cmd_stack.undo_is_empty():
            self.__ui.edit_undo.setEnabled(False)
        self.__ui.edit_redo.setEnabled(True)
        self.__ui.repaint()

    def redo_cb(self, event):
        self.__cmd_stack.redo()
        if self.__cmd_stack.redo_is_empty():
            self.__ui.edit_redo.setEnabled(False)
        self.__ui.edit_undo.setEnabled(True)
        self.__ui.repaint()

    def file_new_cb(self, event):
        self.__file_controller.file_new()

        self.name = (self.__label + " - Untitled")
        self.__ui.setWindowTitle(self.name)

        self.__cur_char = self.__char_set.current_char

        self.__cmd_stack = commands.CommandStack()

    def file_save_as_cb(self, event):
        file_path = self.__file_controller.file_save_as()
        self.__ui.setWindowTitle(self.__label + " - " + file_path)

    def file_save_cb(self, event):
        self.__file_controller.file_save()

    def file_open_cb(self):
        file_path = self.__file_controller.file_open()

        self.__ui.setWindowTitle(self.__label + " - " + file_path)

        self.__selection[self.__current_view_pane] = {}
        self.__ui.repaint()

        self.__layout_abc = layout.Layout()
        self.__layout_abc.init_with_string("TEST", self.__char_set, \
            nib_width=self.__ui.dwg_area.nib.width * 2)

        self.__ui.preview_area.layout = self.__layout_abc

    def create_new_stroke_cb(self, event):
        self.__stroke_controller.create_new_stroke()
        
    def save_glyph_cb(self, event):
        self.__stroke_controller.save_glyph()
        self.__ui.main_view_tabs.setTabEnabled(self.__ui.main_view_tabs.indexOf(self.__ui.stroke_dwg_area), \
            True)

    def add_control_point_cb(self, event):
        self.state = ADDING_CTRL_POINT
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

    def split_at_point_cb(self, event):
        self.state = SPLIT_AT_POINT
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

    def delete_strokes_cb(self, event):
        selected_verts = 0
        for sel_stroke in self.__selection[self.__current_view_pane].keys():
            selected_verts += len(self.__selection[self.__current_view_pane][sel_stroke])

        if selected_verts > 0:
            self.__stroke_controller.delete_control_vertices()
        else:
            self.cut_strokes_cb(event)

    def cut_strokes_cb(self, event):
        self.__clipboard_controller.cut_strokes()

    def copy_strokes_cb(self, event):
        self.__clipboard_controller.copy_strokes()

    def paste_strokes_cb(self, event):
        self.__clipboard_controller.paste_strokes()

    def paste_glyph_from_saved_cb(self, event):
        self.__stroke_controller.paste_glyph_from_saved()

    def delete_saved_glyph_cb(self, event):
        self.__stroke_controller.delete_saved_glyph()

    def view_toggle_snap_axially_cb(self, event):
        self.__snap_controller.toggle_snap_axially()

    def view_toggle_snap_to_grid_cb(self, event):
        self.__snap_controller.toggle_snap_to_grid()

    def view_toggle_snap_to_nib_axes_cb(self, event):
        self.__snap_controller.toggle_snap_to_nib_axes()

    def view_toggle_snap_to_ctrl_pts_cb(self, event):
        self.__snap_controller.toggle_snap_to_ctrl_pts()

    def view_toggle_guidelines_cb(self, event):
        self.__current_view_pane.draw_guidelines = not self.__current_view_pane.draw_guidelines
        self.__ui.repaint()

    def view_toggle_nib_guides_cb(self, event):
        self.__current_view_pane.draw_nib_guides = not self.__current_view_pane.draw_nib_guides
        self.__ui.repaint()

    def view_reset_origin_cb(self, event):
        self.__current_view_pane.origin_delta = QtCore.QPoint(0, 0)
        self.__ui.repaint()

    def view_reset_zoom_cb(self, event):
        self.__current_view_pane.scale = 1
        self.__ui.repaint()

    def set_ui_state_selection(self, state):
        self.__ui.stroke_add_vertex.setEnabled(state)
        self.__ui.stroke_split_at_point.setEnabled(state)
        if self.__current_view_pane == self.__ui.dwg_area:
            self.__ui.stroke_save.setEnabled(state)
        self.__ui.stroke_delete.setEnabled(state)
        self.__ui.edit_cut.setEnabled(state)
        self.__ui.edit_copy.setEnabled(state)
        self.__ui.stroke_straighten.setEnabled(state)
        self.__ui.stroke_join.setEnabled(state)
        self.__ui.stroke_align_tangents.setEnabled(state)
        self.__ui.stroke_smooth_tangents.setEnabled(state)
        self.__ui.stroke_sharpen_tangents.setEnabled(state)

    def straighten_stroke_cb(self, event):
        self.__stroke_controller.straighten_stroke()

    def join_strokes_cb(self, event):
        self.__stroke_controller.join_selected_strokes()

    def flip_stroke_x_cb(self, event):
        self.__stroke_controller.flip_selected_strokes_x()

    def flip_stroke_y_cb(self, event):
        self.__stroke_controller.flip_selected_strokes_y()

    def char_selected_cb(self, event):
        cur_char_idx = self.__ui.char_selector_list.currentRow()
        
        self.__char_set.current_char = cur_char_idx + START_CHAR_CODE
        self.__cur_char = self.__char_set.current_char
        self.__ui.dwg_area.strokes = []
        self.__ui.dwg_area.symbol = self.__cur_char
        
        self.__ui.left_space_spin.setValue(self.__cur_char.left_spacing)
        self.__ui.right_space_spin.setValue(self.__cur_char.right_spacing)
        self.__ui.char_width_spin.setValue(self.__cur_char.width)
        check_state = QtCore.Qt.Unchecked
        if self.__cur_char.override_spacing:
            check_state = QtCore.Qt.Checked
        self.__ui.override_char_set.setCheckState(check_state)
        self.override_char_set_changed_cb(check_state)
        self.__ui.repaint()
        self.set_icon()

    def stroke_selected_cb(self, event):
        if self.__ui.stroke_selector_list.currentRow() >= 0:
            sel_saved_glyph = self.__char_set.get_saved_glyph(self.__ui.stroke_selector_list.currentRow())

            self.__ui.stroke_dwg_area.symbol = sel_saved_glyph
            self.__ui.main_view_tabs.setTabEnabled(self.__ui.main_view_tabs.indexOf(self.__ui.stroke_dwg_area), \
                True)
        else:
            self.__ui.stroke_dwg_area.symbol = None
            self.__ui.main_view_tabs.setTabEnabled(self.__ui.main_view_tabs.indexOf(self.__ui.stroke_dwg_area), \
                False)

        self.__ui.repaint()
        self.set_icon()

    def view_tab_changed_cb(self, event):
        previous_pane = self.__current_view_pane
        self.__current_view_pane = self.__ui.main_view_tabs.currentWidget()
        self.__ui.view_guides.setChecked(self.__current_view_pane.draw_guidelines)

        if self.__current_view_pane == self.__ui.dwg_area:
            self.__ui.stroke_new.setEnabled(True)
            if len(self.__selection.keys()):
                self.set_ui_state_selection(True)
            if self.__ui.stroke_selector_list.count() > 0:
                self.__ui.stroke_load.setEnabled(True)
                self.__ui.glyph_delete.setEnabled(True)
            if previous_pane == self.__ui.stroke_dwg_area:
                previous_pane.symbol.calculate_bound_rect()
        elif self.__current_view_pane == self.__ui.stroke_dwg_area:
            self.__ui.stroke_new.setEnabled(True)
            self.__ui.stroke_delete.setEnabled(True)
            self.__current_view_pane.symbol.selected = False
            self.__ui.stroke_save.setEnabled(False)
            self.__ui.stroke_load.setEnabled(False)
            self.__ui.glyph_delete.setEnabled(False)
        elif self.__current_view_pane == self.__ui.preview_area:
            self.__ui.stroke_new.setEnabled(False)
            self.__ui.view_nib_guides.setEnabled(False)
            self.__ui.stroke_save.setEnabled(False)
            self.__ui.stroke_load.setEnabled(False)
            self.__ui.glyph_delete.setEnabled(False)
            self.__ui.preview_area.layout.update_layout(self.__char_set, \
                nib_width=self.__ui.dwg_area.nib.width * 2)
        else:
            self.__ui.view_nib_guides.setEnabled(True)
            self.__ui.view_nib_guides.setChecked(self.__current_view_pane.draw_nib_guides)
            self.set_icon()

        if self.__current_view_pane not in self.__selection:
            self.__selection[self.__current_view_pane] = {}        
        
        if self.__current_view_pane != self.__ui.preview_area:
            for sel_item in self.__current_view_pane.symbol.children:
                if sel_item in self.__selection[self.__current_view_pane]:
                    sel_item.selected = True
                else:
                    sel_item.selected = False

                if type(sel_item).__name__ == "GlyphInstance":
                    for sel_stroke in sel_item.strokes:
                        if sel_stroke in self.__selection[self.__current_view_pane]:
                            sel_stroke.selected = True
                        else:
                            sel_stroke.selected = False

        self.__ui.repaint()

    def set_icon(self):
        icon_bitmap = self.__current_view_pane.bitmap
        if icon_bitmap:
            if self.__current_view_pane == self.__ui.dwg_area:
                self.__cur_char.bitmap_preview = icon_bitmap
                self.__ui.char_selector_list.currentItem().setIcon(QtGui.QIcon(icon_bitmap))
            elif self.__current_view_pane == self.__ui.stroke_dwg_area:
                if self.__ui.stroke_selector_list.count() > 0:
                    self.__ui.stroke_selector_list.currentItem().setIcon(QtGui.QIcon(icon_bitmap))

    def guide_base_height_changed_cb(self, new_value):
        prev_value = self.__char_set.base_height

        self.__property_controller.base_height_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

    def guide_cap_height_changed_cb(self, new_value):
        prev_value = self.__char_set.cap_height

        self.__property_controller.cap_height_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

    def guide_ascent_changed_cb(self, new_value):
        prev_value = self.__char_set.ascent_height

        self.__property_controller.ascent_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

    def guide_descent_changed_cb(self, new_value):
        prev_value = self.__char_set.descent_height

        self.__property_controller.descent_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

    def guide_gap_height_changed_cb(self, new_value):
        prev_value = self.__char_set.gap_height

        self.__property_controller.gap_height_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

    def guide_angle_changed_cb(self, new_value):
        prev_value = self.__char_set.guide_angle

        self.__property_controller.angle_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

    def guide_nominal_width_changed_cb(self, new_value):
        prev_value = self.__char_set.width

        ctrl_list = [self.__char_set]
        if not self.__cur_char.override_spacing:
            ctrl_list.append(self.__ui.guide_lines)

        self.__property_controller.nominal_width_changed(prev_value, \
            new_value, ctrl_list)

    def char_set_left_space_changed_cb(self, new_value):
        prev_value = self.__char_set.left_spacing

        ctrl_list = [self.__char_set]
        if not self.__cur_char.override_spacing:
            ctrl_list.append(self.__ui.guide_lines)

        self.__property_controller.char_set_left_space_changed(prev_value, \
            new_value, ctrl_list)

    def char_set_right_space_changed_cb(self, new_value):
        prev_value = self.__char_set.right_spacing

        ctrl_list = [self.__char_set]
        if not self.__cur_char.override_spacing:
            ctrl_list.append(self.__ui.guide_lines)

        self.__property_controller.char_set_right_space_changed(prev_value, \
            new_value, ctrl_list)

    def guide_color_changed_cb(self, new_color):
        self.__ui.guide_lines.line_color = new_color
        self.__ui.repaint()

    def char_set_nib_angle_changed_cb(self, new_value):
        prev_value = self.__char_set.nib_angle

        self.__property_controller.char_set_nib_angle_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.dwg_area.nib, \
            self.__ui.dwg_area.nib_instance, self.__ui.stroke_dwg_area.nib])

    def char_width_changed_cb(self, new_value):
        prev_value = self.__cur_char.width

        ctrl_list = [self.__cur_char]
        if self.__cur_char.override_spacing:
            ctrl_list.append(self.__ui.guide_lines)

        self.__property_controller.char_width_changed(prev_value, \
            new_value, ctrl_list)

    def char_left_space_changed_cb(self, new_value):
        prev_value = self.__cur_char.left_spacing

        ctrl_list = [self.__cur_char]
        if self.__cur_char.override_spacing:
            ctrl_list.append(self.__ui.guide_lines)

        self.__property_controller.char_left_space_changed(prev_value, \
            new_value, ctrl_list)

    def char_right_space_changed_cb(self, new_value):
        prev_value = self.__cur_char.right_spacing

        ctrl_list = [self.__cur_char]
        if self.__cur_char.override_spacing:
            ctrl_list.append(self.__ui.guide_lines)

        self.__property_controller.char_right_space_changed(prev_value, \
            new_value, ctrl_list)

    def override_char_set_changed_cb(self, newState):
        if newState == QtCore.Qt.Checked:
            self.__cur_char.override_spacing = True
            self.__ui.guide_lines.left_spacing = self.__cur_char.left_spacing
            self.__ui.guide_lines.right_spacing = self.__cur_char.right_spacing
            self.__ui.guide_lines.width = self.__cur_char.width
        else:
            self.__cur_char.override_spacing = False
            self.__ui.guide_lines.left_spacing = self.__char_set.left_spacing
            self.__ui.guide_lines.right_spacing = self.__char_set.right_spacing
            self.__ui.guide_lines.width = self.__char_set.width

        self.__ui.repaint()

    def vert_behavior_combo_changed_cb(self, new_value):
        if new_value == 0:
            return

        self.__vertex_controller.align_tangents(new_value)

    def align_tangents_symmetrical_cb(self, event):
        self.__vertex_controller.align_tangents_symmetrical()

    def align_tangents_cb(self, event):
        self.__vertex_controller.align_tangents_smooth()

    def break_tangents_cb(self, event):
        self.__vertex_controller.break_tangents()

    def stroke_override_nib_angle_changed_cb(self, newState):
        if newState == QtCore.Qt.Checked:
            for sel_stroke in self.__selection[self.__current_view_pane].keys():
                sel_stroke.override_nib_angle = True
                sel_stroke.nib_angle = self.__ui.stroke_nib_angle_spin.value()
        else:
            for sel_stroke in self.__selection[self.__current_view_pane].keys():
                sel_stroke.override_nib_angle = False
        
        self.__ui.repaint()

    def stroke_nib_angle_changed_cb(self, new_value):
        if len(self.__selection[self.__current_view_pane].keys()) == 1:
            sel_stroke = self.__selection[self.__current_view_pane].keys()[0]
            prev_value = sel_stroke.nib_angle
            if prev_value == new_value:
                return

            self.__property_controller.stroke_nib_angle_changed(prev_value, \
                new_value, [sel_stroke])
        

    def position_x_changed_cb(self, new_value):
        if len(self.__selection[self.__current_view_pane].keys()) and self.__state != DRAWING_NEW_STROKE:
            prev_value = self.__selection[self.__current_view_pane].keys()[0].pos.x()
            if prev_value == new_value:
                return

            self.__stroke_controller.selection_position_changed_x(prev_value, \
                new_value)
     
    def position_y_changed_cb(self, new_value):
        if len(self.__selection[self.__current_view_pane].keys()) and self.__state != DRAWING_NEW_STROKE:
            prev_value = self.__selection[self.__current_view_pane].keys()[0].pos.y()
            if prev_value == new_value:
                return

            self.__stroke_controller.selection_position_changed_y(prev_value, \
                new_value)


