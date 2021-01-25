"""
pytalic_control.py

The main controller module for pyTalic.

Contains PytalicController class.
"""
import os

from PyQt5 import QtGui, QtCore, QtWidgets

import model.commands
import view.pytalic_ui

class PytalicController(object):
    """
    PytalicController is the main Controller for pyTalic
    """
    def __init__(self, w, h, label, script_path):
        self.__label = label
        self.__ui = view.pytalic_ui.PytalicInterface(self, w, h, label)
        #self.__settings_dialog = view.settings_dialog.UserPreferencesDialog(self)

        #self.__settings_file = os.path.join(script_path, "user_settings.json")

        #self.__user_preferences = model.settings.UserPreferences(self.__settings_file, \
        #   dialog=self.__settings_dialog)
        #self.__user_preferences.load()

        #self.__color = QtGui.QColor(125, 25, 25)

        self.__cmd_stack = model.commands.CommandStack(self)
        self.__selection = {}

        self.__char_set = None
        self.__cur_char = None

        self.__state = 0

        self.__ui.create_ui()

        #self.__ui.dwg_area.bitmap_size = view.shared_qt.ICON_SIZE

        #self.__current_view_pane = \
        #    self.__ui.main_view_tabs.currentWidget().findChild(view.paper.Canvas)
        #self.__selection[self.__current_view_pane] = {}

        self.file_new_cb(None)
        #self.__ui.repaint()

    def get_command_stack(self):
        return self.__cmd_stack

    def get_ui(self):
        return self.__ui

    def file_new_cb(self, event):
	    pass

    def activate(self):
        self.__ui.show()
        self.__ui.activateWindow()
        self.__ui.raise_()

    def quit_cb(self, event):
        close = False
        if self.__cmd_stack.save_count == 0:
            self.__ui.close()
            close = True
        else:
            reply = self.__ui.message_dialog.question(self.__ui, \
                'Quit Program', \
                "You have unsaved changes. Are you sure you want to quit?", \
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, \
                QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                self.__ui.close()
                close = True

        return close