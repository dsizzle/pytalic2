"""
pytalic_project.py

This is the main entry point for the pyTalic project tool.  The project tool is for
creating pyTalic projects.
"""
import os
import sys

from PyQt5 import QtWidgets

from project.control import pytalic_control


class PytalicEditorApp(QtWidgets.QApplication):
    """
    PytalicEditorApp

    the main Qt Application class
    """
    def __init__(self, args):
        QtWidgets.QApplication.__init__(self, args)
        QtWidgets.qApp = self


def main(args=None):
    """the main entry point"""
    # bump up stack depth due to pickle failure
    sys.setrecursionlimit(10000)
    my_qt_app = PytalicEditorApp(args)
    script_file_path = os.path.realpath(__file__)
    script_path = os.path.split(script_file_path)[0]

    my_qt_ctrl = pytalic_control.PytalicController(1024, 768, "Pytalic", script_path)

    my_qt_ctrl.activate()

    return my_qt_app.exec_()

main(sys.argv)
