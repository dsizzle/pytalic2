from PyQt5 import QtCore, QtGui

import editor.model.common
import editor.view.handle
import editor.view.shared_qt

KNOT_HANDLE_OBJ      = editor.view.handle.TristateHandle()
SMOOTH_HANDLE_OBJ    = editor.view.handle.RoundHandle()
SHARP_HANDLE_OBJ     = editor.view.handle.TriangleHandle()
SYMMETRIC_HANDLE_OBJ = editor.view.handle.SemicircleHandle()


class Overlay(object):
	def __init__(self):
		pass

	def draw(self, gc):
		pass


class RectHandleOverlay(Overlay):
	def __init__(self, rect=None, scale=1):
		self.__rect = rect
		self.__scale = scale

	def draw(self, gc, handle_size):
		if self.__rect:
			gc.save()
			gc.scale(self.__scale, self.__scale)
			gc.setBrush(editor.view.shared_qt.BRUSH_CLEAR)
			gc.setPen(editor.view.shared_qt.PEN_MD_GRAY_DOT_0)

			gc.drawRect(self.__rect)
			gc.drawRect(self.__rect.bottomRight().x() - handle_size / 2, \
				self.__rect.bottomRight().y() - handle_size / 2, \
				handle_size, handle_size)
			gc.restore()

class VertexHandleOverlay(Overlay):
	def __init__(self, vertex=None, scale=1):
		Overlay.__init__(self)
		self.__vertex = vertex
		self.__scale = scale

	def draw(self, gc, handle_size):
		if self.__vertex:
			gc.save()
			gc.scale(self.__scale, self.__scale)
			knot_pos = self.__vertex.get_pos()

			KNOT_HANDLE_OBJ.size = handle_size / self.__scale

			gc.setPen(editor.view.shared_qt.PEN_MD_GRAY)

			gc.save()
			gc.translate(knot_pos)

			KNOT_HANDLE_OBJ.draw(gc, self.__vertex.selected == editor.model.common.KNOT, \
				self.__vertex.selected and self.__vertex.selected != editor.model.common.KNOT)
			gc.restore()

			if self.__vertex.behavior == editor.model.common.SMOOTH:
				path = SMOOTH_HANDLE_OBJ
			elif self.__vertex.behavior == editor.model.common.SHARP:
				path = SHARP_HANDLE_OBJ
			else:
				path = SYMMETRIC_HANDLE_OBJ

			path.size = handle_size / self.__scale

			handle = self.__vertex.get_handle_pos(editor.model.common.LEFT_HANDLE)
			if handle:
				gc.setPen(editor.view.shared_qt.PEN_LT_GRAY)
				gc.drawLine(knot_pos, handle)
				gc.setPen(editor.view.shared_qt.PEN_LT_GRAY_2)

				gc.save()
				gc.translate(handle)
				path.draw(gc, self.__vertex.selected == editor.model.common.LEFT_HANDLE)
				gc.restore()

			handle = self.__vertex.get_handle_pos(editor.model.common.RIGHT_HANDLE)
			if handle:
				gc.setPen(editor.view.shared_qt.PEN_LT_GRAY)
				gc.drawLine(knot_pos, handle)
				gc.setPen(editor.view.shared_qt.PEN_LT_GRAY_2)

				gc.save()
				gc.translate(handle)
				path.draw(gc, self.__vertex.selected == editor.model.common.RIGHT_HANDLE)
				gc.restore()

			gc.restore()