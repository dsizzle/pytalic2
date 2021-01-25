import shared.model.commands
import editor.model.control_vertex

class VertexController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent

    def align_tangents(self, new_behavior):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()

        if len(cur_view_selection.values()) > 0:
            vert_list = cur_view_selection.values()

            behavior_list = []

            verts_to_process = []
            for vert_dict in vert_list:
                for vert in vert_dict.keys():
                    vert_item = char_set.get_item_by_index(vert)
                    if vert_item.behavior != new_behavior:
                        behavior_list.append(vert_item.behavior)
                        verts_to_process.append(vert_dict)

            if not len(verts_to_process):
                return

            do_args = {
                'verts' : verts_to_process,
                'behaviors' : [new_behavior]
            }

            undo_args = {
                'verts' : verts_to_process,
                'behaviors' : behavior_list
            }

            align_tangents_cmd = shared.model.commands.Command("align_tangents_cmd")

            align_tangents_cmd.set_do_args(do_args)
            align_tangents_cmd.set_undo_args(undo_args)
            align_tangents_cmd.set_do_function(self.set_ctrl_vertex_behavior)
            align_tangents_cmd.set_undo_function(self.set_ctrl_vertex_behavior)

            cmd_stack.do_command(align_tangents_cmd)
            
            ui_ref.edit_undo.setEnabled(True)

            ui_ref.repaint()

    def align_tangents_symmetrical(self):
        self.align_tangents(editor.model.control_vertex.SYMMETRIC)

    def align_tangents_smooth(self):
        self.align_tangents(editor.model.control_vertex.SMOOTH)

    def break_tangents(self):
        self.align_tangents(editor.model.control_vertex.SHARP)

    def set_ctrl_vertex_behavior(self, args):
        ui_ref = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        if 'verts' in args:
            vert_list = args['verts']
        else:
            return

        if 'behaviors' in args:
            behavior_list = args['behaviors']
        else:
            return

        use_same_behavior = (len(behavior_list) == 1)

        for vert_dict in vert_list:
            for i in range(0, len(vert_dict.keys())):
                vert = list(vert_dict)[i]
                vert_item = char_set.get_item_by_index(vert)
                if use_same_behavior:
                    vert_item.behavior = behavior_list[0]
                    ui_ref.behavior_combo.setCurrentIndex(behavior_list[0])
                else:
                    vert_item.behavior = behavior_list[i]
                    ui_ref.behavior_combo.setCurrentIndex(0)

        ui_ref.repaint()
