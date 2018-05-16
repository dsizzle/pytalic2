import character
import random
import pickle

class character_set(object):
	def __init__(self):
		self.__characters = {}
		self.__currentChar = None

		self.__nominalWidthNibs = 4.0
		self.__baseHeightNibs = 5.0
		self.__ascentHeightNibs = 3.0
		self.__descentHeightNibs = 3.0
		self.__capHeightNibs = 2.0
		self.__gapHeightNibs = 1.0
		self.__guideAngle = 5
		self.__nibAngle = 40

		self.__savedStrokes = []

	def newCharacter(self, charCode):
		myChar = character.Character()
		self.__characters[charCode] = myChar
		self.__currentChar = charCode
		
	def deleteChar(self, charToDelete):
		try:
			self.__characters[charToDelete] = None
		except:
			print "ERROR: character to delete doesn't exist!"
	
	def getCurrentChar(self):
		if self.__currentChar is not None:
			return self.__characters[self.__currentChar]
		else:
			return None
		
	def setCurrentChar(self, char):
		if (self.__characters.has_key(char)):
			self.__currentChar = char
		else:
			self.newCharacter(char)

	currentChar = property(getCurrentChar, setCurrentChar)

	def getCurrentCharName(self):
		return unichr(self.__currentChar)
	
	def getCurrentCharIndex(self):
		return self.__currentChar
	
	def getChar(self, char):
		if (self.__characters.has_key(char)):
			return self.__characters[char]
		else:
			return None
		
	def getCharList(self, sorted=True):
		return self.__characters
		
	def getSavedStrokes(self):
		return self.__savedStrokes

	def saveStroke(self, item):
		self.__savedStrokes.append(item)

	def getSavedStroke(self, idx):
		if len(self.__savedStrokes) > idx:
			return self.__savedStrokes[idx]
		else:
			return None

	def setSavedStroke(self, idx, stroke):
		if len(self.__savedStrokes) < idx:
			return 

		tmpStroke = self.__savedStrokes[idx]
		self.__savedStrokes[idx] = stroke
		del(tmpStroke)

	def removeSavedStroke(self, item):
		self.__savedStrokes.remove(item)

	def setNominalWidth(self, newWidth):
		self.__nominalWidthNibs = newWidth

	def getNominalWidth(self):
		return self.__nominalWidthNibs

	nominalWidthNibs = property(getNominalWidth, setNominalWidth)

	def setBaseHeight(self, newBaseHeight):
		self.__baseHeightNibs = newBaseHeight

	def getBaseHeight(self):
		return self.__baseHeightNibs

	baseHeight = property(getBaseHeight, setBaseHeight)

	def setAscentHeight(self, newAscentHeight):
		self.__ascentHeightNibs = newAscentHeight

	def getAscentHeight(self):
		return self.__ascentHeightNibs

	ascentHeight = property(getAscentHeight, setAscentHeight)

	def setDescentHeight(self, newDescentHeight):
		self.__descentHeightNibs = newDescentHeight

	def getDescentHeight(self):
		return self.__descentHeightNibs

	descentHeight = property(getDescentHeight, setDescentHeight)

	def setCapHeight(self, newCapHeight):
		self.__capHeightNibs = newCapHeight

	def getCapHeight(self):
		return self.__capHeightNibs

	capHeight = property(getCapHeight, setCapHeight)

	def setGapHeight(self, newGapHeight):
		self.__gapHeightNibs = newGapHeight

	def getGapHeight(self):
		return self.__gapHeightNibs

	gapHeight = property(getGapHeight, setGapHeight)

	def setGuideAngle(self, newAngle):
		self.__guideAngle = newAngle

	def getGuideAngle(self):
		return self.__guideAngle

	guideAngle = property(getGuideAngle, setGuideAngle)

	def setNominalWidth(self, newWidth):
		self.__nominalWidthNibs = newWidth

	def getNominalWidth(self):
		return self.__nominalWidthNibs

	nominalWidth = property(getNominalWidth, setNominalWidth)

	def setNibAngle(self, newAngle):
		self.__nibAngle = newAngle

	def getNibAngle(self):
		return self.__nibAngle

	nibAngle = property(getNibAngle, setNibAngle)