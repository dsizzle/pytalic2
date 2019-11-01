#!/usr/bin/python
#

from PyQt5 import QtCore, QtGui, uic, QtWidgets

import pytalic2_prefs

class UserPreferencesDialog(QtWidgets.QDialog, pytalic2_prefs.Ui_Dialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)
       
        self.__parent = parent

        self.setupUi(self)