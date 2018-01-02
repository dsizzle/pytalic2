#import character
import random
import pickle

class character_set(object):
	def __init__(self):
		self.__characters = {}
		self.__currentChar = None
		self.__savedStrokes = []

	def newCharacter(self, charCode):
		myChar = None #character.Character()
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
