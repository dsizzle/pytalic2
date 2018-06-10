import model.character

class CharacterSet(object):
    def __init__(self):
        self.__characters = {}
        self.__current_char = None

        self.__nominal_width_nibs = 4.0
        self.__left_spacing = 1.0
        self.__right_spacing = 1.0
        self.__base_height_nibs = 5.0
        self.__ascent_height_nibs = 3.0
        self.__descent_height_nibs = 3.0
        self.__cap_height_nibs = 2.0
        self.__gap_height_nibs = 1.0
        self.__guide_angle = 5
        self.__nib_angle = 40

        self.__saved_glyphs = []

    def new_character(self, char_code):
        my_char = model.character.Character()
        self.__characters[char_code] = my_char
        self.__current_char = char_code

    def delete_char(self, char_to_delete):
        try:
            self.__characters[char_to_delete] = None
        except ValueError:
            print "ERROR: character to delete doesn't exist!"

    def get_current_char(self):
        if self.__current_char is not None:
            return self.__characters[self.__current_char]

        return None

    def set_current_char(self, char):
        unicode_char = unichr(char)
        if unicode_char in self.__characters:
            self.__current_char = unicode_char
        else:
            self.new_character(unicode_char)

    current_char = property(get_current_char, set_current_char)

    def get_current_char_name(self):
        return unichr(self.__current_char)

    def get_current_char_index(self):
        return self.__current_char

    def get_char(self, char_to_get):
        if char_to_get in self.__characters:
            return self.__characters[char_to_get]

        return None

    def get_char_list(self):
        return self.__characters

    def get_saved_glyphs(self):
        return self.__saved_glyphs

    def save_glyph(self, item):
        self.__saved_glyphs.append(item)

    def insert_glyph(self, index, item):
        self.__saved_glyphs.insert(index, item)
        
    def get_saved_glyph(self, index):
        if len(self.__saved_glyphs) > index and index >= 0:
            return self.__saved_glyphs[index]

        return None

    def set_saved_glyph(self, index, stroke):
        if len(self.__saved_glyphs) < index:
            return

        tmp_stroke = self.__saved_glyphs[index]
        self.__saved_glyphs[index] = stroke
        del tmp_stroke

    def remove_saved_glyph(self, item):
        try:
            self.__saved_glyphs.remove(item)
        except IndexError:
            print "ERROR: saved stroke to remove doesn't exist!"

    saved_glyph = property(get_saved_glyph, set_saved_glyph)

    def set_nominal_width(self, new_width):
        self.__nominal_width_nibs = new_width

    def get_nominal_width(self):
        return self.__nominal_width_nibs

    width = property(get_nominal_width, set_nominal_width)

    def set_left_spacing(self, new_left_spacing):
        self.__left_spacing = new_left_spacing

    def get_left_spacing(self):
        return self.__left_spacing

    left_spacing = property(get_left_spacing, set_left_spacing)

    def set_right_spacing(self, new_right_spacing):
        self.__right_spacing = new_right_spacing

    def get_right_spacing(self):
        return self.__right_spacing

    right_spacing = property(get_right_spacing, set_right_spacing) 

    def set_base_height(self, new_base_height):
        self.__base_height_nibs = new_base_height

    def get_base_height(self):
        return self.__base_height_nibs

    base_height = property(get_base_height, set_base_height)

    def set_ascent_height(self, new_ascent_height):
        self.__ascent_height_nibs = new_ascent_height

    def get_ascent_height(self):
        return self.__ascent_height_nibs

    ascent_height = property(get_ascent_height, set_ascent_height)

    def set_descent_height(self, new_descent_height):
        self.__descent_height_nibs = new_descent_height

    def get_descent_height(self):
        return self.__descent_height_nibs

    descent_height = property(get_descent_height, set_descent_height)

    def set_cap_height(self, new_cap_height):
        self.__cap_height_nibs = new_cap_height

    def get_cap_height(self):
        return self.__cap_height_nibs

    cap_height = property(get_cap_height, set_cap_height)

    def set_gap_height(self, new_gap_height):
        self.__gap_height_nibs = new_gap_height

    def get_gap_height(self):
        return self.__gap_height_nibs

    gap_height = property(get_gap_height, set_gap_height)

    def set_guide_angle(self, new_angle):
        self.__guide_angle = new_angle

    def get_guide_angle(self):
        return self.__guide_angle

    guide_angle = property(get_guide_angle, set_guide_angle)

    def set_nib_angle(self, new_angle):
        self.__nib_angle = new_angle

    def get_nib_angle(self):
        return self.__nib_angle

    nib_angle = property(get_nib_angle, set_nib_angle)
