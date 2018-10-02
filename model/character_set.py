import model.character
import model.instance
import model.stroke

class CharacterSet(object):
    def __init__(self):
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

        self.__current_char = None

        self.__char_type = type(model.character.Character(self)).__name__
        self.__stroke_type = type(model.stroke.Stroke()).__name__
        self.__glyph_type = type(model.character.Glyph(self)).__name__
        self.__stroke_inst_type = type(model.instance.StrokeInstance()).__name__
        self.__glyph_inst_type = type(model.instance.GlyphInstance(self)).__name__

        self.__objects = {}
        self.__objects[self.__char_type] = {}
        self.__objects[self.__stroke_type] = {}
        self.__objects[self.__glyph_type] = {}
        self.__objects[self.__stroke_inst_type] = {}
        self.__objects[self.__glyph_inst_type] = {}
        
        self.__character_xref = {}

        self.__char_id = 0
        self.__glyph_id = 0
        self.__stroke_id = 0
        self.__glyph_inst_id = 0

    def __get_next_char_id(self):
        self.__char_id += 1
        return "C" + '{:010d}'.format(self.__char_id)

    def __get_next_glyph_id(self):
        self.__glyph_id += 1
        return "G" + '{:010d}'.format(self.__glyph_id)

    def __get_next_stroke_id(self):
        self.__stroke_id += 1
        return "S" + '{:010d}'.format(self.__stroke_id)

    def __get_next_glyph_inst_id(self):
        self.__glyph_inst_id += 1
        return "X" + '{:010d}'.format(self.__glyph_inst_id)

    def new_character(self, char_code):
        new_char = model.character.Character(self)
        new_char_id = self.__get_next_char_id()
        
        self.__objects[self.__char_type][new_char_id] = new_char

        if char_code:
            new_char.unicode_character = char_code
            self.__character_xref[unichr(char_code)] = new_char_id

        self.__current_char = new_char_id

        return new_char_id

    def delete_char(self, char_to_delete):
        if char_to_delete in self.__objects[self.__char_type]:
            char_code = self.__objects[self.__char_type][char_to_delete].unicode_character
            self.__objects[self.__char_type][char_to_delete] = None
            del self.__character_xref[unichr(char_code)]
        elif char_to_delete in self.__character_xref:
            char = self.__character_xref[char_to_delete]
            self.__objects[self.__char_type][char] = None
            del self.__character_xref[char_to_delete]

    def get_current_char(self):
        if self.__current_char is not None:
            return self.__objects[self.__char_type][self.__current_char]

        return None

    def set_current_char(self, char):
        unicode_char = unichr(char)
        if unicode_char in self.__character_xref:
            self.__current_char = self.__character_xref[unicode_char]
        else:
            self.new_character(char)

    current_char = property(get_current_char, set_current_char)

    def get_current_char_name(self):
        current_char_object = self.__objects[self.__char_type][self.__current_char]
        return unichr(current_char_object.unicode_character)

    def get_current_char_index(self):
        return self.__current_char

    def get_char(self, char_to_get):
        if char_to_get in self.__objects[self.__char_type]:
            return self.__objects[self.__char_type][char_to_get]

        if char_to_get in self.__character_xref:
            char_id = self.__character_xref[char_to_get]
            return self.__objects[self.__char_type][char_id]

        return None

    def get_char_index(self, char_to_get):
        if char_to_get in self.__character_xref:
            return self.__character_xref[char_to_get]

        return None

    @property
    def objects(self):
        return self.__objects

    @property
    def characters(self):
        return self.__objects[self.__char_type]

    def get_char_by_index(self, char_index):
        char_to_get = unichr(char_index)
        return self.get_char(char_to_get)

    def get_char_list(self):
        return self.__objects[self.__char_type]

    @property
    def glyphs(self):
        return self.__objects[self.__glyph_type]

    def save_glyph(self, item):
        glyph_id = self.__get_next_glyph_id()
        self.__objects[self.__glyph_type][glyph_id] = item
        return glyph_id

    def insert_glyph(self, glyph_id, item):
        self.__objects[self.__glyph_type][glyph_id] = item
        
    def get_saved_glyph(self, glyph_id):
        if glyph_id in self.__objects[self.__glyph_type]:
            return self.__objects[self.__glyph_type][glyph_id]

        return None

    def set_saved_glyph(self, glyph_id, stroke):
        if glyph_id not in self.__objects[self.__glyph_type]:
            return

        tmp_stroke = self.__objects[self.__glyph_type][glyph_id]
        self.__objects[self.__glyph_type][glyph_id] = stroke
        del tmp_stroke

    def remove_saved_glyph(self, glyph_id):
        try:
            del self.__objects[self.__glyph_type][glyph_id]
        except IndexError:
            print "ERROR: saved glyph to remove doesn't exist!"

    saved_glyph = property(get_saved_glyph, set_saved_glyph)

    def new_glyph_instance(self, glyph):
        new_inst = model.instance.GlyphInstance(char_set=self)

        new_inst_id = self.__get_next_glyph_inst_id()
        
        self.__objects[self.__glyph_inst_type][new_inst_id] = new_inst

        if glyph:
            new_inst.instanced_object = glyph
        
        return new_inst_id

    def get_saved_glyph_instance(self, glyph_id):
        if glyph_id in self.__objects[self.__glyph_inst_type]:
            return self.__objects[self.__glyph_inst_type][glyph_id]

        return None

    def get_item_by_index(self, item_id):
        item_type = None

        if type(item_id).__name__ == 'Stroke':
            return None
            
        if item_id[0] == 'S':
            item_type = self.__stroke_type
        elif item_id[0] == 'G':
            item_type = self.__glyph_type
        elif item_id[0] == 'X':
            item_type = self.__glyph_inst_type
        elif item_id[0] == 'C':
            item_type = self.__char_type

        if item_type and item_id in self.__objects[item_type]:
            return self.__objects[item_type][item_id]

        return None    

    # attributes

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

    @property
    def height(self):
        return self.__base_height_nibs + self.__descent_height_nibs + \
            self.__ascent_height_nibs
             
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
