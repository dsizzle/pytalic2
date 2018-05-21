from PyQt4 import QtCore, QtGui

import edit_control
from model import commands

class mouse_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent
		self.__savedMousePosPaper = {}
		self.__moveDelta = QtCore.QPoint(0, 0)

	def mouseEvent(self, event):
		currentView = self.__mainCtrl.get_current_view()

		if currentView.underMouse() or currentView.rect().contains(event.pos()):
			if event.type() == QtCore.QEvent.MouseButtonPress:
				self.mousePressEventPaper(event)
			elif event.type() == QtCore.QEvent.MouseButtonRelease:
				self.mouseReleaseEventPaper(event)
			else:
				self.mouseMoveEventPaper(event)

			event.accept()

	def wheelEvent(self, event):
		currentView = self.__mainCtrl.get_current_view()
		ui = self.__mainCtrl.get_ui()

		if currentView.underMouse() or currentView.rect().contains(event.pos()):
			scaleChange = 0
			if event.delta() > 0:
				scaleChange = -0.02
			else:
				scaleChange = 0.02

			currentView.scale += scaleChange
			
			paperPos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
			paperPos.setY(paperPos.y() - ui.mainViewTabs.tabBar().height())
			zoomPos = (paperPos - currentView.getOrigin()) * scaleChange

			currentView.originDelta -= zoomPos
			self.__savedMousePosPaper[currentView] = paperPos

			event.accept()
			ui.repaint()

	def mousePressEventPaper(self, event):
		btn = event.buttons()
		mod = event.modifiers()
		ui = self.__mainCtrl.get_ui()
		
		cmdDown = mod & QtCore.Qt.ControlModifier
		altDown = mod & QtCore.Qt.AltModifier
		shiftDown = mod & QtCore.Qt.ShiftModifier

		leftDown = btn & QtCore.Qt.LeftButton
		rightDown = btn & QtCore.Qt.RightButton

		paperPos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
		paperPos.setY(paperPos.y() - ui.mainViewTabs.tabBar().height())

	def mouseReleaseEventPaper(self, event):
		currentView = self.__mainCtrl.get_current_view()
		
		btn = event.button()
		mod = event.modifiers()
		ui = self.__mainCtrl.get_ui()

		cmdDown = mod & QtCore.Qt.ControlModifier
		altDown = mod & QtCore.Qt.AltModifier
		shiftDown = mod & QtCore.Qt.ShiftModifier

		leftUp = btn & QtCore.Qt.LeftButton
		rightUp = btn & QtCore.Qt.RightButton

		if self.__mainCtrl.state == edit_control.MOVING_PAPER and leftUp:
			self.__mainCtrl.state = edit_control.IDLE
		else:
			if rightUp:
				self.__onRButtonUpPaper()
			elif leftUp:
				self.__onLButtonUpPaper(event.pos(), shiftDown)
				
		ui.repaint()
		if currentView != ui.previewArea:
			self.__mainCtrl.setIcon()

	def mouseMoveEventPaper(self, event):
		btn = event.buttons()
		mod = event.modifiers()
		ui = self.__mainCtrl.get_ui()
		currentView = self.__mainCtrl.get_current_view()
		selection = self.__mainCtrl.get_selection()
		curViewSelection = selection[currentView]

		leftDown = btn & QtCore.Qt.LeftButton
		rightDown = btn & QtCore.Qt.RightButton

		altDown = mod & QtCore.Qt.AltModifier

		paperPos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
		paperPos.setY(paperPos.y() - ui.mainViewTabs.tabBar().height())
		
		if self.__mainCtrl.state == edit_control.MOVING_PAPER:
			delta = paperPos - self.__savedMousePosPaper[currentView]
			currentView.originDelta += delta
			self.__savedMousePosPaper[currentView] = paperPos
		elif self.__mainCtrl.state == edit_control.DRAGGING:
			normPaperPos = currentView.getNormalizedPosition(paperPos) 
			deltaPos = paperPos - normPaperPos
			
			snapControl = self.__mainCtrl.get_snap_controller()
			strokeCtrl = self.__mainCtrl.get_stroke_controller()
			if snapControl.getSnap() > 0:
				currentView.snapPoints = snapControl.getSnappedPoints(normPaperPos)
			else:
				currentView.snapPoints = []
					
			delta = (paperPos - self.__savedMousePosPaper[currentView]) / currentView.scale
			self.__moveDelta += delta
			self.__savedMousePosPaper[currentView] = paperPos
			args = {
				'strokes' : curViewSelection,
				'delta' : delta,
			}

			if len(currentView.snapPoints) > 0:
				args['snapPoint'] = currentView.snapPoints[0]

			strokeCtrl.moveSelected(args)
		elif leftDown and altDown and self.__mainCtrl.state == edit_control.IDLE:
			self.__savedMousePosPaper[currentView] = paperPos		
			self.__mainCtrl.state = edit_control.MOVING_PAPER
		elif leftDown and self.__mainCtrl.state == edit_control.IDLE:
			self.__mainCtrl.state = edit_control.DRAGGING
			self.__savedMousePosPaper[currentView] = paperPos
			self.__moveDelta = QtCore.QPoint(0, 0)

		ui.repaint()
		if currentView != ui.previewArea:
			self.__mainCtrl.setIcon()

	def __onRButtonUpPaper(self):
		currentView = self.__mainCtrl.get_current_view()
		selection = self.__mainCtrl.get_selection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.get_ui()
		cmdStack = self.__mainCtrl.get_command_stack()

		if self.__mainCtrl.state == edit_control.DRAWING_NEW_STROKE:
			strokeCtrl = self.__mainCtrl.get_stroke_controller()
			strokeCtrl.addNewStroke()
			QtGui.qApp.restoreOverrideCursor()

	def __onLButtonUpPaper(self, pos, shiftDown):
		currentView = self.__mainCtrl.get_current_view()
		selection = self.__mainCtrl.get_selection()
		curViewSelection = selection[currentView]

		ui = self.__mainCtrl.get_ui()
		strokeCtrl = self.__mainCtrl.get_stroke_controller()
		cmdStack = self.__mainCtrl.get_command_stack()

		adjustedPos = pos - ui.mainSplitter.pos() - ui.mainWidget.pos()
		adjustedPos.setY(adjustedPos.y() - ui.mainViewTabs.tabBar().height())

		paperPos = currentView.getNormalizedPosition(adjustedPos)
		
		currentView.snapPoints = []
		if self.__mainCtrl.state == edit_control.DRAWING_NEW_STROKE:
			strokeCtrl.strokePts.append([paperPos.x(), paperPos.y()])
			strokeCtrl.tmpStroke.generateCtrlVerticesFromPoints(strokeCtrl.strokePts)
			strokeCtrl.tmpStroke.updateCtrlVertices()

		elif self.__mainCtrl.state == edit_control.DRAGGING:
			move_cmd = commands.Command('move_stroke_cmd')
			selection_copy = curViewSelection.copy()
			do_args = {
				'strokes' : selection_copy, 
				'delta' : self.__moveDelta,
			}

			undo_args = {
				'strokes' : selection_copy,
				'delta' : QtCore.QPoint(0, 0) - self.__moveDelta,
			}

			move_cmd.set_do_args(do_args)
			move_cmd.set_undo_args(undo_args)
			move_cmd.set_do_function(strokeCtrl.moveSelected)
			move_cmd.set_undo_function(strokeCtrl.moveSelected)
		
			cmdStack.add_to_undo(move_cmd)
			cmdStack.save_count += 1
			ui.editUndo.setEnabled(True)

			self.__mainCtrl.state = edit_control.IDLE
			self.__moveDelta = QtCore.QPoint(0, 0)
		elif self.__mainCtrl.state == edit_control.ADDING_CTRL_POINT:
			if len(curViewSelection.keys()) > 0:
				for selStroke in curViewSelection.keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
						strokeCtrl.addControlPoint(selStroke, insideInfo)
						break

			self.__mainCtrl.state = edit_control.IDLE
			QtGui.qApp.restoreOverrideCursor()
		elif self.__mainCtrl.state == edit_control.SPLIT_AT_POINT:
			if len(curViewSelection.keys()) > 0:
				for selStroke in curViewSelection.keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
						strokeCtrl.splitStrokeAtPoint(selStroke, insideInfo)
						break

			self.__mainCtrl.state = edit_control.IDLE
			QtGui.qApp.restoreOverrideCursor()
		else:
			if len(curViewSelection.keys()) > 0:
				for selStroke in curViewSelection.keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
						ctrlVertexNum = int((insideInfo[1]+1) / 3)
						ctrlVert = selStroke.getCtrlVertex(ctrlVertexNum)
						
						handleIndex = (insideInfo[1]+1) % 3 +1
						if not shiftDown:
							selStroke.deselectCtrlVerts()
							curViewSelection[selStroke] = {}

						curViewSelection[selStroke][ctrlVert] = handleIndex

						for ctrlVert in curViewSelection[selStroke].keys():
							ctrlVert.selectHandle(curViewSelection[selStroke][ctrlVert])

						selStroke.selected = True
						
					else:
						if shiftDown:
							if not curViewSelection.has_key(selStroke):
								curViewSelection[selStroke] = {}
								selStroke.deselectCtrlVerts()

							selStroke.selected = True
						else:
							if curViewSelection.has_key(selStroke):
								del curViewSelection[selStroke]

							selStroke.selected = False
							selStroke.deselectCtrlVerts()

				vertList = curViewSelection.values()
				behaviorList = []
				
				for vertDict in vertList:
					for vert in vertDict.keys():
						behaviorList.append(vert.getBehavior())

				behaviorList = list(set(behaviorList))
				if len(behaviorList) == 1:
					ui.behaviorCombo.setCurrentIndex(behaviorList[0])
				else:
					ui.behaviorCombo.setCurrentIndex(0)

			if len(curViewSelection.keys()) == 0 or shiftDown:
				for selStroke in currentView.strokes:
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[0] == True and (len(curViewSelection.keys()) == 0 or shiftDown):
						if not curViewSelection.has_key(selStroke):
							curViewSelection[selStroke] = {}	
							selStroke.deselectCtrlVerts()

						selStroke.selected = True	
					elif not shiftDown:
						selStroke.selected = False
						selStroke.deselectCtrlVerts()

			if len(curViewSelection.keys()) > 0:
				self.__mainCtrl.setUIStateSelection(True)
			else:
				self.__mainCtrl.setUIStateSelection(False)
				ui.behaviorCombo.setCurrentIndex(0)