from PyQt5 import QtCore, QtGui

import editor.view.shared_qt


class Handle(object):
    def __init__(self, size=10):
        self.__path = QtGui.QPainterPath()
        self.__size = size
        self.__scale = 1.0
        self.__pos = QtCore.QPoint()
        self.make_path()

    def make_path(self):
        self.path = QtGui.QPainterPath()
        self.path.addRect(-self.__size/2, -self.__size/2, self.__size, self.__size)

    def get_size(self):
        return self.__size

    def set_size(self, new_size):
        self.__size = new_size
        self.make_path()

    size = property(get_size, set_size)

    def get_scale(self):
        return self.__scale

    def set_scale(self, new_scale):
        self.__scale = new_scale

    scale = property(get_scale, set_scale)

    def get_path(self):
        return self.__path

    def set_path(self, new_path):
        self.__path = new_path

    path = property(get_path, set_path)

    def draw(self, gc, selected=False):
        gc.setPen(editor.view.shared_qt.PEN_MD_GRAY)

        if selected:
            gc.setBrush(editor.view.shared_qt.BRUSH_GREEN_SOLID)
        else:
            gc.setBrush(editor.view.shared_qt.BRUSH_CLEAR)

        gc.save()
        gc.scale(self.scale, self.scale)
        gc.drawPath(self.path)
        gc.restore()


class RoundHandle(Handle):
    def __init__(self, size=10):
        super(RoundHandle, self).__init__(size)

    def make_path(self):
        self.path = QtGui.QPainterPath()
        self.path.addEllipse(-self.size/2, -self.size/2, self.size, self.size)


class TriangleHandle(Handle):
    def __init__(self, size=10):
        super(TriangleHandle, self).__init__(size)

    def make_path(self):
        self.path = QtGui.QPainterPath()
        self.path.moveTo(0, self.size/2)
        self.path.lineTo(-self.size/2, self.size/2)
        self.path.lineTo(0, -self.size/2)
        self.path.lineTo(self.size/2, self.size/2)
        self.path.lineTo(0, self.size/2)


class SemicircleHandle(Handle):
    def __init__(self, size=10):
        super(SemicircleHandle, self).__init__(size)

    def make_path(self):
        self.path = QtGui.QPainterPath()
        self.path.moveTo(0, 0)
        self.path.arcTo(-self.size/2, -self.size/2, self.size, self.size, 270, 180)
        self.path.lineTo(0, 0)


class TristateHandle(Handle):
    def __init__(self, size=10):
        super(TristateHandle, self).__init__(size)

    def draw(self, gc, selected=False, child_selected=False):
        if selected:
            gc.setBrush(editor.view.shared_qt.BRUSH_GREEN_SOLID)
        elif child_selected:
            gc.setBrush(editor.view.shared_qt.BRUSH_YELLOW_SOLID)
        else:
            gc.setBrush(editor.view.shared_qt.BRUSH_MD_GRAY_SOLID)

        gc.save()
        gc.scale(self.scale, self.scale)
        gc.drawPath(self.path)
        gc.restore()

