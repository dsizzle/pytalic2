class commandStack(object):
	def __init__(self):
		self.__undoStack = []
		self.__redoStack = []

	def clear(self):
		self.clearUndo()
		self.clearRedo()

	def clearUndo(self):
		self.__undoStack[:] = []

	def clearRedo(self):
		self.__redoStack[:] = []

	def undo(self):
		if len(self.__undoStack) > 0:
			lastCmd = self.__undoStack.pop()

			self.__redoStack.append(lastCmd)

			lastCmd.undoIt()

	def redo(self):
		if len(self.__redoStack) > 0:
			lastCmd = self.__redoStack.pop()

			self.__undoStack.append(lastCmd)

			lastCmd.doIt()

	def doCommand(self, newCmd):
		self.addToUndo(newCmd)

		newCmd.doIt()

	def addToUndo(self, newCmd):
		self.__undoStack.append(newCmd)
		self.clearRedo()

	def undoIsEmpty(self):
		return len(self.__undoStack) == 0


class command(object):
	def __init__(self):
		self.__doArgs = {}
		self.__doFunction = None

		self.__undoArgs = {}
		self.__undoFunction = None

		self.__description = ""

	def doIt(self):
		self.__doFunction(self.__doArgs)

	def undoIt(self):
		self.__undoFunction(self.__undoArgs)

	def setUndoArgs(self, newUndoArgs):
		self.__undoArgs = newUndoArgs

	def setDoArgs(self, newDoArgs):
		self.__doArgs = newDoArgs

	def setUndoFunction(self, undoFunction):
		self.__undoFunction = undoFunction

	def setDoFunction(self, doFunction):
		self.__doFunction = doFunction

	def setDescription(self, newDescription):
		self.__description = newDescription

	def getDescription(self):
		return self.__description

	description = property(getDescription, setDescription)