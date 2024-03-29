import math

from PyQt5 import QtCore, QtGui, QtWidgets

import editor.control.edit_control
import shared.model.commands
import editor.model.stroke
import editor.model.common

class StrokeController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__tmp_stroke = None
        self.__stroke_pts = []

    def get_tmp_stroke(self):
        return self.__tmp_stroke

    def set_tmp_stroke(self, new_tmp_stroke):
        self.__tmp_stroke = new_tmp_stroke

    tmp_stroke = property(get_tmp_stroke, set_tmp_stroke)

    def get_stroke_pts(self):
        return self.__stroke_pts

    def set_stroke_pts(self, new_stroke_pts):
        self.__stroke_pts = new_stroke_pts

    stroke_pts = property(get_stroke_pts, set_stroke_pts)

    def create_new_stroke(self):
        if self.__main_ctrl.state == editor.control.edit_control.DRAWING_NEW_STROKE:
            return

        current_view = self.__main_ctrl.get_current_view()
        ui_ref = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        self.__main_ctrl.state = editor.control.edit_control.DRAWING_NEW_STROKE
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

        ui_ref.setUpdatesEnabled(False)
        dwg_tab = ui_ref.main_view_tabs.indexOf(current_view.parent())

        for idx in range(0, ui_ref.main_view_tabs.count()):
            if idx != dwg_tab:
                ui_ref.main_view_tabs.setTabEnabled(idx, False)
        ui_ref.setUpdatesEnabled(True)

        self.__stroke_pts = []
        self.__tmp_stroke = editor.model.stroke.Stroke(char_set)
        current_view.strokes.append(self.__tmp_stroke)
        self.__tmp_stroke.selected = True

    def save_glyph(self):
        selected_strokes = []
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()

        for sel_stroke in cur_view_selection.keys():
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if type(sel_stroke_item).__name__ == 'Stroke':
                selected_strokes.append(sel_stroke)

        if len(selected_strokes) == 0:
            return

        glyph_id = char_set.new_glyph(selected_strokes)
        glyph_instance_id = char_set.new_glyph_instance(glyph_id)

        item_num = ui_ref.stroke_selector_list.count()

        save_glyph_cmd = shared.model.commands.Command('save_glyph_cmd')

        do_args = {
            'strokes' : selected_strokes,
            'glyph' : glyph_instance_id,
            'first_item' : item_num,
            'character' : current_view.symbol
        }

        undo_args = {
            'glyph' : glyph_instance_id,
            'first_item' : item_num,
            'character' : current_view.symbol
        }

        save_glyph_cmd.set_do_args(do_args)
        save_glyph_cmd.set_undo_args(undo_args)
        save_glyph_cmd.set_do_function(self.save_glyphs)
        save_glyph_cmd.set_undo_function(self.unsave_glyphs)

        cmd_stack.do_command(save_glyph_cmd)
        ui_ref.edit_undo.setEnabled(True)

        ui_ref.repaint()

    def save_glyphs(self, args):
        deleted_strokes = []
        char_set = self.__main_ctrl.get_character_set()

        if 'strokes' in args:
            saved_selection = args['strokes']
        else:
            return

        if 'glyph' in args:
            glyph_instance_id = args['glyph']
            glyph_instance = char_set.get_saved_glyph_instance(glyph_instance_id)
        else:
            return

        if 'first_item' in args:
            first_item = args['first_item']
        else:
            return

        if 'character' in args:
            cur_char = args['character']
        else:
            return

        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()

        bitmap = ui_ref.dwg_area.draw_icon(None, saved_selection)
        glyph_item = QtWidgets.QListWidgetItem()
        glyph_item.setText(str(first_item))
        glyph_item.setData(QtCore.Qt.UserRole, glyph_instance.instanced_object)
        glyph_item.setIcon(QtGui.QIcon(bitmap))
        ui_ref.stroke_selector_list.addItem(glyph_item)
        ui_ref.stroke_selector_list.setCurrentRow(first_item)

        for sel_stroke in saved_selection:
            deleted_strokes.append(sel_stroke)
            cur_char.delete_stroke({'stroke' : sel_stroke})

            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if sel_stroke not in cur_view_selection:
                cur_view_selection = {}
                sel_stroke_item.deselect_ctrl_verts()

            sel_stroke_item.selected = True

        # should just add the id!
        cur_char.add_glyph(glyph_instance_id)
        glyph_instance.selected = True
        cur_view_selection[glyph_instance_id] = {}

        for sel_stroke in deleted_strokes:
            if sel_stroke in cur_view_selection:
                del cur_view_selection[sel_stroke]

            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            sel_stroke_item.selected = False

        ui_ref.stroke_load.setEnabled(True)
        ui_ref.glyph_delete.setEnabled(True)
        self.__main_ctrl.set_ui_state_selection(True)

    def unsave_glyphs(self, args):
        added_strokes = []
        char_set = self.__main_ctrl.get_character_set()

        if 'glyph' in args:
            glyph_instance_id = args['glyph']
            glyph_instance = char_set.get_saved_glyph_instance(glyph_instance_id)
        else:
            return

        if 'first_item' in args:
            first_item = args['first_item']
        else:
            return

        if 'character' in args:
            cur_char = args['character']
        else:
            return

        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()

        cur_char.remove_glyph(glyph_instance_id)

        for sel_stroke in glyph_instance.strokes:
            cur_char.add_stroke({'stroke' : sel_stroke})
            added_strokes.append(sel_stroke)

        ui_ref.stroke_selector_list.takeItem(first_item)

        for sel_stroke in added_strokes:
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if sel_stroke not in cur_view_selection:
                cur_view_selection[sel_stroke] = {}
                sel_stroke_item.deselect_ctrl_verts()

            sel_stroke_item.selected = True

        self.__main_ctrl.set_ui_state_selection(True)

        if ui_ref.stroke_selector_list.count() == 0:
            ui_ref.stroke_load.setEnabled(False)
            ui_ref.glyph_delete.setEnabled(False)

    def paste_glyph_from_saved(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()
        ui_ref = self.__main_ctrl.get_ui()

        char_index = ui_ref.char_selector_list.currentRow()
        glyph_item = ui_ref.stroke_selector_list.currentItem()
        glyph_index = str(glyph_item.data(QtCore.Qt.UserRole))
        new_glyph_inst_id = char_set.new_glyph_instance(glyph_index)

        paste_glyph_saved_cmd = shared.model.commands.Command('paste_glyph_saved_cmd')

        do_args = {
            'strokes' : new_glyph_inst_id,
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : new_glyph_inst_id,
            'char_index' : char_index,
        }

        paste_glyph_saved_cmd.set_do_args(do_args)
        paste_glyph_saved_cmd.set_undo_args(undo_args)
        paste_glyph_saved_cmd.set_do_function(self.paste_glyph)
        paste_glyph_saved_cmd.set_undo_function(self.delete_glyph)

        cmd_stack.do_command(paste_glyph_saved_cmd)
        ui_ref.edit_undo.setEnabled(True)

        ui_ref.repaint()

    def paste_glyph(self, args):
        char_set = self.__main_ctrl.get_character_set()

        if 'char_index' in args:
            char_index = args['char_index']
        else:
            return

        if 'strokes' in args:
            glyph_instance_id = args['strokes']
            glyph_instance = char_set.get_saved_glyph_instance(glyph_instance_id)
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        self.__main_ctrl.clear_selection()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()

        ui_ref.char_selector_list.setCurrentRow(char_index)

        cur_char.add_glyph(glyph_instance_id)
        cur_view_selection[glyph_instance_id] = {}
        glyph_instance.selected = True

        ui_ref.dwg_area.repaint()
        self.__main_ctrl.set_icon()

    def delete_glyph(self, args):
        char_set = self.__main_ctrl.get_character_set()

        if 'strokes' in args:
            glyph_instance_id = args['strokes']
            glyph_instance = char_set.get_saved_glyph_instance(glyph_instance_id)
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()

        cur_char.remove_glyph(glyph_instance_id)
        if glyph_instance in cur_view_selection:
            del cur_view_selection[glyph_instance_id]

        ui_ref.dwg_area.repaint()

    def delete_saved_glyph(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        ui_ref = self.__main_ctrl.get_ui()

        glyph_index = ui_ref.stroke_selector_list.currentRow()

        cur_item = ui_ref.stroke_selector_list.currentItem()
        cur_item_icon = cur_item.icon()
        glyph_id = str(cur_item.data(QtCore.Qt.UserRole).toString())

        delete_saved_glyph_cmd = shared.model.commands.Command('delete_saved_glyph_cmd')

        do_args = {
            'glyph_index' : glyph_index,
            'glyph_id' : glyph_id
        }

        undo_args = {
            'glyph_index' : glyph_index,
            'bitmap' : cur_item_icon,
            'glyph_id' : glyph_id
        }

        delete_saved_glyph_cmd.set_do_args(do_args)
        delete_saved_glyph_cmd.set_undo_args(undo_args)
        delete_saved_glyph_cmd.set_do_function(self.remove_saved_glyph)
        delete_saved_glyph_cmd.set_undo_function(self.add_saved_glyph)

        cmd_stack.do_command(delete_saved_glyph_cmd)
        ui_ref.edit_undo.setEnabled(True)

        if ui_ref.stroke_selector_list.count() == 0:
            ui_ref.stroke_load.setEnabled(False)
            ui_ref.glyph_delete.setEnabled(False)

        ui_ref.repaint()

    def remove_saved_glyph(self, args):
        if 'glyph_id' in args:
            glyph_id = args['glyph_id']
        else:
            return

        if 'glyph_index' in args:
            glyph_index = args['glyph_index']
        else:
            return

        ui_ref = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        glyph = char_set.glyphs[glyph_id]

        # should we save these to restore once you
        # undelete saved glyph?
        instance_list = glyph.instances.keys()

        for glyph_instance in instance_list:
            glyph_instance_item = char_set.get_item_by_index(glyph_instance)
            char = glyph_instance_item.parent
            char.remove_glyph(glyph_instance)

        ui_ref.stroke_selector_list.takeItem(glyph_index)

        ui_ref.repaint()

    def add_saved_glyph(self, args):
        if 'glyph_index' in args:
            glyph_index = args['glyph_index']
        else:
            return

        if 'glyph_id' in args:
            glyph_id = args['glyph_id']
        else:
            return

        if 'bitmap' in args:
            bitmap = args['bitmap']
        else:
            return

        ui_ref = self.__main_ctrl.get_ui()

        glyph_item = QtWidgets.QListWidgetItem()
        glyph_item.setText(str(glyph_index))
        glyph_item.setData(QtCore.Qt.UserRole, glyph_id)
        glyph_item.setIcon(QtGui.QIcon(bitmap))

        ui_ref.stroke_selector_list.insertItem(glyph_index, glyph_item)

    def straighten_stroke(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        verts_before_list = []
        verts_after_list = []
        behaviors_before_list = []
        behaviors_after_list = []

        for sel_stroke in cur_view_selection.keys():
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            (verts_before, behaviors_before) = sel_stroke_item.get_ctrl_vertices_as_list()

            sel_stroke_item.straighten()

            (verts_after, behaviors_after) = sel_stroke_item.get_ctrl_vertices_as_list()

            verts_before_list.append(verts_before)
            verts_after_list.append(verts_after)
            behaviors_before_list.append(behaviors_before)
            behaviors_after_list.append(behaviors_after)

        stroke_straighten_cmd = shared.model.commands.Command("stroke_straighten_cmd")

        undo_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_before_list,
            'behaviors' : behaviors_before_list
        }

        do_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_after_list,
            'behaviors' : behaviors_after_list
        }

        stroke_straighten_cmd.set_do_args(do_args)
        stroke_straighten_cmd.set_undo_args(undo_args)
        stroke_straighten_cmd.set_do_function(self.set_stroke_control_vertices_from_list)
        stroke_straighten_cmd.set_undo_function(self.set_stroke_control_vertices_from_list)

        cmd_stack.add_to_undo(stroke_straighten_cmd)
        cmd_stack.save_count += 1
        ui_ref.edit_undo.setEnabled(True)

    def join_selected_strokes(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()

        if len(cur_view_selection.keys()) > 1:
            stroke_join_cmd = shared.model.commands.Command("stroke_join_cmd")
            selection_copy = cur_view_selection.copy()

            new_stroke = self.join_strokes(selection_copy)

            do_args = {
                'strokes' : selection_copy,
                'joined_stroke' : new_stroke
            }

            undo_args = {
                'strokes' : selection_copy.copy(),
                'joined_stroke' : new_stroke
            }

            stroke_join_cmd.set_do_args(do_args)
            stroke_join_cmd.set_undo_args(undo_args)
            stroke_join_cmd.set_do_function(self.join_all_strokes)
            stroke_join_cmd.set_undo_function(self.unjoin_all_strokes)

            cmd_stack.add_to_undo(stroke_join_cmd)
            cmd_stack.save_count += 1
            ui_ref.edit_undo.setEnabled(True)
            ui_ref.repaint()

    def join_strokes(self, strokes):
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        stroke_list = strokes.keys()
        cur_stroke = stroke_list.pop(0)
        cur_stroke_item = char_set.get_item_by_index(cur_stroke)
        (vert_list, behaviors) = cur_stroke_item.get_ctrl_vertices_as_list()
        cur_char.delete_stroke({'stroke': cur_stroke})
        if cur_stroke in cur_view_selection:
            cur_stroke_item = char_set.get_item_by_index(cur_stroke)
            del cur_view_selection[cur_stroke]
            cur_stroke_item.selected = False

        while len(stroke_list):
            cur_stroke = stroke_list.pop(0)
            cur_stroke_item = char_set.get_item_by_index(cur_stroke)
            (cur_verts, cur_behaviors) = cur_stroke_item.get_ctrl_vertices_as_list()
            cur_char.delete_stroke({'stroke': cur_stroke})
            if cur_stroke in cur_view_selection:
                cur_stroke_item = char_set.get_item_by_index(cur_stroke)
                del cur_view_selection[cur_stroke]
                cur_stroke_item.selected = False

            dist1 = editor.model.common.dist_between_pts(cur_verts[0], vert_list[0])
            dist2 = editor.model.common.dist_between_pts(cur_verts[-1], vert_list[0])
            dist3 = editor.model.common.dist_between_pts(cur_verts[0], vert_list[-1])
            dist4 = editor.model.common.dist_between_pts(cur_verts[-1], vert_list[-1])

            point_list = [dist1, dist2, dist3, dist4]
            point_list.sort()

            smallest = point_list[0]

            if smallest == dist1:
                cur_verts.reverse()

            if smallest == dist1 or smallest == dist4:
                vert_list.reverse()

            if smallest == dist2:
                (cur_verts, vert_list) = (vert_list, cur_verts)

            vert_list.extend(cur_verts[1:])

        new_stroke = char_set.new_stroke()
        new_stroke_item = char_set.get_item_by_index(new_stroke)
        new_stroke_item.set_ctrl_vertices_from_list(vert_list, behaviors, False)
        new_stroke_item.calc_curve_points()
        cur_char.add_stroke({'stroke': new_stroke})

        cur_view_selection[new_stroke] = {}
        new_stroke_item.selected = True

        return new_stroke

    def unjoin_all_strokes(self, args):
        if 'strokes' in args:
            strokes = args['strokes']
        else:
            return

        if 'joined_stroke' in args:
            joined_stroke = args['joined_stroke']
        else:
            return

        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        cur_char.delete_stroke({'stroke': joined_stroke})
        joined_stroke_item = char_set.get_item_by_index(joined_stroke)
        joined_stroke_item.selected = False
        if joined_stroke in cur_view_selection:
            del cur_view_selection[joined_stroke]

        for sel_stroke in strokes.keys():
            cur_char.add_stroke({'stroke': sel_stroke})
            cur_view_selection[sel_stroke] = {}
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            sel_stroke_item.selected = True

    def join_all_strokes(self, args):
        if 'strokes' in args:
            strokes = args['strokes']
        else:
            return

        if 'joined_stroke' in args:
            joined_stroke = args['joined_stroke']
        else:
            return

        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        cur_char.add_stroke({'stroke': joined_stroke})
        joined_stroke_item = char_set.get_item_by_index(joined_stroke)
        joined_stroke_item.selected = True
        cur_view_selection[joined_stroke] = {}

        for sel_stroke in strokes.keys():
            cur_char.delete_stroke({'stroke': sel_stroke})
            if sel_stroke in cur_view_selection:
                del cur_view_selection[sel_stroke]
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            sel_stroke_item.selected = False

    def delete_control_vertices(self):
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        verts_before_list = []
        verts_after_list = []
        behaviors_before_list = []
        behaviors_after_list = []

        for sel_stroke in cur_view_selection.keys():
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            (verts_before, behaviors_before) = sel_stroke_item.get_ctrl_vertices_as_list()

            for vert_to_delete in cur_view_selection[sel_stroke]:
                sel_stroke_item.delete_ctrl_vertex(vert_to_delete)
                vert_to_delete_item = char_set.get_item_by_index(vert_to_delete)
                vert_to_delete_item.select_handle(None)

            cur_view_selection[sel_stroke] = {}

            (verts_after, behaviors_after) = sel_stroke_item.get_ctrl_vertices_as_list()

            verts_before_list.append(verts_before)
            verts_after_list.append(verts_after)
            behaviors_before_list.append(behaviors_before)
            behaviors_after_list.append(behaviors_after)            

        do_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_after_list,
            'behaviors' : behaviors_after_list
        }

        undo_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_before_list,
            'behaviors' : behaviors_before_list
        }

        vert_delete_cmd = shared.model.commands.Command("vert_delete_cmd")
        vert_delete_cmd.set_do_args(do_args)
        vert_delete_cmd.set_undo_args(undo_args)
        vert_delete_cmd.set_do_function(self.set_stroke_control_vertices_from_list)
        vert_delete_cmd.set_undo_function(self.set_stroke_control_vertices_from_list)

        cmd_stack.add_to_undo(vert_delete_cmd)
        cmd_stack.save_count += 1
        ui_ref.edit_undo.setEnabled(True)
        ui_ref.repaint()

    def set_stroke_control_vertices_from_list(self, args):
        ui_ref = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        if 'strokes' in args:
            sel_stroke_list = args['strokes']
        else:
            return

        if 'ctrl_verts' in args:
            ctrl_vert_list = args['ctrl_verts']
        else:
            return

        if 'behaviors' in args:
            behaviors_list = args['behaviors']
        else:
            behaviors_list = []

        if len(ctrl_vert_list) != len(sel_stroke_list):
            return

        for i in range(0, len(sel_stroke_list)):
            sel_stroke = sel_stroke_list[i]
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if len(behaviors_list):
                behaviors = behaviors_list[i]
            else:
                behaviors = []

            sel_stroke_item.set_ctrl_vertices_from_list(ctrl_vert_list[i], behaviors, False)
            sel_stroke_item.calc_curve_points()

        ui_ref.repaint()

    def split_stroke(self, args):
        ui_ref = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        char_set = self.__main_ctrl.get_character_set()

        if 'strokes' in args:
            sel_stroke = args['strokes']
        else:
            return

        if 'ctrl_verts' in args:
            ctrl_verts = args['ctrl_verts']
        else:
            return

        if 'new_stroke' in args:
            new_stroke = args['new_stroke']
        else:
            return

        if 'behaviors' in args:
            behaviors_list = args['behaviors']
        else:
            behaviors_list = []            

        sel_stroke_item = char_set.get_item_by_index(sel_stroke)
        sel_stroke_item.set_ctrl_vertices_from_list(ctrl_verts, behaviors_list, False)
        sel_stroke_item.calc_curve_points()

        cur_char.add_stroke({'stroke': new_stroke})
        ui_ref.repaint()

    def unsplit_stroke(self, args):
        ui_ref = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        char_set = self.__main_ctrl.get_character_set()

        if 'strokes' in args:
            sel_stroke = args['strokes']
        else:
            return

        if 'ctrl_verts' in args:
            ctrl_verts = args['ctrl_verts']
        else:
            return

        if 'stroke_to_delete' in args:
            del_stroke = args['stroke_to_delete']
        else:
            return

        if 'behaviors' in args:
            behaviors_list = args['behaviors']
        else:
            behaviors_list = []

        sel_stroke_item = char_set.get_item_by_index(sel_stroke)
        sel_stroke_item.set_ctrl_vertices_from_list(ctrl_verts, behaviors_list, False)
        sel_stroke_item.calc_curve_points()
        cur_char.delete_stroke({'stroke': del_stroke})
        ui_ref.repaint()

    def add_control_point(self, sel_stroke, inside_info):
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()
        sel_stroke_item = char_set.get_item_by_index(sel_stroke)

        add_vertex_cmd = shared.model.commands.Command('add_vertex_cmd')

        (verts_before, behaviors_before) = sel_stroke_item.get_ctrl_vertices_as_list()
        undo_args = {
            'strokes' : [sel_stroke],
            'ctrl_verts' : [verts_before],
            'behaviors' : [behaviors_before]
        }

        sel_stroke_item.add_ctrl_vertex(inside_info[2], inside_info[1])
        (verts_after, behaviors_after) = sel_stroke_item.get_ctrl_vertices_as_list()

        do_args = {
            'strokes' : [sel_stroke],
            'ctrl_verts' : [verts_after],
            'behaviors' : [behaviors_after]
        }

        add_vertex_cmd.set_do_args(do_args)
        add_vertex_cmd.set_undo_args(undo_args)
        add_vertex_cmd.set_do_function(self.set_stroke_control_vertices_from_list)
        add_vertex_cmd.set_undo_function(self.set_stroke_control_vertices_from_list)

        cmd_stack.add_to_undo(add_vertex_cmd)
        cmd_stack.save_count += 1
        ui_ref.edit_undo.setEnabled(True)

    def split_stroke_at_point(self, sel_stroke, inside_info):
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()
        sel_stroke_item = char_set.get_item_by_index(sel_stroke)

        split_at_cmd = shared.model.commands.Command('split_at_cmd')
        (verts_before, behaviors_before) = sel_stroke_item.get_ctrl_vertices_as_list()

        (new_verts, new_behaviors) = sel_stroke_item.split_at_point(inside_info[2], inside_info[1])
        (verts_after, behaviors_after) = sel_stroke_item.get_ctrl_vertices_as_list()

        new_stroke = char_set.new_stroke()
        new_stroke_item = char_set.get_item_by_index(new_stroke)
        new_stroke_item.set_ctrl_vertices_from_list(new_verts, new_behaviors, True)

        undo_args = {
            'strokes' : sel_stroke,
            'ctrl_verts' : verts_before,
            'stroke_to_delete' : new_stroke,
            'behaviors' : behaviors_before
        }

        do_args = {
            'strokes' : sel_stroke,
            'new_stroke' : new_stroke,
            'ctrl_verts' : verts_after,
            'behaviors' : behaviors_after
        }

        split_at_cmd.set_do_args(do_args)
        split_at_cmd.set_undo_args(undo_args)
        split_at_cmd.set_do_function(self.split_stroke)
        split_at_cmd.set_undo_function(self.unsplit_stroke)

        cmd_stack.do_command(split_at_cmd)
        ui_ref.edit_undo.setEnabled(True)

    def add_new_stroke(self):
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()

        (verts, behaviors) = self.__tmp_stroke.get_ctrl_vertices_as_list()
        if len(verts) < 2:
            self.__main_ctrl.state = editor.control.edit_control.IDLE
            self.__tmp_stroke = None
            self.__stroke_pts = []
            current_view.strokes = []
            ui_ref.repaint()

            ui_ref.setUpdatesEnabled(False)
            for idx in range(0, ui_ref.main_view_tabs.count()):
                ui_ref.main_view_tabs.setTabEnabled(idx, True)

            if ui_ref.stroke_selector_list.count() <= 0:
                ui_ref.main_view_tabs.setTabEnabled(ui_ref.main_view_tabs.indexOf(ui_ref.stroke_dwg_area.parent()), \
                False)
            ui_ref.setUpdatesEnabled(True)

            return

        self.__main_ctrl.state = editor.control.edit_control.IDLE
        self.__stroke_pts = []

        new_stroke_id = char_set.new_stroke(self.__tmp_stroke)

        add_stroke_cmd = shared.model.commands.Command('add_stroke_cmd')
        do_args = {
            'stroke' : new_stroke_id,
        }

        undo_args = {
            'stroke' : new_stroke_id,
        }

        add_stroke_cmd.set_do_args(do_args)
        add_stroke_cmd.set_undo_args(undo_args)
        add_stroke_cmd.set_do_function(cur_char.add_stroke)
        add_stroke_cmd.set_undo_function(cur_char.delete_stroke)

        cmd_stack.do_command(add_stroke_cmd)
        ui_ref.edit_undo.setEnabled(True)

        cur_view_selection[new_stroke_id] = {}
        new_stroke_item = char_set.get_item_by_index(new_stroke_id)
        new_stroke_item.selected = True
        current_view.strokes = []
        self.__tmp_stroke = None

        self.__main_ctrl.set_ui_state_selection(True)

        ui_ref.setUpdatesEnabled(False)
        for idx in range(0, ui_ref.main_view_tabs.count()):
            ui_ref.main_view_tabs.setTabEnabled(idx, True)

        if ui_ref.stroke_selector_list.count() <= 0:
            ui_ref.main_view_tabs.setTabEnabled(ui_ref.main_view_tabs.indexOf(ui_ref.stroke_dwg_area.parent()), \
                False)
        ui_ref.setUpdatesEnabled(True)

        ui_ref.repaint()

    def flip_selected_strokes_x(self):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()

        flip_strokes_x_cmd = shared.model.commands.Command("flip_strokes_x_cmd")

        do_args = {
            'strokes' : cur_view_selection.keys(),
            'char_set' : char_set
        }

        undo_args = {
            'strokes' : cur_view_selection.keys(),
            'char_set' : char_set
        }

        flip_strokes_x_cmd.set_do_args(do_args)
        flip_strokes_x_cmd.set_undo_args(undo_args)
        flip_strokes_x_cmd.set_do_function(self.flip_strokes_x)
        flip_strokes_x_cmd.set_undo_function(self.flip_strokes_x)

        cmd_stack.do_command(flip_strokes_x_cmd)
        ui_ref.edit_undo.setEnabled(True)

        ui_ref.repaint()

    def flip_strokes_x(self, args):
        if 'strokes' in args:
            strokes_to_flip = args['strokes']
        else:
            return

        if 'char_set' in args:
            char_set = args['char_set']
        else:
            return
            
        for sel_stroke in strokes_to_flip:
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if type(sel_stroke_item).__name__ == "Stroke":
                sel_stroke_item.flip_x()

    def flip_selected_strokes_y(self):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()

        flip_strokes_y_cmd = shared.model.commands.Command("flip_strokes_y_cmd")

        do_args = {
            'strokes' : cur_view_selection.keys(),
            'char_set' : char_set
        }

        undo_args = {
            'strokes' : cur_view_selection.keys(),
            'char_set' : char_set
        }

        flip_strokes_y_cmd.set_do_args(do_args)
        flip_strokes_y_cmd.set_undo_args(undo_args)
        flip_strokes_y_cmd.set_do_function(self.flip_strokes_y)
        flip_strokes_y_cmd.set_undo_function(self.flip_strokes_y)

        cmd_stack.do_command(flip_strokes_y_cmd)
        ui_ref.edit_undo.setEnabled(True)

        ui_ref.repaint()

    def flip_strokes_y(self, args):
        if 'strokes' in args:
            strokes_to_flip = args['strokes']
        else:
            return

        if 'char_set' in args:
            char_set = args['char_set']
        else:
            return

        for sel_stroke in strokes_to_flip:
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if type(sel_stroke_item).__name__ == "Stroke":
                sel_stroke_item.flip_y()

    def move_selected(self, args):
        char_set = self.__main_ctrl.get_character_set()
        if 'strokes' in args:
            selection = args['strokes']
        else:
            return

        if 'delta' in args:
            delta = args['delta']
        else:
            return

        snap_point = None
        if 'snap_point' in args:
            snap_point = args['snap_point']

        for sel_stroke in selection.keys():
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            if len(selection[sel_stroke].keys()) > 0:
                for stroke_pt in selection[sel_stroke].keys():
                    stroke_pt_item = char_set.get_item_by_index(stroke_pt)
                    stroke_pt_item.select_handle(selection[sel_stroke][stroke_pt])
                    if snap_point:
                        stroke_pt_item.selected_handle_pos = (snap_point - sel_stroke_item.pos) / sel_stroke_item.scale
                    elif stroke_pt_item.selected_handle_pos:
                        stroke_pt_item.selected_handle_pos = \
                            stroke_pt_item.selected_handle_pos + delta / sel_stroke_item.scale
            else:
                sel_stroke_item.pos += delta
                
            if type(sel_stroke_item).__name__ == 'Stroke':
                sel_stroke_item.calc_curve_points()

        if len(selection.keys()):
            ui_ref = self.__main_ctrl.get_ui()
            ui_ref.position_x_spin.blockSignals(True)
            ui_ref.position_y_spin.blockSignals(True)
            ui_ref.vertex_x_spin.blockSignals(True)
            ui_ref.vertex_y_spin.blockSignals(True)

            first_object = list(selection)[0]
            first_item = char_set.get_item_by_index(first_object)
            ui_ref.position_x_spin.setValue(first_item.pos.x())
            ui_ref.position_y_spin.setValue(first_item.pos.y())

            if len(selection[first_object].keys()):
                first_vert = list(selection[first_object])[0]

                vert_item = char_set.get_item_by_index(first_vert)
                vert_pos = vert_item.get_pos_of_selected()
                if vert_pos is not None:
                    ui_ref.vertex_x_spin.setValue(vert_pos.x())
                    ui_ref.vertex_y_spin.setValue(vert_pos.y())
                else:
                    print('?', first_vert, vert_item)

            ui_ref.position_x_spin.blockSignals(False)
            ui_ref.position_y_spin.blockSignals(False)
            ui_ref.vertex_x_spin.blockSignals(False)
            ui_ref.vertex_y_spin.blockSignals(False)

    def selection_position_changed_x(self, prev_value, new_value):
        delta = QtCore.QPoint(new_value - prev_value, 0)
        undelta = QtCore.QPoint(prev_value - new_value, 0)

        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        do_args = {
            'strokes' : cur_view_selection,
            'delta' : delta,
        }

        undo_args = {
            'strokes' : cur_view_selection,
            'delta' : undelta
        }

        position_x_cmd = shared.model.commands.Command("position_x_cmd")
        position_x_cmd.set_do_args(do_args)
        position_x_cmd.set_undo_args(undo_args)
        position_x_cmd.set_do_function(self.move_selected)
        position_x_cmd.set_undo_function(self.move_selected)

        cmd_stack.do_command(position_x_cmd)
        ui_ref.edit_undo.setEnabled(True)

        ui_ref.repaint()

    def selection_position_changed_y(self, prev_value, new_value):
        delta = QtCore.QPoint(0, new_value - prev_value)
        undelta = QtCore.QPoint(0, prev_value - new_value)

        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        do_args = {
            'strokes' : cur_view_selection,
            'delta' : delta,
        }

        undo_args = {
            'strokes' : cur_view_selection,
            'delta' : undelta
        }

        position_y_cmd = shared.model.commands.Command("position_y_cmd")
        position_y_cmd.set_do_args(do_args)
        position_y_cmd.set_undo_args(undo_args)
        position_y_cmd.set_do_function(self.move_selected)
        position_y_cmd.set_undo_function(self.move_selected)

        cmd_stack.do_command(position_y_cmd)
        ui_ref.edit_undo.setEnabled(True)

        ui_ref.repaint()

