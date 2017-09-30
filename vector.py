from math import *
import random

class vector:
	def __init__(self, elements, unit=False): #NOFP
		self.elements 	= elements
		self.dim 		= len(elements)
		self.unit 		= unit

	def __len__(self):
		return len(self.elements)

	def __eq__(self, other):
		if (other == None):
			return False
		elif (type(other) == vector):
			if (other.dim == self.dim):
				return (self.elements == other.elements)
			else:
				raise Exception("Error: Inconsistent dimensions in '==' comparison between vectors.")
		elif (other == 0):
			return (abs(self) == other)
		else:
			raise Exception("Error: Unable to check equality between vector and non-vector.")

	def __bool__(self):
		return (abs(self) != 0)

	def __abs__(self):
		return self.getMag()

	def __add__(self, other):
		return self.add(other)

	def __sub__(self, other):
		return self.subtract(other)

	def __truediv__(self, other):
		if (type(other) == vector):
			x = self.isParallel(other)
			return (x if x else False)
		else:
			return self.multiply(1 / other)

	def __iadd__(self, other):
		self = self + other
		if self.unit:
			self = self.mag(1)
		return self

	def __isub__(self, other):
		self = self - other
		if self.unit:
			self = self.mag(1)
		return self

	def __neg__(self):
		return self.reverse()

	def __str__(self): #NOFP
		return ("<" + ", ".join([str(x) for x in self.elements]) + ">")

	# A better way of getting the string format of a vector, allows rounding of each element
	def string(self, rounding=None):
		if rounding:
			return ("<" + ", ".join([str(round(x, rounding)) for x in self]) + ">")
		else:
			return ("<" + ", ".join([str(x) for x in self.elements]) + ">")

	def __repr__(self): #NOFP
		return str(self)

	def __getitem__(self, value):
		return self.elements[value]

	def __mul__(self, value):
		if (type(value) in [int, float]):
			return self.multiply(value)
		elif (type(value) == vector):
			return self.cross(value)
		else:
			raise Exception("Invalid types for multiplying vector, must be vector and a scalar or vector")
			return 0

	def __rmul__(self, value):
		return self * value

	def __imul__(self, value):
		self = self * value
		# print("Warning, attempting to modify magnitude of a unit vector. (Changes won't be made to the vector)")
		if self.unit:
			self = self.mag(1)
		return self

	def __iter__(self):
		return self.elements.__iter__()



	def zero(self):
		self *= 0
		return self

	def define(self, other):
		self.elements	= other.elements
		self.dim 		= len(other.elements)
		self.unit 		= other.unit
		return True

	# Both pretty useless functions
	def elementWiseMultiply(self, other):
		return vector([self[i] * other[i] for i in range(self.dim)])

	def elementWiseDivide(self, other):
		return vector([self[i] / other[i] for i in range(self.dim)])

	# The only function that actually calculates the magnitude. Won't be called usually
	# but it can't be deprecated, abs() calls this!
	def getMag(self):
		mag = sum([x ** 2 for x in self.elements]) ** (1/2)
		return mag

	def isParallel(self, other):
		tempQuot = self.elementWiseDivide(other)
		factor = tempQuot[0]
		tempQuot = tempQuot / factor
		parallel = True
		if [x for x in tempQuot if x != 1]:
			return False
		else:
			return factor

	def mag(self, newMag=None):
		if (newMag == None):
			return abs(self)
		else:
			if (not self):
				return self
			else:
				return (self / abs(self)) * newMag

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



	# This is only useful if a completely new vector is needed with the same
	# dimensions as the old one. Most of the functions return new vectors anyway,
	# so this isn't a really necessary function. Maybe just for peace of mind
	# to avoid annoying pointer related behaviour
	def getClone(self):
		return vector(self.elements)

	# This has been more or less deprecated, to the function '.mag()'
	# which can both retrieve the magnitude or return a *new* vector
	# with a different magnitude
	# This will make a non-unit vector even if the original is a unit vector
	def setMag(self, mag):
		self.define(self / abs(self) * mag)
		return self

	def reverseToMe(self):
		self.define(self.reverse())
		return True

	def reverse(self):
		return self * (-1)

	def add(self, other, element=None):
		if (not element and (self.dim != other.dim)): return False
		tempVec = [x for x in self.elements]
		if element:
			tempVec[element] += other
		else:
			for i in range(self.dim):
				tempVec[i] = tempVec[i] + other.elements[i]
		return vector(tempVec)

	def subtract(self, other, element=None):
		# tempV = other.reverse()
		return self.add(other.reverse())

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

	# Rotates the vector about another vector, maintaining magnitude
	def rotateAbout(self, other, angle):
		selfParaOther = self.project(other)
		selfPerpOther = self - selfParaOther
		crossProd = self.cross(other)
		# crossProd = other.cross(self)
		X = cos(angle) / abs(selfPerpOther)
		Y = sin(angle) / abs(crossProd)
		result = (selfPerpOther * X + crossProd * Y) * abs(selfPerpOther) + selfParaOther
		return result


	# Projects self onto other
	def project(self, other):
		return other * (self.dot(other) / (abs(other) ** 2))

	# Projects self onto other, returns the magnitude of the projection
	def projectMag(self, other):
		return (self.dot(other) / abs(other))

	def relAngle(self, other, plane=None):
		# plane = None or the plane [axis1, axis2]
		if type(other) == int:
			# Gets the angle between the vector and an axis
			return acos(self[other] / abs(self))
		if not plane:
			# Gets the absolute angle between the two vectors
			cosTheta = self.dot(other) / (abs(self) * abs(other))
			if cosTheta > 1:
				cosTheta = 1
			elif cosTheta < -1:
				cosTheta = -1
			return acos(cosTheta)
		else:
			# Gets the relative angle in a particular plane
			angleSelf 	= self.lock(plane).getHeading(plane[0], trueBearing = plane[1])
			angleOther 	= other.lock(plane).getHeading(plane[0], trueBearing = plane[1])
			angle 		= angleSelf - angleOther
			return angle

	# Returns a vector with only the desired elements, the rest become 0
	def lock(self, elements, inverse=False):
		if elements == None:
			return self
		tempVec = vector([0 for x in self.elements])
		for x in enumerate(self.elements):
			if (x[0] in elements and inverse == False) or (inverse == True and x[0] not in elements):
				tempVec.elements[x[0]] = x[1]
		return tempVec

	# Makes the vector orthogonal to other. (?)
	def makeOrthogonal(self, other):
		return other.cross(self).cross(other).mag(abs(self))
		

def randomVector(dim, mag, maxMag=0, fixComponents=[1,1,1]):
	"""(dimensions, magnitude, maximum magnitude (defaults to magnitude),
	fixComponents: default [1,1,1]), multiplies each randomly generated component
	by the respective component in fixComponents, eg. [1,0,0] will limit the
	generated vector to the X-axis, where as [2, 1, 1] will give the vector
	more range along the X-axis than the other axes."""
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
