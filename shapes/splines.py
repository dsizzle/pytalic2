#!/usr/bin/python
#
# NURBS class definitions
#
# Dale Cieslak
#
import math

class baseCurve(object):
	'''
	base curve class
	'''
	def __init__(self):
		self.__ctrlVerts = []
		self.__curvePts = []
		self.__numVerts = 0
		self.__numCurvePts = 50
	
	def setCtrlVertices (self, verts=[]):
		'''
		sets all of the control vertices for the
		curve.
		
		inputs: 
		
		verts[] 
			array of vertex pairs or triples
		'''
		self.__ctrlVerts = verts
		self.__numVerts = len(verts) 
		
	def getCtrlVertices (self):
		'''
		returns list of control vertices for the
		curve.
		'''
		return self.__ctrlVerts
		
	ctrlVertices = property(getCtrlVertices, setCtrlVertices)

	def setNumCurvePoints (self, numPts):
		'''
		sets the number of points to use when
		calculating the curve.
		
		inputs:
		
		numPts
			number of points to calculate
		'''
		self.__numCurvePts = numPts
		
	def getNumCurvePoints (self):
		'''
		returns the number of points used to
		calculate the curve.
		'''
		return self.__numCurvePts
		
	numCurvePts = property(getNumCurvePoints, setNumCurvePoints)

	def getCurvePoints (self):
		'''
		return list of calculated curve points.
		'''
		return self.__curvePts
	
	def calcCurvePoints(self):
		'''
		calculate points on the curve
		'''
		return self.__curvePts
	
class nurbsCurve(baseCurve):
	'''
	class to calculate and represent a NURBS curve 
	in either 2 or 3 dimensions.
	
	knot vector, basis vector, and curve calculation
	based heavily on C code from An Introduction To NURBS
	by David F. Rogers, copyright 2000.  Used without 
	permission.
	'''
	def __init__(self, dimension=2, order=0):
		baseCurve.__init__(self)
		self.__order = order
		self.__ctrlWeights = []
		self.__dimension = dimension
		
	def setCtrlWeights (self, weights=[]):
		'''
		sets all of the control vertex weights
		for the curve.
		
		inputs:
		
		weights[]
			array of weights
		'''
		self.__ctrlWeights = weights
			
	def getCtrlWeights (self):
		'''
		returns list of control vertex weights
		for the curve.
		'''
		return self.__ctrlWeights
		
	ctrlWeights = property(getCtrlWeights, setCtrlWeights)

	def openKnotVec(self):
		knotVec = [0]
		
		knotVecSize = self.numVerts + self.__order
		
		for i in range(1, (knotVecSize)):
			if  (i > self.__order) and (i < (self.numVerts+2) ):
				knotVec.append(knotVec[i-1] + 1)
			else:
				knotVec.append(knotVec[i-1])
				
		return knotVec
		
	def periodicKnotVec(self):
		knotVecSize = self.numVerts + self.__order
		
		knotVec = []
		
		for i in range(1, (knotVecSize+1)):
			knotVec.append(i-1)
	
		return knotVec
	
	def calcBasisVector(self, t, knotVec):
		'''
		calculates the basis vector for specified time.
		
		inputs:
		
		t
			time to calculate.
			
		knotVec
			knot vector to use for calculation.
		'''
		temp = []
		knotVecSize = len(knotVec) #-1
		basisVec = []
		
		# calculate the first order nonrational basis functions 
		for i in range (0, knotVecSize):
		   	if (( t >= knotVec[i]) and (t < knotVec[i+1])):
				temp.append(1.0)
			else:
				temp.append(0.0)
		
		# calculate the higher order nonrational basis functions
		for k in range (1, self.__order):
			for i in range (0, (knotVecSize - k)):
				# if the lower order basis function is zero skip the calculation
				if (temp[i] == 0) or ((knotVec[i+k]-knotVec[i]) == 0) :
					d = 0.0
				elif (temp[i] != 0):
					d = ((t - knotVec[i]) * temp[i]) / (knotVec[i+k]-knotVec[i])
				
				if (temp[i+1] == 0) or ((knotVec[i+k]-knotVec[i+1]) == 0):
					e = 0.0
				elif not (temp[i+1] == 0):
					e = ((knotVec[i+k]-t) * temp[i+1]) / (knotVec[i+k]-knotVec[i+1])
				
				temp[i] = d + e
		
		if (t == knotVec[knotVecSize-1]):
		 	temp.append(1)
			
		# calculate sum for denominator of rational basis functions 
		sum = 0
		for i in range (0, self.__numVerts):
		    sum = sum + temp[i] * self.__ctrlWeights[i]
		
		# form rational basis functions and put in basis vector 
		for i in range (0, self.__numVerts):
		   	if not (sum == 0):
		   		basisVec.append((temp[i] * self.__ctrlWeights[i]) / (sum))
			else:
				basisVec.append(0)
				
		return basisVec
	
	def calcCurvePoints(self):
		'''
		calculate points for NURBS curve.
		'''
		knotVec = self.periodicKnotVec()
		
		lastKnot = knotVec[len(knotVec)-1]
		
		t = 0.0
		step = float(lastKnot)/(self.__numCurvePts)
		
		icount = 0
		
		self.curvePts = []
		for i in range (0, self.__numCurvePts):
			temp = []
			for j in range (0, self.__dimension):
				temp.append(0)
			self.curvePts.append(temp)
			
		for m in range (0, self.__numCurvePts):
			
			if (lastKnot - t < 5e-6):
				t = lastKnot
			
			basisVec = self.calcBasisVector(t, knotVec)
			
			for j in range (0, self.__dimension):
				self.curvePts[m][j] = 0.0
				for i in range (0, self.numVerts):
					temp = basisVec[i] * self.ctrlVerts[i][j]
					self.curvePts[m][j] += temp
					
			t += step
		
		tmpCurvePts = []
		nullPt = []
		
		for i in range (0, self.__dimension):
			nullPt.append(0.0)
		
		for pt in self.curvePts:
			if pt != nullPt:
				tmpCurvePts.append(pt)
			
		self.curvePts = tmpCurvePts
		
		return self.curvePts

		
class CardinalSpline(baseCurve):
	'''
	class to calculate and represent a Cardinal
	spline in either 2 or 3 dimensions.
	'''
	def __init__(self, dimension=2, alpha=1.0):
		baseCurve.__init__(self)
		self.__dimension = dimension
		self.__alpha = alpha
	
	def calcCurvePoints(self):
		'''
		calculate the points on the curve
		'''
		self.curvePts = []
		ptsPerSection = int(self.numCurvePts / self.numVerts)
		step = 1.0/ptsPerSection
		nullPt = []
		
		for ii in range (0, self.numCurvePts):
			temp = []
			for jj in range (0, self.__dimension):
				temp.append(0)
			self.curvePts.append(temp)		

		for i in range (0, self.__dimension):
			nullPt.append(0.0)
		
		m = 0
		for j in range (0, self.numVerts-1):
			t = 0.0
						
			p2 = self.ctrlVerts[j]
			
			try:
				p1 = self.ctrlVerts[j-1]
			except:
				p1 = p2
				
			try:
				p3 = self.ctrlVerts[j+1]
			except:
				p3 = p2
				
			try:
				p4 = self.ctrlVerts[j+2]
			except:
				p4 = p3
			
			while t	< 1.0:
				pt = nullPt
				
				t2 = t * t
				t3 = t2 * t
				t3x2 = t3+t3
				t2x3 = t2+t2+t2
				t2x2 = t2+t2
				
				# calculate basis function
				a = (t3x2) - (t2x3) + 1
				b = -(t3x2) + (t2x3)
				c = self.__alpha * (t3 - t2x2 + t)
				d = self.__alpha * (t3 - t2)
				
				for k in range (0, self.__dimension):
					self.curvePts[m][k] = a * p2[k] + b * p3[k] + c * (p3[k] - p1[k]) + d * (p4[k] - p2[k])
					
				t = t+step
				m = m+1
			
			
		tmpCurvePts = []
			
		for pt in self.curvePts:
			if pt != nullPt:
				tmpCurvePts.append(pt)
					
		self.curvePts = tmpCurvePts
		
		return self.curvePts
		
class CatmullRomSpline(CardinalSpline):
	def __init__(self, dimension=2, alpha=0.5):
		CardinalSpline.__init__(self, dimension, 0.5)
	
class TCBSpline(baseCurve):
	'''
	class to calculate and represent a TCB (or KB)
	spline in either 2 or 3 dimensions.
	'''
	def __init__(self, dimension=2, alpha=1.0):
		baseCurve.__init__(self)
		self.__dimension = dimension
		self.__tcbValues = []
	
	
	def setTcbValues (self, vals=[]):
			'''
			sets all of the control vertices for the
			curve.
			
			inputs: 
			
			verts[] 
				array of vertex pairs or triples
			'''
			self.__tcbValues = vals
			
	
	def calcCurvePoints(self):
		'''
		calculate the points on the curve
		'''
		self.curvePts = []
		
		ptsPerSection = int(self.numCurvePts / self.numVerts)
		step = 1.0/ptsPerSection
		nullPt = []
		
		for ii in range (0, self.numCurvePts):
			temp = []
			for jj in range (0, self.__dimension):
				temp.append(0)
			self.curvePts.append(temp)		
		
		for i in range (0, self.__dimension):
			nullPt.append(0.0)
		
		m = 0
		for j in range (0, self.numVerts-1):
			t = 0.0
						
			p2 = self.ctrlVerts[j]
			
			if ((j-1) < 0):
				p1 = p2
			else:
				p1 = self.ctrlVerts[j-1]
			
			if ((j+1) > (self.numVerts-1)):
				p3 = p2
			else:
				p3 = self.ctrlVerts[j+1]
				
			if ((j+2) > (self.numVerts-1)):
				p4 = p3
			else:
				p4 = self.ctrlVerts[j+2]
				
			[tt, cc, bb] = self.__tcbValues[j]
			[tt2, cc2, bb2] = self.__tcbValues[j+1]
			#print "[ "+str(tt)+", "+str(cc)+", "+str(bb)+"]"
			
			tcb1 = ((1.0-tt)*(1.0-cc)*(1.0+bb))/2.0
			tcb2 = ((1.0-tt2)*(1.0+cc2)*(1.0-bb2))/2.0
			tcb3 = ((1.0-tt)*(1.0+cc)*(1.0+bb))/2.0
			tcb4 = ((1.0-tt2)*(1.0-cc2)*(1.0-bb2))/2.0
				
			#print str(p1) + str(p2) + str(p3) + str(p4)
			while t	< 1.0:
				pt = nullPt
				
				t2 = t * t
				t3 = t2 * t
				t3x2 = t3+t3
				t2x3 = t2+t2+t2
				t2x2 = t2+t2
				
				# calculate basis function
				a = (t3x2) - (t2x3) + 1
				b = -(t3x2) + (t2x3)
				c = (t3 - t2x2 + t)
				d = (t3 - t2)
				
				for k in range (0, self.__dimension):
					
					tt1 = tcb1 * (p3[k]-p2[k]) + \
					     tcb2 * (p4[k]-p3[k])
					tt2 = tcb3 * (p2[k]-p1[k]) + \
					     tcb4 * (p3[k]-p2[k])
					self.__curvePts[m][k] = a * p2[k] + b * p3[k] + c * tt2 + d * tt1
					
				t = t+step
				m = m+1
		
			
		tmpCurvePts = []
			
		for pt in self.__curvePts:
			if pt != nullPt:
				tmpCurvePts.append(pt)
					
		self.curvePts = tmpCurvePts
		
		return self.curvePts
		

class BezierSpline(baseCurve):
	
	def __init__(self, dimension=2, alpha=1.0):
		baseCurve.__init__(self)
		self.__dimension = dimension
	
	def calcCtrlVertices(self, pts):
		'''
		calculate the control points from a set of given points
		'''
		ctrlPts = []
		p3 = [0, 0]
		
		for j in range(0, (len(pts)-3), 3):
			p0 = pts[j]
			p1 = pts[j+1]
			p2 = pts[j+2]
			p3 = pts[j+3]
		
			c1 = math.sqrt(((p1[0]-p0[0]) * (p1[0]-p0[0])) + ((p1[1]-p0[1]) * (p1[1]-p0[1])))
			c2 = math.sqrt(((p2[0]-p1[0]) * (p2[0]-p1[0])) + ((p2[1]-p1[1]) * (p2[1]-p1[1])))
			c3 = math.sqrt(((p3[0]-p2[0]) * (p3[0]-p2[0])) + ((p3[1]-p2[1]) * (p3[1]-p2[1])))
			
			cSum = c1 + c2 + c3
			
			if (cSum) != 0:
				t1 = c1 / (cSum)
				t2 = (c1 + c2) / (cSum)
			else:
				t1 = 0
				t2 = 0
				
			# b0 = (1-t)^3
			# 			b1 = 3t * (1-t)^2
			# 			b2 = 3t^2 * (1-t)
			# 			b3 = t^3
			 			
			b1t1 = (3 * t1) * ((1-t1) ** 2)
			b2t1 = (3 * (t1 ** 2)) * (1 - t1)
			b0t1 = (1-t1) ** 3
			b3t1 = t1 ** 3 
			b1t2 = (3 * t2) * ((1-t2) ** 2)
			b2t2 = (3 * (t2 ** 2)) * (1 - t2)
			b0t2 = (1-t2) ** 3
			b3t2 = t2 ** 3
			 
			x4 = (p1[0] * b1t1) + (p2[0] * b2t1) + (p0[0] * b0t1) + (p3[0] * b3t1)
			x5 = (p1[0] * b1t2) + (p2[0] * b2t2) + (p0[0] * b0t2) + (p3[0] * b3t2) 
			y4 = (p1[1] * b1t1) + (p2[1] * b2t1) + (p0[1] * b0t1) + (p3[1] * b3t1)
			y5 = (p1[1] * b1t2) + (p2[1] * b2t2) + (p0[1] * b0t2) + (p3[1] * b3t2) 
			
			ctrlPts.append(p0)
			ctrlPts.append([x4,y4])
			ctrlPts.append([x5,y5])
			#ctrlPts.add(p3)
			
			#x4 = x1B1(t1) + x2B2(t1) + x0B0(t1) + x3B3(t1)
			#x5 = x1B1(t2) + x2B2(t2) + x0B0(t2) + x3B3(t2)
		ctrlPts.append([x5,y5])
		ctrlPts.append(p3)
		
		l = len(ctrlPts)-1
		while ((l % 3) != 0):
			ctrlPts.pop()
			l = len(ctrlPts)-1
		
		for j in range(0, (len(ctrlPts))):
			if ((j % 3) == 0):
				if (j == 0):
					continue
				elif (j == (len(ctrlPts)-1)):
					continue
				else:
					pt1 = ctrlPts[j-1]
					mpt = ctrlPts[j]
					pt2 = ctrlPts[j+1]
					
					deltaX = pt2[0]-pt1[0]
					deltaY = pt2[1]-pt1[1]
					
					ctrlPts[j-1][0] = mpt[0]-deltaX/2
					ctrlPts[j-1][1] = mpt[1]-deltaY/2
					ctrlPts[j+1][0] = mpt[0]+deltaX/2
					ctrlPts[j+1][1] = mpt[1]+deltaY/2
					
					#ctrlPts[j-1] = mpt
					#ctrlPts[j+1] = mpt
		
		return ctrlPts[:]
		
	def calcCurvePoints(self):
	
		'''
		calculate the points on the curve
		'''
		self.curvePts[:] = []
		
		sections = (len(self.ctrlVerts) / 3) 
		ptsPerSection = int(self.numCurvePts / sections) 
		#ptsPerSection = 10
		
		step = float(1.0/(ptsPerSection)) 
		nullPt = []
		
		for i in range (0, self.__dimension):
			nullPt.append(0.0)
				
		for ii in range (0, self.numCurvePts+3):
			self.curvePts.append(nullPt[:])
			
		m = 0

		try:

			for j in range(0, self.numVerts-3, 3):
				t = 0.0
				
				p0 = self.ctrlVerts[j]
				p1 = self.ctrlVerts[j+1]
				p2 = self.ctrlVerts[j+2]
				p3 = self.ctrlVerts[j+3]
					
				while t <= (1.0-step):
					t2 = t * t
					t3 = t2 * t
					tx3 = t+t+t
					t2x3 = t2+t2+t2
					omt = 1.0 - t
					omt2 = omt * omt
					omt3 = omt2 * omt
					
					for k in range (0, self.__dimension):
						self.curvePts[m][k] = float(omt3 * p0[k]) + \
						                      float(tx3 * omt2 * p1[k]) + \
											  float(t2x3 * omt * p2[k]) + \
											  float(t3 * p3[k])
						
					t = t + step
					m = m + 1
			
				for k in range (0, self.__dimension):
					self.curvePts[m][k] = self.ctrlVerts[j+3][k]
				
				m = m+1
		except IndexError:
			pass

		while (self.curvePts[-1] == nullPt):
			self.curvePts.pop()
		
		return self.curvePts
		
	def calcCurvePoints_smoother(self):

		'''
		calculate the points on the curve
		'''
		self.curvePts = []
	
		print self.numCurvePts
		print self.ctrlVerts
		
		ptsPerSection = int(self.numCurvePts / len(self.ctrlVerts))
		#print ptsPerSection
		step = float(1.0/ptsPerSection)
		#print step
		
		nullPt = []
		omtPts = []
		tPts = []
		
		print len(self.ctrlVerts)
		print self.numVerts
			
		for i in range (0, self.__dimension):
			nullPt.append(0.0)
				
		for ii in range (0, self.numCurvePts+5):
			self.curvePts.append(nullPt[:])
	
		if (len(self.ctrlVerts) < 4):
			return self.curvePts
		else:
			self.curvePts = self.recursiveQuadBezierCurve(self.ctrlVerts, step)
			print self.curvePts
			
			return self.curvePts
	
	def recursiveQuadBezierCurve(self, ctrlVerts, step):
		curvePts = []
		
		if (len(ctrlVerts) == 4):
			curvePts = self.generateQuadBezierCurve(ctrlVerts, step)
		else:
			curvePts = []
			omtPts = self.recursiveQuadBezierCurve(ctrlVerts[0:-1], step)
			tPts = self.recursiveQuadBezierCurve(ctrlVerts[1:], step)
		
			t = 0.0
			for i in range(0, len(omtPts)):
				newPt = []
				for k in range(0, self.__dimension):
					omtPtNew = (1.0 - t) * omtPts[i][k]	
					tPtNew = t * tPts[i][k]
					
					newPt.append(omtPtNew+tPtNew)
				
				curvePts.append(newPt)
					
				t = t+step		
		
		return curvePts[:]
	
	def generateQuadBezierCurve(self, ctrlVerts, step):
		curvePts = []
		
		m = 0
		
		t = 0.0
		
		p0 = ctrlVerts[0]
		p1 = ctrlVerts[1]
		p2 = ctrlVerts[2]
		p3 = ctrlVerts[3]
		
		while t <= 1.0:
				
			t2 = t * t
			t3 = t2 * t
			tx3 = t+t+t
			t2x3 = t2+t2+t2
			omt = 1.0 - t
			omt2 = omt * omt
			omt3 = omt2 * omt
			
			curvePt = []
			for k in range (0, self.__dimension):
				curvePt.append(float(omt3 * p0[k]) + \
				               float(tx3 * omt2 * p1[k]) + \
							   float(t2x3 * omt * p2[k]) + \
							   float(t3 * p3[k]))
			curvePts.append(curvePt)
			
			t = t+step
			m = m+1
		
		print curvePts
		
		return curvePts[:]
