
import math
import struct

from PyQt5 import QtCore, QtGui

import editor.model.common


class ControlVertex(object):
    def __init__(self, left=None, knot=QtCore.QPointF(), right=None, \
        new_behavior=editor.model.common.SMOOTH, char_set=None):
        self.__pressure = 1.0
        self.__behavior = new_behavior
        self.__handle_pos = [0, left, knot, right]
        self.__handle_scale = 1.0
        self.__char_set = char_set
        self.__selected = None

    def get_char_set(self):
        return self.__char_set

    def set_char_set(self, new_char_set):
        self.__char_set = new_char_set

    char_set = property(get_char_set, set_char_set)

    def serialize(self):
        data = struct.pack("<fH", self.__pressure, \
            self.__behavior)
        
        for i in range(1, 4):
            if self.__handle_pos[i] is not None:
                data += struct.pack("<dd", self.__handle_pos[i].x(), \
                    self.__handle_pos[i].y())
            else:
                data += struct.pack("<dd", editor.model.common.MAGIC_NONE, editor.model.common.MAGIC_NONE)

        data += struct.pack("<f", self.__handle_scale)
        
        return data

    def unserialize(self, data):
        offset = 0
        (self.__pressure, self.__behavior) = struct.unpack_from("<fH", data)
        offset += struct.calcsize("<fH")
        for i in range(1, 4):
            (x, y) = struct.unpack_from("<dd", data, offset)
            offset += struct.calcsize("<dd")
            if x == editor.model.common.MAGIC_NONE and y == editor.model.common.MAGIC_NONE:
                self.__handle_pos[i] = None
            else:
                self.__handle_pos[i] = QtCore.QPointF(x, y)

        self.__handle_scale = struct.unpack_from("<f", data, offset)[0]
        self.__selected = None

    def contains(self, test_point, handle_size):
        test_rect = QtCore.QRectF(- handle_size / 2, - handle_size/2, \
                handle_size, handle_size)
        
        for i in range(1, 4):
            pos = self.__handle_pos[i]
            if pos is None:
                continue

            if test_rect.contains(test_point-pos):
                return i
        
        return 0

    def set_pos(self, point):
        self.set_handle_pos(point, editor.model.common.KNOT)

    def get_pos(self):
        return self.__handle_pos[editor.model.common.KNOT]

    pos = property(get_pos, set_pos)

    def get_selected_handle(self):
        return self.__selected

    def get_handle_pos(self, handle):
        return self.__handle_pos[handle]

    def clear_handle_pos(self, handle):
        self.__handle_pos[handle] = QtCore.QPointF(0, 0)

    def set_handle_pos(self, point, handle):
        if not point:
            if handle != editor.model.common.KNOT:
                self.__handle_pos[handle] = None
            return

        knot_delta = self.__handle_pos[editor.model.common.KNOT] - point

        self.__handle_pos[handle] = QtCore.QPointF(point)

        if self.__handle_pos[editor.model.common.LEFT_HANDLE]:
            l_delta = self.__handle_pos[editor.model.common.LEFT_HANDLE] - self.__handle_pos[editor.model.common.KNOT]
        else:
            l_delta = QtCore.QPointF(0, 0)
        
        if self.__handle_pos[editor.model.common.RIGHT_HANDLE]:
            r_delta = self.__handle_pos[editor.model.common.KNOT] - self.__handle_pos[editor.model.common.RIGHT_HANDLE]
        else:
            r_delta = QtCore.QPointF(0, 0)

        left_len = math.sqrt(float(l_delta.x() * l_delta.x()) + \
            float(l_delta.y() * l_delta.y()))
        right_len = math.sqrt(float(r_delta.x() * r_delta.x()) + \
            float(r_delta.y() * r_delta.y()))

        if handle == editor.model.common.KNOT:
            if self.__handle_pos[editor.model.common.LEFT_HANDLE]:
                self.__handle_pos[editor.model.common.LEFT_HANDLE] -= knot_delta
            if self.__handle_pos[editor.model.common.RIGHT_HANDLE]:
                self.__handle_pos[editor.model.common.RIGHT_HANDLE] -= knot_delta

        elif self.__behavior == editor.model.common.SMOOTH:
            if handle == editor.model.common.RIGHT_HANDLE and self.__handle_pos[editor.model.common.LEFT_HANDLE]:
                if right_len > 0:
                    l_delta = r_delta * left_len / right_len
                self.__handle_pos[editor.model.common.LEFT_HANDLE] = self.__handle_pos[editor.model.common.KNOT] + l_delta
            elif self.__handle_pos[editor.model.common.RIGHT_HANDLE]:
                if left_len > 0:
                    r_delta = l_delta * right_len / left_len
                self.__handle_pos[editor.model.common.RIGHT_HANDLE] = self.__handle_pos[editor.model.common.KNOT] - r_delta

        elif self.__behavior == editor.model.common.SYMMETRIC:
            if handle == editor.model.common.RIGHT_HANDLE and self.__handle_pos[editor.model.common.LEFT_HANDLE]:
                self.__handle_pos[editor.model.common.LEFT_HANDLE] = self.__handle_pos[editor.model.common.KNOT] + old_r_delta
            elif self.__handle_pos[editor.model.common.RIGHT_HANDLE]:
                self.__handle_pos[editor.model.common.RIGHT_HANDLE] = self.__handle_pos[editor.model.common.KNOT] - old_l_delta


    def get_handle_pos_as_list(self):
        knot = [self.__handle_pos[editor.model.common.KNOT].x(), self.__handle_pos[editor.model.common.KNOT].y()]
        handle_list = []

        if self.__handle_pos[editor.model.common.LEFT_HANDLE]:
            handle_list.append([self.__handle_pos[editor.model.common.LEFT_HANDLE].x(), \
                self.__handle_pos[editor.model.common.LEFT_HANDLE].y()])

        handle_list.append(knot)

        if self.__handle_pos[editor.model.common.RIGHT_HANDLE]:
            handle_list.append([self.__handle_pos[editor.model.common.RIGHT_HANDLE].x(), \
                self.__handle_pos[editor.model.common.RIGHT_HANDLE].y()])

        return handle_list

    def select_handle(self, select):
        if select and ((select == editor.model.common.LEFT_HANDLE) or \
            (select == editor.model.common.RIGHT_HANDLE) or \
            (select == editor.model.common. KNOT)):
            self.__selected = select
        else:
            self.__selected = None

    def select_left_handle(self, select=False):
        if select:
            self.__selected = editor.model.common.LEFT_HANDLE
        elif self.__selected == editor.model.common.LEFT_HANDLE:
            self.__selected = None

    def select_right_handle(self, select=False):
        if select:
            self.__selected = editor.model.common.RIGHT_HANDLE
        elif self.__selected == editor.model.common.RIGHT_HANDLE:
            self.__selected = None

    def select_knot(self, select=False):
        if select:
            self.__selected = editor.model.common.KNOT
        elif self.__selected == editor.model.common.KNOT:
            self.__selected = None

    def is_right_handle_selected(self):
        return (self.__selected is not None) and (self.__selected == editor.model.common.RIGHT_HANDLE)

    def is_left_handle_selected(self):
        return (self.__selected is not None) and (self.__selected == editor.model.common.LEFT_HANDLE)

    def is_knot_selected(self):
        return (self.__selected is not None) and (self.__selected == editor.model.common.KNOT)

    selected = property(get_selected_handle, select_handle)

    def set_pos_of_selected(self, point):
        if self.__selected is None:
            pass
        elif self.__selected == editor.model.common.KNOT:
            self.set_pos(point)
        else:
            self.set_handle_pos(point, self.__selected)

    def get_pos_of_selected(self):
        if self.__selected is None:
            return None
        else:
            return self.__handle_pos[self.__selected]

    selected_handle_pos = property(get_pos_of_selected, set_pos_of_selected)

    def set_behavior(self, new_behavior):
        if self.__selected is None:
            return

        self.__behavior = new_behavior

        if self.__behavior == editor.model.common.SHARP:
            return

        self.set_handle_pos(self.__handle_pos[self.__selected], self.__selected)

    def set_behavior_to_smooth(self):
        self.set_behavior(editor.model.common.SMOOTH)

    def set_behavior_to_sharp(self):
        self.set_behavior(editor.model.common.SHARP)

    def set_behavior_to_symmetric(self):
        self.set_behavior(editor.model.common.SYMMETRIC)

    def get_behavior(self):
        return self.__behavior

    behavior = property(get_behavior, set_behavior)

    def draw(self, gc):
        return
