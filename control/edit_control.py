import os
import os.path
import pickle

from PyQt4 import QtGui, QtCore

import control.mouse_operations
import control.property_operations
import control.snap_operations
import control.stroke_operations
import control.vertex_operations
from model import character_set, commands, stroke
from view import edit_ui

ICON_SIZE = 40

IDLE = 0
MOVING_PAPER = 1
DRAWING_NEW_STROKE = 2
DRAGGING = 3
ADDING_CTRL_POINT = 4
SPLIT_AT_POINT = 5

class EditorController(object):
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
        self.__ui.dwg_area.bitmapSize = ICON_SIZE

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
        if self.__cmd_stack.save_count == 0:
            self.__ui.close()
        else:
            reply = self.__ui.message_dialog.question(self.__ui, \
                'Quit Program', \
                "You have unsaved changes. Are you sure you want to quit?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
                QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                self.__ui.close()

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

        self.__char_set = character_set.character_set()
        self.__ui.baseHeightSpin.setValue(self.__char_set.baseHeight)
        self.__ui.capHeightSpin.setValue(self.__char_set.capHeight)
        self.__ui.capHeightSpin.setMaximum(self.__char_set.ascentHeight)
        self.__ui.ascentHeightSpin.setValue(self.__char_set.ascentHeight)
        self.__ui.descentHeightSpin.setValue(self.__char_set.descentHeight)
        self.__ui.angleSpin.setValue(5)

        self.name = (self.__label + " - Untitled")
        self.__ui.setWindowTitle(self.name)

        self.__ui.stroke_selector_list.clear()

        for idx in range(0, self.__ui.char_selector_list.count()):
            self.__ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))

        self.__ui.char_selector_list.setCurrentRow(0)
        self.__cur_char = self.__char_set.getCurrentChar()

        self.__cmd_stack = commands.CommandStack()
        self.__ui.edit_undo.setEnabled(False)
        self.__ui.edit_redo.setEnabled(False)
        self.__ui.file_save.setEnabled(False)

    def file_save_as_cb(self, event):
        file_name = self.__ui.file_save_dialog.getSaveFileName(self.__ui,
             "Save Character Set", self.__dir_name,
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
        file_name = self.__ui.file_open_dialog.getOpenFileName(self.__ui,
             "Open Character Set", self.__dir_name,
             "Character Set Files (*.cs)")

        if file_name:
            self.load(file_name)

            self.__ui.baseHeightSpin.setValue(self.__char_set.baseHeight)
            self.__ui.guide_lines.baseHeight = self.__char_set.baseHeight
            self.__ui.capHeightSpin.setValue(self.__char_set.capHeight)
            self.__ui.guide_lines.capHeight = self.__char_set.capHeight
            self.__ui.capHeightSpin.setMaximum(self.__char_set.ascentHeight)
            self.__ui.ascentHeightSpin.setValue(self.__char_set.ascentHeight)
            self.__ui.guide_lines.ascentHeight = self.__char_set.ascentHeight
            self.__ui.descentHeightSpin.setValue(self.__char_set.descentHeight)
            self.__ui.guide_lines.descentHeight = self.__char_set.descentHeight
            self.__ui.angleSpin.setValue(self.__char_set.guideAngle)
            self.__ui.guide_lines.guideAngle = self.__char_set.guideAngle
            self.__ui.charSetNibAngleSpin.setValue(self.__char_set.nibAngle)
            self.__ui.guide_lines.nibAngle = self.__char_set.nibAngle
            self.__ui.dwg_area.nib.angle = self.__char_set.nibAngle
            self.__ui.dwg_area.instNib.angle = self.__char_set.nibAngle
            self.__ui.stroke_dwg_area.nib.angle = self.__char_set.nibAngle
            self.__ui.nominalWidthSpin.setValue(self.__char_set.nominalWidth)
            self.__ui.guide_lines.nominalWidth = self.__char_set.nominalWidth

            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))

            self.__ui.setWindowTitle(self.__label + " - " + self.__file_name)

            self.__ui.stroke_selector_list.clear()

            savedStrokeList = self.__char_set.getSavedStrokes()
            if len(savedStrokeList) > 0:
                i = 0
                self.__ui.stroke_load.setEnabled(True)
                for selStroke in savedStrokeList:
                    bitmap = self.__ui.dwg_area.drawIcon(None, [selStroke])
                    self.__ui.stroke_selector_list.addItem(str(i))
                    curItem = self.__ui.stroke_selector_list.item(i)
                    self.__ui.stroke_selector_list.setCurrentRow(i)
                    curItem.setIcon(QtGui.QIcon(bitmap))
                    i += 1

            for idx in range(0, self.__ui.char_selector_list.count()):
                self.__ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))

            idx = 0
            char_list = self.__char_set.getCharList()

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
            dataFileFd = open(file_name, 'wb')
        except IOError:
            print "ERROR: Couldn't open %s for writing." % (file_name)
            return 1

        try:
            dataPickler = pickle.Pickler(dataFileFd, pickle.HIGHEST_PROTOCOL)
            dataPickler.dump(self.__char_set)
        except pickle.PicklingError:
            print "ERROR: Couldn't serialize data"
            return 1

        if dataFileFd:
            dataFileFd.close()

    def load(self, file_name):
        try:
            dataFileFd = open(file_name, 'rb')
        except IOError:
            print "ERROR: Couldn't open %s for reading." % (file_name)
            return 1

        try:
            dataPickler = pickle.Unpickler(dataFileFd)      
            self.__char_set = dataPickler.load()
        except pickle.UnpicklingError:
            print "ERROR: Couldn't unserialize data"
            return 1
        except:
            print "ERROR: OTHER"
            return 1

        if dataFileFd:
            dataFileFd.close()

    def create_new_stroke_cb(self, event):
        self.__stroke_controller.create_new_stroke()

    def save_stroke_cb(self, event):
        self.__stroke_controller.save_stroke()

    def add_control_point_cb(self, event):
        self.state = ADDING_CTRL_POINT
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

    def split_at_point_cb(self, event):
        self.state = SPLIT_AT_POINT
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

    def delete_strokes_cb(self, event):
        selectedVerts = 0
        for selStroke in self.__selection[self.__current_view_pane].keys():
            for vert in self.__selection[self.__current_view_pane][selStroke]:
                selectedVerts += 1

        if selectedVerts > 0:
            self.__stroke_controller.delete_control_vertices()
        else:
            self.cut_strokes_cb(event)

    def cut_strokes_cb(self, event):
        cut_strokes_cmd = commands.Command('cut_strokes_cmd')
        char_index = self.__char_set.getCurrentCharIndex()

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
            strokesToCut = args['strokes']
        else:
            return

        self.__ui.char_selector_list.setCurrentRow(char_index)
        self.__clipboard = []
        for selStroke in strokesToCut:
            self.__cur_char.deleteStroke({'stroke' : selStroke})
            self.__clipboard.append(selStroke)
            if self.__selection[self.__current_view_pane].has_key(selStroke):
                del self.__selection[self.__current_view_pane][selStroke]
            selStroke.selected = False

        self.__ui.edit_paste.setEnabled(True)
        self.__ui.repaint() 

    def copy_strokes_cb(self, event):
        copy_strokes_cmd = commands.Command('copy_strokes_cmd')
        char_index = self.__char_set.getCurrentCharIndex()

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
            strokesToCopy = args['strokes']
        else:
            return

        self.__ui.char_selector_list.setCurrentRow(char_index)
        self.__clipboard = []
        for selStroke in strokesToCopy.keys():
            self.__clipboard.append(selStroke)
 
        self.__ui.edit_paste.setEnabled(True)
        self.__ui.repaint() 

    def paste_strokes_cb(self, event):
        paste_strokes_cmd = commands.Command('paste_strokes_cmd')
        char_index = self.__char_set.getCurrentCharIndex()

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
            strokesToPaste = args['strokes']
        else:
            return

        if args.has_key('copy'):
            copyStrokes = args['copy']
        else:
            copyStrokes = True

        self.__ui.char_selector_list.setCurrentRow(char_index)

        for selStroke in self.__selection[self.__current_view_pane].keys():
            selStroke.selected = False

        self.__selection[self.__current_view_pane] = {}

        for selStroke in strokesToPaste:
            if copyStrokes and type(selStroke).__name__ == 'Stroke':
                pasteStroke = stroke.Stroke(fromStroke=selStroke)
            else:
                pasteStroke = selStroke

            self.__selection[self.__current_view_pane][pasteStroke] = {}
            pasteStroke.selected = True
            if type(pasteStroke).__name__ == 'Stroke':
                self.__cur_char.addStroke({'stroke' : pasteStroke, 'copyStroke' : False})
            else:
                self.__cur_char.newStrokeInstance({'stroke' : pasteStroke})

        self.set_ui_state_selection(True)
        self.__ui.repaint() 

    def paste_instance_from_saved_cb(self, event):
        self.__stroke_controller.paste_instance_from_saved()

    def view_toggle_snap_axially_cb(self, event):
        self.__snap_controller.toggleSnapAxially()

    def view_toggle_snap_to_grid_cb(self, event):
        self.__snap_controller.toggleSnapToGrid()

    def view_toggle_snap_to_nib_axes_cb(self, event):
        self.__snap_controller.toggleSnapToNibAxes()

    def view_toggle_snap_to_ctrl_pts_cb(self, event):
        self.__snap_controller.toggleSnapToCtrlPts()

    def view_toggle_guidelines_cb(self, event):
        self.__current_view_pane.drawGuidelines = not self.__current_view_pane.drawGuidelines
        self.__ui.repaint()

    def view_toggle_nib_guides_cb(self, event):
        self.__current_view_pane.drawNibGuides = not self.__current_view_pane.drawNibGuides
        self.__ui.repaint()

    def view_reset_origin_cb(self, event):
        self.__current_view_pane.originDelta = QtCore.QPoint(0, 0)
        self.__ui.repaint()

    def view_reset_zoom_cb(self, event):
        self.__current_view_pane.scale = 1
        self.__ui.repaint()

    def set_ui_state_selection(self, state):
        self.__ui.stroke_add_vertex.setEnabled(state)
        self.__ui.stroke_split_at_point.setEnabled(state)
        self.__ui.stroke_save.setEnabled(state)
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
        self.__char_set.setCurrentChar(cur_char_idx)
        self.__cur_char = self.__char_set.getCurrentChar()
        self.__ui.dwg_area.strokesSpecial = []
        self.__ui.dwg_area.strokes = self.__cur_char.strokes
        self.__ui.repaint()
        self.set_icon()

    def stroke_selected_cb(self, event):
        sel_saved_stroke = self.__char_set.getSavedStroke(self.__ui.stroke_selector_list.currentRow())
 
        self.__ui.stroke_dwg_area.strokes = [sel_saved_stroke]
        self.__ui.repaint()
        self.set_icon()

    def view_tab_changed_cb(self, event):
        self.__current_view_pane = self.__ui.main_view_tabs.currentWidget()

        if self.__current_view_pane == self.__ui.dwg_area:
            self.__ui.stroke_new.setEnabled(True)
        elif self.__current_view_pane == self.__ui.stroke_dwg_area:
            self.__ui.stroke_new.setEnabled(False)
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
            self.__ui.view_guides.setChecked(self.__current_view_pane.drawGuidelines)
            self.__ui.view_nib_guides.setChecked(self.__current_view_pane.drawNibGuides)
            self.set_icon()

        self.__ui.repaint()

    def set_icon(self):
        iconBitmap = self.__current_view_pane.getBitmap()
        if iconBitmap:
            if self.__current_view_pane == self.__ui.dwg_area:
                self.__cur_char.bitmapPreview = iconBitmap
                self.__ui.char_selector_list.currentItem().setIcon(QtGui.QIcon(iconBitmap))
            elif self.__current_view_pane == self.__ui.stroke_dwg_area:
                if self.__ui.stroke_selector_list.count() > 0:
                    self.__ui.stroke_selector_list.currentItem().setIcon(QtGui.QIcon(iconBitmap))

    def guideBaseHeightChanged_cb(self, new_value):
        prev_value = self.__char_set.baseHeight

        self.__property_controller.base_height_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])


    def guideCapHeightChanged_cb(self, new_value):
        prev_value = self.__char_set.capHeight

        self.__property_controller.cap_height_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])

    def guideAscentChanged_cb(self, new_value):
        prev_value = self.__char_set.ascentHeight

        self.__property_controller.ascent_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])

    def guideDescentChanged_cb(self, new_value):
        prev_value = self.__char_set.descentHeight

        self.__property_controller.descent_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])

    def guideGapHeightChanged_cb(self, new_value):
        prev_value = self.__char_set.gapHeight

        self.__property_controller.gap_height_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])

    def guideAngleChanged_cb(self, new_value):
        prev_value = self.__char_set.guideAngle

        self.__property_controller.angle_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])

    def guideNominalWidthChanged_cb(self, new_value):
        prev_value = self.__char_set.nominalWidth

        self.__property_controller.nominal_width_changed(prev_value, new_value, [self.__char_set, self.__ui.guide_lines])

    def guideColorChanged_cb(self, new_color):
        self.__ui.guide_lines.setLineColor(new_color)
        self.__ui.repaint()

    def charSetNibAngleChanged_cb(self, new_value):
        prev_value = self.__char_set.nibAngle

        self.__property_controller.char_set_nib_angle_changed(prev_value, \
            new_value, [self.__char_set, self.__ui.dwg_area.nib, \
            self.__ui.dwg_area.instNib, self.__ui.stroke_dwg_area.nib])

    def charWidthChanged_cb(self, new_value):
        prev_value = self.__cur_char.width

        self.__property_controller.char_width_changed(prev_value, \
            new_value, [self.__cur_char])

    def charLeftSpaceChanged_cb(self, new_value):
        prev_value = self.__cur_char.leftSpacing

        self.__property_controller.char_left_space_changed(prev_value, \
            new_value, [self.__cur_char])

    def charRightSpaceChanged_cb(self, new_value):
        prev_value = self.__cur_char.rightSpacing

        self.__property_controller.char_right_space_changed(prev_value, \
            new_value, [self.__cur_char])

    def vertBehaviorComboChanged_cb(self, new_value):
        if new_value == 0:
            return

        self.__vertex_controller.align_tangents(new_value)

    def align_tangents_symmetrical_cb(self, event):
        self.__vertex_controller.align_tangents_symmetrical()

    def align_tangents_cb(self, event):
        self.__vertex_controller.align_tangents()

    def break_tangents_cb(self, event):
        self.__vertex_controller.break_tangents()
