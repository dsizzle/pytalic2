from PyQt4 import QtGui, QtCore

class MySplitter(QtGui.QSplitter):
	def __init__(self, parent):
		QtGui.QSplitter.__init__(self, parent)
		self.parent = parent
		self.maxPaneWidth = 0

	def createHandle(self):
		splitterHandle = MySplitterHandle(1, self)
		QtCore.QObject.connect(splitterHandle, QtCore.SIGNAL("doubleClickSignal"), self.onSashDoubleClick)
		return splitterHandle

	def onSashDoubleClick(self):
		dwgArea = self.widget(0)
		toolPane = self.widget(1)
		
		if (self.maxPaneWidth == 0):
			self.maxPaneWidth = toolPane.width()
		
		if (toolPane.size().width() > 0):
			self.moveSplitter(self.width(), 1)
		else:
			self.moveSplitter(self.width()-self.maxPaneWidth, 1)
		
		self.repaint()
		
	def setMaxPaneWidth(self, width):
		self.maxPaneWidth = width
		
			
class MySplitterHandle(QtGui.QSplitterHandle):
	def __init__(self, orientation, parent):
		QtGui.QSplitterHandle.__init__(self, orientation, parent)
		self.doubleClickSignal = QtCore.pyqtSignal()
		
	def mouseDoubleClickEvent(self, event):
		self.emit(QtCore.SIGNAL("doubleClickSignal"))