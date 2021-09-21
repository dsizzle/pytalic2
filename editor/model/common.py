SMOOTH      = 1
SHARP       = 2
SYMMETRIC   = 3

LEFT_HANDLE     = 1
KNOT            = 2
RIGHT_HANDLE    = 3

MAGIC_NONE = 987654321

DEFAULT_SETTINGS = {
	'handle_size_spin' : 10,
	'guides_color_button' : [200, 195, 180, 255],
	'stroke_color_button' : [125, 25, 25, 255],
	'glyph_color_button' : [25, 155, 25, 255],
	'special_color_stroke_button' : [25, 25, 125, 255],

	'nominal_width_spin' : 4.0,
	'char_set_left_space_spin' : 1.0,
	'char_set_right_space_spin' : 1.0,
	'base_height_spin' : 5.0,
	'ascent_height_spin' : 3.0,
	'descent_height_spin' : 3.0,
	'cap_height_spin' : 2.0,
	'gap_height_spin' : 1.0,
	'guide_angle_spin' : 0,
	'nib_angle_spin' : 40
}

SETTINGS_CONTROLS_TO_SETTINGS = {
	'nominal_width_spin' : '__nominal_nib_widths',
	'char_set_left_space_spin' : '__left_spacing',
	'char_set_right_space_spin' : '__right_spacing',
	'base_height_spin' : '__base_height',
	'ascent_height_spin' : '__ascent_height',
	'descent_height_spin' : '__descent_height',
	'cap_height_spin' : '__cap_height',
	'gap_height_spin' : '__gap_height',
	'guide_angle_spin' : '__guide_angle',
	'nib_angle_spin' : '__nib_angle'

}

