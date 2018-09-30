from PyQt4 import QtCore

import model.character_set
import view.shared_qt

class Instance(object):
    def __init__(self, parent=None, char_set=None):
        self.__instanced_object = None
        self.__pos = QtCore.QPoint()
        self.__parent = parent
        self.__char_set = char_set
        self.__is_selected = False
        self.__obj_type = None

    def __del__(self):
        pass
        #if self.__instanced_object:
        #    self.__instanced_object.remove_instance(self)

    def set_pos(self, point):
        self.__pos = QtCore.QPoint(point)

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def get_obj_type(self):
        return self.__obj_type

    def set_obj_type(self, new_obj_type):
        self.__obj_type = new_obj_type

    obj_type = property(get_obj_type, set_obj_type)

    def set_instanced_object(self, new_instanced_object):
        if self.__instanced_object:
            self.actual_object.remove_instance(self)
        
        self.__instanced_object = new_instanced_object

        if self.__char_set:    
            self.__pos = QtCore.QPoint(self.actual_object.get_pos())
        
            self.actual_object.add_instance(self)

    def get_instanced_object(self):
        return self.__instanced_object

    instanced_object = property(get_instanced_object, set_instanced_object)

    def get_actual_object(self):
        if self.__char_set:
            return self.__char_set.objects[self.obj_type][self.__instanced_object]

        return None

    actual_object = property(get_actual_object)

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
        if self.__instanced_object and self.__char_set:
            test_point = point - self.__pos
            is_inside =  self.actual_object.is_inside(test_point)
        else:
            is_inside = (False, -1, None)

        return is_inside

    def is_contained(self, rect):
        if self.__instanced_object is not None:
            return self.actual_object.is_contained(rect)
        
        return False

    @property
    def bound_rect(self):
        if self.actual_object:
            return self.actual_object.bound_rect
            
    def draw(self, gc, nib=None):
        if self.actual_object is None:
            return

        object_to_draw = self.actual_object
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
            gc.setPen(view.shared_qt.PEN_DK_GRAY_DASH_0)

            gc.drawRect(bound_rect)

            gc.restore()


class StrokeInstance(Instance):
    def __init__(self, parent=None, char_set=None):
        Instance.__init__(self, parent, char_set)
        self.obj_type = "Stroke"

    stroke = property(Instance.get_instanced_object, Instance.set_instanced_object)

    def get_stroke_shape(self):
        return self.stroke.get_stroke_shape()

    def get_bound_rect(self):
        return self.stroke.get_bound_rect()

    def is_inside(self, point):
        if self.stroke is not None:
            stroke_pos = self.stroke.pos
            test_point = point + stroke_pos - self.__pos
            is_inside = self.stroke.is_inside(test_point)
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
    def __init__(self, parent=None, char_set=None):
        Instance.__init__(self, parent, char_set)
        self.obj_type = "Glyph"

    glyph = property(Instance.get_actual_object)

    @property
    def strokes(self):
        if self.glyph:
            return self.glyph.strokes

        return []

class CharacterInstance(Instance):
    def __init__(self, parent=None, char_set=None):
        Instance.__init__(self, parent, char_set)
        self.obj_type = "Character"

    character = property(Instance.get_actual_object)

    @property
    def children(self):
        if self.character:
            return self.character.children

        return []