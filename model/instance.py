from PyQt4 import QtCore

import view.shared_qt

class Instance(object):
    def __init__(self, parent=None):
        self.__instanced_object = None
        self.__pos = QtCore.QPoint()
        self.__parent = parent
        self.__is_selected = False

    def __del__(self):
        if self.__instanced_object:
            self.__instanced_object.remove_instance(self)

    def set_pos(self, point):
        self.__pos = point

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def set_instanced_object(self, new_instanced_object):
        if self.__instanced_object:
            self.__instanced_object.remove_instance(self)

        self.__instanced_object = new_instanced_object

        self.__pos = QtCore.QPoint(new_instanced_object.get_pos())
        
        self.__instanced_object.add_instance(self)

    def get_instanced_object(self):
        return self.__instanced_object

    instanced_object = property(get_instanced_object, set_instanced_object)

    def set_parent(self, parent):
        self.__parent = parent

    def get_parent(self):
        return self.__parent

    parent = property(get_parent, set_parent)

    def get_select_state(self):
        return self.__is_selected

    def set_select_state(self, new_state):
        self.__is_selected = new_state

    selected = property(get_select_state, set_select_state)

    def is_inside(self, point):
        if self.__instanced_object is not None:
            test_point = point - self.__pos
            is_inside = self.__instanced_object.is_inside(test_point)
        else:
            is_inside = (False, -1, None)

        return is_inside

    def draw(self, gc, nib=None):
        if self.__instanced_object is None:
            return

        object_to_draw = self.__instanced_object
        object_pos = object_to_draw.pos

        gc.save()
        gc.translate(-object_pos)
        gc.translate(self.__pos)

        object_to_draw.draw(gc, nib)
        gc.restore()

        bound_rect = object_to_draw.bound_rect

        if self.__is_selected:
            gc.save()

            gc.translate(self.__pos)
            gc.setBrush(view.shared_qt.BRUSH_CLEAR)
            gc.setPen(view.shared_qt.PEN_MD_GRAY_DOT_2)

            gc.drawRect(bound_rect)

            gc.restore()


class StrokeInstance(Instance):
    def __init__(self, parent=None):
        Instance.__init__(self, parent)

    stroke = property(Instance.get_instanced_object, Instance.set_instanced_object)

    def get_stroke_shape(self):
        return self.stroke.get_stroke_shape()

    def get_bound_rect(self):
        return self.__stroke.get_bound_rect()

    def is_inside(self, point):
        if self.__stroke is not None:
            stroke_pos = self.__stroke.pos
            test_point = point + stroke_pos - self.__pos
            is_inside = self.__stroke.is_inside(test_point)
        else:
            is_inside = (False, -1, None)

        return is_inside

    def deselect_ctrl_verts(self):
        if self.stroke:
            self.stroke.deselect_ctrl_verts()

    def calc_curve_points(self):
        if self.stroke:
            self.stroke.calc_curve_points()


class GlyphInstance(Instance):
    def __init__(self, parent=None):
        Instance.__init__(self, parent)

    glyph = property(Instance.get_instanced_object, Instance.set_instanced_object)

    @property
    def strokes(self):
        if self.glyph:
            return self.glyph.strokes

        return None


class CharacterInstance(Instance):
    def __init__(self, parent=None):
        Instance.__init__(self, parent)

    character = property(Instance.get_instanced_object, Instance.set_instanced_object)
