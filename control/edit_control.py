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
        self.__ui = edit_ui.edit_interface(self, w, h, label)

        self.__color = QtGui.QColor(125, 25, 25)

        self.__file_name = None
        self.__dir_name = os.getcwd()
        self.__clipboard = []
        self.__cmd_stack = commands.commandStack()
        self.__selection = {}
        self.__char_set = None
        self.__cur_char = None

        self.__state = 0

        char_list = []
        for i in range(32, 128):
            char_list.append(str(unichr(i)))

        self.__ui.createUI()
        self.__ui.charSelectorList.addItems(QtCore.QStringList(char_list))

        self.blank_pixmap = QtGui.QPixmap(ICON_SIZE, ICON_SIZE)
        self.blank_pixmap.fill(QtGui.QColor(240, 240, 240))

        for idx in range(0, self.__ui.charSelectorList.count()):
            self.__ui.charSelectorList.item(idx).setIcon(QtGui.QIcon(self.blank_pixmap))
        self.__ui.dwgArea.bitmapSize = ICON_SIZE

        self.__current_view_pane = self.__ui.mainViewTabs.currentWidget()
        self.__selection[self.__current_view_pane] = {}

        self.__property_controller = control.property_operations.property_controller(self)
        self.__mouse_controller = control.mouse_operations.mouse_controller(self)
        self.__snap_controller = control.snap_operations.snap_controller(self)
        self.__stroke_controller = control.stroke_operations.stroke_controller(self)
        self.__vertex_controller = control.vertex_operations.vertex_controller(self)

        self.fileNew_cb(None)

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

    def mouseEvent(self, event):
        self.__mouse_controller.mouseEvent(event)

    def wheelEvent(self, event):
        self.__mouse_controller.wheelEvent(event)

    def quit_cb(self, event):
        if self.__cmd_stack.saveCount == 0:
            self.__ui.close()
        else:
            reply = self.__ui.messageDialog.question(self.__ui, \
                'Quit Program', \
                "You have unsaved changes. Are you sure you want to quit?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
                QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                self.__ui.close()

    def undo_cb(self, event):
        self.__cmd_stack.undo()
        if self.__cmd_stack.undoIsEmpty():
            self.__ui.editUndo.setEnabled(False)
        self.__ui.editRedo.setEnabled(True)
        self.__ui.repaint()

    def redo_cb(self, event):
        self.__cmd_stack.redo()
        if self.__cmd_stack.redoIsEmpty():
            self.__ui.editRedo.setEnabled(False)
        self.__ui.editUndo.setEnabled(True)
        self.__ui.repaint()

    def fileNew_cb(self, event):
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

        self.__cmd_stack = commands.commandStack()
        self.__ui.editUndo.setEnabled(False)
        self.__ui.editRedo.setEnabled(False)
        self.__ui.fileSave.setEnabled(False)

    def fileSaveAs_cb(self, event):
        file_name = self.__ui.fileSaveDialog.getSaveFileName(self.__ui,
             "Save Character Set", self.__dir_name,
             "Character Set Files (*.cs)")
            
        if file_name:
            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))
            (name, ext) = os.path.splitext(self.__file_name) 

            if ext != ".cs":
                self.__file_name += ".cs"

            self.save(self.__file_name)
            self.__ui.setWindowTitle(self.__label + " - " + self.__file_name)
            self.__cmd_stack.resetSaveCount()
            self.__ui.fileSave.setEnabled(True)

    def fileSave_cb(self, event):
        if self.__file_name and os.path.isfile(self.__file_name):
            self.save(self.__file_name)
            self.__cmd_stack.resetSaveCount()
        else:
            self.fileSaveAs_cb(event)

    def fileOpen_cb(self):
        file_name = None
        file_name = self.__ui.fileOpenDialog.getOpenFileName(self.__ui,
             "Open Character Set", self.__dir_name,
             "Character Set Files (*.cs)")

        if file_name:
            self.load(file_name)

            self.__ui.baseHeightSpin.setValue(self.__char_set.baseHeight)
            self.__ui.guideLines.baseHeight = self.__char_set.baseHeight
            self.__ui.capHeightSpin.setValue(self.__char_set.capHeight)
            self.__ui.guideLines.capHeight = self.__char_set.capHeight
            self.__ui.capHeightSpin.setMaximum(self.__char_set.ascentHeight)
            self.__ui.ascentHeightSpin.setValue(self.__char_set.ascentHeight)
            self.__ui.guideLines.ascentHeight = self.__char_set.ascentHeight
            self.__ui.descentHeightSpin.setValue(self.__char_set.descentHeight)
            self.__ui.guideLines.descentHeight = self.__char_set.descentHeight
            self.__ui.angleSpin.setValue(self.__char_set.guideAngle)
            self.__ui.guideLines.guideAngle = self.__char_set.guideAngle
            self.__ui.charSetNibAngleSpin.setValue(self.__char_set.nibAngle)
            self.__ui.guideLines.nibAngle = self.__char_set.nibAngle
            self.__ui.dwgArea.nib.angle = self.__char_set.nibAngle
            self.__ui.dwgArea.instNib.angle = self.__char_set.nibAngle
            self.__ui.strokeDwgArea.nib.angle = self.__char_set.nibAngle
            self.__ui.nominalWidthSpin.setValue(self.__char_set.nominalWidth)
            self.__ui.guideLines.nominalWidth = self.__char_set.nominalWidth

            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))

            self.__ui.setWindowTitle(self.__label + " - " + self.__file_name)

            self.__ui.strokeSelectorList.clear()

            savedStrokeList = self.__char_set.getSavedStrokes()
            if len(savedStrokeList) > 0:
                i = 0
                self.__ui.strokeLoad.setEnabled(True)
                for selStroke in savedStrokeList:
                    bitmap = self.__ui.dwgArea.drawIcon(None, [selStroke])
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
            self.__cmd_stack.resetSaveCount()
            self.__ui.fileSave.setEnabled(True)

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
        cutStrokesCmd = commands.command('cutStrokesCmd')
        charIndex = self.__char_set.getCurrentCharIndex()

        doArgs = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'charIndex' : charIndex,
        }

        undoArgs = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'charIndex' : charIndex,
            'copy' : False,
        }

        cutStrokesCmd.setDoArgs(doArgs)
        cutStrokesCmd.setUndoArgs(undoArgs)
        cutStrokesCmd.setDoFunction(self.cutClipboard)
        cutStrokesCmd.setUndoFunction(self.pasteClipboard)

        self.__cmd_stack.doCommand(cutStrokesCmd)
        self.__ui.editUndo.setEnabled(True)

        self.__ui.repaint()

    def cutClipboard(self, args):
        if args.has_key('charIndex'):
            charIndex = args['charIndex']
        else:
            return

        if args.has_key('strokes'):
            strokesToCut = args['strokes']
        else:
            return

        self.__ui.charSelectorList.setCurrentRow(charIndex)
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
        copyStrokesCmd = commands.command('copyStrokesCmd')
        charIndex = self.__char_set.getCurrentCharIndex()

        doArgs = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'charIndex' : charIndex,
        }

        undoArgs = {
            'strokes' : self.__selection[self.__current_view_pane].copy(),
            'charIndex' : charIndex,
        }

        copyStrokesCmd.setDoArgs(doArgs)
        copyStrokesCmd.setUndoArgs(undoArgs)
        copyStrokesCmd.setDoFunction(self.copyClipboard)
        copyStrokesCmd.setUndoFunction(self.pasteClipboard)

        self.__cmd_stack.doCommand(copyStrokesCmd)
        self.__ui.editUndo.setEnabled(True)

        self.__ui.repaint()

    def copyClipboard(self, args):
        if args.has_key('charIndex'):
            charIndex = args['charIndex']
        else:
            return

        if args.has_key('strokes'):
            strokesToCopy = args['strokes']
        else:
            return

        self.__ui.charSelectorList.setCurrentRow(charIndex)
        self.__clipboard = []
        for selStroke in strokesToCopy.keys():
            self.__clipboard.append(selStroke)
 
        self.__ui.editPaste.setEnabled(True)
        self.__ui.repaint() 

    def pasteStrokes_cb(self, event):
        pasteStrokesCmd = commands.command('pasteStrokesCmd')
        charIndex = self.__char_set.getCurrentCharIndex()

        doArgs = {
            'strokes' : self.__clipboard[:],
            'charIndex' : charIndex,
        }

        undoArgs = {
            'strokes' : self.__clipboard[:],
            'charIndex' : charIndex,
            'copy' : True,
        }

        pasteStrokesCmd.setDoArgs(doArgs)
        pasteStrokesCmd.setUndoArgs(undoArgs)
        pasteStrokesCmd.setDoFunction(self.pasteClipboard)
        pasteStrokesCmd.setUndoFunction(self.cutClipboard)

        self.__cmd_stack.doCommand(pasteStrokesCmd)
        self.__ui.editUndo.setEnabled(True)

        self.__ui.repaint()

    def pasteClipboard(self, args):
        if args.has_key('charIndex'):
            charIndex = args['charIndex']
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

        self.__ui.charSelectorList.setCurrentRow(charIndex)

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
        self.__ui.dwgArea.strokesSpecial = []
        self.__ui.dwgArea.strokes = self.__cur_char.strokes
        self.__ui.repaint()
        self.setIcon()

    def strokeSelected(self, event):
        selSavedStroke = self.__char_set.getSavedStroke(self.__ui.strokeSelectorList.currentRow())
 
        self.__ui.strokeDwgArea.strokes = [selSavedStroke]
        self.__ui.repaint()
        self.setIcon()

    def viewTabChanged_cb(self, event):
        self.__current_view_pane = self.__ui.mainViewTabs.currentWidget()

        if self.__current_view_pane == self.__ui.dwgArea:
            self.__ui.strokeNew.setEnabled(True)
        elif self.__current_view_pane == self.__ui.strokeDwgArea:
            self.__ui.strokeNew.setEnabled(False)
        elif self.__current_view_pane == self.__ui.previewArea:
            self.__ui.strokeNew.setEnabled(False)
            self.__ui.viewGuides.setEnabled(False)
            self.__ui.viewNibGuides.setEnabled(False)

        if not self.__selection.has_key(self.__current_view_pane):
            self.__selection[self.__current_view_pane] = {}
        if self.__current_view_pane == self.__ui.previewArea:
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
            if self.__current_view_pane == self.__ui.dwgArea:
                self.__cur_char.bitmapPreview = iconBitmap
                self.__ui.charSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))
            elif self.__current_view_pane == self.__ui.strokeDwgArea:
                if self.__ui.strokeSelectorList.count() > 0:
                    self.__ui.strokeSelectorList.currentItem().setIcon(QtGui.QIcon(iconBitmap))

    def guideBaseHeightChanged_cb(self, newValue):
        prevValue = self.__char_set.baseHeight

        self.__property_controller.baseHeightChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])


    def guideCapHeightChanged_cb(self, newValue):
        prevValue = self.__char_set.capHeight

        self.__property_controller.capHeightChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])

    def guideAscentChanged_cb(self, newValue):
        prevValue = self.__char_set.ascentHeight

        self.__property_controller.ascentChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])

    def guideDescentChanged_cb(self, newValue):
        prevValue = self.__char_set.descentHeight

        self.__property_controller.descentChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])

    def guideGapHeightChanged_cb(self, newValue):
        prevValue = self.__char_set.gapHeight

        self.__property_controller.gapHeightChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])

    def guideAngleChanged_cb(self, newValue):
        prevValue = self.__char_set.guideAngle

        self.__property_controller.angleChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])

    def guideNominalWidthChanged_cb(self, newValue):
        prevValue = self.__char_set.nominalWidth

        self.__property_controller.nominalWidthChanged(prevValue, newValue, [self.__char_set, self.__ui.guideLines])

    def guideColorChanged_cb(self, newColor):
        self.__ui.guideLines.setLineColor(newColor)
        self.__ui.repaint()

    def charSetNibAngleChanged_cb(self, newValue):
        prevValue = self.__char_set.nibAngle

        self.__property_controller.charSetNibAngleChanged(prevValue, newValue, 
                [self.__char_set, self.__ui.dwgArea.nib, 
                self.__ui.dwgArea.instNib, self.__ui.strokeDwgArea.nib])

    def charWidthChanged_cb(self, newValue):
        prevValue = self.__cur_char.width

        self.__property_controller.charWidthChanged(prevValue, newValue, [self.__cur_char])

    def charLeftSpaceChanged_cb(self, newValue):
        prevValue = self.__cur_char.leftSpacing

        self.__property_controller.charLeftSpaceChanged(prevValue, newValue, [self.__cur_char])

    def charRightSpaceChanged_cb(self, newValue):
        prevValue = self.__cur_char.rightSpacing

        self.__property_controller.charRightSpaceChanged(prevValue, newValue, [self.__cur_char])

    def vertBehaviorComboChanged_cb(self, newValue):
        if newValue == 0:
            return

        self.__vertex_controller.alignTangents(newValue)

    def alignTangentsSymmetrical_cb(self, event):
        self.__vertex_controller.alignTangentsSymmetrical()

    def alignTangents_cb(self, event):
        self.__vertex_controller.alignTangents()

    def breakTangents_cb(self, event):
        self.__vertex_controller.breakTangents()
