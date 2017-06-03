from math import *
import random

class vector:
	def __init__(self, elements):
		self.elements = elements
		self.dim = len(elements)
		# self.type = "c" #,'c' --> cartesian, 'p' --> polar

	def __len__(self):
		return len(self.elements)

	def __abs__(self):
		return self.getMag()

	def __add__(self, other):
		return self.add(other)

	def __sub__(self, other):
		return self.subtract(other)

	def __truediv__(self, other):
		return self.multiply(1 / other)

	def __iadd__(self, other):
		self = self + other
		return self

	def __isub__(self, other):
		self = self - other
		return self

	def __neg__(self):
		return self.reverse()

	def __str__(self):
		return ("<" + ", ".join([str(x) for x in self.elements]) + ">")

	def string(self, rounding=None):
		if rounding:
			return ("<" + ", ".join([str(round(x, rounding)) for x in self]) + ">")
		else:
			return ("<" + ", ".join([str(x) for x in self.elements]) + ">")


	def __repr__(self):
		return self.elements

	def __getitem__(self, value):
		return self.elements[value]

	def __mul__(self, value):
		if (type(value) in [int, float]):
			return self.multiply(value)
		else:
			raise Exception("Invalid types for multiplying vector, must be <vector> and a scalar")
			return 0

	def __rmul__(self, value):
		return self * value

	def __imul__(self, value):
		self = self * value
		return self

	def __iter__(self):
		return self.elements.__iter__()

	def define(self, other):
		self.elements = other.elements
		self.dim = len(other.elements)
		return True

	def elementWiseMultiply(self, other):
		return vector([self[i] * other[i] for i, x in enumerate(self)])

	def getMag(self):
		mag = sum([x ** 2 for x in self.elements]) ** (1/2)
		return mag

	def getHeading(self, axis=0, aCos=True, trueBearing=None, lock=None):
		# true bearing: an angle will be given in the direction of the axis trueBearing
		# Uses dot product; cos(angle) = a . b / |a||b|
		angle = False
		if self.lock(lock).getMag() == 0:
			return 0 # Mag of 0 has no angle
		angle = (self.elements[axis])/self.lock(lock).getMag()
		if aCos:
			angle = acos(angle) # Sometimes cos(angle) is all thats needed, this is an attempt to save some processing time
			if trueBearing:
				if self.elements[trueBearing] < 0:
					angle = -angle

		return angle

	def setHeading(self, angle, plane = [0, 1], increment=False):
		# plane --> plane of the angle. default XY plane, wil change only x and y values.
		# Not the same angles as getHeading!, angle must be within (-pi, pi]
		if (len(self) not in [2, 3]): print("Warning: setHeading used on vector of dimension {}, not 2 or 3.".format(len(self)))

		if (type(plane) == int):
			radius = self.getMag()
			if increment:
				initialAngle = self.relAngle(plane)
			else:
				initialAngle = 0
			if (initialAngle + angle > pi or initialAngle + angle < 0):
				self.reverseToMe()
			self.elements[plane] = radius * cos(initialAngle + angle)
		else:
			radius = self.lock(plane).getMag()
			if increment:
				initialAngle = self.getHeading(axis = plane[0], trueBearing = plane[1], lock = plane)
			else:
				initialAngle = 0
			self.elements[plane[0]] = radius * cos(angle + initialAngle)
			self.elements[plane[1]] = radius * sin(angle + initialAngle)



	def getClone(self):
		# This is pretty useless
		return vector(self.elements)

	def setMag(self, mag):
		self.define(self / abs(self) * mag)
		return self

	# For most of the following functions (add, subtract etc.) there is a respective 'functionToMe',
	# The only difference is that the original function returns a new vector without changing any other vector.
	# functionToMe will change the original vector.
	# eg. a.add(b) --> c = (a + b), a.addToMe(b) --> a = (a + b)
	# There might be a better way to do this than have seperate functions?

	def reverseToMe(self):
		self.define(self.reverse())
		return True

	def reverse(self):
		return vector([-x for x in self.elements])

	# def addToMe(self, other, element=None):
	# 	self.define(self.add(other, element))
	# 	return True

	def add(self, other, element=None):
		if (not element and (self.dim != other.dim)): return False
		tempVec = [x for x in self.elements]
		if element:
			tempVec[element] += other
		else:
			for i in range(self.dim):
				tempVec[i] = tempVec[i] + other.elements[i]
		return vector(tempVec)

	# def subtractToMe(self, other):
	# 	self.define(self.subtract(other))
	# 	return True

	def subtract(self, other, element=None):
		# tempV = other.reverse()
		return self.add(other.reverse())

	# def multiplyToMe(self, scalar):
	# 	self.define(self.multiply(scalar))
	# 	return True

	def multiply(self, scalar):
		return vector([x * scalar for x in self.elements])

	def cross(self, other):
		if (len(self) != 3 or len(other) != 3):
			print("Unable to do cross product on size {} and {} vectors".format(len(self), len(other)))
			return None
		return vector([
			self[1] * other[2] - self[2] * other[1],
			self[2] * other[0] - self[0] * other[2],
			self[0] * other[1] - self[1] * other[0]
		])

	def dot(self, other):
		product = 0
		if self.dim != other.dim: return False
		for i in range(self.dim):
			product += self.elements[i] * other.elements[i]
		return product

	def rotateAbout(self, other, angle):
		selfParaOther = self.project(other)
		selfPerpOther = self - selfParaOther
		crossProd = self.cross(other)
		X = cos(angle) / abs(selfPerpOther)
		Y = sin(angle) / abs(crossProd)
		result = (selfPerpOther * X + crossProd * Y) * abs(selfPerpOther) + selfParaOther
		return result


	def project(self, other):
		# Projects self onto other
		return other * (self.dot(other) / (abs(other) ** 2))

	def projectMag(self, other):
		# Projects self onto other
		return (self.dot(other) / abs(other))

	def relAngle(self, other, plane=None):
		# plane = None or the plane [axis1, axis2]
		if type(other) == int:
			return acos(self[other] / abs(self))
		if not plane:
			cosTheta = self.dot(other) / (abs(self) * abs(other))
			if cosTheta > 1:
				cosTheta = 1
			elif cosTheta < -1:
				cosTheta = -1
			return acos(cosTheta)
		else:
			angleSelf 	= self.lock(plane).getHeading(plane[0], trueBearing = plane[1])
			angleOther 	= other.lock(plane).getHeading(plane[0], trueBearing = plane[1])
			angle 		= angleSelf - angleOther
			return angle

	def lock(self, elements, inverse=False):
		if elements == None:
			return self
		tempVec = vector([0 for x in self.elements])
		for x in enumerate(self.elements):
			if (x[0] in elements and inverse == False) or (inverse == True and x[0] not in elements):
				tempVec.elements[x[0]] = x[1]
		return tempVec

	def makeOrthogonal(self, other, element=2):
		"""element --> index of the array of elements, default 2
		Maintains magnitude"""
		initialMag = self.getMag()
		if self.dim != other.dim: return False
		result = 0
		if other.elements[element] == 0:
			while other.elements[element] == 0:
				element = (element + 1) % self.dim
		for i in range(self.dim):
			if i != element:
				result += self.elements[i] * other.elements[i]
		result = -(result / other.elements[element])
		self.elements[element] = result
		self.setMag(initialMag)
		return True

def randomVector(dim, mag, maxMag=0, fixComponents=[1,1,1]):
	"""dimensions, magnitude, maximum magnitude (defaults to magnitude),
	fixComponents: default [1,1,1], multiplies each randomly generated component
	by the respective component in fixComponents, eg. [1,0,0] will limit the
	generated vector to the X-axis."""
	if dim != len(fixComponents) and fixComponents != [1,1,1]: return False
	tempVec = []
	X = (random.random() - 1/2) * 2 * fixComponents[0]
	for i in range(dim):
		tempVec.append((random.random() - 1/2) * 2 * fixComponents[i])
	if maxMag == 0:
		endMag = mag
	else:
		endMag = random.random() * abs(maxMag - mag) + mag
	return vector(tempVec).setMag(endMag)
