class stroke_controller():
	def __init__(self, parent):
		self.__mainCtrl = parent
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