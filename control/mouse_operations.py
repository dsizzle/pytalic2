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
			scaleChange = 0
			if event.delta() > 0:
				scaleChange = -0.02
			else:
				scaleChange = 0.02

			current_view.scale += scaleChange
			
			paper_pos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
			paper_pos.setY(paper_pos.y() - ui.mainViewTabs.tabBar().height())
			zoomPos = (paper_pos - current_view.getOrigin()) * scaleChange

			current_view.originDelta -= zoomPos
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

		paper_pos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
		paper_pos.setY(paper_pos.y() - ui.mainViewTabs.tabBar().height())

	def mouse_release_event_paper(self, event):
		current_view = self.__main_ctrl.get_current_view()
		
		btn = event.button()
		mod = event.modifiers()
		ui = self.__main_ctrl.get_ui()

		cmd_down = mod & QtCore.Qt.ControlModifier
		alt_down = mod & QtCore.Qt.AltModifier
		shift_down = mod & QtCore.Qt.ShiftModifier

		leftUp = btn & QtCore.Qt.LeftButton
		rightUp = btn & QtCore.Qt.RightButton

		if self.__main_ctrl.state == edit_control.MOVING_PAPER and leftUp:
			self.__main_ctrl.state = edit_control.IDLE
		else:
			if rightUp:
				self.__on_r_button_up_paper()
			elif leftUp:
				self.__on_l_button_up_paper(event.pos(), shift_down)
				
		ui.repaint()
		if current_view != ui.preview_area:
			self.__main_ctrl.setIcon()

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

		paper_pos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
		paper_pos.setY(paper_pos.y() - ui.mainViewTabs.tabBar().height())
		
		if self.__main_ctrl.state == edit_control.MOVING_PAPER:
			delta = paper_pos - self.__saved_mouse_pos_paper[current_view]
			current_view.originDelta += delta
			self.__saved_mouse_pos_paper[current_view] = paper_pos
		elif self.__main_ctrl.state == edit_control.DRAGGING:
			normpaper_pos = current_view.getNormalizedPosition(paper_pos) 
			deltaPos = paper_pos - normpaper_pos
			
			snap_ctrl = self.__main_ctrl.get_snap_controller()
			stroke_ctrl = self.__main_ctrl.get_stroke_controller()
			if snap_ctrl.getSnap() > 0:
				current_view.snapPoints = snap_ctrl.getSnappedPoints(normpaper_pos)
			else:
				current_view.snapPoints = []
					
			delta = (paper_pos - self.__saved_mouse_pos_paper[current_view]) / current_view.scale
			self.__move_delta += delta
			self.__saved_mouse_pos_paper[current_view] = paper_pos
			args = {
				'strokes' : cur_view_selection,
				'delta' : delta,
			}

			if len(current_view.snapPoints) > 0:
				args['snapPoint'] = current_view.snapPoints[0]

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
			self.__main_ctrl.setIcon()

	def __on_r_button_up_paper(self):
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()
		cmdStack = self.__main_ctrl.get_command_stack()

		if self.__main_ctrl.state == edit_control.DRAWING_NEW_STROKE:
			stroke_ctrl = self.__main_ctrl.get_stroke_controller()
			stroke_ctrl.add_new_stroke()
			QtGui.qApp.restoreOverrideCursor()

	def __on_l_button_up_paper(self, pos, shift_down):
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]

		ui = self.__main_ctrl.get_ui()
		stroke_ctrl = self.__main_ctrl.get_stroke_controller()
		cmdStack = self.__main_ctrl.get_command_stack()

		adjustedPos = pos - ui.mainSplitter.pos() - ui.mainWidget.pos()
		adjustedPos.setY(adjustedPos.y() - ui.mainViewTabs.tabBar().height())

		paper_pos = current_view.getNormalizedPosition(adjustedPos)
		
		current_view.snapPoints = []
		if self.__main_ctrl.state == edit_control.DRAWING_NEW_STROKE:
			stroke_ctrl.stroke_pts.append([paper_pos.x(), paper_pos.y()])
			stroke_ctrl.tmp_stroke.generateCtrlVerticesFromPoints(stroke_ctrl.stroke_pts)
			stroke_ctrl.tmp_stroke.updateCtrlVertices()

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
		
			cmdStack.add_to_undo(move_cmd)
			cmdStack.save_count += 1
			ui.edit_undo.setEnabled(True)

			self.__main_ctrl.state = edit_control.IDLE
			self.__move_delta = QtCore.QPoint(0, 0)
		elif self.__main_ctrl.state == edit_control.ADDING_CTRL_POINT:
			if len(cur_view_selection.keys()) > 0:
				for sel_stroke in cur_view_selection.keys():
					inside_info = sel_stroke.insideStroke(paper_pos)
					if inside_info[1] >= 0:
						stroke_ctrl.add_control_point(sel_stroke, inside_info)
						break

			self.__main_ctrl.state = edit_control.IDLE
			QtGui.qApp.restoreOverrideCursor()
		elif self.__main_ctrl.state == edit_control.SPLIT_AT_POINT:
			if len(cur_view_selection.keys()) > 0:
				for sel_stroke in cur_view_selection.keys():
					inside_info = sel_stroke.insideStroke(paper_pos)
					if inside_info[1] >= 0:
						stroke_ctrl.split_stroke_at_point(sel_stroke, inside_info)
						break

			self.__main_ctrl.state = edit_control.IDLE
			QtGui.qApp.restoreOverrideCursor()
		else:
			if len(cur_view_selection.keys()) > 0:
				for sel_stroke in cur_view_selection.keys():
					inside_info = sel_stroke.insideStroke(paper_pos)
					if inside_info[1] >= 0:
						ctrl_vertex_num = int((inside_info[1]+1) / 3)
						ctrl_vert = sel_stroke.getCtrlVertex(ctrl_vertex_num)
						
						handle_index = (inside_info[1]+1) % 3 +1
						if not shift_down:
							sel_stroke.deselectCtrlVerts()
							cur_view_selection[sel_stroke] = {}

						cur_view_selection[sel_stroke][ctrl_vert] = handle_index

						for ctrl_vert in cur_view_selection[sel_stroke].keys():
							ctrl_vert.selectHandle(cur_view_selection[sel_stroke][ctrl_vert])

						sel_stroke.selected = True
						
					else:
						if shift_down:
							if not cur_view_selection.has_key(sel_stroke):
								cur_view_selection[sel_stroke] = {}
								sel_stroke.deselectCtrlVerts()

							sel_stroke.selected = True
						else:
							if cur_view_selection.has_key(sel_stroke):
								del cur_view_selection[sel_stroke]

							sel_stroke.selected = False
							sel_stroke.deselectCtrlVerts()

				vert_list = cur_view_selection.values()
				behavior_list = []
				
				for vert_dict in vert_list:
					for vert in vert_dict.keys():
						behavior_list.append(vert.getBehavior())

				behavior_list = list(set(behavior_list))
				if len(behavior_list) == 1:
					ui.behaviorCombo.setCurrentIndex(behavior_list[0])
				else:
					ui.behaviorCombo.setCurrentIndex(0)

			if len(cur_view_selection.keys()) == 0 or shift_down:
				for sel_stroke in current_view.strokes:
					inside_info = sel_stroke.insideStroke(paper_pos)
					if inside_info[0] == True and (len(cur_view_selection.keys()) == 0 or shift_down):
						if not cur_view_selection.has_key(sel_stroke):
							cur_view_selection[sel_stroke] = {}	
							sel_stroke.deselectCtrlVerts()

						sel_stroke.selected = True	
					elif not shift_down:
						sel_stroke.selected = False
						sel_stroke.deselectCtrlVerts()

			if len(cur_view_selection.keys()) > 0:
				self.__main_ctrl.set_ui_state_selection(True)
			else:
				self.__main_ctrl.set_ui_state_selection(False)
				ui.behaviorCombo.setCurrentIndex(0)