import sys

from PyQt4 import QtGui

from control import edit_control

class PytalicEditorApp(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
        QtGui.qApp = self


def main(args=None):
    my_qt_app = PytalicEditorApp(args)
    my_qt_ctrl = edit_control.EditorController(1024, 768, "Pytalic Character Editor")

    my_qt_ctrl.activate()

    return my_qt_app.exec_()

main(sys.argv)
