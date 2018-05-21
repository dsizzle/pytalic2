from model import commands, control_vertex

class vertex_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent

	def alignTangents(self, newBehavior):
		currentView = self.__mainCtrl.get_current_view()
		selection = self.__mainCtrl.get_selection()
		curViewSelection = selection[currentView]
		ui = self.__mainCtrl.get_ui()
		cmdStack = self.__mainCtrl.get_command_stack()

		if len(curViewSelection.values()) > 0:
			vertList = curViewSelection.values()
			
			doArgs = {
				'verts' : vertList,
				'behaviors' : [newBehavior]
			}

			behaviorList = []

			for vertDict in vertList:
				for vert in vertDict.keys():
					behaviorList.append(vert.getBehavior())

			undoArgs = {
				'verts' : vertList,
				'behaviors' : behaviorList 
			}

			alignTangentsSymCmd = commands.command("alignTangentsSymCmd")

			alignTangentsSymCmd.setDoArgs(doArgs)
			alignTangentsSymCmd.setUndoArgs(undoArgs)
			alignTangentsSymCmd.setDoFunction(self.setCtrlVertexBehavior)
			alignTangentsSymCmd.setUndoFunction(self.setCtrlVertexBehavior)

			cmdStack.doCommand(alignTangentsSymCmd)
			ui.editUndo.setEnabled(True)

			ui.repaint()

	def alignTangentsSymmetrical(self):
		self.alignTangents(control_vertex.SYMMETRIC)

	def alignTangentsSmooth(self):
		self.alignTangents(control_vertex.SMOOTH)

	def breakTangents(self):
		self.alignTangents(control_vertex.SHARP)

	def setCtrlVertexBehavior(self, args):
		ui = self.__mainCtrl.get_ui()
		
		if args.has_key('verts'):
			vertList = args['verts']
		else:
			return

		if args.has_key('behaviors'):
			behaviorList = args['behaviors']
		else:
			return

		if len(behaviorList) == 1:
			useSameBehavior = True
		else:
			useSameBehavior = False

		for vertDict in vertList:
			for i in range(0, len(vertDict.keys())):
				if useSameBehavior:
					vertDict.keys()[i].setBehavior(behaviorList[0])
					ui.behaviorCombo.setCurrentIndex(behaviorList[0])
				else:
					vertDict.keys()[i].setBehavior(behaviorList[i])
					ui.behaviorCombo.setCurrentIndex(0)