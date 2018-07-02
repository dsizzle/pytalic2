import math

from PyQt4 import QtCore, QtGui

import control.edit_control
from model import character, commands, stroke, instance

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
        if self.__main_ctrl.state == control.edit_control.DRAWING_NEW_STROKE:
            return

        current_view = self.__main_ctrl.get_current_view()
        ui = self.__main_ctrl.get_ui()

        self.__main_ctrl.state = control.edit_control.DRAWING_NEW_STROKE
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

        dwg_tab = ui.main_view_tabs.indexOf(current_view)

        for idx in range(0, ui.main_view_tabs.count()):
            if idx != dwg_tab:
                ui.main_view_tabs.setTabEnabled(idx, False)

        self.__stroke_pts = []
        self.__tmp_stroke = stroke.Stroke()
        current_view.strokes.append(self.__tmp_stroke)
        self.__tmp_stroke.selected = True

    def save_glyph(self):
        selected_strokes = []
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        for sel_stroke in cur_view_selection.keys():
            if type(sel_stroke).__name__ == 'Stroke':
                selected_strokes.append(sel_stroke)

        if len(selected_strokes) == 0:
            return

        new_glyph = character.Glyph()
        new_glyph.strokes = selected_strokes
        glyph_instance = instance.GlyphInstance()
        glyph_instance.glyph = new_glyph

        item_num = ui.stroke_selector_list.count()

        save_glyph_cmd = commands.Command('save_glyph_cmd')

        do_args = {
            'strokes' : selected_strokes,
            'glyph' : glyph_instance,
            'first_item' : item_num,
            'character' : current_view.symbol
        }

        undo_args = {
            'glyph' : glyph_instance,
            'first_item' : item_num,
            'character' : current_view.symbol
        }

        save_glyph_cmd.set_do_args(do_args)
        save_glyph_cmd.set_undo_args(undo_args)
        save_glyph_cmd.set_do_function(self.save_glyphs)
        save_glyph_cmd.set_undo_function(self.unsave_glyphs)

        cmd_stack.do_command(save_glyph_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def save_glyphs(self, args):
        deleted_strokes = []
        
        if 'strokes' in args:
            saved_selection = args['strokes']
        else:
            return

        if 'glyph' in args:
            glyph_instance = args['glyph']
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

        char_set = self.__main_ctrl.get_character_set()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        char_set.save_glyph(glyph_instance.glyph)
        bitmap = ui.dwg_area.draw_icon(None, saved_selection)
        ui.stroke_selector_list.addItem(str(first_item))
        cur_item = ui.stroke_selector_list.item(first_item)
        ui.stroke_selector_list.setCurrentRow(first_item)
        cur_item.setIcon(QtGui.QIcon(bitmap))

        for sel_stroke in saved_selection: 
            deleted_strokes.append(sel_stroke)
            cur_char.delete_stroke({'stroke' : sel_stroke})
            
            if sel_stroke not in cur_view_selection:
                cur_view_selection = {}
                sel_stroke.deselect_ctrl_verts()

            sel_stroke.selected = True
            
        cur_char.add_glyph(glyph_instance)

        for sel_stroke in deleted_strokes:
            if sel_stroke in cur_view_selection:
                del cur_view_selection[sel_stroke]

            sel_stroke.selected = False

        ui.stroke_load.setEnabled(True)
        ui.glyph_delete.setEnabled(True)
        self.__main_ctrl.set_ui_state_selection(True)

    def unsave_glyphs(self, args):
        added_strokes = []
        
        if 'glyph' in args:
            glyph_instance = args['glyph']
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

        char_set = self.__main_ctrl.get_character_set()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        char_set.remove_saved_glyph(glyph_instance.glyph)
        cur_char.remove_glyph(glyph_instance)

        for sel_stroke in glyph_instance.strokes:
            cur_char.add_stroke({'stroke' : sel_stroke, 'copy_stroke' : False})
            added_strokes.append(sel_stroke)

        ui.stroke_selector_list.takeItem(first_item)
            
        for sel_stroke in added_strokes:
            if sel_stroke not in cur_view_selection:
                cur_view_selection[sel_stroke] = {}
                sel_stroke.deselect_ctrl_verts()

            sel_stroke.selected = True

        self.__main_ctrl.set_ui_state_selection(True)

        if ui.stroke_selector_list.count() == 0:
            ui.stroke_load.setEnabled(False)
            ui.glyph_delete.setEnabled(False)

    def paste_glyph_from_saved(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()

        char_index = char_set.get_current_char_index()
        glyph_index = ui.stroke_selector_list.currentRow()
        saved_glyph = char_set.get_saved_glyph(glyph_index)
        new_glyph = instance.GlyphInstance() 
        new_glyph.glyph = saved_glyph

        paste_glyph_saved_cmd = commands.Command('paste_glyph_saved_cmd')

        do_args = {
            'strokes' : new_glyph,
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : new_glyph,
            'char_index' : char_index,
        }

        paste_glyph_saved_cmd.set_do_args(do_args)
        paste_glyph_saved_cmd.set_undo_args(undo_args)
        paste_glyph_saved_cmd.set_do_function(self.paste_glyph)
        paste_glyph_saved_cmd.set_undo_function(self.delete_glyph)

        cmd_stack.do_command(paste_glyph_saved_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def paste_glyph(self, args):
        if 'char_index' in args:
            char_index = args['char_index']
        else:
            return

        if 'strokes' in args:
            glyph_instance = args['strokes']
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        ui.char_selector_list.setCurrentRow(char_index)

        cur_char.add_glyph(glyph_instance)
        cur_view_selection[glyph_instance] = {}

        ui.dwg_area.repaint()
        self.__main_ctrl.set_icon()

    def delete_glyph(self, args):
        if 'char_index' in args:
            char_index = args['char_index']
        else:
            return

        if 'strokes' in args:
            stroke_to_del = args['strokes']
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        cur_char.remove_glyph(stroke_to_del)
        if stroke_to_del in cur_view_selection:
            del cur_view_selection[stroke_to_del]

        ui.dwg_area.repaint()

    def delete_saved_glyph(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        ui = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        glyph_index = ui.stroke_selector_list.currentRow()
        
        saved_glyph = char_set.get_saved_glyph(glyph_index)
        
        if not saved_glyph:
            return

        cur_item = ui.stroke_selector_list.item(glyph_index)
        cur_item_icon = cur_item.icon()

        delete_saved_glyph_cmd = commands.Command('delete_saved_glyph_cmd')

        do_args = {
            'glyph' : saved_glyph,
            'glyph_index' : glyph_index,
        }

        undo_args = {
            'glyph' : saved_glyph,
            'glyph_index' : glyph_index,
            'bitmap' : cur_item_icon,
        }

        delete_saved_glyph_cmd.set_do_args(do_args)
        delete_saved_glyph_cmd.set_undo_args(undo_args)
        delete_saved_glyph_cmd.set_do_function(self.remove_saved_glyph)
        delete_saved_glyph_cmd.set_undo_function(self.add_saved_glyph)

        cmd_stack.do_command(delete_saved_glyph_cmd)
        ui.edit_undo.setEnabled(True)

        if ui.stroke_selector_list.count() == 0:
            ui.stroke_load.setEnabled(False)
            ui.glyph_delete.setEnabled(False)

        ui.repaint()

    def remove_saved_glyph(self, args):
        if 'glyph_index' in args:
            glyph_index = args['glyph_index']
        else:
            return

        if 'glyph' in args:
            glyph = args['glyph']
        else:
            return

        ui = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()
        
        ui.stroke_selector_list.takeItem(glyph_index)
        char_set.remove_saved_glyph(glyph)
        instance_list = glyph.instances.keys()

        for glyph_instance in instance_list:
            char = glyph_instance.parent
            char.remove_glyph(glyph_instance)

    def add_saved_glyph(self, args):
        if 'glyph_index' in args:
            glyph_index = args['glyph_index']
        else:
            return

        if 'glyph' in args:
            glyph = args['glyph']
        else:
            return

        if 'bitmap' in args:
            bitmap = args['bitmap']
        else:
            return

        ui = self.__main_ctrl.get_ui()
        char_set = self.__main_ctrl.get_character_set()

        ui.stroke_selector_list.insertItem(glyph_index, str(glyph_index))
        new_item = ui.stroke_selector_list.item(glyph_index)
        new_item.setIcon(bitmap)

        char_set.insert_glyph(glyph_index, glyph)

    def straighten_stroke(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        verts_before_list = []
        verts_after_list = []

        for sel_stroke in cur_view_selection.keys():
            verts_before = sel_stroke.get_ctrl_vertices_as_list()

            sel_stroke.straighten()

            verts_after = sel_stroke.get_ctrl_vertices_as_list()

            verts_before_list.append(verts_before)
            verts_after_list.append(verts_after)

        stroke_straighten_cmd = commands.Command("stroke_straighten_cmd")

        undo_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_before_list
        }

        do_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_after_list
        }

        stroke_straighten_cmd.set_do_args(do_args)
        stroke_straighten_cmd.set_undo_args(undo_args)
        stroke_straighten_cmd.set_do_function(self.set_stroke_control_vertices)
        stroke_straighten_cmd.set_undo_function(self.set_stroke_control_vertices)

        cmd_stack.add_to_undo(stroke_straighten_cmd)
        cmd_stack.save_count += 1
        ui.edit_undo.setEnabled(True)

    def join_selected_strokes(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        if len(cur_view_selection.keys()) > 1:
            stroke_join_cmd = commands.Command("stroke_join_cmd")
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
            ui.edit_undo.setEnabled(True)
            ui.repaint()

    def join_strokes(self, strokes):
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        stroke_list = strokes.keys()
        cur_stroke = stroke_list.pop(0)
        vert_list = cur_stroke.get_ctrl_vertices_as_list()
        cur_char.delete_stroke({'stroke': cur_stroke})
        if cur_stroke in cur_view_selection:
            del cur_view_selection[cur_stroke]
            cur_stroke.selected = False

        while len(stroke_list):
            cur_stroke = stroke_list.pop(0)
            cur_verts = cur_stroke.get_ctrl_vertices_as_list()
            cur_char.delete_stroke({'stroke': cur_stroke})
            if cur_stroke in cur_view_selection:
                del cur_view_selection[cur_stroke]
                cur_stroke.selected = False

            dist1 = dist_between_pts(cur_verts[0], vert_list[0])
            dist2 = dist_between_pts(cur_verts[-1], vert_list[0])
            dist3 = dist_between_pts(cur_verts[0], vert_list[-1])
            dist4 = dist_between_pts(cur_verts[-1], vert_list[-1])

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

        new_stroke = stroke.Stroke()
        new_stroke.set_ctrl_vertices_from_list(vert_list, False)
        new_stroke.calc_curve_points()
        cur_char.add_stroke({'stroke': new_stroke, 'copy_stroke': False})

        cur_view_selection[new_stroke] = {}
        new_stroke.selected = True

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

        cur_char.delete_stroke({'stroke': joined_stroke})
        joined_stroke.selected = False
        if joined_stroke in cur_view_selection:
            del cur_view_selection[joined_stroke]

        for sel_stroke in strokes.keys():
            cur_char.add_stroke({'stroke': sel_stroke, 'copy_stroke': False})
            cur_view_selection[sel_stroke] = {}
            sel_stroke.selected = True

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

        cur_char.add_stroke({'stroke': joined_stroke, 'copy_stroke': False})
        joined_stroke.selected = True
        cur_view_selection[joined_stroke] = {}

        for sel_stroke in strokes.keys():
            cur_char.delete_stroke({'stroke': sel_stroke})
            if sel_stroke in cur_view_selection:
                del cur_view_selection[sel_stroke]
            sel_stroke.selected = False

    def delete_control_vertices(self):
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        verts_before_list = []
        verts_after_list = []

        for sel_stroke in cur_view_selection.keys():
            verts_before = sel_stroke.get_ctrl_vertices_as_list()

            for vert_to_delete in cur_view_selection[sel_stroke]:
                sel_stroke.delete_ctrl_vertex(vert_to_delete)

            cur_view_selection[sel_stroke] = {}

            verts_after = sel_stroke.get_ctrl_vertices_as_list()

            verts_before_list.append(verts_before)
            verts_after_list.append(verts_after)

        do_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_after_list
        }

        undo_args = {
            'strokes' : cur_view_selection.keys(),
            'ctrl_verts' : verts_before_list
        }

        vert_delete_cmd = commands.Command("vert_delete_cmd")
        vert_delete_cmd.set_do_args(do_args)
        vert_delete_cmd.set_undo_args(undo_args)
        vert_delete_cmd.set_do_function(self.set_stroke_control_vertices)
        vert_delete_cmd.set_undo_function(self.set_stroke_control_vertices)

        cmd_stack.add_to_undo(vert_delete_cmd)
        cmd_stack.save_count += 1
        ui.edit_undo.setEnabled(True)
        ui.repaint()

    def set_stroke_control_vertices(self, args):
        ui = self.__main_ctrl.get_ui()

        if 'strokes' in args:
            sel_stroke_list = args['strokes']
        else:
            return

        if 'ctrl_verts' in args:
            ctrl_vert_list = args['ctrl_verts']
        else:
            return

        if len(ctrl_vert_list) != len(sel_stroke_list):
            return

        for i in range(0, len(sel_stroke_list)):
            sel_stroke = sel_stroke_list[i]
            sel_stroke.set_ctrl_vertices_from_list(ctrl_vert_list[i], False)
            sel_stroke.calc_curve_points()

        ui.repaint()

    def split_stroke(self, args):
        ui = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol

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

        sel_stroke.set_ctrl_vertices_from_list(ctrl_verts, False)
        sel_stroke.calc_curve_points()

        cur_char.add_stroke({'stroke': new_stroke, 'copy_stroke': False})
        ui.repaint()

    def unsplit_stroke(self, args):
        ui = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol

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

        sel_stroke.set_ctrl_vertices_from_list(ctrl_verts, False)
        sel_stroke.calc_curve_points()
        cur_char.delete_stroke({'stroke': del_stroke})
        ui.repaint()

    def add_control_point(self, sel_stroke, inside_info):
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        add_vertex_cmd = commands.Command('add_vertex_cmd')

        undo_args = {
            'strokes' : [sel_stroke],
            'ctrl_verts' : [sel_stroke.get_ctrl_vertices_as_list()]
        }

        sel_stroke.add_ctrl_vertex(inside_info[2], inside_info[1])

        do_args = {
            'strokes' : [sel_stroke],
            'ctrl_verts' : [sel_stroke.get_ctrl_vertices_as_list()]
        }

        add_vertex_cmd.set_do_args(do_args)
        add_vertex_cmd.set_undo_args(undo_args)
        add_vertex_cmd.set_do_function(self.set_stroke_control_vertices)
        add_vertex_cmd.set_undo_function(self.set_stroke_control_vertices)

        cmd_stack.add_to_undo(add_vertex_cmd)
        cmd_stack.save_count += 1
        ui.edit_undo.setEnabled(True)

    def split_stroke_at_point(self, sel_stroke, inside_info):
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        split_at_cmd = commands.Command('split_at_cmd')
        verts_before = sel_stroke.get_ctrl_vertices_as_list()

        new_verts = sel_stroke.split_at_point(inside_info[2], inside_info[1])
        verts_after = sel_stroke.get_ctrl_vertices_as_list()

        new_stroke = stroke.Stroke()
        new_stroke.set_ctrl_vertices_from_list(new_verts, False)

        undo_args = {
            'strokes' : sel_stroke,
            'ctrl_verts' : verts_before,
            'stroke_to_delete' : new_stroke,
        }

        do_args = {
            'strokes' : sel_stroke,
            'new_stroke' : new_stroke,
            'ctrl_verts' : verts_after,
        }

        split_at_cmd.set_do_args(do_args)
        split_at_cmd.set_undo_args(undo_args)
        split_at_cmd.set_do_function(self.split_stroke)
        split_at_cmd.set_undo_function(self.unsplit_stroke)

        cmd_stack.do_command(split_at_cmd)
        ui.edit_undo.setEnabled(True)

    def add_new_stroke(self):
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()

        verts = self.__tmp_stroke.get_ctrl_vertices_as_list()
        if len(verts) < 2:
            self.__main_ctrl.state = control.edit_control.IDLE
            self.__tmp_stroke = None
            self.__stroke_pts = []
            current_view.strokes = []
            ui.repaint()
            return

        self.__main_ctrl.state = control.edit_control.IDLE
        self.__stroke_pts = []

        add_stroke_cmd = commands.Command('add_stroke_cmd')
        do_args = {
            'stroke' : self.__tmp_stroke,
            'copy_stroke' : False,
        }

        undo_args = {
            'stroke' : self.__tmp_stroke,
        }

        add_stroke_cmd.set_do_args(do_args)
        add_stroke_cmd.set_undo_args(undo_args)
        add_stroke_cmd.set_do_function(cur_char.add_stroke)
        add_stroke_cmd.set_undo_function(cur_char.delete_stroke)

        cmd_stack.do_command(add_stroke_cmd)
        ui.edit_undo.setEnabled(True)

        cur_view_selection[self.__tmp_stroke] = {}
        self.__tmp_stroke.selected = True
        current_view.strokes = []
        self.__tmp_stroke = None

        self.__main_ctrl.set_ui_state_selection(True)

        for idx in range(0, ui.main_view_tabs.count()):
            ui.main_view_tabs.setTabEnabled(idx, True)

        if len(char_set.get_saved_glyphs()) == 0:
            ui.main_view_tabs.setTabEnabled(ui.main_view_tabs.indexOf(ui.stroke_dwg_area), \
                False)

        ui.repaint()

    def flip_selected_strokes_x(self):
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        flip_strokes_x_cmd = commands.Command("flip_strokes_x_cmd")

        do_args = {
            'strokes' : cur_view_selection.keys()
        }

        undo_args = {
            'strokes' : cur_view_selection.keys()
        }

        flip_strokes_x_cmd.set_do_args(do_args)
        flip_strokes_x_cmd.set_undo_args(undo_args)
        flip_strokes_x_cmd.set_do_function(self.flip_strokes_x)
        flip_strokes_x_cmd.set_undo_function(self.flip_strokes_x)
        
        cmd_stack.do_command(flip_strokes_x_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def flip_strokes_x(self, args):
        if 'strokes' in args:
            strokes_to_flip = args['strokes']
        else:
            return

        for sel_stroke in strokes_to_flip:
            sel_stroke.flip_x()

    def flip_selected_strokes_y(self):
        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        flip_strokes_y_cmd = commands.Command("flip_strokes_y_cmd")

        do_args = {
            'strokes' : cur_view_selection.keys()
        }

        undo_args = {
            'strokes' : cur_view_selection.keys()
        }

        flip_strokes_y_cmd.set_do_args(do_args)
        flip_strokes_y_cmd.set_undo_args(undo_args)
        flip_strokes_y_cmd.set_do_function(self.flip_strokes_y)
        flip_strokes_y_cmd.set_undo_function(self.flip_strokes_y)
        
        cmd_stack.do_command(flip_strokes_y_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def flip_strokes_y(self, args):
        if 'strokes' in args:
            strokes_to_flip = args['strokes']
        else:
            return

        for sel_stroke in strokes_to_flip:
            sel_stroke.flip_y()

    def move_selected(self, args):
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
            if len(selection[sel_stroke].keys()) > 0:
                for stroke_pt in selection[sel_stroke].keys():
                    stroke_pt.select_handle(selection[sel_stroke][stroke_pt])
                    if snap_point:
                        stroke_pt.selected_handle_pos = snap_point - sel_stroke.pos
                    else:
                        stroke_pt.selected_handle_pos = stroke_pt.selected_handle_pos + delta
            else:
                sel_stroke.pos += delta

            if type(sel_stroke).__name__ == 'Stroke':
                sel_stroke.calc_curve_points()

        if len(selection.keys()):
            ui = self.__main_ctrl.get_ui()        
            ui.position_x_spin.setValue(selection.keys()[0].pos.x())
            ui.position_y_spin.setValue(selection.keys()[0].pos.y())

    def selection_position_changed_x(self, prev_value, new_value):
        delta = QtCore.QPoint(new_value - prev_value, 0)
        undelta = QtCore.QPoint(prev_value - new_value, 0)

        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        do_args = {
            'strokes' : cur_view_selection,
            'delta' : delta,
        }

        undo_args = {
            'strokes' : cur_view_selection,
            'delta' : undelta
        }

        position_x_cmd = commands.Command("position_x_cmd")
        position_x_cmd.set_do_args(do_args)
        position_x_cmd.set_undo_args(undo_args)
        position_x_cmd.set_do_function(self.move_selected)
        position_x_cmd.set_undo_function(self.move_selected)

        cmd_stack.do_command(position_x_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def selection_position_changed_y(self, prev_value, new_value):
        delta = QtCore.QPoint(0, new_value - prev_value)
        undelta = QtCore.QPoint(0, prev_value - new_value)

        current_view = self.__main_ctrl.get_current_view()
        cur_char = current_view.symbol
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        do_args = {
            'strokes' : cur_view_selection,
            'delta' : delta,
        }

        undo_args = {
            'strokes' : cur_view_selection,
            'delta' : undelta
        }

        position_y_cmd = commands.Command("position_y_cmd")
        position_y_cmd.set_do_args(do_args)
        position_y_cmd.set_undo_args(undo_args)
        position_y_cmd.set_do_function(self.move_selected)
        position_y_cmd.set_undo_function(self.move_selected)

        cmd_stack.do_command(position_y_cmd)
        ui.edit_undo.setEnabled(True)
        
        ui.repaint()


def dist_between_pts(p0, p1):
    return math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]))
