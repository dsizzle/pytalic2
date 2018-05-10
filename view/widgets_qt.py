from PyQt4 import QtCore, QtGui

class select_color_button(QtGui.QPushButton):
    def __init__(self, parent, defaultColor=None):
        QtGui.QPushButton.__init__(self)
        self.__color = QtGui.QColor()
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
        newColor = QtGui.QColorDialog.getColor(self.__color, self.__parent)
        if ( newColor != self.__color ):
            self.setColor( newColor )
