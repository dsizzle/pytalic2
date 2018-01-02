import sys

from PyQt4 import QtGui, QtCore

import editcontrol

class pytalic_editor_app(QtGui.QApplication):
	def __init__(self, args):
		QtGui.QApplication.__init__(self, args)
		QtGui.qApp = self
		
		
def main(args=None):
	myQtApp = pytalic_editor_app(args)
	myQtCtrl = editcontrol.editor_controller(1024, 768, "Pytalic Character Editor")
	
	myQtCtrl.activate()

	return myQtApp.exec_()
	
main(sys.argv)