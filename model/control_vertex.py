
import math
import struct

from PyQt4 import QtCore, QtGui

import view.handle
import view.shared_qt

SMOOTH      = 1
SHARP       = 2
SYMMETRIC   = 3

LEFT_HANDLE     = 1
RIGHT_HANDLE    = 3
KNOT            = 2

MAGIC_NONE = 987654321

KNOT_HANDLE_OBJ      = view.handle.TristateHandle()
SMOOTH_HANDLE_OBJ    = view.handle.RoundHandle()
SHARP_HANDLE_OBJ     = view.handle.TriangleHandle()
SYMMETRIC_HANDLE_OBJ = view.handle.SemicircleHandle()

class ControlVertex(object):
    def __init__(self, left=None, knot=QtCore.QPointF(), right=None, \
        new_behavior=SMOOTH, char_set=None):
        self.__pressure = 1.0
        self.__behavior = new_behavior
        self.__handle_pos = [0, left, knot, right]
        self.__handle_scale = 1.0
        self.__char_set = char_set
        self.__selected = None

    def serialize(self):
        data = struct.pack("<fH", self.__pressure, \
            self.__behavior)
        
        for i in range(1, 4):
            if self.__handle_pos[i] is not None:
                data += struct.pack("<dd", self.__handle_pos[i].x(), \
                    self.__handle_pos[i].y())
            else:
                data += struct.pack("<dd", MAGIC_NONE, MAGIC_NONE)

        data += struct.pack("<f", self.__handle_scale)
        
        return data

    def unserialize(self, data):
        offset = 0
        (self.__pressure, self.__behavior) = struct.unpack_from("<fH", data)
        offset += struct.calcsize("<fH")
        for i in range(1, 4):
            (x, y) = struct.unpack_from("<dd", data, offset)
            offset += struct.calcsize("<dd")
            if x == MAGIC_NONE and y == MAGIC_NONE:
                self.__handle_pos[i] = None
            else:
                self.__handle_pos[i] = QtCore.QPointF(x, y)

        self.__handle_scale = struct.unpack_from("<f", data, offset)[0]
        self.__selected = None

    def contains(self, test_point):
        handle_size = self.__char_set.user_preferences.preferences['handle_size_spin']
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
        self.set_handle_pos(point, KNOT)

    def get_pos(self):
        return self.__handle_pos[KNOT]

    pos = property(get_pos, set_pos)

    def get_selected_handle(self):
        return self.__selected

    def get_handle_pos(self, handle):
        return self.__handle_pos[handle]

    def clear_handle_pos(self, handle):
        self.__handle_pos[handle] = QtCore.QPointF(0, 0)

    def set_handle_pos(self, point, handle):
        if not point:
            if handle != KNOT:
                self.__handle_pos[handle] = None
            return

        if self.__handle_pos[LEFT_HANDLE]:
            old_l_delta = self.__handle_pos[LEFT_HANDLE] - self.__handle_pos[KNOT]
        else:
            old_l_delta = QtCore.QPointF(0, 0)

        old_knot_delta = self.__handle_pos[KNOT] - point

        if self.__handle_pos[RIGHT_HANDLE]:
            old_r_delta = self.__handle_pos[KNOT] - self.__handle_pos[RIGHT_HANDLE]
        else:
            old_r_delta = QtCore.QPointF(0, 0)

        left_len = math.sqrt(float(old_l_delta.x() * old_l_delta.x()) + \
            float(old_l_delta.y() * old_l_delta.y()))
        right_len = math.sqrt(float(old_r_delta.x() * old_r_delta.x()) + \
            float(old_r_delta.y() * old_r_delta.y()))

        if handle == KNOT:
            if self.__handle_pos[LEFT_HANDLE]:
                self.__handle_pos[LEFT_HANDLE] -= old_knot_delta
            if self.__handle_pos[RIGHT_HANDLE]:
                self.__handle_pos[RIGHT_HANDLE] -= old_knot_delta

        elif self.__behavior == SMOOTH:
            if handle == RIGHT_HANDLE and self.__handle_pos[LEFT_HANDLE]:
                if right_len == 0:
                    l_delta = old_l_delta
                else:
                    l_delta = -old_r_delta * left_len / right_len
                self.__handle_pos[LEFT_HANDLE] = self.__handle_pos[KNOT] - l_delta
            elif self.__handle_pos[RIGHT_HANDLE]:
                if left_len == 0:
                    r_delta = old_r_delta
                else:
                    r_delta = -old_l_delta * right_len / left_len
                self.__handle_pos[RIGHT_HANDLE] = self.__handle_pos[KNOT] + r_delta

        elif self.__behavior == SYMMETRIC:
            if handle == RIGHT_HANDLE and self.__handle_pos[LEFT_HANDLE]:
                self.__handle_pos[LEFT_HANDLE] = self.__handle_pos[KNOT] + old_r_delta
            elif self.__handle_pos[RIGHT_HANDLE]:
                self.__handle_pos[RIGHT_HANDLE] = self.__handle_pos[KNOT] - old_l_delta

        self.__handle_pos[handle] = QtCore.QPointF(point)

    def get_handle_pos_as_list(self):
        knot = [self.__handle_pos[KNOT].x(), self.__handle_pos[KNOT].y()]
        handle_list = []

        if self.__handle_pos[LEFT_HANDLE]:
            handle_list.append([self.__handle_pos[LEFT_HANDLE].x(), \
                self.__handle_pos[LEFT_HANDLE].y()])

        handle_list.append(knot)

        if self.__handle_pos[RIGHT_HANDLE]:
            handle_list.append([self.__handle_pos[RIGHT_HANDLE].x(), \
                self.__handle_pos[RIGHT_HANDLE].y()])

        return handle_list

    def select_handle(self, select):
        if select and ((select == LEFT_HANDLE) or (select == RIGHT_HANDLE) or (select == KNOT)):
            self.__selected = select
        else:
            self.__selected = None

    def select_left_handle(self, select=False):
        if select:
            self.__selected = LEFT_HANDLE
        elif self.__selected == LEFT_HANDLE:
            self.__selected = None

    def select_right_handle(self, select=False):
        if select:
            self.__selected = RIGHT_HANDLE
        elif self.__selected == RIGHT_HANDLE:
            self.__selected = None

    def select_knot(self, select=False):
        if select:
            self.__selected = KNOT
        elif self.__selected == KNOT:
            self.__selected = None

    def is_right_handle_selected(self):
        return (self.__selected is not None) and (self.__selected == RIGHT_HANDLE)

    def is_left_handle_selected(self):
        return (self.__selected is not None) and (self.__selected == LEFT_HANDLE)

    def is_knot_selected(self):
        return (self.__selected is not None) and (self.__selected == KNOT)

    def set_pos_of_selected(self, point):
        if self.__selected is None:
            pass
        elif self.__selected == KNOT:
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

        if self.__behavior == SHARP:
            return

        self.set_handle_pos(self.__handle_pos[self.__selected], self.__selected)

    def set_behavior_to_smooth(self):
        self.set_behavior(SMOOTH)

    def set_behavior_to_sharp(self):
        self.set_behavior(SHARP)

    def set_behavior_to_symmetric(self):
        self.set_behavior(SYMMETRIC)

    def get_behavior(self):
        return self.__behavior

    behavior = property(get_behavior, set_behavior)

    def draw(self, gc):
        vert = self.__handle_pos[KNOT]

        handle_size = self.__char_set.user_preferences.preferences['handle_size_spin']
        KNOT_HANDLE_OBJ.size = handle_size

        gc.setPen(view.shared_qt.PEN_MD_GRAY)

        gc.save()
        gc.translate(vert)
        KNOT_HANDLE_OBJ.draw(gc, self.__selected == KNOT, self.__selected and self.__selected != KNOT)
        gc.restore()

        if self.__behavior == SMOOTH:
            path = SMOOTH_HANDLE_OBJ
        elif self.__behavior == SHARP:
            path = SHARP_HANDLE_OBJ
        else:
            path = SYMMETRIC_HANDLE_OBJ

        path.size = handle_size

        vert = self.__handle_pos[LEFT_HANDLE]
        if vert:
            gc.setPen(view.shared_qt.PEN_LT_GRAY)
            gc.drawLine(self.__handle_pos[KNOT], vert)
            gc.setPen(view.shared_qt.PEN_LT_GRAY_2)

            gc.save()
            gc.translate(vert)
            path.draw(gc, self.__selected == LEFT_HANDLE)
            gc.restore()

        vert = self.__handle_pos[RIGHT_HANDLE]
        if vert:
            gc.setPen(view.shared_qt.PEN_LT_GRAY)
            gc.drawLine(self.__handle_pos[KNOT], vert)
            gc.setPen(view.shared_qt.PEN_LT_GRAY_2)

            gc.save()
            gc.translate(vert)
            path.draw(gc, self.__selected == RIGHT_HANDLE)
            gc.restore()
