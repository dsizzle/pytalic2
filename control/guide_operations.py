from model import commands

class guide_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent

	def __guidePropChange(self, prevValue, newValue, objects, attrName, ctrlName):
		if newValue == prevValue:
			return

		cmdStack = self.__mainCtrl.getCommandStack()
		ui = self.__mainCtrl.getUI()

		doArgs = {
			'value' : newValue,
			'attrName' : attrName,
			'ctrlName' : ctrlName,
			'objects' : objects
		}

		undoArgs = {
			'value' : prevValue,
			'attrName' : attrName,
			'ctrlName' : ctrlName,
			'objects' : objects
		}

		changeCmd = commands.command("change"+attrName+"Cmd")

		changeCmd.setDoArgs(doArgs)
		changeCmd.setUndoArgs(undoArgs)
		changeCmd.setDoFunction(self.__mainCtrl.changePropertyControl)
		changeCmd.setUndoFunction(self.__mainCtrl.changePropertyControl)

		cmdStack.doCommand(changeCmd)
		ui.editUndo.setEnabled(True)

		ui.repaint()
		
	def baseHeightChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'baseHeight', 'baseHeightSpin')

	def capHeightChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'capHeight', 'capHeightSpin')
		
	def ascentChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'ascentHeight', 'ascentHeightSpin')
		
	def descentChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'descentHeight', 'descentHeightSpin')
		
	def gapHeightChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'gapHeight', 'gapHeightSpin')
		
	def angleChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'angle', 'angleSpin')
		
	def nominalWidthChanged(self, prevValue, newValue, objects):
		self.__guidePropChange(prevValue, newValue, objects, 'nominalWidth', 'nominalWidthSpin')
		