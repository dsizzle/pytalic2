from PyQt4 import QtCore

import model.instance

class Layout(object):
    def __init__(self):
        self.__object_list = []
        self.__string = ""
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

    def init_with_string(self, string_to_layout, char_set, nib_width, line_width=10):
        height = char_set.base_height * nib_width
        cur_char = char_set.get_current_char_index()

        for char in self.object_list:
            del char

        self.object_list = []

        self.__string = string_to_layout

        for char in self.__string:
            char_object = char_set.get_char(char)

            if char_object is None:
                char_set.new_character(ord(char))
                char_object = char_set.get_char(char)

            new_character = model.instance.CharacterInstance()
            new_character.character = char_object
            self.add_object(new_character)
        
        char_set.set_current_char(cur_char)

        self.update_layout(char_set, nib_width, line_width)

    def update_layout(self, char_set, nib_width, line_width=10):
        layout_total_height = 0
        current_x = 0
        current_y = 0
        gap_height = char_set.gap_height
        height = char_set.height
        max_x = nib_width * line_width * \
            (char_set.width + char_set.left_spacing + char_set.right_spacing)

        lines = self.__lay_out_with_wrap(self.__string, line_width)
        char_obj_idx = 0
            
        for line in lines:
            num_chars = 0
            for char in line:
                char_object = self.__object_list[char_obj_idx]
                while char_object.character.name != char:
                    start_char_idx = char_obj_idx
                    char_obj_idx += 1
                    try:
                        char_object = self.__object_list[char_obj_idx]
                    except IndexError:
                        char_obj_idx = start_char_idx
                        break

                if char_object.character.override_spacing:
                    width = char_object.character.width
                    left_space = char_object.character.left_spacing
                    right_space = char_object.character.right_spacing
                else:
                    width = char_set.width
                    left_space = char_set.left_spacing
                    right_space = char_set.right_spacing

                current_x += (left_space + width) * nib_width
                char_object.pos = QtCore.QPoint(current_x, current_y)

                delta_x = right_space * nib_width 
                current_x += delta_x
                char_obj_idx += 1
                num_chars += 1

            center_x = current_x / 2
            start = char_obj_idx - 1
            end = start - num_chars
            center_delta = QtCore.QPoint(center_x, 0)
            for idx in range(start, end, -1):
                self.__object_list[idx].pos -= center_delta

            current_x = 0
            current_y += (height + gap_height) * nib_width
            layout_total_height += (height + gap_height) * nib_width

        self.__pos = QtCore.QPoint(-max_x / 2, -layout_total_height / 2)

    def __lay_out_with_wrap(self, string_to_layout, line_width=10):
        token_list = string_to_layout.split()
        token_list.reverse() 

        line = []
        lines = []
        chars_left = line_width
        while (len(token_list)):
            token = token_list.pop()
            
            if len(token) > line_width:
                token_rem = token[line_width:]
                token_list.append(token_rem)
                token_list.append(token[:line_width])

            elif len(token) <= chars_left:
                line.append(token)
                chars_left -= len(token)
            
            else:
                line_string = ' '.join(line)
                line = []
                chars_left = line_width

                lines.append(line_string)
                token_list.append(token)               

        line_string = ' '.join(line)
        lines.append(line_string)

        return lines