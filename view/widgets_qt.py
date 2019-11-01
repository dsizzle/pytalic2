"""
widgets_qt

This file contains custom widgets.
"""
from PyQt5 import QtCore, QtGui, QtWidgets

class SelectColorButton(QtWidgets.QPushButton):
    def __init__(self, parent, default_color=None):
        QtWidgets.QPushButton.__init__(self)
        self.__color = QtGui.QColor()
        if default_color:
            self.__color = default_color
        self.__parent = parent
        self.clicked.connect(self.changeColor)

    def setColor(self, newColor):
        self.__color = newColor
        self.updateColor()

    def getColor(self):
        return self.__color

    color = property(getColor, setColor)

    def setValue(self, color_value):
        self.__color = QtGui.QColor(color_value[0], color_value[1], color_value[2])
        if len(color_value) > 3:
            self.__color.setAlpha(color_value[3])
        self.updateColor()

    def value(self):
        return [self.__color.red(), self.__color.green(), self.__color.blue(), self.__color.alpha()]

    @QtCore.pyqtSlot()
    def updateColor(self):
        self.setStyleSheet("background-color: " + self.__color.name())
        #self.valueChanged[QColor].emit(self.__color)

    @QtCore.pyqtSlot()
    def changeColor(self):
        new_color = QtWidgets.QColorDialog.getColor(self.__color, self.__parent)
        if new_color != self.__color and new_color.isValid():
            self.setColor(new_color)


class DoubleClickSplitter(QtWidgets.QSplitter):
    def __init__(self, parent):
        QtWidgets.QSplitter.__init__(self, parent)
        self.__parent = parent
        self.__max_pane_size = 0
        self.__pane_to_close = 1

    def createHandle(self):
        splitter_handle = DoubleClickSplitterHandle(self.orientation(), self)
        splitter_handle.doubleClickSignal.connect(self.onSashDoubleClick)
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


class DoubleClickSplitterHandle(QtWidgets.QSplitterHandle):
    def __init__(self, orientation, parent):
        QtWidgets.QSplitterHandle.__init__(self, orientation, parent)
        self.doubleClickSignal = QtCore.pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClickSignal.emit()