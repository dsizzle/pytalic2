#!/usr/bin/python
#

from PyQt5 import QtCore, QtGui, uic, QtWidgets

import pytalic2_ui 

class PytalicInterface(QtWidgets.QMainWindow, pytalic2_ui.Ui_MainWindow):
    def __init__(self, parent, width, height, label):
        QtWidgets.QMainWindow.__init__(self)
       
        self.message_dialog = QtWidgets.QMessageBox()
        self.file_open_dialog = QtWidgets.QFileDialog()
        self.file_save_dialog = QtWidgets.QFileDialog()
        self.__parent = parent

        self.setupUi(self)
        self.__dwg_context_menu = QtWidgets.QMenu()
        self.setWindowTitle(label)

        self.setAcceptDrops(True)

    def create_ui(self):
    	self.create_menu()

    def create_menu(self):
    	self.file_quit.triggered.connect(self.__parent.quit_cb)

    def paintEvent(self, event):
        QtWidgets.QMainWindow.paintEvent(self, event)

    def closeEvent(self, event):
        close = self.__parent.quit_cb(event)

        if close:
            event.accept()
        else:
            event.ignore()