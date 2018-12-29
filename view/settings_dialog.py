#!/usr/bin/python
#

from PyQt4 import QtCore, QtGui, uic

import pytalic2_prefs

class UserPreferencesDialog(QtGui.QDialog, pytalic2_prefs.Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
       
        self.__parent = parent

        self.setupUi(self)