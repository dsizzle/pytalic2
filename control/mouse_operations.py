from PyQt4 import QtCore, QtGui

import control.edit_control
import model.commands

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
        ui_ref = self.__main_ctrl.get_ui()

        if current_view.underMouse() or current_view.rect().contains(event.pos()):
            scale_change = 0.0
            if event.delta() > 0:
                scale_change = -0.02
            else:
                scale_change = 0.02

            current_view.scale += scale_change

            paper_pos = event.pos() - ui_ref.main_splitter.pos() - ui_ref.main_widget.pos()
            paper_pos.setY(paper_pos.y() - ui_ref.main_view_tabs.tabBar().height())
            norm_paper_pos = current_view.get_normalized_position(paper_pos)
            zoom_pos = norm_paper_pos * scale_change

            current_view.origin_delta -= zoom_pos
            self.__saved_mouse_pos_paper[current_view] = paper_pos

            event.accept()
            ui_ref.repaint()

    def mouse_press_event_paper(self, event):
        btn = event.buttons()
        mod = event.modifiers()
        ui_ref = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()

        alt_down = mod & QtCore.Qt.AltModifier
        shift_down = mod & QtCore.Qt.ShiftModifier

        left_down = btn & QtCore.Qt.LeftButton

        paper_pos = event.pos() - ui_ref.main_splitter.pos() - ui_ref.main_widget.pos()
        paper_pos.setY(paper_pos.y() - ui_ref.main_view_tabs.tabBar().height())

        if self.__main_ctrl.state == control.edit_control.IDLE and left_down:
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            self.__on_l_button_down_paper(event.pos(), shift_down, alt_down)

    def mouse_release_event_paper(self, event):
        current_view = self.__main_ctrl.get_current_view()

        btn = event.button()
        mod = event.modifiers()
        ui_ref = self.__main_ctrl.get_ui()

        shift_down = mod & QtCore.Qt.ShiftModifier

        left_up = btn & QtCore.Qt.LeftButton
        right_up = btn & QtCore.Qt.RightButton

        if self.__main_ctrl.state == control.edit_control.MOVING_PAPER and left_up:
            self.__main_ctrl.state = control.edit_control.IDLE
        else:
            if right_up:
                self.__on_r_button_up_paper()
            elif left_up:
                self.__on_l_button_up_paper(event.pos(), shift_down)

        ui_ref.repaint()
        if current_view != ui_ref.preview_area:
            self.__main_ctrl.set_icon()

    def mouse_move_event_paper(self, event):
        btn = event.buttons()
        mod = event.modifiers()
        ui_ref = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        left_down = btn & QtCore.Qt.LeftButton

        alt_down = mod & QtCore.Qt.AltModifier

        paper_pos = event.pos() - ui_ref.main_splitter.pos() - ui_ref.main_widget.pos()
        paper_pos.setY(paper_pos.y() - ui_ref.main_view_tabs.tabBar().height())
        norm_paper_pos = current_view.get_normalized_position(paper_pos)

        if self.__main_ctrl.state == control.edit_control.MOVING_PAPER:
            delta = paper_pos - self.__saved_mouse_pos_paper[current_view]
            current_view.origin_delta += delta
            self.__saved_mouse_pos_paper[current_view] = paper_pos
        elif self.__main_ctrl.state == control.edit_control.DRAGGING:
            snap_ctrl = self.__main_ctrl.get_snap_controller()
            stroke_ctrl = self.__main_ctrl.get_stroke_controller()
            if snap_ctrl.get_snap() > 0:
                current_view.snap_points = snap_ctrl.get_snapped_points(norm_paper_pos)
            else:
                current_view.snap_points = []

            delta = (paper_pos - self.__saved_mouse_pos_paper[current_view]) / current_view.scale
            if snap_ctrl.is_constrained_x():
                delta.setY(0)

            if snap_ctrl.is_constrained_y():
                delta.setX(0)

            self.__move_delta += delta
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            args = {
                'strokes' : cur_view_selection,
                'delta' : delta,
            }

            if len(current_view.snap_points) > 0:
                args['snap_point'] = current_view.snap_points[0]

            stroke_ctrl.move_selected(args)
        elif left_down and alt_down and self.__main_ctrl.state == control.edit_control.IDLE:
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            self.__main_ctrl.state = control.edit_control.MOVING_PAPER
        elif left_down and self.__main_ctrl.state == control.edit_control.IDLE:
            self.__main_ctrl.state = control.edit_control.DRAGGING
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            self.__move_delta = QtCore.QPoint(0, 0)
        elif self.__main_ctrl.state == control.edit_control.SELECT_DRAGGING:
            top_left = QtCore.QPoint(min(self.__saved_mouse_pos_paper[current_view].x(), \
                norm_paper_pos.x()), \
                min(self.__saved_mouse_pos_paper[current_view].y(), \
                norm_paper_pos.y()))
            bot_right = QtCore.QPoint(max(self.__saved_mouse_pos_paper[current_view].x(), \
                norm_paper_pos.x()), \
                max(self.__saved_mouse_pos_paper[current_view].y(), \
                norm_paper_pos.y()))

            current_view.select_rect = QtCore.QRectF(top_left, bot_right)

        ui_ref.repaint()
        if current_view != ui_ref.preview_area:
            self.__main_ctrl.set_icon()

    def __on_r_button_up_paper(self):
        if self.__main_ctrl.state == control.edit_control.DRAWING_NEW_STROKE:
            stroke_ctrl = self.__main_ctrl.get_stroke_controller()
            stroke_ctrl.add_new_stroke()
            QtGui.qApp.restoreOverrideCursor()

    def __on_l_button_down_paper(self, pos, shift_down, alt_down):
        ui_ref = self.__main_ctrl.get_ui()
        current_view = self.__main_ctrl.get_current_view()
        adjusted_pos = pos - ui_ref.main_splitter.pos() - \
            ui_ref.main_widget.pos() - current_view.pos()
        adjusted_pos.setY(adjusted_pos.y() - ui_ref.main_view_tabs.tabBar().height())

        paper_pos = current_view.get_normalized_position(adjusted_pos)

        self.update_selection(paper_pos, shift_down)

        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]

        if len(cur_view_selection.keys()) > 0:
            self.__main_ctrl.state = control.edit_control.DRAGGING
        elif not alt_down:
            self.__saved_mouse_pos_paper[current_view] = paper_pos
            self.__main_ctrl.state = control.edit_control.SELECT_DRAGGING

    def __on_l_button_up_paper(self, pos, shift_down):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        ui_ref = self.__main_ctrl.get_ui()
        stroke_ctrl = self.__main_ctrl.get_stroke_controller()
        cmd_stack = self.__main_ctrl.get_command_stack()

        adjusted_pos = pos - ui_ref.main_splitter.pos() - \
            ui_ref.main_widget.pos() - current_view.pos()
        adjusted_pos.setY(adjusted_pos.y() - ui_ref.main_view_tabs.tabBar().height())
       
        paper_pos = current_view.get_normalized_position(adjusted_pos)

        current_view.snap_points = []
        
        if self.__main_ctrl.state == control.edit_control.DRAWING_NEW_STROKE:
            stroke_ctrl.stroke_pts.append([paper_pos.x(), paper_pos.y()])

            new_points = stroke_ctrl.tmp_stroke.generate_ctrl_vertices_from_points(stroke_ctrl.stroke_pts)
            stroke_ctrl.tmp_stroke.update_ctrl_vertices()
            if shift_down:
                verts = stroke_ctrl.tmp_stroke.get_ctrl_vertices(False)
                last_vert = char_set.get_item_by_index(verts[-1])
                last_vert.select_knot(True)
                last_vert.behavior = 2
                last_vert.select_knot(False)
                stroke_ctrl.stroke_pts = new_points
            
            ui_ref.position_x_spin.setValue(stroke_ctrl.tmp_stroke.pos.x())
            ui_ref.position_y_spin.setValue(stroke_ctrl.tmp_stroke.pos.y())

        elif self.__main_ctrl.state == control.edit_control.DRAGGING:
            move_cmd = model.commands.Command('move_stroke_cmd')
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
            ui_ref.edit_undo.setEnabled(True)

            self.__main_ctrl.state = control.edit_control.IDLE
            self.__move_delta = QtCore.QPoint(0, 0)
        elif self.__main_ctrl.state == control.edit_control.ADDING_CTRL_POINT:
            if len(cur_view_selection.keys()) > 0:
                for sel_stroke in cur_view_selection.keys():
                    sel_stroke_item = char_set.get_item_by_index(sel_stroke)
                    inside_info = sel_stroke_item.is_inside(paper_pos, get_closest_vert=True)
                    if inside_info[1] >= 0:
                        stroke_ctrl.add_control_point(sel_stroke, inside_info)
                        break

            self.__main_ctrl.state = control.edit_control.IDLE
            QtGui.qApp.restoreOverrideCursor()
        elif self.__main_ctrl.state == control.edit_control.SPLIT_AT_POINT:
            if len(cur_view_selection.keys()) > 0:
                for sel_stroke in cur_view_selection.keys():
                    sel_stroke_item = char_set.get_item_by_index(sel_stroke)
                    inside_info = sel_stroke_item.is_inside(paper_pos, get_closest_vert=True)
                    if inside_info[1] >= 0:
                        stroke_ctrl.split_stroke_at_point(sel_stroke, inside_info)
                        break

            self.__main_ctrl.state = control.edit_control.IDLE
            QtGui.qApp.restoreOverrideCursor()
        elif self.__main_ctrl.state == control.edit_control.SELECT_DRAGGING:
            self.__main_ctrl.state = control.edit_control.IDLE
            self.update_selection(paper_pos, shift_down, current_view.select_rect)
            current_view.select_rect = None

    def update_selection(self, paper_pos, shift_down, select_rect=None):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        ui_ref = self.__main_ctrl.get_ui()

        if len(cur_view_selection.keys()) > 0:
            self.__update_current_selection(paper_pos, shift_down)

        if len(cur_view_selection.keys()) == 0 or shift_down or select_rect:
            self.__update_empty_selection(paper_pos, shift_down, select_rect)

        if len(cur_view_selection.keys()) > 0:
            self.__main_ctrl.set_ui_state_selection(True)
            check_state = QtCore.Qt.Unchecked
            nib_angle_override = None
            first_object = cur_view_selection.keys()[0]
            first_item = char_set.get_item_by_index(first_object)
            if type(first_item).__name__ != 'GlyphInstance' and \
                type(first_item).__name__ != 'CharacterInstance' and \
                first_item.override_nib_angle:
                check_state = QtCore.Qt.Checked
                nib_angle_override = first_item.nib_angle

            ui_ref.stroke_override_nib_angle.setCheckState(check_state)

            ui_ref.position_x_spin.setValue(first_item.pos.x())
            ui_ref.position_y_spin.setValue(first_item.pos.y())
            if type(first_item).__name__ != 'GlyphInstance' and \
                type(first_item).__name__ != 'CharacterInstance' and \
                nib_angle_override:
                ui_ref.stroke_nib_angle_spin.setValue(nib_angle_override)
            else:
                ui_ref.stroke_nib_angle_spin.setValue(ui_ref.char_set_nib_angle_spin.value())

            if len(cur_view_selection[first_object].keys()):
                first_vert = cur_view_selection[first_object].keys()[0]

                vert_item = char_set.get_item_by_index(first_vert)
                if vert_item.get_pos_of_selected():
                    ui_ref.vertex_x_spin.setValue(vert_item.get_pos_of_selected().x())
                    ui_ref.vertex_y_spin.setValue(vert_item.get_pos_of_selected().y())

        else:
            self.__main_ctrl.set_ui_state_selection(False)
            ui_ref.behavior_combo.setCurrentIndex(0)
            ui_ref.position_x_spin.setValue(0)
            ui_ref.position_y_spin.setValue(0)
            ui_ref.vertex_x_spin.setValue(0)
            ui_ref.vertex_y_spin.setValue(0)
            ui_ref.stroke_nib_angle_spin.setValue(ui_ref.char_set_nib_angle_spin.value())
            ui_ref.stroke_override_nib_angle.setCheckState(QtCore.Qt.Unchecked)

    def __update_current_selection(self, paper_pos, shift_down):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()
        ui_ref = self.__main_ctrl.get_ui()
        
        if current_view == ui_ref.preview_area:
            layout_pos = ui_ref.preview_area.layout.pos
            test_pos = paper_pos - layout_pos
        else:
            test_pos = paper_pos

        inside_strokes = {}
        for sel_stroke in cur_view_selection.keys():
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            inside_info = sel_stroke_item.is_inside(test_pos)
            if inside_info[0]:
                inside_strokes[sel_stroke] = inside_info

        if len(inside_strokes):
            for sel_stroke in inside_strokes:
                sel_stroke_item = char_set.get_item_by_index(sel_stroke)
                inside_info = inside_strokes[sel_stroke]

                if inside_info[1] >= 0:
                    ctrl_vertex_num = int((inside_info[1]+1) / 3)
                    ctrl_vert = sel_stroke_item.get_ctrl_vertex(ctrl_vertex_num)

                    handle_index = (inside_info[1] + 1) % 3 + 1
                    if not shift_down:
                        if type(sel_stroke_item).__name__ == 'Stroke':
                            sel_stroke_item.deselect_ctrl_verts()
                        cur_view_selection[sel_stroke] = {}

                    cur_view_selection[sel_stroke][ctrl_vert] = handle_index

                    for ctrl_vert in cur_view_selection[sel_stroke].keys():
                        ctrl_vert_item = char_set.get_item_by_index(ctrl_vert)
                        ctrl_vert_item.select_handle(cur_view_selection[sel_stroke][ctrl_vert])

        elif not shift_down:
            self.__main_ctrl.deselect_all_strokes_cb()
            cur_view_selection = selection[current_view]

        behavior_list = []

        for vert_dict in cur_view_selection.values():
            for vert in vert_dict.keys():
                vert_item = char_set.get_item_by_index(vert)
                behavior_list.append(vert_item.behavior)

        behavior_list = list(set(behavior_list))
        if len(behavior_list) == 1:
            ui_ref.behavior_combo.setCurrentIndex(behavior_list[0])
        else:
            ui_ref.behavior_combo.setCurrentIndex(0)
        
    def __update_empty_selection(self, paper_pos, shift_down, select_rect):
        current_view = self.__main_ctrl.get_current_view()
        selection = self.__main_ctrl.get_selection()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()
        ui_ref = self.__main_ctrl.get_ui()
        test_list = []
        test_rect = select_rect

        if current_view == ui_ref.preview_area:
            layout_pos = ui_ref.preview_area.layout.pos
            test_pos = paper_pos - layout_pos
            test_list = ui_ref.preview_area.layout.object_list
            if select_rect:
                test_rect = select_rect.translated(-layout_pos)
        else:
            test_pos = paper_pos
            if current_view.symbol:
                test_list = current_view.symbol.children
            
        for sel_stroke in test_list:
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)
            inside_rect = False
            inside_info = [False]
            if select_rect:
                inside_rect = sel_stroke_item.is_contained(test_rect)
            else:
                inside_info = sel_stroke_item.is_inside(test_pos)

            if (inside_info[0] or inside_rect) \
                and (len(cur_view_selection.keys()) == 0 or \
                    shift_down or select_rect):
                if sel_stroke not in cur_view_selection:
                    cur_view_selection[sel_stroke] = {}
                    if type(sel_stroke_item).__name__ == 'Stroke':
                        sel_stroke_item.deselect_ctrl_verts()

                sel_stroke_item.selected = True
            elif not shift_down and not inside_rect:
                sel_stroke_item.selected = False
                if sel_stroke in cur_view_selection:
                    del cur_view_selection[sel_stroke]
                if type(sel_stroke_item).__name__ == 'Stroke':
                    sel_stroke_item.deselect_ctrl_verts()