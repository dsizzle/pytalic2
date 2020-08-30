from PyQt5 import QtCore, QtGui
import view.handle
import view.shared_qt

SMOOTH      = 1
SHARP       = 2
SYMMETRIC   = 3

LEFT_HANDLE     = 1
RIGHT_HANDLE    = 3
KNOT            = 2

KNOT_HANDLE_OBJ      = view.handle.TristateHandle()
SMOOTH_HANDLE_OBJ    = view.handle.RoundHandle()
SHARP_HANDLE_OBJ     = view.handle.TriangleHandle()
SYMMETRIC_HANDLE_OBJ = view.handle.SemicircleHandle()


class Overlay(object):
	def __init__(self):
		pass

	def draw(self, gc):
		pass


class RectHandleOverlay(Overlay):
	def __init__(self, rect = None):
		self.__rect = rect

	def draw(self, gc):
		if self.__rect:
			gc.setBrush(view.shared_qt.BRUSH_CLEAR)
			gc.setPen(view.shared_qt.PEN_BLUE_DASH_DOT)

			gc.drawRect(self.__rect)


class VertexHandleOverlay(Overlay):
	def __init__(self):
		Overlay.__init__(self)

	def draw(self, gc, vertex, size):
		knot_pos = vertex.get_pos()

		handle_size = size
		KNOT_HANDLE_OBJ.size = handle_size

		gc.setPen(view.shared_qt.PEN_MD_GRAY)

		gc.save()
		gc.translate(knot_pos)
		KNOT_HANDLE_OBJ.draw(gc, vertex.selected == KNOT, vertex.selected and vertex.selected != KNOT)
		gc.restore()

		if vertex.behavior == SMOOTH:
			path = SMOOTH_HANDLE_OBJ
		elif vertex.behavior == SHARP:
			path = SHARP_HANDLE_OBJ
		else:
			path = SYMMETRIC_HANDLE_OBJ

		path.size = handle_size

		handle = vertex.get_handle_pos(LEFT_HANDLE)
		if handle:
			gc.setPen(view.shared_qt.PEN_LT_GRAY)
			gc.drawLine(knot_pos, handle)
			gc.setPen(view.shared_qt.PEN_LT_GRAY_2)

			gc.save()
			gc.translate(handle)
			path.draw(gc, vertex.selected == LEFT_HANDLE)
			gc.restore()

		handle = vertex.get_handle_pos(RIGHT_HANDLE)
		if handle:
			gc.setPen(view.shared_qt.PEN_LT_GRAY)
			gc.drawLine(knot_pos, handle)
			gc.setPen(view.shared_qt.PEN_LT_GRAY_2)

			gc.save()
			gc.translate(handle)
			path.draw(gc, vertex.selected == RIGHT_HANDLE)
			gc.restore()
