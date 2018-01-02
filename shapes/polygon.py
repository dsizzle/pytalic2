class Quad():
	def __init__(self, pts=[]):
		self.pts = pts
		
		# must be at least 3 pts or else it's not a poly
		if len(self.pts < 4):
			self.pts = []
		
		self.windPoly(self.pts)
		
	def windPoly(self, pts):
		rx1, ry1 = (pts[0][0], pts[0][1])
		rx2, ry2 = (pts[0][0], pts[0][1])
		
def calcPoly(x, y, widthX, widthY, x2=None,y2=None):
	rx1, ry1 = (x-widthX, y+widthY)
	rx2, ry2 = (x+widthX, y-widthY)
	if (x2 == None):
		x2 = x
	if (y2 == None):
		y2 = y
	rx3, ry3 = (x2+widthX, y2-widthY)
	rx4, ry4 = (x2-widthX, y2+widthY)

	# make sure winding order is correct...if not, flip it.
	if (__isLeft([rx1, ry1],[rx3, ry3], [rx2, ry2]) > 0) and \
	   (__isLeft([rx1, ry1],[rx3, ry3], [rx4, ry4]) < 0):
		   (rx1, rx2, rx3, rx4) = (rx1, rx4, rx3, rx2)
		   (ry1, ry2, ry3, ry4) = (ry1, ry4, ry3, ry2)

	return [[int(rx1), int(ry1)],[int(rx2), int(ry2)], [int(rx3), int(ry3)], [int(rx4), int(ry4)]]
			

def normalizePolyRotation(pts):
	(rx1, ry1) = (pts[0][0], pts[0][1])
	(rx2, ry2) = (pts[1][0], pts[1][1])
	(rx3, ry3) = (pts[2][0], pts[2][1])
	(rx4, ry4) = (pts[3][0], pts[3][1])

	# rotate so rx1, ry1 is always "top-left"
	count = 0
	while (count < 4):
		if (rx1 <= rx3) and (rx1 <= rx4) and (rx1 <= rx2) and (ry1 > ry2):
			break
		else:
			(rx1, rx2, rx3, rx4) = (rx2, rx3, rx4, rx1)
			(ry1, ry2, ry3, ry4) = (ry2, ry3, ry4, ry1)
			count += 1
	
	return [[rx1, ry1], [rx2, ry2], [rx3, ry3], [rx4, ry4]]		

def getCentroid(pts, normalize=False):	
	if normalize:
		normPts = normalizePolyRotation(pts)
	else:
		normPts = pts

	xList, yList = zip(*pts)
	
	maxX = max(xList)
	maxY = max(yList)
	minX = min(xList)
	minY = min(yList)

	return [ minX+((maxX-minX)/2), minY+((maxY-minY)/2)]
	
def __isLeft(pt0, pt1, pt2):
			
		return ((pt1[0] - pt0[0]) * (pt2[1] - pt0[1]) - \
		        (pt2[0] - pt0[0]) * (pt1[1] - pt0[1]))
		        
def windingNum(pt, polyPts, numVerts):
		wn = 0
		y = pt[1]
		
		for i in range(0, numVerts):
			p1 = polyPts[i]
			p1y = p1[1]
			
			try:
				p2 = polyPts[i+1]
			except:
				p2 = polyPts[0]
			
			p2y = p2[1]
			
			if p1y <= y:
				
				if p2y > y:
					if (__isLeft(p1, p2, pt) > 0):
						wn = wn + 1
			else:
				if p2y <= y:
					if (__isLeft(p1, p2, pt) < 0):
						wn = wn - 1
						
		return wn
		    
