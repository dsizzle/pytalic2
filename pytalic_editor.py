"""
pytalic_editor.py

This is the main entry point for the pyTalic editor.  The editor is for
creating and editing character sets for use with pyTalic.
"""
import os
import sys

from PyQt4 import QtGui

from control import edit_control


class PytalicEditorApp(QtGui.QApplication):
    """
    PytalicEditorApp

    the main Qt Application class
    """
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
        QtGui.qApp = self


def main(args=None):
    """the main entry point"""
    # bump up stack depth due to pickle failure
    sys.setrecursionlimit(10000)
    my_qt_app = PytalicEditorApp(args)
    script_file_path = os.path.realpath(__file__)
    script_path = os.path.split(script_file_path)[0]

    my_qt_ctrl = edit_control.EditorController(1024, 768, "Pytalic Character Editor", script_path)

    my_qt_ctrl.activate()

    return my_qt_app.exec_()

main(sys.argv)
