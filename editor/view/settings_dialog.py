#!/usr/bin/python
#

from PyQt5 import QtCore, QtGui, uic, QtWidgets

import editor.pytalic2_prefs

class UserPreferencesDialog(QtWidgets.QDialog, editor.pytalic2_prefs.Ui_Dialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)
       
        self.__parent = parent

        self.setupUi(self)