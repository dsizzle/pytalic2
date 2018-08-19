from PyQt4 import QtCore, QtGui

import edit_control
from model import commands

class MouseController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__saved_mouse_pos_paper = {}
        self.__move_delta = QtCore.QPoint(0, 0)

    def mouse_event(self, event):
        current_view = self.__main_ctrl.get_current_view()

        if current_view.underMouse() or current_view.rect().contains(event.pos()):
            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.mouse_press_event_paper(event)
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.mouse_release_event_paper(event)
            else:
                self.mouse_move_event_paper(event)

            event.accept()

    def wheel_event(self, event):
        current_view = self.__main_ctrl.get_current_view()
        ui = self.__main_ctrl.get_ui()

        if current_view.underMouse() or current_view.rect().contains(event.pos()):
            scale_change = 0
            if event.delta() > 0:
                scale_change = -0.02
            else:
                scale_change = 0.02

            current_view.scale += scale_change
            
            paper_pos = event.pos() - ui.main_splitter.pos() - ui.main_widget.pos()
            paper_pos.setY(paper_pos.y() - ui.main_view_tabs.tabBar().height())
            zoom_pos = (paper_pos - current_view.origin) * scale_change

            current_view.origin_delta -= zoom_pos
            self.__saved_mouse_pos_paper[current_view] = paper_pos

            event.accept()
            ui.repaint()

    def mouse_press_event_paper(self, event):
        btn = event.buttons()
        mod = event.modifiers()
        ui = self.__main_ctrl.get_ui()
        
        cmd_down = mod & QtCore.Qt.ControlModifier
        alt_down = mod & QtCore.Qt.AltModifier
        shift_down = mod & QtCore.Qt.ShiftModifier

        left_down = btn & QtCore.Qt.LeftButton
        right_down = btn & QtCore.Qt.RightButton

        paper_pos = event.pos() - ui.main_splitter.pos() - ui.main_widget.pos()
        paper_pos.setY(paper_pos.y() - ui.main_view_tabs.tabBar().height())

    def mouse_release_event_paper(self, event):
        current_view = self.__main_ctrl.get_current_view()
        
        btn = event.button()
        mod = event.modifiers()
        ui = self.__main_ctrl.get_ui()

        cmd_down = mod & QtCore.Qt.ControlModifier
        alt_down = mod & QtCore.Qt.AltModifier
        shift_down = mod & QtCore.Qt.ShiftModifier

        left_up = btn & QtCore.Qt.LeftButton
        right_up = btn & QtCore.Qt.RightButton

        if self.__main_ctrl.state == edit_control.MOVING_PAPER and left_up:
            self.__main_ctrl.state = edit_control.IDLE
        else:
            if right_up:
                self.__on_r_button_up_paper()
            elif left_up:
                self.__on_l_button_up_paper(event.pos(), shift_down)
                
        ui.repaint()
        if current_view != ui.preview_area:
            self.__main_ctrl.set_icon()

    def mouse_move_event_paper(self, event):
        btn = event.buttons()
        mod = event.modifiers()
        ui = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        left_down = btn & QtCore.Qt.LeftButton
        right_down = btn & QtCore.Qt.RightButton

        alt_down = mod & QtCore.Qt.AltModifier

        paper_pos = event.pos() - ui.main_splitter.pos() - ui.main_widget.pos()
        paper_pos.setY(paper_pos.y() - ui.main_view_tabs.tabBar().height())
        
        if self.__main_ctrl.state == edit_control.MOVING_PAPER:
            delta = paper_pos - self.__saved_mouse_pos_paper[current_view]
            current_view.origin_delta += delta
            self.__saved_mouse_pos_paper[current_view] = paper_pos
        elif self.__main_ctrl.state == edit_control.DRAGGING:
            norm_paper_pos = current_view.get_normalized_position(paper_pos)
            delta_pos = paper_pos - norm_paper_pos
            
            snap_ctrl = self.__main_ctrl.get_snap_controller()
            stroke_ctrl = self.__main_ctrl.get_stroke_controller()
            if snap_ctrl.get_snap() > 0:
                current_view.snap_points = snap_ctrl.get_snapped_points(norm_paper_pos)
            else:
                current_view.snap_points = []
                    
            delta = (paper_pos - self.__saved_mouse_pos_paper[current_view]) / current_view.scale
            self.__move_delta += delta
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            args = {
                'strokes' : cur_view_selection,
                'delta' : delta,
            }

            if len(current_view.snap_points) > 0:
                args['snap_point'] = current_view.snap_points[0]

            stroke_ctrl.move_selected(args)
        elif left_down and alt_down and self.__main_ctrl.state == edit_control.IDLE:
            self.__saved_mouse_pos_paper[current_view] = paper_pos      
            self.__main_ctrl.state = edit_control.MOVING_PAPER
        elif left_down and self.__main_ctrl.state == edit_control.IDLE:
            self.__main_ctrl.state = edit_control.DRAGGING
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            self.__move_delta = QtCore.QPoint(0, 0)

        ui.repaint()
        if current_view != ui.preview_area:
            self.__main_ctrl.set_icon()

    def __on_r_button_up_paper(self):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        if self.__main_ctrl.state == edit_control.DRAWING_NEW_STROKE:
            stroke_ctrl = self.__main_ctrl.get_stroke_controller()
            stroke_ctrl.add_new_stroke()
            QtGui.qApp.restoreOverrideCursor()

    def __on_l_button_up_paper(self, pos, shift_down):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        cur_char = self.__main_ctrl.get_current_char()

        ui = self.__main_ctrl.get_ui()
        stroke_ctrl = self.__main_ctrl.get_stroke_controller()
        cmd_stack = self.__main_ctrl.get_command_stack()

        adjusted_pos = pos - ui.main_splitter.pos() - ui.main_widget.pos()
        adjusted_pos.setY(adjusted_pos.y() - ui.main_view_tabs.tabBar().height())

        paper_pos = current_view.get_normalized_position(adjusted_pos)
        
        current_view.snap_points = []
        if self.__main_ctrl.state == edit_control.DRAWING_NEW_STROKE:
            stroke_ctrl.stroke_pts.append([paper_pos.x(), paper_pos.y()])
            stroke_ctrl.tmp_stroke.generate_ctrl_vertices_from_points(stroke_ctrl.stroke_pts)
            stroke_ctrl.tmp_stroke.update_ctrl_vertices()
            ui.position_x_spin.setValue(stroke_ctrl.tmp_stroke.pos.x())
            ui.position_y_spin.setValue(stroke_ctrl.tmp_stroke.pos.y())

        elif self.__main_ctrl.state == edit_control.DRAGGING:
            move_cmd = commands.Command('move_stroke_cmd')
            selection_copy = cur_view_selection.copy()
            do_args = {
                'strokes' : selection_copy, 
                'delta' : self.__move_delta,
            }

            undo_args = {
                'strokes' : selection_copy,
                'delta' : QtCore.QPoint(0, 0) - self.__move_delta,
            }

            move_cmd.set_do_args(do_args)
            move_cmd.set_undo_args(undo_args)
            move_cmd.set_do_function(stroke_ctrl.move_selected)
            move_cmd.set_undo_function(stroke_ctrl.move_selected)
        
            cmd_stack.add_to_undo(move_cmd)
            cmd_stack.save_count += 1
            ui.edit_undo.setEnabled(True)

            self.__main_ctrl.state = edit_control.IDLE
            self.__move_delta = QtCore.QPoint(0, 0)
        elif self.__main_ctrl.state == edit_control.ADDING_CTRL_POINT:
            if len(cur_view_selection.keys()) > 0:
                for sel_stroke in cur_view_selection.keys():
                    inside_info = sel_stroke.is_inside(paper_pos)
                    if inside_info[1] >= 0:
                        stroke_ctrl.add_control_point(sel_stroke, inside_info)
                        break

            self.__main_ctrl.state = edit_control.IDLE
            QtGui.qApp.restoreOverrideCursor()
        elif self.__main_ctrl.state == edit_control.SPLIT_AT_POINT:
            if len(cur_view_selection.keys()) > 0:
                for sel_stroke in cur_view_selection.keys():
                    inside_info = sel_stroke.is_inside(paper_pos)
                    if inside_info[1] >= 0:
                        stroke_ctrl.split_stroke_at_point(sel_stroke, inside_info)
                        break

            self.__main_ctrl.state = edit_control.IDLE
            QtGui.qApp.restoreOverrideCursor()
        else:
            self.update_selection(paper_pos, shift_down)

    def update_selection(self, paper_pos, shift_down):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        cur_char = self.__main_ctrl.get_current_char()

        ui = self.__main_ctrl.get_ui()
        
        if len(cur_view_selection.keys()) > 0:
            for sel_stroke in cur_view_selection.keys():
                inside_info = sel_stroke.is_inside(paper_pos)
                if inside_info[1] >= 0:
                    ctrl_vertex_num = int((inside_info[1]+1) / 3)
                    ctrl_vert = sel_stroke.get_ctrl_vertex(ctrl_vertex_num)
                    
                    handle_index = (inside_info[1] + 1) % 3 +1
                    if not shift_down:
                        if type(sel_stroke).__name__ == 'Stroke':
                            sel_stroke.deselect_ctrl_verts()
                        cur_view_selection[sel_stroke] = {}

                    cur_view_selection[sel_stroke][ctrl_vert] = handle_index

                    for ctrl_vert in cur_view_selection[sel_stroke].keys():
                        ctrl_vert.select_handle(cur_view_selection[sel_stroke][ctrl_vert])

                    sel_stroke.selected = True
                    
                else:
                    if shift_down:
                        if sel_stroke not in cur_view_selection:
                            cur_view_selection[sel_stroke] = {}
                            if type(sel_stroke).__name__ == 'Stroke':
                                sel_stroke.deselect_ctrl_verts()

                        sel_stroke.selected = True
                    else:
                        if sel_stroke in cur_view_selection:
                            del cur_view_selection[sel_stroke]

                        sel_stroke.selected = False
                        if type(sel_stroke).__name__ == 'Stroke':
                            sel_stroke.deselect_ctrl_verts()

            vert_list = cur_view_selection.values()
            behavior_list = []
            
            for vert_dict in vert_list:
                for vert in vert_dict.keys():
                    behavior_list.append(vert.behavior)

            behavior_list = list(set(behavior_list))
            if len(behavior_list) == 1:
                ui.behavior_combo.setCurrentIndex(behavior_list[0])
            else:
                ui.behavior_combo.setCurrentIndex(0)

        if len(cur_view_selection.keys()) == 0 or shift_down:
            if current_view != ui.preview_area:
                for sel_stroke in current_view.symbol.children:
                    inside_info = sel_stroke.is_inside(paper_pos)
                    if inside_info[0] == True and (len(cur_view_selection.keys()) == 0 or shift_down):
                        if sel_stroke not in cur_view_selection:
                            cur_view_selection[sel_stroke] = {} 
                            if type(sel_stroke).__name__ == 'Stroke':
                                sel_stroke.deselect_ctrl_verts()

                        sel_stroke.selected = True  
                    elif not shift_down:
                        sel_stroke.selected = False
                        if type(sel_stroke).__name__ == 'Stroke':
                            sel_stroke.deselect_ctrl_verts()
            else:
                for sel_symbol in ui.preview_area.layout.object_list:
                    inside_info = sel_symbol.is_inside(paper_pos)
                    if inside_info[0] == True and (len(cur_view_selection.keys()) == 0 or shift_down):
                        if sel_symbol not in cur_view_selection:
                            cur_view_selection[sel_symbol] = {}     
                        sel_symbol.selected = True  
                    elif not shift_down:
                        sel_symbol.selected = False
                        
        if len(cur_view_selection.keys()) > 0:
            self.__main_ctrl.set_ui_state_selection(True)
            ui.position_x_spin.setValue(cur_view_selection.keys()[0].pos.x())
            ui.position_y_spin.setValue(cur_view_selection.keys()[0].pos.y())
            if type(cur_view_selection.keys()[0]).__name__ != 'GlyphInstance' and \
                cur_view_selection.keys()[0].nib_angle:
                ui.stroke_nib_angle_spin.setValue(cur_view_selection.keys()[0].nib_angle)
            else:
                ui.stroke_nib_angle_spin.setValue(ui.char_set_nib_angle_spin.value())
            check_state = QtCore.Qt.Unchecked
            if type(cur_view_selection.keys()[0]).__name__ != 'GlyphInstance' and \
                cur_view_selection.keys()[0].override_nib_angle:
                check_state = QtCore.Qt.Checked
            ui.stroke_override_nib_angle.setCheckState(check_state)
        else:
            self.__main_ctrl.set_ui_state_selection(False)
            ui.behavior_combo.setCurrentIndex(0)
            ui.position_x_spin.setValue(0)
            ui.position_y_spin.setValue(0)
            ui.stroke_nib_angle_spin.setValue(ui.char_set_nib_angle_spin.value())
            ui.stroke_override_nib_angle.setCheckState(QtCore.Qt.Unchecked)