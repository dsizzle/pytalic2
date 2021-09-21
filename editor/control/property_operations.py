import shared.model.commands

class PropertyController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent

    def __prop_change(self, prev_value, new_value, objects, attr_name, ctrl_name):
        if new_value == prev_value:
            return

        cmd_stack = self.__main_ctrl.get_command_stack()
        ui_ref = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        do_args = {
            'value' : new_value,
            'attr_names' : attr_name,
            'ctrl_names' : ctrl_name,
            'objects' : objects
        }

        undo_args = {
            'value' : prev_value,
            'attr_names' : attr_name,
            'ctrl_names' : ctrl_name,
            'objects' : objects
        }

        change_cmd = shared.model.commands.Command("change_"+attr_name[0]+"_cmd")

        change_cmd.set_do_args(do_args)
        change_cmd.set_undo_args(undo_args)
        change_cmd.set_do_function(self.change_property_control)
        change_cmd.set_undo_function(self.change_property_control)

        cmd_stack.do_command(change_cmd)
        ui_ref.edit_undo.setEnabled(True)

        if ui_ref.preview_area.layout:
            ui_ref.preview_area.layout.update_layout(char_set, \
                nib_width=ui_ref.dwg_area.nib.width*2)
        ui_ref.repaint()

    def change_property_control(self, args):
        if 'value' in args:
            val = args['value']
        else:
            return

        if 'attr_names' in args:
            attr_names = args['attr_names']
        else:
            return

        if 'ctrl_names' in args:
            ctrl_names = args['ctrl_names']
        else:
            return

        if 'objects' in args:
            objects_to_set = args['objects']
        else:
            return

        use_same_attr = False
        if len(attr_names) == 1:
            use_same_attr = True

        for i in range(0, len(objects_to_set)):
            if use_same_attr:
                attr_name = attr_names[0]
            else:
                attr_name = attr_names[i]

            setattr(objects_to_set[i], attr_name, val)

        ui_ref = self.__main_ctrl.get_ui()
        for ctrl_name in ctrl_names:
            ui_control = getattr(ui_ref, ctrl_name)
            ui_control.setValue(val)

        ui_ref.repaint()

    def base_height_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['base_height'], \
            ['base_height_spin'])

    def cap_height_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['cap_height'], \
            ['cap_height_spin'])

    def ascent_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['ascent_height'], \
            ['ascent_height_spin'])

    def descent_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['descent_height'], \
            ['descent_height_spin'])

    def gap_height_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['gap_height'], \
            ['gap_height_spin'])

    def angle_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['guide_angle'], \
            ['angle_spin'])

    def nominal_width_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['width'], \
            ['nominal_width_spin'])

    def char_set_left_space_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['left_spacing'], \
            ['char_set_left_space_spin'])

    def char_set_right_space_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['right_spacing'], \
            ['char_set_right_space_spin'])

    def char_set_nib_angle_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, \
            ['nib_angle', 'angle', 'angle', 'angle', 'angle', 'angle'], \
            ['char_set_nib_angle_spin'])

    def char_width_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['width'], \
            ['char_width_spin'])

    def char_left_space_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['left_spacing'], \
            ['left_space_spin'])

    def char_right_space_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['right_spacing'], \
            ['right_space_spin'])

    def stroke_nib_angle_changed(self, prev_value, new_value, objects):
        self.__prop_change(prev_value, new_value, objects, ['nib_angle'], \
            ['stroke_nib_angle_spin'])
