from model import commands

class property_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent

	def __propChange(self, prevValue, newValue, objects, attrName, ctrlName):
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
		changeCmd.setDoFunction(self.changePropertyControl)
		changeCmd.setUndoFunction(self.changePropertyControl)

		cmdStack.doCommand(changeCmd)
		ui.editUndo.setEnabled(True)

		ui.repaint()
	
	def changePropertyControl(self, args):
		if (args.has_key('value')):
			val = args['value']
		else:
			return

		if (args.has_key('attrName')):
			attrName = args['attrName']
		else:
			return

		if (args.has_key('ctrlName')):
			ctrlName = args['ctrlName']
		else:
			return

		if (args.has_key('objects')):
			objectsToSet = args['objects']
		else:
			return

		for objectName in objectsToSet:
			setattr(objectName, attrName, val)
		
		ui = self.__mainCtrl.getUI()
		uiControl = getattr(ui, ctrlName)
		uiControl.setValue(val)
		
		ui.repaint()

	def baseHeightChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'baseHeight', 'baseHeightSpin')

	def capHeightChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'capHeight', 'capHeightSpin')
		
	def ascentChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'ascentHeight', 'ascentHeightSpin')
		
	def descentChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'descentHeight', 'descentHeightSpin')
		
	def gapHeightChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'gapHeight', 'gapHeightSpin')
		
	def angleChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'angle', 'angleSpin')
		
	def nominalWidthChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'nominalWidth', 'nominalWidthSpin')
		
	def charWidthChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'width', 'charWidthSpin')

	def charLeftSpaceChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'leftSpacing', 'charLeftSpaceSpin')

	def charRightSpaceChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'rightSpacing', 'charRightSpaceSpin')

