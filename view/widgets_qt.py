"""
widgets_qt

This file contains custom widgets.
"""
from PyQt4 import QtCore, QtGui

class SelectColorButton(QtGui.QPushButton):
    def __init__(self, parent, default_color=None):
        QtGui.QPushButton.__init__(self)
        self.__color = QtGui.QColor()
        if default_color:
            self.__color = default_color
        self.__parent = parent
        QtCore.QObject.connect(self, QtCore.SIGNAL("clicked()"), self.changeColor)

    def setColor(self, newColor):
        self.__color = newColor
        self.updateColor()

    def getColor(self):
        return self.__color

    @QtCore.pyqtSlot()
    def updateColor(self):
        self.setStyleSheet("background-color: " + self.__color.name())
        self.emit(QtCore.SIGNAL("valueChanged(QColor)"), self.__color)

    @QtCore.pyqtSlot()
    def changeColor(self):
        new_color = QtGui.QColorDialog.getColor(self.__color, self.__parent)
        if new_color != self.__color and new_color.isValid():
            self.setColor(new_color)


class DoubleClickSplitter(QtGui.QSplitter):
    def __init__(self, parent):
        QtGui.QSplitter.__init__(self, parent)
        self.__parent = parent
        self.__max_pane_size = 0
        self.__pane_to_close = 1

    def createHandle(self):
        splitter_handle = DoubleClickSplitterHandle(self.orientation(), self)
        QtCore.QObject.connect(splitter_handle, QtCore.SIGNAL("doubleClickSignal"), \
            self.onSashDoubleClick)
        return splitter_handle

    def onSashDoubleClick(self):
        max_pane = self.widget(self.__pane_to_close)

        size_to_use = max_pane.width()
        cur_size = self.width()

        if self.orientation() == QtCore.Qt.Vertical:
            size_to_use = max_pane.height()
            cur_size = self.height()

        if self.__max_pane_size == 0:
            self.__max_pane_size = size_to_use

        if size_to_use > 0:
            self.moveSplitter(cur_size, 1)
        else:
            self.moveSplitter(cur_size - self.__max_pane_size, 1)
        
        self.repaint()

    def setMaxPaneSize(self, new_size):
        self.__max_pane_size = new_size

    def getMaxPaneSize(self):
        return self.__max_pane_size


class DoubleClickSplitterHandle(QtGui.QSplitterHandle):
    def __init__(self, orientation, parent):
        QtGui.QSplitterHandle.__init__(self, orientation, parent)
        self.doubleClickSignal = QtCore.pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.emit(QtCore.SIGNAL("doubleClickSignal"))
