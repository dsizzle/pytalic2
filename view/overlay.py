from PyQt5 import QtCore, QtGui

import model.common
import view.handle
import view.shared_qt

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

	def draw(self, gc, handle_size):
		if self.__rect:
			gc.setBrush(view.shared_qt.BRUSH_CLEAR)
			gc.setPen(view.shared_qt.PEN_MD_GRAY_DOT_0)

			gc.drawRect(self.__rect)
			gc.drawRect(self.__rect.bottomRight().x() - handle_size / 2, \
				self.__rect.bottomRight().y() - handle_size / 2, \
				handle_size, handle_size)


class VertexHandleOverlay(Overlay):
	def __init__(self, vertex=None):
		Overlay.__init__(self)
		self.__vertex = vertex

	def draw(self, gc, handle_size):
		if self.__vertex:
			knot_pos = self.__vertex.get_pos()

			KNOT_HANDLE_OBJ.size = handle_size

			gc.setPen(view.shared_qt.PEN_MD_GRAY)

			gc.save()
			gc.translate(knot_pos)
			KNOT_HANDLE_OBJ.draw(gc, self.__vertex.selected == model.common.KNOT, \
				self.__vertex.selected and self.__vertex.selected != model.common.KNOT)
			gc.restore()

			if self.__vertex.behavior == model.common.SMOOTH:
				path = SMOOTH_HANDLE_OBJ
			elif self.__vertex.behavior == model.common.SHARP:
				path = SHARP_HANDLE_OBJ
			else:
				path = SYMMETRIC_HANDLE_OBJ

			path.size = handle_size

			handle = self.__vertex.get_handle_pos(model.common.LEFT_HANDLE)
			if handle:
				gc.setPen(view.shared_qt.PEN_LT_GRAY)
				gc.drawLine(knot_pos, handle)
				gc.setPen(view.shared_qt.PEN_LT_GRAY_2)

				gc.save()
				gc.translate(handle)
				path.draw(gc, self.__vertex.selected == model.common.LEFT_HANDLE)
				gc.restore()

			handle = self.__vertex.get_handle_pos(model.common.RIGHT_HANDLE)
			if handle:
				gc.setPen(view.shared_qt.PEN_LT_GRAY)
				gc.drawLine(knot_pos, handle)
				gc.setPen(view.shared_qt.PEN_LT_GRAY_2)

				gc.save()
				gc.translate(handle)
				path.draw(gc, self.__vertex.selected == model.common.RIGHT_HANDLE)
				gc.restore()
