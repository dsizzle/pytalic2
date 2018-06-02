"""
edit_control.py

The main controller module for pyTalic Editor.

Contains EditorController class.
"""
import os
import os.path
import pickle

from PyQt4 import QtGui, QtCore

import control.mouse_operations
import control.property_operations
import control.snap_operations
import control.stroke_operations
import control.vertex_operations
from model import character_set, character, commands, stroke
from view import edit_ui

ICON_SIZE = 40

IDLE = 0
MOVING_PAPER = 1
DRAWING_NEW_STROKE = 2
DRAGGING = 3
ADDING_CTRL_POINT = 4
SPLIT_AT_POINT = 5

class EditorController(object):
    """
    EditorController is the main Controller for pyTalic Editor
    """
    def __init__(self, w, h, label):
        self.__label = label
        self.__ui = edit_ui.EditInterface(self, w, h, label)

        self.__color = QtGui.QColor(125, 25, 25)

        self.__file_name = None
        self.__dir_name = os.getcwd()
        self.__clipboard = []
        self.__cmd_stack = commands.CommandStack()
        self.__selection = {}
        self.__char_set = None
        self.__cur_char = None

        self.__state = 0

        char_list = []
        for i in range(32, 128):
            char_list.append(str(unichr(i)))

        self.__ui.create_ui()
        self.__ui.char_selector_list.addItems(QtCore.QStringList(char_list))

        self.blank_pixmap = QtGui.QPixmap(ICON_SIZE, ICON_SIZE)
        self.blank_pixmap.fill(QtGui.QColor(240, 240, 240))

        for idx in range(0, self.__ui.char_selector_list.count()):
            self.__ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))
        self.__ui.dwg_area.bitmap_size = ICON_SIZE

        self.__current_view_pane = self.__ui.main_view_tabs.currentWidget()
        self.__selection[self.__current_view_pane] = {}

        self.__property_controller = control.property_operations.PropertyController(self)
        self.__mouse_controller = control.mouse_operations.MouseController(self)
        self.__snap_controller = control.snap_operations.SnapController(self)
        self.__stroke_controller = control.stroke_operations.StrokeController(self)
        self.__vertex_controller = control.vertex_operations.VertexController(self)

        self.file_new_cb(None)

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
        self.__file_name = None

        self.__char_set = character_set.CharacterSet()
        self.__ui.base_height_spin.setValue(self.__char_set.base_height)
        self.__ui.cap_height_spin.setValue(self.__char_set.cap_height)
        self.__ui.cap_height_spin.setMaximum(self.__char_set.ascent_height)
        self.__ui.ascent_height_spin.setValue(self.__char_set.ascent_height)
        self.__ui.descent_height_spin.setValue(self.__char_set.descent_height)
        self.__ui.angle_spin.setValue(5)

        self.name = (self.__label + " - Untitled")
        self.__ui.setWindowTitle(self.name)

        self.__ui.stroke_selector_list.clear()

        for idx in range(0, self.__ui.char_selector_list.count()):
            self.__ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))

        self.__ui.char_selector_list.setCurrentRow(0)
        self.__cur_char = self.__char_set.current_char

        self.__cmd_stack = commands.CommandStack()
        self.__ui.edit_undo.setEnabled(False)
        self.__ui.edit_redo.setEnabled(False)
        self.__ui.file_save.setEnabled(False)

    def file_save_as_cb(self, event):
        file_name = self.__ui.file_save_dialog.getSaveFileName(self.__ui, \
             "Save Character Set", self.__dir_name, \
             "Character Set Files (*.cs)")

        if file_name:
            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))
            (name, ext) = os.path.splitext(self.__file_name)

            if ext != ".cs":
                self.__file_name += ".cs"

            self.save(self.__file_name)
            self.__ui.setWindowTitle(self.__label + " - " + self.__file_name)
            self.__cmd_stack.reset_save_count()
            self.__ui.file_save.setEnabled(True)

    def file_save_cb(self, event):
        if self.__file_name and os.path.isfile(self.__file_name):
            self.save(self.__file_name)
            self.__cmd_stack.reset_save_count()
        else:
            self.file_save_as_cb(event)

    def file_open_cb(self):
        file_name = None
        file_name = self.__ui.file_open_dialog.getOpenFileName(self.__ui, \
             "Open Character Set", self.__dir_name, \
             "Character Set Files (*.cs)")

        if file_name:
            self.load(file_name)

            self.__ui.base_height_spin.setValue(self.__char_set.base_height)
            self.__ui.guide_lines.base_height = self.__char_set.base_height
            self.__ui.cap_height_spin.setValue(self.__char_set.cap_height)
            self.__ui.guide_lines.cap_height = self.__char_set.cap_height
            self.__ui.cap_height_spin.setMaximum(self.__char_set.ascent_height)
            self.__ui.ascent_height_spin.setValue(self.__char_set.ascent_height)
            self.__ui.guide_lines.ascent_height = self.__char_set.ascent_height
            self.__ui.descent_height_spin.setValue(self.__char_set.descent_height)
            self.__ui.guide_lines.descent_height = self.__char_set.descent_height
            self.__ui.angle_spin.setValue(self.__char_set.guide_angle)
            self.__ui.guide_lines.guide_angle = self.__char_set.guide_angle
            self.__ui.char_set_nib_angle_spin.setValue(self.__char_set.nib_angle)
            self.__ui.guide_lines.nib_angle = self.__char_set.nib_angle
            self.__ui.dwg_area.nib.angle = self.__char_set.nib_angle
            self.__ui.dwg_area.nib_instance.angle = self.__char_set.nib_angle
            self.__ui.stroke_dwg_area.nib.angle = self.__char_set.nib_angle
            self.__ui.nominal_width_spin.setValue(self.__char_set.nominal_width)
            self.__ui.guide_lines.nominal_width = self.__char_set.nominal_width

            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))

            self.__ui.setWindowTitle(self.__label + " - " + self.__file_name)

            self.__ui.stroke_selector_list.clear()

            saved_stroke_list = self.__char_set.get_saved_strokes()
            if len(saved_stroke_list) > 0:
                i = 0
                self.__ui.stroke_load.setEnabled(True)
                for sel_stroke in saved_stroke_list:
                    bitmap = self.__ui.dwg_area.draw_icon(None, sel_stroke.strokes)
                    self.__ui.stroke_selector_list.addItem(str(i))
                    cur_item = self.__ui.stroke_selector_list.item(i)
                    self.__ui.stroke_selector_list.setCurrentRow(i)
                    cur_item.setIcon(QtGui.QIcon(bitmap))
                    i += 1

            for idx in range(0, self.__ui.char_selector_list.count()):
                self.__ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))

            idx = 0
            char_list = self.__char_set.get_char_list()

            for character in char_list.keys():
                if len(char_list[character].strokes) > 0:
                    self.__ui.char_selector_list.setCurrentRow(idx)
                    self.__ui.repaint()

                idx += 1

            self.__ui.char_selector_list.setCurrentRow(1)
            self.__ui.char_selector_list.setCurrentRow(0)

            self.__selection[self.__current_view_pane] = {}
            self.__ui.repaint()

            self.__cmd_stack.clear()
            self.__cmd_stack.reset_save_count()
            self.__ui.file_save.setEnabled(True)

    def save(self, file_name):
        try:
            data_file_fd = open(file_name, 'wb')
        except IOError:
            print "ERROR: Couldn't open %s for writing." % (file_name)
            return 1

        try:
            data_pickler = pickle.Pickler(data_file_fd, pickle.HIGHEST_PROTOCOL)
            data_pickler.dump(self.__char_set)
        except pickle.PicklingError:
            print "ERROR: Couldn't serialize data"
            return 1

        if data_file_fd:
            data_file_fd.close()

    def load(self, file_name):
        try:
            data_file_fd = open(file_name, 'rb')
        except IOError:
            print "ERROR: Couldn't open %s for reading." % (file_name)
            return 1

        try:
            data_pickler = pickle.Unpickler(data_file_fd)
            self.__char_set = data_pickler.load()
        except pickle.UnpicklingError:
            print "ERROR: Couldn't unserialize data"
            return 1
        except Exception:
            print "ERROR: OTHER"
            return 1

        if data_file_fd:
            data_file_fd.close()

    def create_new_stroke_cb(self, event):
        self.__stroke_controller.create_new_stroke()

    def save_stroke_cb(self, event):
        self.__stroke_controller.save_stroke()
        self.__ui.main_view_tabs.setTabEnabled(1, True)

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
        cut_strokes_cmd = commands.Command('cut_strokes_cmd')
        char_index = self.__char_set.get_current_char_index()

        do_args = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'char_index' : char_index,
            'copy' : False,
        }

        cut_strokes_cmd.set_do_args(do_args)
        cut_strokes_cmd.set_undo_args(undo_args)
        cut_strokes_cmd.set_do_function(self.cut_clipboard)
        cut_strokes_cmd.set_undo_function(self.paste_clipboard)

        self.__cmd_stack.do_command(cut_strokes_cmd)
        self.__ui.edit_undo.setEnabled(True)

        self.__ui.repaint()

    def cut_clipboard(self, args):
        if args.has_key('char_index'):
            char_index = args['char_index']
        else:
            return

        if args.has_key('strokes'):
            strokes_to_cut = args['strokes']
        else:
            return

        self.__ui.char_selector_list.setCurrentRow(char_index)
        self.__clipboard = []
        for sel_stroke in strokes_to_cut:
            #self.__cur_char.delete_stroke({'stroke' : sel_stroke})
            if type(sel_stroke).__name__ == 'Stroke':
                self.__current_view_pane.character.delete_stroke({'stroke' : sel_stroke})
            else:
                self.__current_view_pane.character.remove_glyph(sel_stroke)

            self.__clipboard.append(sel_stroke)
            if self.__selection[self.__current_view_pane].has_key(sel_stroke):
                del self.__selection[self.__current_view_pane][sel_stroke]
            sel_stroke.selected = False

        self.__ui.edit_paste.setEnabled(True)
        self.__ui.repaint()

    def copy_strokes_cb(self, event):
        copy_strokes_cmd = commands.Command('copy_strokes_cmd')
        char_index = self.__char_set.get_current_char_index()

        do_args = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'char_index' : char_index,
        }

        copy_strokes_cmd.set_do_args(do_args)
        copy_strokes_cmd.set_undo_args(undo_args)
        copy_strokes_cmd.set_do_function(self.copy_clipboard)
        copy_strokes_cmd.set_undo_function(self.paste_clipboard)

        self.__cmd_stack.do_command(copy_strokes_cmd)
        self.__ui.edit_undo.setEnabled(True)

        self.__ui.repaint()

    def copy_clipboard(self, args):
        if args.has_key('char_index'):
            char_index = args['char_index']
        else:
            return

        if args.has_key('strokes'):
            strokes_to_copy = args['strokes']
        else:
            return

        self.__ui.char_selector_list.setCurrentRow(char_index)
        self.__clipboard = []
        for sel_stroke in strokes_to_copy.keys():
            self.__clipboard.append(sel_stroke)

        self.__ui.edit_paste.setEnabled(True)
        self.__ui.repaint()

    def paste_strokes_cb(self, event):
        paste_strokes_cmd = commands.Command('paste_strokes_cmd')
        char_index = self.__char_set.get_current_char_index()

        do_args = {
            'strokes' : self.__clipboard[:],
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : self.__clipboard[:],
            'char_index' : char_index,
            'copy' : True,
        }

        paste_strokes_cmd.set_do_args(do_args)
        paste_strokes_cmd.set_undo_args(undo_args)
        paste_strokes_cmd.set_do_function(self.paste_clipboard)
        paste_strokes_cmd.set_undo_function(self.cut_clipboard)

        self.__cmd_stack.do_command(paste_strokes_cmd)
        self.__ui.edit_undo.setEnabled(True)

        self.__ui.repaint()

    def paste_clipboard(self, args):
        if args.has_key('char_index'):
            char_index = args['char_index']
        else:
            return

        if args.has_key('strokes'):
            strokes_to_paste = args['strokes']
        else:
            return

        if args.has_key('copy'):
            copy_strokes = args['copy']
        else:
            copy_strokes = True

        self.__ui.char_selector_list.setCurrentRow(char_index)

        for sel_stroke in self.__selection[self.__current_view_pane].keys():
            sel_stroke.selected = False

        self.__selection[self.__current_view_pane] = {}

        for sel_stroke in strokes_to_paste:
            if copy_strokes and type(sel_stroke).__name__ == 'Stroke':
                paste_stroke = stroke.Stroke(from_stroke=sel_stroke)
            else:
                paste_stroke = sel_stroke

            self.__selection[self.__current_view_pane][paste_stroke] = {}
            paste_stroke.selected = True
            if type(paste_stroke).__name__ == 'Stroke':
                #self.__cur_char.add_stroke({'stroke' : paste_stroke, 'copyStroke' : False})
                self.__current_view_pane.character.add_stroke({'stroke' : paste_stroke, 'copy_stroke' : False})
            else:
                #self.__cur_char.new_stroke_instance({'stroke' : paste_stroke})
                new_glyph = character.Glyph()
                new_glyph.set_strokes(paste_stroke.strokes)
                #self.__current_view_pane.character.new_stroke_instance({'stroke' : paste_stroke})
                self.__current_view_pane.character.add_glyph(new_glyph)

        self.set_ui_state_selection(True)
        self.__ui.repaint()

    def paste_instance_from_saved_cb(self, event):
        self.__stroke_controller.paste_instance_from_saved()

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

    def char_selected_cb(self, event):
        cur_char_idx = self.__ui.char_selector_list.currentRow()
        self.__char_set.current_char = cur_char_idx
        self.__cur_char = self.__char_set.current_char
        self.__ui.dwg_area.strokes = []
        self.__ui.dwg_area.character = self.__cur_char
        self.__ui.repaint()
        self.set_icon()

    def stroke_selected_cb(self, event):
        sel_saved_stroke = self.__char_set.get_saved_stroke(self.__ui.stroke_selector_list.currentRow())

        self.__ui.stroke_dwg_area.character = sel_saved_stroke

        self.__ui.repaint()
        self.set_icon()

    def view_tab_changed_cb(self, event):
        self.__current_view_pane = self.__ui.main_view_tabs.currentWidget()

        if self.__current_view_pane == self.__ui.dwg_area:
            self.__ui.stroke_new.setEnabled(True)
            if len(self.__selection.keys()):
                self.set_ui_state_selection(True)
        elif self.__current_view_pane == self.__ui.stroke_dwg_area:
            self.__ui.stroke_new.setEnabled(True)
            self.__ui.stroke_delete.setEnabled(True)
            self.__current_view_pane.character.selected = False
        elif self.__current_view_pane == self.__ui.preview_area:
            self.__ui.stroke_new.setEnabled(False)
            self.__ui.view_guides.setEnabled(False)
            self.__ui.view_nib_guides.setEnabled(False)

        if not self.__selection.has_key(self.__current_view_pane):
            self.__selection[self.__current_view_pane] = {}
        if self.__current_view_pane == self.__ui.preview_area:
            self.__ui.view_guides.setEnabled(False)
            self.__ui.view_nib_guides.setEnabled(False)
        else:
            self.__ui.view_guides.setEnabled(True)
            self.__ui.view_nib_guides.setEnabled(True)
            self.__ui.view_guides.setChecked(self.__current_view_pane.draw_guidelines)
            self.__ui.view_nib_guides.setChecked(self.__current_view_pane.draw_nib_guides)
            self.set_icon()

        for sel_stroke in self.__current_view_pane.character.children:
            if self.__selection[self.__current_view_pane].has_key(sel_stroke):
                sel_stroke.selected = True
            else:
                sel_stroke.selected = False

        if type(self.__current_view_pane.character).__name__ == "Character":
            for sel_glyph in self.__current_view_pane.character.glyphs:

                for sel_stroke in sel_glyph.strokes:
                    if self.__selection[self.__current_view_pane].has_key(sel_stroke):
                        sel_stroke.selected = True
                    else:
                        sel_stroke.selected = False

        self.__ui.repaint()

    def set_icon(self):
        icon_bitmap = self.__current_view_pane.get_bitmap()
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
        prev_value = self.__char_set.nominal_width

        self.__property_controller.nominal_width_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.guide_lines])

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

        self.__property_controller.char_width_changed(prev_value, \
            new_value, [self.__cur_char])

    def char_left_space_changed_cb(self, new_value):
        prev_value = self.__cur_char.left_spacing

        self.__property_controller.char_left_space_changed(prev_value, \
            new_value, [self.__cur_char])

    def char_right_space_changed_cb(self, new_value):
        prev_value = self.__cur_char.right_spacing

        self.__property_controller.char_right_space_changed(prev_value, \
            new_value, [self.__cur_char])

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
