from PyQt4 import QtCore, QtGui

import math

import edit_control
from model import commands, stroke

class stroke_controller():
	def __init__(self, parent):
		self.__main_ctrl = parent
		self.__tmpStroke = None
		self.__strokePts = []

	def getTmpStroke(self):
		return self.__tmpStroke

	def setTmpStroke(self, newTmpStroke):
		self.__tmpStroke = newTmpStroke

	tmpStroke = property(getTmpStroke, setTmpStroke)

	def getStrokePts(self):
		return self.__strokePts

	def setStrokePts(self, newStrokePts):
		self.__strokePts = newStrokePts

	strokePts = property(getStrokePts, setStrokePts)

	def createNewStroke(self):
		if self.__main_ctrl.state == edit_control.DRAWING_NEW_STROKE:
			return
		
		ui = self.__main_ctrl.get_ui()

		self.__main_ctrl.state = edit_control.DRAWING_NEW_STROKE
		QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)

		dwgTab = ui.mainViewTabs.indexOf(ui.dwgArea)

		for idx in range(0, ui.mainViewTabs.count()):
			if idx != dwgTab:
				ui.mainViewTabs.setTabEnabled(idx, False)

		self.__strokePts = []
		self.__tmpStroke = stroke.Stroke()
		ui.dwgArea.strokesSpecial.append(self.__tmpStroke)

	def saveStroke(self):
		selectedStrokes = []
		instances = []
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()
		cmd_stack = self.__main_ctrl.get_command_stack()

		for sel_stroke in cur_view_selection.keys():
			if type(sel_stroke).__name__ == 'Stroke':
				selectedStrokes.append(sel_stroke)

				newStrokeInstance = stroke.StrokeInstance()
				instances.append(newStrokeInstance)

		itemNum = ui.strokeSelectorList.count()

		save_stroke_cmd = commands.Command('save_stroke_cmd')
		
		do_args = {
			'strokes' : selectedStrokes,
			'instances' : instances,
			'first_item' : itemNum,
		}

		undo_args = {
			'instances' : instances,
			'first_item' : itemNum,
		}

		save_stroke_cmd.set_do_args(do_args)
		save_stroke_cmd.set_undo_args(undo_args)
		save_stroke_cmd.set_do_function(self.save_strokes)
		save_stroke_cmd.set_undo_function(self.unsave_strokes)
		
		cmd_stack.do_command(save_stroke_cmd)
		ui.editUndo.setEnabled(True)

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

		char_set = self.__main_ctrl.getCharacterSet()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()

		for sel_stroke in cur_view_selection:
			char_set.saveStroke(sel_stroke)
			bitmap = ui.dwgArea.drawIcon(None, [sel_stroke])
			ui.strokeSelectorList.addItem(str(first_item+i))
			cur_item = ui.strokeSelectorList.item(first_item+i)
			ui.strokeSelectorList.setCurrentRow(first_item+i)
			cur_item.setIcon(QtGui.QIcon(bitmap))
			cur_char = char_set.get_current_char()
			deleted_strokes.append(sel_stroke)
			cur_char.deleteStroke({'stroke' : sel_stroke})
			sel_stroke = char_set.getSavedStroke(first_item+i)
			instances[i].setStroke(sel_stroke)
			cur_char.addStrokeInstance(instances[i])
			if not cur_view_selection.has_key(sel_stroke):
				cur_view_selection = {}
				sel_stroke.deselectCtrlVerts()

			sel_stroke.selected = True
			i += 1
				
		for sel_stroke in deleted_strokes:
			if cur_view_selection.has_key(sel_stroke):
				del cur_view_selection[sel_stroke]

			sel_stroke.selected = False	

		ui.strokeLoad.setEnabled(True)
		self.__main_ctrl.setUIStateSelection(True)

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

		char_set = self.__main_ctrl.getCharacterSet()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()

		instances.reverse()
		for inst in instances:
			sel_stroke = inst.getStroke()
			ui.strokeSelectorList.takeItem(first_item+i)
			char_set.removeSavedStroke(sel_stroke)
			cur_char = char_set.get_current_char()
			cur_char.deleteStroke({'stroke' : inst})
			cur_char.addStroke({'stroke' : sel_stroke, 'copyStroke' : False})
			added_strokes.append(sel_stroke)
			i -= 1
			
		for sel_stroke in added_strokes:
			if not cur_view_selection.has_key(sel_stroke):
				cur_view_selection[sel_stroke] = {}
				sel_stroke.deselectCtrlVerts()
			
			sel_stroke.selected = True

		if ui.strokeSelectorList.count() == 0:
			ui.strokeLoad.setEnabled(False)
			
		self.__main_ctrl.setUIStateSelection(True)
		
	def pasteInstanceFromSaved(self):
		cmd_stack = self.__main_ctrl.get_command_stack()
		charSet = self.__main_ctrl.getCharacterSet()
		ui = self.__main_ctrl.get_ui()

		charIndex = charSet.get_current_charIndex()
		strokeIndex = ui.strokeSelectorList.currentRow()
		savedStroke = charSet.getSavedStroke(strokeIndex)
		newStrokeInstance = stroke.StrokeInstance()
		newStrokeInstance.setStroke(savedStroke)

		paste_instance_saved_cmd = commands.Command('paste_instance_saved_cmd')
		
		do_args = {
			'strokes' : newStrokeInstance,
			'char_index' : char_index,
		}

		undo_args = {
			'strokes' : newStrokeInstance,
			'char_index' : char_index,
		}

		paste_instance_saved_cmd.set_do_args(do_args)
		paste_instance_saved_cmd.set_undo_args(undo_args)
		paste_instance_saved_cmd.set_do_function(self.paste_instance)
		paste_instance_saved_cmd.set_undo_function(self.delete_instance)
		
		cmd_stack.do_command(paste_instance_saved_cmd)
		ui.editUndo.setEnabled(True)

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

		ui.charSelectorList.setCurrentRow(char_index)

		cur_char.addStrokeInstance(stroke_instance)
		cur_view_selection[stroke_instance] = {}
		
		ui.dwgArea.repaint()
		self.__main_ctrl.setIcon()

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

		cur_char.deleteStroke({'stroke' : stroke_to_del})
		if cur_view_selection.has_key(stroke_to_del):
			del cur_view_selection[stroke_to_del]

		ui.dwgArea.repaint()

	def straightenStroke(self):
		cmd_stack = self.__main_ctrl.get_command_stack()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()

		verts_before_list = []
		verts_after_list = []

		for sel_stroke in cur_view_selection.keys():
			verts_before = sel_stroke.getCtrlVerticesAsList()

			sel_stroke.straighten()

			verts_after = sel_stroke.getCtrlVerticesAsList()

			verts_before_list.append(verts_before)
			verts_after_list.append(verts_after)

		stroke_straighten_cmd = commands.Command("stroke_straighten_cmd")

		undo_args = {
			'strokes' : cur_view_selection.keys(),
			'ctrlVerts' : verts_before_list
		}

		do_args = {
			'strokes' : cur_view_selection.keys(),
			'ctrlVerts' : verts_after_list
		}

		stroke_straighten_cmd.set_do_args(do_args)
		stroke_straighten_cmd.set_undo_args(undo_args)
		stroke_straighten_cmd.set_do_function(self.set_stroke_control_vertices)
		stroke_straighten_cmd.set_undo_function(self.set_stroke_control_vertices)
					
		cmd_stack.add_to_undo(stroke_straighten_cmd)
		cmd_stack.save_count += 1
		ui.editUndo.setEnabled(True)

	def joinSelectedStrokes(self):
		cmd_stack = self.__main_ctrl.get_command_stack()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()

		if len(cur_view_selection.keys()) > 1:
			strokeJoinCmd = commands.Command("strokeJoinCmd")
			selectionCopy = cur_view_selection.copy()

			newStroke = self.joinStrokes(selectionCopy)

			do_args = {
				'strokes' : selectionCopy,
				'joinedStroke' : newStroke
			}

			undo_args = {
				'strokes' : selectionCopy.copy(),
				'joinedStroke' : newStroke
			}
			
			strokeJoinCmd.set_do_args(do_args)
			strokeJoinCmd.set_undo_args(undo_args)
			strokeJoinCmd.set_do_function(self.joinAllStrokes)
			strokeJoinCmd.set_undo_function(self.unjoinAllStrokes)

			cmd_stack.add_to_undo(strokeJoinCmd)
			cmd_stack.save_count += 1
			ui.editUndo.setEnabled(True)
			ui.repaint()
			
	def joinStrokes(self, strokes):
		cur_char = self.__main_ctrl.get_current_char()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		
		strokeList = strokes.keys()
		curStroke = strokeList.pop(0)
		vertList = curStroke.getCtrlVerticesAsList()
		cur_char.deleteStroke({'stroke': curStroke})
		if cur_view_selection.has_key(curStroke):
			del cur_view_selection[curStroke]
			curStroke.selected = False

		while len(strokeList):
			curStroke = strokeList.pop(0)
			curVerts = curStroke.getCtrlVerticesAsList()
			cur_char.deleteStroke({'stroke': curStroke})
			if cur_view_selection.has_key(curStroke):
				del cur_view_selection[curStroke]
				curStroke.selected = False

			d1 = distBetweenPts(curVerts[0], vertList[0])
			d2 = distBetweenPts(curVerts[-1], vertList[0])
			d3 = distBetweenPts(curVerts[0], vertList[-1])
			d4 = distBetweenPts(curVerts[-1], vertList[-1])

			ptList = [d1, d2, d3, d4]
			ptList.sort()

			smallest = ptList[0]

			if smallest == d1:
				curVerts.reverse()

			if smallest == d1 or smallest == d4:
				vertList.reverse()

			if smallest == d2:
				(curVerts, vertList) = (vertList, curVerts)

			vertList.extend(curVerts[1:])

		newStroke = stroke.Stroke()
		newStroke.setCtrlVerticesFromList(vertList)
		newStroke.calcCurvePoints()
		cur_char.addStroke({'stroke': newStroke, 'copyStroke': False})
		
		cur_view_selection[newStroke] = {}
		newStroke.selected = True

		return newStroke

	def unjoinAllStrokes(self, args):
		if args.has_key('strokes'):
			strokes = args['strokes']
		else:
			return

		if args.has_key('joinedStroke'):
			joinedStroke = args['joinedStroke']
		else:
			return

		cur_char = self.__main_ctrl.get_current_char()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		
		cur_char.deleteStroke({'stroke': joinedStroke})
		joinedStroke.selected = False
		if cur_view_selection.has_key(joinedStroke):
			del cur_view_selection[joinedStroke]

		for sel_stroke in strokes.keys():
			cur_char.addStroke({'stroke': sel_stroke, 'copyStroke': False})
			cur_view_selection[sel_stroke] = {}
			sel_stroke.selected = True

	def joinAllStrokes(self, args):
		if args.has_key('strokes'):
			strokes = args['strokes']
		else:
			return

		if args.has_key('joinedStroke'):
			joinedStroke = args['joinedStroke']
		else:
			return

		cur_char = self.__main_ctrl.get_current_char()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]

		cur_char.addStroke({'stroke': joinedStroke, 'copyStroke': False})
		joinedStroke.selected = True
		cur_view_selection[joinedStroke] = {}

		for sel_stroke in strokes.keys():
			cur_char.deleteStroke({'stroke': sel_stroke})
			if cur_view_selection.has_key(sel_stroke):
				del cur_view_selection[sel_stroke]
			sel_stroke.selected = False

	def deleteControlVertices(self):
		ui = self.__main_ctrl.get_ui()
		cmd_stack = self.__main_ctrl.get_command_stack()
		cur_char = self.__main_ctrl.get_current_char()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]

		vertsBeforeList = []
		vertsAfterList = []

		for sel_stroke in cur_view_selection.keys():
			vertsBefore = sel_stroke.getCtrlVerticesAsList()

			for vertToDelete in cur_view_selection[sel_stroke]:
				sel_stroke.deleteCtrlVertex(vertToDelete)

			cur_view_selection[sel_stroke] = {}

			vertsAfter = sel_stroke.getCtrlVerticesAsList()

			vertsBeforeList.append(vertsBefore)
			vertsAfterList.append(vertsAfter)

		do_args = {
			'strokes' : cur_view_selection.keys(),
			'ctrlVerts' : vertsAfterList
		}

		undo_args = {
			'strokes' : cur_view_selection.keys(),
			'ctrlVerts' : vertsBeforeList
		}

		vertDeleteCmd = commands.Command("vertDeleteCmd")
		vertDeleteCmd.set_do_args(do_args)
		vertDeleteCmd.set_undo_args(undo_args)
		vertDeleteCmd.set_do_function(self.setStrokeControlVertices)
		vertDeleteCmd.set_undo_function(self.setStrokeControlVertices)

		cmd_stack.add_to_undo(vertDeleteCmd)
		cmd_stack.save_count += 1
		ui.editUndo.setEnabled(True)
		ui.repaint()

	def setStrokeControlVertices(self, args):
		ui = self.__main_ctrl.get_ui()

		if args.has_key('strokes'):
			sel_strokeList = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVertList = args['ctrlVerts']
		else:
			return

		if len(ctrlVertList) != len(sel_strokeList):
			return

		for i in range(0, len(sel_strokeList)):	
			sel_stroke = sel_strokeList[i]
			sel_stroke.setCtrlVerticesFromList(ctrlVertList[i])
			sel_stroke.calcCurvePoints()

		ui.repaint()

	def splitStroke(self, args):
		ui = self.__main_ctrl.get_ui()
		cur_char = self.__main_ctrl.get_current_char()

		if args.has_key('strokes'):
			sel_stroke = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVerts = args['ctrlVerts']
		else:
			return

		if args.has_key('newStroke'):
			newStroke = args['newStroke']
		else:
			return

		sel_stroke.setCtrlVerticesFromList(ctrlVerts)
		sel_stroke.calcCurvePoints()
		
		cur_char.addStroke({'stroke': newStroke, 'copyStroke': False})
		ui.repaint()

	def unsplitStroke(self, args):
		ui = self.__main_ctrl.get_ui()
		cur_char = self.__main_ctrl.get_current_char()

		if args.has_key('strokes'):
			sel_stroke = args['strokes']
		else:
			return

		if args.has_key('ctrlVerts'):
			ctrlVerts = args['ctrlVerts']
		else:
			return

		if args.has_key('strokeToDelete'):
			delStroke = args['strokeToDelete']
		else:
			return

		sel_stroke.setCtrlVerticesFromList(ctrlVerts)
		sel_stroke.calcCurvePoints()
		cur_char.deleteStroke({'stroke': delStroke})
		ui.repaint()

	def addControlPoint(self, sel_stroke, insideInfo):
		ui = self.__main_ctrl.get_ui()
		cmd_stack = self.__main_ctrl.get_command_stack()

		addVertexCmd = commands.Command('addVertexCmd')
						
		undo_args = {
			'strokes' : [sel_stroke],
			'ctrlVerts' : [sel_stroke.getCtrlVerticesAsList()]
		}

		sel_stroke.addCtrlVertex(insideInfo[2], insideInfo[1])
		
		do_args = {
			'strokes' : [sel_stroke],
			'ctrlVerts' : [sel_stroke.getCtrlVerticesAsList()]
		}

		addVertexCmd.set_do_args(do_args)
		addVertexCmd.set_undo_args(undo_args)
		addVertexCmd.set_do_function(self.setStrokeControlVertices)
		addVertexCmd.set_undo_function(self.setStrokeControlVertices)
		
		cmd_stack.add_to_undo(addVertexCmd)
		cmd_stack.save_count += 1
		ui.editUndo.setEnabled(True)

	def splitStrokeAtPoint(self, sel_stroke, insideInfo):
		ui = self.__main_ctrl.get_ui()
		cmd_stack = self.__main_ctrl.get_command_stack()

		splitAtCmd = commands.Command('splitAtCmd')
		vertsBefore = sel_stroke.getCtrlVerticesAsList()

		newVerts = sel_stroke.splitAtPoint(insideInfo[2], insideInfo[1])
		vertsAfter = sel_stroke.getCtrlVerticesAsList()

		newStroke = stroke.Stroke()
		newStroke.setCtrlVerticesFromList(newVerts)

		undo_args = {
			'strokes' : sel_stroke,
			'ctrlVerts' : vertsBefore,
			'strokeToDelete' : newStroke,
		}

		do_args = {
			'strokes' : sel_stroke,
			'newStroke' : newStroke,
			'ctrlVerts' : vertsAfter,
		}

		splitAtCmd.set_do_args(do_args)
		splitAtCmd.set_undo_args(undo_args)
		splitAtCmd.set_do_function(self.splitStroke)
		splitAtCmd.set_undo_function(self.unsplitStroke)
		
		cmd_stack.do_command(splitAtCmd)
		ui.editUndo.setEnabled(True)

	def addNewStroke(self):
		cur_char = self.__main_ctrl.get_current_char()
		current_view = self.__main_ctrl.get_current_view()
		selection = self.__main_ctrl.get_selection()
		cur_view_selection = selection[current_view]
		ui = self.__main_ctrl.get_ui()
		cmd_stack = self.__main_ctrl.get_command_stack()

		verts = self.__tmpStroke.getCtrlVerticesAsList()
		if len(verts) < 2:
			self.__main_ctrl.state = edit_control.IDLE
			self.__tmpStroke = None
			self.__strokePts = []
			current_view.strokesSpecial = []
			ui.repaint()
			return

		self.__main_ctrl.state = edit_control.IDLE
		self.__strokePts = []
		
		add_stroke_cmd = commands.Command('add_stroke_cmd')
		do_args = {
			'stroke' : self.__tmpStroke,
			'copyStroke' : False,
		}

		undo_args = {
			'stroke' : self.__tmpStroke,
		}

		add_stroke_cmd.set_do_args(do_args)
		add_stroke_cmd.set_undo_args(undo_args)
		add_stroke_cmd.set_do_function(cur_char.addStroke)
		add_stroke_cmd.set_undo_function(cur_char.deleteStroke)
		
		cmd_stack.do_command(add_stroke_cmd)
		ui.editUndo.setEnabled(True)

		cur_view_selection[self.__tmpStroke] = {}
		self.__tmpStroke.selected = True
		current_view.strokesSpecial = []
		self.__tmpStroke = None

		self.__main_ctrl.setUIStateSelection(True)
		
		for idx in range(0, ui.mainViewTabs.count()):
			ui.mainViewTabs.setTabEnabled(idx, True)
		
		ui.repaint()

	def moveSelected(self, args):
		if args.has_key('strokes'):
			selection = args['strokes']
		else:
			return

		if args.has_key('delta'):
			delta = args['delta']
		else:
			return

		snapPoint = None
		if args.has_key('snapPoint'):
			snapPoint = args['snapPoint']
		
		for stroke in selection.keys():
			if len(selection[stroke].keys()) > 0:
				for strokePt in selection[stroke].keys():
					strokePt.selectHandle(selection[stroke][strokePt])
					if snapPoint:
						strokePt.selectedHandlePos = snapPoint-stroke.pos
					else:
						strokePt.selectedHandlePos = strokePt.selectedHandlePos + delta
			else:
				stroke.pos += delta
			
			stroke.calcCurvePoints()

def distBetweenPts (p0, p1):
	return math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]))