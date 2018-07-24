from PyQt4 import QtCore

import model.instance

class Layout(object):
    def __init__(self):
        self.__object_list = []
        self.__pos = QtCore.QPoint()

    def set_object_list(self, new_object_list):
        self.__object_list = new_object_list

    def get_object_list(self):
        return self.__object_list

    object_list = property(get_object_list, set_object_list)

    def add_object(self, object_to_add):
        self.__object_list.append(object_to_add)
        object_to_add.parent = self

    def remove_object(self, object_to_remove):
        self.__object_list.remove(object_to_remove)
        object_to_remove.parent = None

    def set_pos(self, point):
        self.__pos = point

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def init_with_string(self, string_to_layout, char_set, nib_width):
        height = char_set.base_height * nib_width
        cur_char = char_set.get_current_char_index()

        for char in self.object_list:
            del char

        self.object_list = []

        for char in string_to_layout:
            char_object = char_set.get_char(char)

            if char_object is None:
                char_set.new_character(ord(char))
                char_object = char_set.get_char(char)

            new_character = model.instance.CharacterInstance()
            new_character.character = char_object
            self.add_object(new_character)
        
        char_set.set_current_char(cur_char)
        self.update_layout(char_set, nib_width)

    def update_layout(self, char_set, nib_width):
        layout_total_length = 0
        current_x = 0
        prev_right_space = 0

        for char_object in self.object_list:
            if char_object.character.override_spacing:
                width = char_object.character.width
                left_space = char_object.character.left_spacing
                right_space = char_object.character.right_spacing
            else:
                width = char_set.width
                left_space = char_set.left_spacing
                right_space = char_set.right_spacing

            delta_x = (width + left_space + prev_right_space) * nib_width 
            current_x += delta_x
            prev_right_space = right_space

            char_object.pos = QtCore.QPoint(current_x, 0)

            layout_total_length += delta_x 

        self.__pos = QtCore.QPoint(-layout_total_length / 2, 0)