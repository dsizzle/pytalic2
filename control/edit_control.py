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
        self.__ui.charSelectorList.addItems(QtCore.QStringList(char_list))

        self.blank_pixmap = QtGui.QPixmap(ICON_SIZE, ICON_SIZE)
        self.blank_pixmap.fill(QtGui.QColor(240, 240, 240))

        for idx in range(0, self.__ui.charSelectorList.count()):
            self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))
        self.__ui.dwg_area.bitmapSize = ICON_SIZE

        self.__current_view_pane = self.__ui.mainViewTabs.currentWidget()
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
            self.__ui.editUndo.setEnabled(False)
        self.__ui.editRedo.setEnabled(True)
        self.__ui.repaint()

    def redo_cb(self, event):
        self.__cmd_stack.redo()
        if self.__cmd_stack.redo_is_empty():
            self.__ui.editRedo.setEnabled(False)
        self.__ui.editUndo.setEnabled(True)
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

        self.__ui.strokeSelectorList.clear()

        for idx in range(0, self.__ui.charSelectorList.count()):
            self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))

        self.__ui.charSelectorList.setCurrentRow(0)
        self.__cur_char = self.__char_set.getCurrentChar()

        self.__cmd_stack = commands.CommandStack()
        self.__ui.editUndo.setEnabled(False)
        self.__ui.editRedo.setEnabled(False)
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

            self.__ui.strokeSelectorList.clear()

            savedStrokeList = self.__char_set.getSavedStrokes()
            if len(savedStrokeList) > 0:
                i = 0
                self.__ui.strokeLoad.setEnabled(True)
                for selStroke in savedStrokeList:
                    bitmap = self.__ui.dwg_area.drawIcon(None, [selStroke])
                    self.__ui.strokeSelectorList.addItem(str(i))
                    curItem = self.__ui.strokeSelectorList.item(i)
                    self.__ui.strokeSelectorList.setCurrentRow(i)
                    curItem.setIcon(QtGui.QIcon(bitmap))
                    i += 1

            for idx in range(0, self.__ui.charSelectorList.count()):
                self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))

            idx = 0
            char_list = self.__char_set.getCharList()

            for character in char_list.keys():
                if len(char_list[character].strokes) > 0:
                    self.__ui.charSelectorList.setCurrentRow(idx)
                    self.__ui.repaint()

                idx += 1

            self.__ui.charSelectorList.setCurrentRow(1)
            self.__ui.charSelectorList.setCurrentRow(0)

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

    def createNewStroke_cb(self, event):
        self.__stroke_controller.createNewStroke()

    def saveStroke_cb(self, event):
        self.__stroke_controller.saveStroke()

    def addControlPoint_cb(self, event):
        self.state = ADDING_CTRL_POINT
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

    def splitAtPoint_cb(self, event):
        self.state = SPLIT_AT_POINT
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

    def deleteStrokes_cb(self, event):
        selectedVerts = 0
        for selStroke in self.__selection[self.__current_view_pane].keys():
            for vert in self.__selection[self.__current_view_pane][selStroke]:
                selectedVerts += 1

        if selectedVerts > 0:
            self.__stroke_controller.deleteControlVertices()
        else:
            self.cutStrokes_cb(event)

    def cutStrokes_cb(self, event):
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
        self.__ui.editUndo.setEnabled(True)

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

        self.__ui.charSelectorList.setCurrentRow(char_index)
        self.__clipboard = []
        for selStroke in strokesToCut:
            self.__cur_char.deleteStroke({'stroke' : selStroke})
            self.__clipboard.append(selStroke)
            if self.__selection[self.__current_view_pane].has_key(selStroke):
                del self.__selection[self.__current_view_pane][selStroke]
            selStroke.selected = False

        self.__ui.editPaste.setEnabled(True)
        self.__ui.repaint() 

    def copyStrokes_cb(self, event):
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
        self.__ui.editUndo.setEnabled(True)

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

        self.__ui.charSelectorList.setCurrentRow(char_index)
        self.__clipboard = []
        for selStroke in strokesToCopy.keys():
            self.__clipboard.append(selStroke)
 
        self.__ui.editPaste.setEnabled(True)
        self.__ui.repaint() 

    def pasteStrokes_cb(self, event):
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
        self.__ui.editUndo.setEnabled(True)

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

        self.__ui.charSelectorList.setCurrentRow(char_index)

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

        self.setUIStateSelection(True)
        self.__ui.repaint() 

    def pasteInstanceFromSaved_cb(self, event):
        self.__stroke_controller.pasteInstanceFromSaved()

    def viewToggleSnapAxially_cb(self, event):
        self.__snap_controller.toggleSnapAxially()

    def viewToggleSnapToGrid_cb(self, event):
        self.__snap_controller.toggleSnapToGrid()

    def viewToggleSnapToNibAxes_cb(self, event):
        self.__snap_controller.toggleSnapToNibAxes()

    def viewToggleSnapToCtrlPts_cb(self, event):
        self.__snap_controller.toggleSnapToCtrlPts()

    def viewToggleGuidelines_cb(self, event):
        self.__current_view_pane.drawGuidelines = not self.__current_view_pane.drawGuidelines
        self.__ui.repaint()

    def viewToggleNibGuides_cb(self, event):
        self.__current_view_pane.drawNibGuides = not self.__current_view_pane.drawNibGuides
        self.__ui.repaint()

    def viewResetOrigin(self, event):
        self.__current_view_pane.originDelta = QtCore.QPoint(0, 0)
        self.__ui.repaint()

    def viewResetZoom(self, event):
        self.__current_view_pane.scale = 1
        self.__ui.repaint()

    def setUIStateSelection(self, state):
        self.__ui.strokeAddVertex.setEnabled(state)
        self.__ui.strokeSplitAtPoint.setEnabled(state)
        self.__ui.strokeSave.setEnabled(state)
        self.__ui.editCut.setEnabled(state)
        self.__ui.editCopy.setEnabled(state)
        self.__ui.strokeStraighten.setEnabled(state)
        self.__ui.strokeJoin.setEnabled(state)
        self.__ui.strokeAlignTangents.setEnabled(state)
        self.__ui.strokeSmoothTangents.setEnabled(state)
        self.__ui.strokeSharpenTangents.setEnabled(state)       

    def straightenStroke_cb(self, event):
        self.__stroke_controller.straightenStroke()

    def joinStrokes_cb(self, event):
        self.__stroke_controller.joinSelectedStrokes()

    def charSelected(self, event):
        curCharIdx = self.__ui.charSelectorList.currentRow()
        self.__char_set.setCurrentChar(curCharIdx)
        self.__cur_char = self.__char_set.getCurrentChar()
        self.__ui.dwg_area.strokesSpecial = []
        self.__ui.dwg_area.strokes = self.__cur_char.strokes
        self.__ui.repaint()
        self.setIcon()

    def strokeSelected(self, event):
        selSavedStroke = self.__char_set.getSavedStroke(self.__ui.strokeSelectorList.currentRow())
 
        self.__ui.stroke_dwg_area.strokes = [selSavedStroke]
        self.__ui.repaint()
        self.setIcon()

    def viewTabChanged_cb(self, event):
        self.__current_view_pane = self.__ui.mainViewTabs.currentWidget()

        if self.__current_view_pane == self.__ui.dwg_area:
            self.__ui.strokeNew.setEnabled(True)
        elif self.__current_view_pane == self.__ui.stroke_dwg_area:
            self.__ui.strokeNew.setEnabled(False)
        elif self.__current_view_pane == self.__ui.preview_area:
            self.__ui.strokeNew.setEnabled(False)
            self.__ui.viewGuides.setEnabled(False)
            self.__ui.viewNibGuides.setEnabled(False)

        if not self.__selection.has_key(self.__current_view_pane):
            self.__selection[self.__current_view_pane] = {}
        if self.__current_view_pane == self.__ui.preview_area:
            self.__ui.viewGuides.setEnabled(False)
            self.__ui.viewNibGuides.setEnabled(False)
        else:
            self.__ui.viewGuides.setEnabled(True)
            self.__ui.viewNibGuides.setEnabled(True)
            self.__ui.viewGuides.setChecked(self.__current_view_pane.drawGuidelines)
            self.__ui.viewNibGuides.setChecked(self.__current_view_pane.drawNibGuides)
            self.setIcon()

        self.__ui.repaint()

    def setIcon(self):
        iconBitmap = self.__current_view_pane.getBitmap()
        if iconBitmap:
            if self.__current_view_pane == self.__ui.dwg_area:
                self.__cur_char.bitmapPreview = iconBitmap
                self.__ui.charSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))
            elif self.__current_view_pane == self.__ui.stroke_dwg_area:
                if self.__ui.strokeSelectorList.count() > 0:
                    self.__ui.strokeSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))

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

    def alignTangentsSymmetrical_cb(self, event):
        self.__vertex_controller.alignTangentsSymmetrical()

    def alignTangents_cb(self, event):
        self.__vertex_controller.alignTangents()

    def breakTangents_cb(self, event):
        self.__vertex_controller.breakTangents()
