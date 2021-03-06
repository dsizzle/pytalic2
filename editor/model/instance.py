import struct

from PyQt5 import QtCore

#import editor.view.shared_qt

class Instance(object):
    def __init__(self, char_set=None, parent=None):
        self.__instanced_object = None
        self.__pos = QtCore.QPoint()
        self.__parent = parent
        self.__char_set = char_set
        self.__is_selected = False
        self.__obj_type = None

        self.__scale = 1

    def serialize(self):
        data = struct.pack("<11s", self.__instanced_object.encode('utf-8'))

        data += struct.pack("<dd", self.__pos.x(), self.__pos.y())
        # instances?
        data += struct.pack("<15s", self.__obj_type.encode('utf-8'))
        data += struct.pack("<f", self.__scale)

        return data

    def unserialize(self, data):
        offset = 0
        self.__instanced_object = struct.unpack_from("<11s", data)[0].decode('utf-8')
        offset += struct.calcsize("<11s")
        (x, y) = struct.unpack_from("<dd", data, offset)
        offset += struct.calcsize("<dd")
        self.__pos = QtCore.QPoint(x, y)
        (self.__obj_type, self.__scale) = struct.unpack_from("<15sf", data, offset)
        self.__obj_type = self.__obj_type.decode('utf-8').strip('\0')

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

    def get_scale(self):
        return self.__scale

    def set_scale(self, new_scale):
        self.__scale = new_scale

    scale = property(get_scale, set_scale)

    def is_inside(self, point, handle_size=None):
        if self.__instanced_object and self.__char_set:
            test_point = (point - self.__pos) / self.__scale  #(point / self.__scale) - self.__pos
            is_inside =  self.actual_object.is_inside(test_point)
        else:
            is_inside = (False, -1, None)

        return is_inside

    def is_contained(self, rect):
        if self.__instanced_object is not None:
            return self.actual_object.is_contained(rect.translated(-self.pos))
        
        return False

    @property
    def bound_rect(self):
        if self.actual_object:
            return self.actual_object.bound_rect
            
    def draw(self, gc, nib=None, draw_color=None):
        if self.actual_object is None:
            return

        object_to_draw = self.actual_object
        object_pos = object_to_draw.pos

        gc.save()
        
        gc.translate(-object_pos)
        gc.translate(self.__pos)
        gc.scale(self.__scale, self.__scale)
        object_to_draw.draw(gc, nib=nib, draw_color=draw_color)
        gc.restore()


class StrokeInstance(Instance):
    def __init__(self, char_set=None, parent=None):
        Instance.__init__(self, char_set, parent)
        self.obj_type = "Stroke"

    stroke = property(Instance.get_instanced_object, Instance.set_instanced_object)

    def get_stroke_shape(self):
        return self.stroke.get_stroke_shape()

    def get_bound_rect(self):
        return self.stroke.get_bound_rect()

    def is_inside(self, point, handle_size=None):
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
    def __init__(self, char_set=None, parent=None):
        Instance.__init__(self, char_set, parent)
        self.obj_type = "Glyph"

    glyph = property(Instance.get_actual_object)

    @property
    def strokes(self):
        if self.glyph:
            return self.glyph.strokes

        return []

class CharacterInstance(Instance):
    def __init__(self, char_set=None, parent=None):
        Instance.__init__(self, char_set, parent)
        self.obj_type = "Character"

    character = property(Instance.get_actual_object)

    @property
    def children(self):
        if self.character:
            return self.character.children

        return []
