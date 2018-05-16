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
			'attrNames' : attrName,
			'ctrlNames' : ctrlName,
			'objects' : objects
		}

		undoArgs = {
			'value' : prevValue,
			'attrNames' : attrName,
			'ctrlNames' : ctrlName,
			'objects' : objects
		}

		changeCmd = commands.command("change"+attrName[0]+"Cmd")

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

		if (args.has_key('attrNames')):
			attrNames = args['attrNames']
		else:
			return

		if (args.has_key('ctrlNames')):
			ctrlNames = args['ctrlNames']
		else:
			return

		if (args.has_key('objects')):	
			objectsToSet = args['objects']
		else:
			return

		useSameAttr = False
		if len(attrNames) == 1:
			useSameAttr = True

		for i in range(0, len(objectsToSet)):
			if useSameAttr:
				attrName = attrNames[0]
			else:
				attrName = attrNames[i]

			setattr(objectsToSet[i], attrName, val)
		
		ui = self.__mainCtrl.getUI()
		for ctrlName in ctrlNames:
			uiControl = getattr(ui, ctrlName)
			uiControl.setValue(val)
		
		ui.repaint()

	def baseHeightChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['baseHeight'], ['baseHeightSpin'])

	def capHeightChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['capHeight'], ['capHeightSpin'])
		
	def ascentChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['ascentHeight'], ['ascentHeightSpin'])
		
	def descentChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['descentHeight'], ['descentHeightSpin'])
		
	def gapHeightChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['gapHeight'], ['gapHeightSpin'])
		
	def angleChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['guideAngle'], ['angleSpin'])
		
	def nominalWidthChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['nominalWidth'], ['nominalWidthSpin'])

	def charSetNibAngleChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, ['nibAngle','angle'], ['charSetNibAngleSpin'])
		
	def charWidthChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'width', 'charWidthSpin')

	def charLeftSpaceChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'leftSpacing', 'charLeftSpaceSpin')

	def charRightSpaceChanged(self, prevValue, newValue, objects):
		self.__propChange(prevValue, newValue, objects, 'rightSpacing', 'charRightSpaceSpin')

