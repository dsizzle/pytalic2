from PyQt4 import QtCore

import control.edit_control
from model import commands

class KeyboardController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__move_x = QtCore.QPoint(2, 0)
        self.__move_y = QtCore.QPoint(0, 2)

    def key_event(self, event):
        current_view = self.__main_ctrl.get_current_view()
        ui_ref = self.__main_ctrl.get_ui()

        if ui_ref.dwg_area.hasFocus() or \
            ui_ref.stroke_dwg_area.hasFocus() or \
            ui_ref.preview_area.hasFocus() or \
            current_view.underMouse():

            if event.type() == QtCore.QEvent.KeyRelease:
                self.__key_release_event_paper(event)
            else:
                self.__key_press_event_paper(event)

            event.accept()
        else:
            event.ignore()

    def __key_press_event_paper(self, event):
        pass

    def __key_release_event_paper(self, event):
        ui_ref = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        stroke_ctrl = self.__main_ctrl.get_stroke_controller()
        cmd_stack = self.__main_ctrl.get_command_stack()

        if self.__main_ctrl.state == control.edit_control.IDLE:
            if event.key() == QtCore.Qt.Key_Left:
                move_delta = QtCore.QPoint() - self.__move_x
            elif event.key() == QtCore.Qt.Key_Right:
                move_delta = QtCore.QPoint(self.__move_x)
            elif event.key() == QtCore.Qt.Key_Up:
                move_delta = QtCore.QPoint() - self.__move_y
            elif event.key() == QtCore.Qt.Key_Down:
                move_delta = QtCore.QPoint(self.__move_y)
            else:
                move_delta = QtCore.QPoint()

            if event.modifiers() & QtCore.Qt.AltModifier:
                move_delta = move_delta * 5 / 2
            elif event.modifiers() & QtCore.Qt.ControlModifier:
                move_delta /= 2

            if move_delta != QtCore.QPoint() and \
                len(cur_view_selection.keys()) > 0:

                move_cmd = commands.Command('move_stroke_cmd')
                selection_copy = cur_view_selection.copy()
                do_args = {
                    'strokes' : selection_copy,
                    'delta' : move_delta,
                }

                undo_args = {
                    'strokes' : selection_copy,
                    'delta' : QtCore.QPoint(0, 0) - move_delta,
                }

                move_cmd.set_do_args(do_args)
                move_cmd.set_undo_args(undo_args)
                move_cmd.set_do_function(stroke_ctrl.move_selected)
                move_cmd.set_undo_function(stroke_ctrl.move_selected)

                cmd_stack.do_command(move_cmd)
                cmd_stack.save_count += 1
                ui_ref.edit_undo.setEnabled(True)

                ui_ref.repaint()
