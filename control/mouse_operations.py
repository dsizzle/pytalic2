from PyQt4 import QtCore, QtGui

import edit_control
from model import commands

class mouse_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent
		self.__savedMousePosPaper = {}
		self.__moveDelta = QtCore.QPoint(0, 0)

	def mouseEvent(self, event):
		currentView = self.__mainCtrl.getCurrentView()

		if currentView.underMouse() or currentView.rect().contains(event.pos()):
			if event.type() == QtCore.QEvent.MouseButtonPress:
				self.mousePressEventPaper(event)
			elif event.type() == QtCore.QEvent.MouseButtonRelease:
				self.mouseReleaseEventPaper(event)
			else:
				self.mouseMoveEventPaper(event)

			event.accept()

	def wheelEvent(self, event):
		currentView = self.__mainCtrl.getCurrentView()
		ui = self.__mainCtrl.getUI()

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
		ui = self.__mainCtrl.getUI()
		
		cmdDown = mod & QtCore.Qt.ControlModifier
		altDown = mod & QtCore.Qt.AltModifier
		shiftDown = mod & QtCore.Qt.ShiftModifier

		leftDown = btn & QtCore.Qt.LeftButton
		rightDown = btn & QtCore.Qt.RightButton

		paperPos = event.pos() - ui.mainSplitter.pos() - ui.mainWidget.pos()
		paperPos.setY(paperPos.y() - ui.mainViewTabs.tabBar().height())

	def mouseReleaseEventPaper(self, event):
		btn = event.button()
		mod = event.modifiers()
		ui = self.__mainCtrl.getUI()

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
		self.__mainCtrl.setIcon()

	def mouseMoveEventPaper(self, event):
		btn = event.buttons()
		mod = event.modifiers()
		ui = self.__mainCtrl.getUI()
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
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
			
			snapControl = self.__mainCtrl.getSnapController()
			if snapControl.getSnap() > 0:
				currentView.snapPoints = snapControl.getSnappedPoints(normPaperPos)
				if len(currentView.snapPoints) > 0 and currentView.snapPoints[0] is not QtCore.QPoint(-1, -1):
					paperPos = currentView.snapPoints[0] + deltaPos
					
			delta = (paperPos - self.__savedMousePosPaper[currentView]) / currentView.scale
			self.__moveDelta += delta
			self.__savedMousePosPaper[currentView] = paperPos
			args = {
				'strokes' : curViewSelection,
				'delta' : delta,
			}
			self.__mainCtrl.moveSelected(args)
		elif leftDown and altDown and self.__mainCtrl.state == edit_control.IDLE:
			self.__savedMousePosPaper[currentView] = paperPos		
			self.__mainCtrl.state = edit_control.MOVING_PAPER
		elif leftDown and self.__mainCtrl.state == edit_control.IDLE:
			self.__mainCtrl.state = edit_control.DRAGGING
			self.__savedMousePosPaper[currentView] = paperPos
			self.__moveDelta = QtCore.QPoint(0, 0)

		ui.repaint()
		self.__mainCtrl.setIcon()

	def __onRButtonUpPaper(self):
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.getUI()
		cmdStack = self.__mainCtrl.getCommandStack()

		if self.__mainCtrl.state == edit_control.DRAWING_NEW_STROKE:
			strokeCtrl = self.__mainCtrl.getStrokeController()
			curChar = self.__mainCtrl.getCurrentChar()

			verts = strokeCtrl.tmpStroke.getCtrlVerticesAsList()
			if len(verts) == 0:
				self.__mainCtrl.state = edit_control.IDLE
				strokeCtrl.tmpStroke = None
				return

			self.__mainCtrl.state = edit_control.IDLE
			strokeCtrl.strokePts = []
			addStrokeCmd = commands.command('addStrokeCmd')
			doArgs = {
				'stroke' : strokeCtrl.tmpStroke,
				'copyStroke' : False,
			}

			undoArgs = {
				'stroke' : strokeCtrl.tmpStroke,
			}

			addStrokeCmd.setDoArgs(doArgs)
			addStrokeCmd.setUndoArgs(undoArgs)
			addStrokeCmd.setDoFunction(curChar.addStroke)
			addStrokeCmd.setUndoFunction(curChar.deleteStroke)
			
			cmdStack.doCommand(addStrokeCmd)
			ui.editUndo.setEnabled(True)

			curViewSelection[strokeCtrl.tmpStroke] = {}
			strokeCtrl.tmpStroke.selected = True
			currentView.strokesSpecial = []
			strokeCtrl.tmpStroke = None

			self.__mainCtrl.setUIStateSelection(True)
			
			for idx in range(0, ui.mainViewTabs.count()):
				ui.mainViewTabs.setTabEnabled(idx, True)
			
			ui.repaint()

	def __onLButtonUpPaper(self, pos, shiftDown):
		currentView = self.__mainCtrl.getCurrentView()
		selection = self.__mainCtrl.getSelection()
		curViewSelection = selection[currentView]

		ui = self.__mainCtrl.getUI()
		strokeCtrl = self.__mainCtrl.getStrokeController()
		cmdStack = self.__mainCtrl.getCommandStack()

		adjustedPos = pos - ui.mainSplitter.pos() - ui.mainWidget.pos()
		adjustedPos.setY(adjustedPos.y() - ui.mainViewTabs.tabBar().height())

		paperPos = currentView.getNormalizedPosition(adjustedPos)
		
		currentView.snapPoints = []
		if self.__mainCtrl.state == edit_control.DRAWING_NEW_STROKE:
			strokeCtrl.strokePts.append([paperPos.x(), paperPos.y()])
			strokeCtrl.tmpStroke.generateCtrlVerticesFromPoints(strokeCtrl.strokePts)
			strokeCtrl.tmpStroke.updateCtrlVertices()

		elif self.__mainCtrl.state == edit_control.DRAGGING:
			moveCmd = commands.command('moveStrokeCmd')
			selectionCopy = curViewSelection.copy()
			doArgs = {
				'strokes' : selectionCopy, 
				'delta' : self.__moveDelta,
			}

			undoArgs = {
				'strokes' : selectionCopy,
				'delta' : QtCore.QPoint(0, 0) - self.__moveDelta,
			}

			moveCmd.setDoArgs(doArgs)
			moveCmd.setUndoArgs(undoArgs)
			moveCmd.setDoFunction(self.__mainCtrl.moveSelected)
			moveCmd.setUndoFunction(self.__mainCtrl.moveSelected)
		
			cmdStack.addToUndo(moveCmd)
			cmdStack.saveCount += 1
			ui.editUndo.setEnabled(True)

			self.__mainCtrl.state = edit_control.IDLE
			self.__moveDelta = QtCore.QPoint(0, 0)
		elif self.__mainCtrl.state == edit_control.ADDING_CTRL_POINT:
			if len(curViewSelection.keys()) > 0:
				for selStroke in curViewSelection.keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
						addVertexCmd = commands.command('addVertexCmd')
						
						undoArgs = {
							'strokes' : selStroke,
							'ctrlVerts' : selStroke.getCtrlVerticesAsList()
						}

						selStroke.addCtrlVertex(insideInfo[2], insideInfo[1])
						
						doArgs = {
							'strokes' : selStroke,
							'ctrlVerts' : selStroke.getCtrlVerticesAsList()
						}

						addVertexCmd.setDoArgs(doArgs)
						addVertexCmd.setUndoArgs(undoArgs)
						addVertexCmd.setDoFunction(self.setStrokeControlVertices)
						addVertexCmd.setUndoFunction(self.setStrokeControlVertices)
						
						cmdStack.addToUndo(addVertexCmd)
						cmdStack.saveCount += 1
						ui.editUndo.setEnabled(True)
						break

			self.__mainCtrl.state = edit_control.IDLE
		elif self.__mainCtrl.state == edit_control.SPLIT_AT_POINT:
			if len(curViewSelection.keys()) > 0:
				for selStroke in curViewSelection.keys():
					insideInfo = selStroke.insideStroke(paperPos)
					if insideInfo[1] >= 0:
						splitAtCmd = commands.command('splitAtCmd')
						vertsBefore = selStroke.getCtrlVerticesAsList()

						newVerts = selStroke.splitAtPoint(insideInfo[2], insideInfo[1])
						vertsAfter = selStroke.getCtrlVerticesAsList()

						newStroke = stroke.Stroke()
						newStroke.setCtrlVerticesFromList(newVerts)

						undoArgs = {
							'strokes' : selStroke,
							'ctrlVerts' : vertsBefore,
							'strokeToDelete' : newStroke,
						}

						doArgs = {
							'strokes' : selStroke,
							'newStroke' : newStroke,
							'ctrlVerts' : vertsAfter,
						}

						splitAtCmd.setDoArgs(doArgs)
						splitAtCmd.setUndoArgs(undoArgs)
						splitAtCmd.setDoFunction(self.splitStroke)
						splitAtCmd.setUndoFunction(self.unsplitStroke)
						
						cmdStack.doCommand(splitAtCmd)
						ui.editUndo.setEnabled(True)
						break

			self.__mainCtrl.state = edit_control.IDLE
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