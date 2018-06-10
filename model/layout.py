from PyQt4 import QtCore

import model.instance

class Layout(object):
    def __init__(self):
        self.__object_list = []
        self.__pos = QtCore.QPoint()

    def set_object_list(self, new_objects):
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

    def init_with_string(self, string_to_layout, char_set, nib_width=20):
        layout_total_length = 0
        height = char_set.base_height * nib_width
        current_x = 0

        prev_left_space = 0
        for char in string_to_layout:
            char_object = char_set.get_char(char)

            if char_object is None:
                char_set.new_character(unichr(ord(char)))
                char_object = char_set.get_char(char)

            if char_object.override_spacing:
                width = char_object.width
                left_space = char_object.left_spacing
                right_space = char_object.right_spacing
            else:
                width = char_set.width
                left_space = char_set.left_spacing
                right_space = char_set.right_spacing

            current_x += (width + right_space + prev_left_space) * nib_width
            prev_left_space = left_space

            new_character = model.instance.CharacterInstance()
            new_character.character = char_object
            new_character.pos = QtCore.QPoint(current_x, 0)
            self.add_object(new_character)

            layout_total_length += (width + left_space + right_space) * nib_width 

        self.__pos = QtCore.QPoint(-layout_total_length / 2, 0)

    def update_layout(self):
        pass