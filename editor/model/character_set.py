import struct

from editor.model.character import Character, Glyph
from editor.model.instance import CharacterInstance, GlyphInstance, StrokeInstance
from editor.model.stroke import Stroke
from editor.model.control_vertex import ControlVertex
import editor.model.common

CHAR_TYPE = type(Character(None)).__name__
STROKE_TYPE = type(Stroke(None)).__name__
GLYPH_TYPE = type(Glyph(None)).__name__
STROKE_INST_TYPE = type(StrokeInstance()).__name__
GLYPH_INST_TYPE = type(GlyphInstance(None)).__name__
CHAR_INST_TYPE = type(CharacterInstance(None)).__name__
VERTEX_TYPE = type(ControlVertex(None)).__name__

STROKE_TYPE_ID = 'S'
STROKE_INST_TYPE_ID = 'Z'
GLYPH_TYPE_ID = 'G'
GLYPH_INST_TYPE_ID = 'X'
CHAR_TYPE_ID = 'C'
CHAR_INST_TYPE_ID = 'D'
VERTEX_TYPE_ID = 'V'

TYPE_MAP = {
    STROKE_TYPE_ID : STROKE_TYPE,
    GLYPH_TYPE_ID : GLYPH_TYPE,
    GLYPH_INST_TYPE_ID : GLYPH_INST_TYPE,
    CHAR_TYPE_ID : CHAR_TYPE,
    CHAR_INST_TYPE_ID : CHAR_INST_TYPE,
    VERTEX_TYPE_ID : VERTEX_TYPE,
    STROKE_INST_TYPE_ID : STROKE_INST_TYPE
}

INV_TYPE_MAP = {
    STROKE_TYPE : STROKE_TYPE_ID,
    GLYPH_TYPE : GLYPH_TYPE_ID,
    GLYPH_INST_TYPE : GLYPH_INST_TYPE_ID,
    CHAR_TYPE : CHAR_TYPE_ID,
    CHAR_INST_TYPE : CHAR_INST_TYPE_ID,
    VERTEX_TYPE : VERTEX_TYPE_ID,
    STROKE_INST_TYPE : STROKE_INST_TYPE_ID
}

VERSION = 1.0

class CharacterSet(object):
    def __init__(self, user_settings=None):
        self.__objects = {}
        
        self.__ids = {}

        self.__nominal_width_nibs = 0.0
        self.__left_spacing = 0.0
        self.__right_spacing = 0.0
        self.__base_height_nibs = 0.0
        self.__ascent_height_nibs = 0.0
        self.__descent_height_nibs = 0.0
        self.__cap_height_nibs = 0.0
        self.__gap_height_nibs = 0.0
        self.__guide_angle = 0
        self.__nib_angle = 0
        self.__user_preferences = user_settings

        self.reset()

    def reset(self):
        if self.__user_preferences:
            for preference in self.__user_preferences.preferences.keys():
                if preference in editor.model.common.SETTINGS_CONTROLS_TO_SETTINGS:
                    setattr(self, editor.model.common.SETTINGS_CONTROLS_TO_SETTINGS[preference], \
                        self.__user_preferences.preferences[preference])

        self.__current_char = None

        self.__objects[CHAR_TYPE] = {}
        self.__objects[STROKE_TYPE] = {}
        self.__objects[GLYPH_TYPE] = {}
        self.__objects[CHAR_INST_TYPE] = {}
        self.__objects[STROKE_INST_TYPE] = {}
        self.__objects[GLYPH_INST_TYPE] = {}
        self.__objects[VERTEX_TYPE] = {}
        
        self.__character_xref = {}

        self.__ids[CHAR_TYPE] = 0
        self.__ids[STROKE_TYPE] = 0
        self.__ids[GLYPH_TYPE] = 0
        self.__ids[CHAR_INST_TYPE] = 0
        self.__ids[STROKE_INST_TYPE] = 0
        self.__ids[GLYPH_INST_TYPE] = 0
        self.__ids[VERTEX_TYPE] = 0

    def get_preferences(self):
        return self.__user_preferences

    def set_preferences(self, new_user_settings):
        self.__user_preferences = new_user_settings

    user_preferences = property(get_preferences, set_preferences)

    def __get_next_id(self, item_type):
        if item_type in self.__ids:
            self.__ids[item_type] += 1

            return INV_TYPE_MAP[item_type] + '{:010d}'.format(self.__ids[item_type])

    def new_control_vertex(self, left, center, right, behavior=1):
        new_ctrl_vertex = ControlVertex(left, center, right, behavior, char_set=self)
        new_ctrl_vertex_id = self.__get_next_id(VERTEX_TYPE)
        self.__objects[VERTEX_TYPE][new_ctrl_vertex_id] = new_ctrl_vertex

        return new_ctrl_vertex_id

    def delete_control_vertex(self, vertex_id):
        if vertex_id in self.__objects[VERTEX_TYPE]:
            self.__objects[VERTEX_TYPE][vertex_id] = None

            del self.__objects[VERTEX_TYPE][vertex_id]

    def new_character_instance(self, char_index):
        new_char_inst = CharacterInstance(char_set=self)
        new_char_inst.instanced_object = char_index
        new_char_inst_id = self.__get_next_id(CHAR_INST_TYPE)
        new_char_inst.actual_object.add_instance(new_char_inst_id)

        self.__objects[CHAR_INST_TYPE][new_char_inst_id] = new_char_inst

        return new_char_inst_id

    def delete_character_instance(self, char_inst_to_delete):
        if char_inst_to_delete in self.__objects[CHAR_INST_TYPE]:
            self.__objects[CHAR_INST_TYPE][char_inst_to_delete] = None
            del self.__objects[CHAR_INST_TYPE][char_inst_to_delete]

    def new_character(self, char_code):
        new_char = Character(self)
        new_char_id = self.__get_next_id(CHAR_TYPE)
        
        self.__objects[CHAR_TYPE][new_char_id] = new_char

        if char_code:
            new_char.unicode_character = char_code
            self.__character_xref[chr(char_code)] = new_char_id

        self.__current_char = new_char_id

        return new_char_id

    def delete_char(self, char_to_delete):
        if char_to_delete in self.__objects[CHAR_TYPE]:
            char_code = self.__objects[CHAR_TYPE][char_to_delete].unicode_character
            self.__objects[CHAR_TYPE][char_to_delete] = None
            del self.__objects[CHAR_TYPE][char_to_delete]
            del self.__character_xref[chr(char_code)]
        elif char_to_delete in self.__character_xref:
            char = self.__character_xref[char_to_delete]
            self.__objects[CHAR_TYPE][char] = None
            del self.__objects[CHAR_TYPE][char]
            del self.__character_xref[char_to_delete]

    def get_current_char(self):
        if self.__current_char is not None:
            return self.__objects[CHAR_TYPE][self.__current_char]

        return None

    def set_current_char(self, char):
        unicode_char = chr(char)
        if unicode_char in self.__character_xref:
            self.__current_char = self.__character_xref[unicode_char]
        else:
            self.__current_char = self.new_character(char)

    current_char = property(get_current_char, set_current_char)

    def set_current_char_by_index(self, char_index):
        self.__current_char = char_index

    def get_current_char_name(self):
        current_char_object = self.__objects[CHAR_TYPE][self.__current_char]
        return chr(current_char_object.unicode_character)

    def get_current_char_index(self):
        return self.__current_char

    def get_char(self, char_to_get):
        if char_to_get in self.__objects[CHAR_TYPE]:
            return self.__objects[CHAR_TYPE][char_to_get]

        if char_to_get in self.__character_xref:
            char_id = self.__character_xref[char_to_get]
            return self.__objects[CHAR_TYPE][char_id]

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
        return self.__objects[CHAR_TYPE]

    @property
    def strokes(self):
        return self.__objects[STROKE_TYPE]

    def get_char_by_index(self, char_index):
        char_to_get = chr(char_index)
        return self.get_char(char_to_get)

    @property
    def glyphs(self):
        return self.__objects[GLYPH_TYPE]

    def new_glyph(self, strokes=None):
        new_glyph = Glyph(char_set=self)
        if strokes:
            new_glyph.strokes = strokes
        glyph_id = self.__get_next_id(GLYPH_TYPE)
        self.__objects[GLYPH_TYPE][glyph_id] = new_glyph

        return glyph_id
        
    def get_saved_glyph(self, glyph_id):
        if glyph_id in self.__objects[GLYPH_TYPE]:
            return self.__objects[GLYPH_TYPE][glyph_id]

        return None

    def set_saved_glyph(self, glyph_id, stroke):
        if glyph_id not in self.__objects[GLYPH_TYPE]:
            return

        tmp_stroke = self.__objects[GLYPH_TYPE][glyph_id]
        self.__objects[GLYPH_TYPE][glyph_id] = stroke
        del tmp_stroke

    def remove_saved_glyph(self, glyph_id):
        try:
            del self.__objects[GLYPH_TYPE][glyph_id]
        except IndexError:
            print("ERROR: saved glyph to remove doesn't exist!")

    saved_glyph = property(get_saved_glyph, set_saved_glyph)

    def new_glyph_instance(self, glyph):
        new_inst = GlyphInstance(char_set=self)

        new_inst_id = self.__get_next_id(GLYPH_INST_TYPE)
        
        self.__objects[GLYPH_INST_TYPE][new_inst_id] = new_inst

        if glyph:
            new_inst.instanced_object = glyph
            new_inst.actual_object.add_instance(new_inst_id)
        
        return new_inst_id

    def get_saved_glyph_instance(self, glyph_id):
        if glyph_id in self.__objects[GLYPH_INST_TYPE]:
            return self.__objects[GLYPH_INST_TYPE][glyph_id]

        return None

    def new_stroke(self, stroke=None):
        new_stroke = Stroke(char_set=self, from_stroke=stroke)
        new_stroke_id = self.__get_next_id(STROKE_TYPE)
        
        self.__objects[STROKE_TYPE][new_stroke_id] = new_stroke

        return new_stroke_id

    def delete_stroke(self, stroke_to_delete):
        if stroke_to_delete in self.__objects[STROKE_TYPE]:
            self.__objects[STROKE_TYPE][stroke_to_delete] = None
            del self.__objects[STROKE_TYPE][stroke_to_delete]

    def get_item_by_index(self, item_id):
        item_type = None

        if type(item_id).__name__ == 'Stroke':
            return None

        if item_id[0] in TYPE_MAP:
            item_type = TYPE_MAP[item_id[0]]
                    
            if item_id in self.__objects[item_type]:
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

    def save(self, fd):
        if not fd:
            return

        fd.write(struct.pack("<4sd", "PTCS".encode('utf-8'), VERSION))

        char_set_metadata = struct.pack("<ffffffffII", \
            self.__nominal_width_nibs, \
            self.__left_spacing, self.__right_spacing, \
            self.__base_height_nibs, \
            self.__ascent_height_nibs, \
            self.__descent_height_nibs, \
            self.__cap_height_nibs, \
            self.__gap_height_nibs, \
            self.__guide_angle, \
            self.__nib_angle \
            )

        fd.write(char_set_metadata)

        for item_type in self.__objects:
            num_items = self.__ids[item_type]
            fd.write(struct.pack("<cL", INV_TYPE_MAP[item_type].encode('utf-8'), num_items))

            for item_id in self.__objects[item_type]:
                fd.write(struct.pack("<11s", item_id.encode('utf-8')))

                item = self.__objects[item_type][item_id]
                try:
                    data = item.serialize()
                    fd.write(struct.pack("<L", len(data)))
                    fd.write(data)
                except IOError:
                    raise
                except Exception as err:
                    print("ERROR: Couldn't serialize {}".format(item_id))
                    print(err)
                    raise

    def load(self, fd):
        if not fd:
            return
        
        magic = ""
        version_check = 0

        magic, version_check = struct.unpack("<4sd", fd.read(struct.calcsize("<4sd")))
        
        if magic != "PTCS" and version_check != VERSION:
            return

        char_set_metadata = fd.read(struct.calcsize("<ffffffffII"))

        (self.__nominal_width_nibs, \
            self.__left_spacing, self.__right_spacing, \
            self.__base_height_nibs, \
            self.__ascent_height_nibs, \
            self.__descent_height_nibs, \
            self.__cap_height_nibs, \
            self.__gap_height_nibs, \
            self.__guide_angle, \
            self.__nib_angle) = struct.unpack("<ffffffffII", char_set_metadata)

        while True:
            try:
                safe_dict = dict([ (k, globals().get(k, None)) for k in INV_TYPE_MAP.keys() ])
                num_items_raw = fd.read(struct.calcsize("<cL"))
                if len(num_items_raw) == 0:
                    break

                (item_type_key, num_items) = struct.unpack("<cL", num_items_raw)
                item_type = TYPE_MAP[item_type_key.decode('utf-8')]

                self.__ids[item_type] = num_items

                for i in range(0, num_items):
                    item_id = struct.unpack("<11s", fd.read(struct.calcsize("<11s")))[0].decode('utf-8')
                    data_size = struct.unpack("<L", fd.read(struct.calcsize("<L")))[0]
                    data_blob = fd.read(data_size)

                    item_object = eval(item_type, safe_dict, {})(self)
                    
                    item_object.unserialize(data_blob)
                    self.__objects[item_type][item_id] = item_object    

            except IOError:
                raise
            except EOFError:
                raise
            except Exception:
                raise
                
        for char_id in self.__objects[CHAR_TYPE].keys():
            char_item = self.get_item_by_index(char_id)
            if char_item.unicode_character >= 0:
                self.__character_xref[chr(char_item.unicode_character)] = char_id

        for vert_id in self.__objects[VERTEX_TYPE].keys():
            vert_item = self.get_item_by_index(vert_id)
            vert_item.char_set  = self
            
