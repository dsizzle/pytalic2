import math

from PyQt4 import QtCore, QtGui

import control.edit_control
from model import commands, stroke

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

        ui = self.__main_ctrl.get_ui()

        self.__main_ctrl.state = control.edit_control.DRAWING_NEW_STROKE
        QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

        dwg_tab = ui.main_view_tabs.indexOf(ui.dwg_area)

        for idx in range(0, ui.main_view_tabs.count()):
            if idx != dwg_tab:
                ui.main_view_tabs.setTabEnabled(idx, False)

        self.__stroke_pts = []
        self.__tmp_stroke = stroke.Stroke()
        ui.dwg_area.strokesSpecial.append(self.__tmp_stroke)

    def save_stroke(self):
        selected_strokes = []
        instances = []
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        for sel_stroke in cur_view_selection.keys():
            if type(sel_stroke).__name__ == 'Stroke':
                selected_strokes.append(sel_stroke)

                new_stroke_instance = stroke.StrokeInstance()
                instances.append(new_stroke_instance)

        item_num = ui.stroke_selector_list.count()

        save_stroke_cmd = commands.Command('save_stroke_cmd')

        do_args = {
            'strokes' : selected_strokes,
            'instances' : instances,
            'first_item' : item_num,
        }

        undo_args = {
            'instances' : instances,
            'first_item' : item_num,
        }

        save_stroke_cmd.set_do_args(do_args)
        save_stroke_cmd.set_undo_args(undo_args)
        save_stroke_cmd.set_do_function(self.save_strokes)
        save_stroke_cmd.set_undo_function(self.unsave_strokes)

        cmd_stack.do_command(save_stroke_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def save_strokes(self, args):
        deleted_strokes = []
        i = 0

        if args.has_key('strokes'):
            selection = args['strokes']
        else:
            return

        if args.has_key('instances'):
            instances = args['instances']
        else:
            return

        if args.has_key('first_item'):
            first_item = args['first_item']
        else:
            return

        char_set = self.__main_ctrl.get_character_set()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        for sel_stroke in cur_view_selection:
            char_set.save_stroke(sel_stroke)
            bitmap = ui.dwg_area.drawIcon(None, [sel_stroke])
            ui.stroke_selector_list.addItem(str(first_item+i))
            cur_item = ui.stroke_selector_list.item(first_item+i)
            ui.stroke_selector_list.setCurrentRow(first_item+i)
            cur_item.setIcon(QtGui.QIcon(bitmap))
            cur_char = char_set.current_char
            deleted_strokes.append(sel_stroke)
            cur_char.delete_stroke({'stroke' : sel_stroke})
            sel_stroke = char_set.get_saved_stroke(first_item+i)
            instances[i].setStroke(sel_stroke)
            cur_char.add_stroke_instance(instances[i])
            if not cur_view_selection.has_key(sel_stroke):
                cur_view_selection = {}
                sel_stroke.deselectCtrlVerts()

            sel_stroke.selected = True
            i += 1

        for sel_stroke in deleted_strokes:
            if cur_view_selection.has_key(sel_stroke):
                del cur_view_selection[sel_stroke]

            sel_stroke.selected = False

        ui.stroke_load.setEnabled(True)
        self.__main_ctrl.set_ui_state_selection(True)

    def unsave_strokes(self, args):
        added_strokes = []
        i = 0

        if args.has_key('instances'):
            instances = args['instances']
            i = len(instances)-1
        else:
            return

        if args.has_key('first_item'):
            first_item = args['first_item']
        else:
            return

        char_set = self.__main_ctrl.get_character_set()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        instances.reverse()
        for inst in instances:
            sel_stroke = inst.getStroke()
            ui.stroke_selector_list.takeItem(first_item+i)
            char_set.remove_saved_stroke(sel_stroke)
            cur_char = char_set.current_char
            cur_char.delete_stroke({'stroke' : inst})
            cur_char.add_stroke({'stroke' : sel_stroke, 'copy_stroke' : False})
            added_strokes.append(sel_stroke)
            i -= 1

        for sel_stroke in added_strokes:
            if not cur_view_selection.has_key(sel_stroke):
                cur_view_selection[sel_stroke] = {}
                sel_stroke.deselectCtrlVerts()

            sel_stroke.selected = True

        if ui.stroke_selector_list.count() == 0:
            ui.stroke_load.setEnabled(False)

        self.__main_ctrl.set_ui_state_selection(True)

    def paste_instance_from_saved(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()

        char_index = char_set.get_current_char_index()
        stroke_index = ui.stroke_selector_list.currentRow()
        saved_stroke = char_set.get_saved_stroke(stroke_index)
        new_stroke_instance = stroke.StrokeInstance()
        new_stroke_instance.setStroke(saved_stroke)

        paste_instance_saved_cmd = commands.Command('paste_instance_saved_cmd')

        do_args = {
            'strokes' : new_stroke_instance,
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : new_stroke_instance,
            'char_index' : char_index,
        }

        paste_instance_saved_cmd.set_do_args(do_args)
        paste_instance_saved_cmd.set_undo_args(undo_args)
        paste_instance_saved_cmd.set_do_function(self.paste_instance)
        paste_instance_saved_cmd.set_undo_function(self.delete_instance)

        cmd_stack.do_command(paste_instance_saved_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def paste_instance(self, args):
        if args.has_key('char_index'):
            char_index = args['char_index']
        else:
            return

        if args.has_key('strokes'):
            stroke_instance = args['strokes']
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        ui.char_selector_list.setCurrentRow(char_index)

        cur_char.add_stroke_instance(stroke_instance)
        cur_view_selection[stroke_instance] = {}

        ui.dwg_area.repaint()
        self.__main_ctrl.set_icon()

    def delete_instance(self, args):
        if args.has_key('char_index'):
            char_index = args['char_index']
        else:
            return

        if args.has_key('strokes'):
            stroke_to_del = args['strokes']
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()

        cur_char.delete_stroke({'stroke' : stroke_to_del})
        if cur_view_selection.has_key(stroke_to_del):
            del cur_view_selection[stroke_to_del]

        ui.dwg_area.repaint()

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
        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        stroke_list = strokes.keys()
        cur_stroke = stroke_list.pop(0)
        vert_list = cur_stroke.get_ctrl_vertices_as_list()
        cur_char.delete_stroke({'stroke': cur_stroke})
        if cur_view_selection.has_key(cur_stroke):
            del cur_view_selection[cur_stroke]
            cur_stroke.selected = False

        while len(stroke_list):
            cur_stroke = stroke_list.pop(0)
            cur_verts = cur_stroke.get_ctrl_vertices_as_list()
            cur_char.delete_stroke({'stroke': cur_stroke})
            if cur_view_selection.has_key(cur_stroke):
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
        new_stroke.set_ctrl_vertices_from_list(vert_list)
        new_stroke.calc_curve_points()
        cur_char.add_stroke({'stroke': new_stroke, 'copy_stroke': False})

        cur_view_selection[new_stroke] = {}
        new_stroke.selected = True

        return new_stroke

    def unjoin_all_strokes(self, args):
        if args.has_key('strokes'):
            strokes = args['strokes']
        else:
            return

        if args.has_key('joined_stroke'):
            joined_stroke = args['joined_stroke']
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        cur_char.delete_stroke({'stroke': joined_stroke})
        joined_stroke.selected = False
        if cur_view_selection.has_key(joined_stroke):
            del cur_view_selection[joined_stroke]

        for sel_stroke in strokes.keys():
            cur_char.add_stroke({'stroke': sel_stroke, 'copy_stroke': False})
            cur_view_selection[sel_stroke] = {}
            sel_stroke.selected = True

    def join_all_strokes(self, args):
        if args.has_key('strokes'):
            strokes = args['strokes']
        else:
            return

        if args.has_key('joined_stroke'):
            joined_stroke = args['joined_stroke']
        else:
            return

        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        cur_char.add_stroke({'stroke': joined_stroke, 'copy_stroke': False})
        joined_stroke.selected = True
        cur_view_selection[joined_stroke] = {}

        for sel_stroke in strokes.keys():
            cur_char.delete_stroke({'stroke': sel_stroke})
            if cur_view_selection.has_key(sel_stroke):
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

        if args.has_key('strokes'):
            sel_stroke_list = args['strokes']
        else:
            return

        if args.has_key('ctrl_verts'):
            ctrl_vert_list = args['ctrl_verts']
        else:
            return

        if len(ctrl_vert_list) != len(sel_stroke_list):
            return

        for i in range(0, len(sel_stroke_list)):
            sel_stroke = sel_stroke_list[i]
            sel_stroke.set_ctrl_vertices_from_list(ctrl_vert_list[i])
            sel_stroke.calc_curve_points()

        ui.repaint()

    def split_stroke(self, args):
        ui = self.__main_ctrl.get_ui()
        cur_char = self.__main_ctrl.get_current_char()

        if args.has_key('strokes'):
            sel_stroke = args['strokes']
        else:
            return

        if args.has_key('ctrl_verts'):
            ctrl_verts = args['ctrl_verts']
        else:
            return

        if args.has_key('new_stroke'):
            new_stroke = args['new_stroke']
        else:
            return

        sel_stroke.set_ctrl_vertices_from_list(ctrl_verts)
        sel_stroke.calc_curve_points()

        cur_char.add_stroke({'stroke': new_stroke, 'copy_stroke': False})
        ui.repaint()

    def unsplit_stroke(self, args):
        ui = self.__main_ctrl.get_ui()
        cur_char = self.__main_ctrl.get_current_char()

        if args.has_key('strokes'):
            sel_stroke = args['strokes']
        else:
            return

        if args.has_key('ctrl_verts'):
            ctrl_verts = args['ctrl_verts']
        else:
            return

        if args.has_key('stroke_to_delete'):
            del_stroke = args['stroke_to_delete']
        else:
            return

        sel_stroke.set_ctrl_vertices_from_list(ctrl_verts)
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
        new_stroke.set_ctrl_vertices_from_list(new_verts)

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
        cur_char = self.__main_ctrl.get_current_char()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        verts = self.__tmp_stroke.get_ctrl_vertices_as_list()
        if len(verts) < 2:
            self.__main_ctrl.state = control.edit_control.IDLE
            self.__tmp_stroke = None
            self.__stroke_pts = []
            current_view.strokesSpecial = []
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
        current_view.strokesSpecial = []
        self.__tmp_stroke = None

        self.__main_ctrl.set_ui_state_selection(True)

        for idx in range(0, ui.main_view_tabs.count()):
            ui.main_view_tabs.setTabEnabled(idx, True)

        ui.repaint()

    def move_selected(self, args):
        if args.has_key('strokes'):
            selection = args['strokes']
        else:
            return

        if args.has_key('delta'):
            delta = args['delta']
        else:
            return

        snap_point = None
        if args.has_key('snap_point'):
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

            sel_stroke.calc_curve_points()

def dist_between_pts(p0, p1):
    return math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]))
