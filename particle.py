from vector import *
from math import *
import numpy as np
import random

particleList  = []
staticList    = []
nonStaticList = []
orderedList   = []
idxList = np.array([], dtype=int)

markerList   = []

defaultDensity = 1
radiusLimit    = 250

ALL_IMMUNE	   = False
voidRadius 	   = 5000
CAMERA_UNTRACK_IF_DIE = True
USE_NUMPY      = True

# G = 6.67408e-11
G = 1

TestMode = False
R_POWER = 2 # For N-power force function, force is GMm/(r^n)

particlePosList = None
particleMassList = np.array([])
particleRadiusList = np.array([])
pListMap = {}

### FORCE FUNCTIONS
# Example generic force function, given 2 particles A and B
# returns the force vector acting on A
def gravitationalForce(particleA, particleB):
	mag = G * particleA.mass * particleB.mass / abs(particleA.pos - particleB.pos)**2
	vec = mag * unit(particleB.pos - particleA.pos)
	return vec

## Returns net force on a particle, and the absolute distance
# to all other particles as an array
def gravitationalForceL(selfMass, massList, distList):
	# Ignore 0/0 division errors
	with np.errstate(invalid='ignore'):
		distAbs = np.linalg.norm(distList, 2, axis=1)
		forces = G * massList * selfMass / (distAbs ** 3)

		# print(distList)
		# print(forces)
		# forces = np.multiply(distList, forces)

		ret = (distList.T * forces).T
		# print("ret:",ret)
		# print("ret.T:", ret.T)
		ret = -np.nansum(ret.T, axis=1).T
		# print("ret:",ret)
		# exit()
		return ret, distAbs

def cubicForce(particleA, particleB):
	mag = G * particleA.mass * particleB.mass / abs(particleA.pos - particleB.pos)**3
	vec = mag * unit(particleB.pos - particleA.pos)
	return vec

def nPowerForce(particleA, particleB):
	mag = G * particleA.mass * particleB.mass / abs(particleA.pos - particleB.pos)**R_POWER
	vec = mag * unit(particleB.pos - particleA.pos)
	return vec


### CIRCULARISE FUNCTIONS
# def gravitationalCircularise(particleA, particleB):





class particle:
	def __init__(
			self, mass=None, position=0, velocity=0, acceleration=0,
			density=defaultDensity, autoColour=True, colour=[0, 0, 1],
			limitRadius=True, name=None, static=False, immune=False,
			radius=None, respawn=True):
		global particlePosList
		global particleMassList
		global particleRadiusList
		global idxList
		global pListMap
		massProv = mass != None
		densityProv = density != defaultDensity
		radiusProv = radius != None
		# print([massProv, densityProv, radiusProv].count(True), "values given")
		if [massProv, radiusProv].count(True) < 1:
			print("Error: particle/__init__(): Atleast mass or radius must be provided")
			exit()
		else:
			# If either mass or radius is provided, then the other is calculated
			# If mass and radius are provided, density is ignored and recalculated
			#   regardless of if it was also provided as an argument. If density
			#   is provided along with mass and radius then a warning is given
			if not radiusProv:
				self.mass = mass
				self.density = density
				self.radius = (3 * abs(mass)/(4 * pi * abs(density)))**(1/3)
			elif not massProv:
				self.radius = radius
				self.density = density
				self.mass = abs(density) * (4/3 * pi) * radius**3
			else:
				self.density = abs(mass) / (4/3 * pi * radius**3)
				self.mass = mass
				self.radius = radius
				if (densityProv): print("Warning: particle/__init__(): radius, mass and density provided, density will be ignored and re-calculated.")


		self.pos = position
		self.limitRadius = limitRadius
		self.name = name
		self.static = static
		self.system = [] # If this is not empty, then the particle will only feel force from the bodies in this list
		self.info = {}

		dims = [x.dim for x in [position, velocity, acceleration] if type(x) == vector]
		if dims:
			# A vector value is given
			if (max(dims) == min(dims)):
				# All dims are equal
				self.dim = dims[0]
			else:
				print("Error: particle/__init__(): Inconsistent dimensions of position, velocity and acceleration")
				exit()
		else:
			print("Error: particle/__init__(): No vector quantity provided in position, velocity or acceleration.")
			exit()

		if position == 0:
			self.pos = vector(0, dim = self.dim)
		elif (type(position) == vector):
			self.pos = position
		else:
			print("Error: particle/__init__(): Non zero scalar provided where vector or zero scalar expected for position")

		if velocity == 0:
			self.vel = vector(0, dim = self.dim)
		elif (type(velocity) == vector):
			self.vel = velocity
		else:
			print("Error: particle/__init__(): Non zero scalar provided where vector or zero scalar expected for velocity")

		if acceleration == 0:
			self.acc = vector(0, dim = self.dim)
		elif (type(acceleration) == vector):
			self.acc = acceleration
		else:
			print("Error: particle/__init__(): Non zero scalar provided where vector or zero scalar expected for acceleration")

		self.colour = [0, 0, 0]
		self.autoColour = autoColour
		self.immune = immune
		if not autoColour:
			self.setColour(colour)
		else:
			self.setColour()
		particleList.append(self)
		orderedList.append(self)
		if static:
			staticList.append(self)
		else:
			nonStaticList.append(self)

		# Add this particle to the relevant lists/arrays
		if (len(pListMap) == 0):
			particlePosList  = np.zeros([0, 3])
			particlePosList  = np.append(particlePosList, self.pos.elements)
		else:
			particlePosList  = np.append(particlePosList, self.pos.elements)

		particleMassList = np.append(particleMassList, self.mass)
		particleRadiusList = np.append(particleRadiusList, self.radius)
		particlePosList = particlePosList.reshape([len(particleMassList), 3])
		pListMap[self] = len(particlePosList) - 1
		# The position of this particle in the pos/mass/radius lists
		# also holds the position of its index in idxList,
		# an index which will forever hold the index of this particle
		# in the orderedList.
		idxList = np.append(idxList, pListMap[self])

		# Record the collisions detected after a single step, if
		# they aren't checked straight away.
		self.collisions = []

		self._respawn = respawn

	alive = True
	specialColour = False
	forceFunc = gravitationalForce
	forceFuncList = gravitationalForceL

	inbound = False

	newMass = False # the mass of the particle after it respawns
	# colour parameter only used if autoColour is off
	def idx(self):
		if (self not in particleList):
			# The particle does not exist in the simulation.
			return None
		idx = pListMap[self]
		# if (particleList[idx] != self):


		return idx

	def delete(self):
		# print("deleting:", self)
		global particleList
		global particlePosList
		global particleMassList
		global particleRadiusList
		global orderedList
		global pListMap
		global idxList
		# print("Initial idxList:", idxList)
		# print("Initial Map:", pListMap)
		self.alive = False
		idx = self.idx()
		if (idx == None): return # the particle has already been deleted.
		particleList.remove(self)
		particlePosList = np.delete(particlePosList, idx, axis=0)
		particleMassList = np.delete(particleMassList, idx)
		particleRadiusList = np.delete(particleRadiusList, idx)
		idxList = np.delete(idxList, idx)
		mask = idxList > idx
		mask = np.ones(mask.size, dtype=int) * mask
		idxList -= mask
		orderedList.remove(self)
		for i in idxList:
			p = orderedList[i]
			pListMap[p] = i
		# orderedList.remove(self)
		# print("Final Map:", pListMap)
		# print("Final idxList:", idxList)


	def __getattr__(self, attr):
		if (attr in self.info):
			return self.info[attr]
		else:
			return None
	def setColour(self, colour=None):
		if self.autoColour:
			self.colour = [min(self.radius/radiusLimit, 1), 0, min(1, (0 if (radiusLimit < self.radius) else (radiusLimit - self.radius)/radiusLimit))]
		elif colour:
			self.colour = colour
		else:
			return False

	def setRadius(self, newRadius=None):
		if (newRadius == None):
			self.radius = (0.75 * (abs(self.mass)/self.density) / pi) ** (1/3)
		else:
			self.radius = newRadius
			self.mass = (4 * newRadius**3 * self.density * pi) / 3
		self.setColour()


	def calcAcc(self, other, returnResult=False):
		if (self.pos == other.pos): return None
		forceVector = particle.forceFunc(self, other)
		# force = abs(forceVector)
		if (not returnResult):
			self.acc += (forceVector / self.mass)
		else:
			return (forceVector / self.mass)

	def checkCollision(self, other):
		if other.alive and (self.mass > 0) and (abs(self.pos.subtract(other.pos)) < self.radius + other.radius):
			# print("    {} contesting with {}".format(self.idx(), other.idx()))
			self.contest(other)
			return True
		else:
			# print("    Ignoring collision between {} and {}".format(self.idx(), other.idx()))
			# print("    Their altitude is: {}".format(abs(other.pos - self.pos) - self.radius - other.radius))
			return False

	def runLoop(self):
		if USE_NUMPY:
			global particleMassList

			self.collisions = [] # Clear the collision list

			# if not self.system:
			pList = particlePosList
			mList = particleMassList
			try:
				mList[pListMap[self]] = 0
			except IndexError:
				print("Error: particle's index is invalid")
				print("self:", self, "\nidx:", self.idx(), "\nalive:", self.alive)
				exit()
			dist =  np.array(self.pos) - pList
			# distAbs = np.linalg.norm(dist, 2, axis)

			# Use 1 instead of actual mass to get acceleration instead of Force
			force, distAbs = particle.forceFuncList(1, mList, dist)
			alt = distAbs - (particleRadiusList + self.radius)
			collisions = alt < 0
			collisions[self.idx()] = False
			# print(particleMassList[collisions])
			badAlts = alt[alt < 0]
			idxs = []
			if (collisions.any()):
				idxs = idxList[collisions]
				# print("Collisions:", self.idx(), [[x,y] for x, y in zip(idxs, badAlts)])
				[self.collisions.append(orderedList[x]) for x in idxs]
			self.acc += vector(force.tolist())
			# print(force)
			if not self.system:
				mList[pListMap[self]] = self.mass
		else:

			for p in particleList:
			# 	altDiff = self.radius + p.radius
			# 	missedCollisions = []
				if p == self: continue
		# 	if (abs(p.pos - self.pos) - altDiff) < 0:
		# 		if p.idx() not in idxs:
		# 			missedCollisions.append(p.idx())
		# 	if missedCollisions:
		# 		print("Missed collisions with {}: ".format(self.idx()), missedCollisions)
		# else:
			# print("No collisions")

		# acc = force / self.mass
		# print(force)
		# print("force", force)

		# exit()
		# print(force)
		# exit()
		# else:
		# 	posList = np.zeros([len(self.system), self.pos.dim])
		# 	massList = np.array(len(self.system))
		# 	for i, p in enumerate(self.system):
		# 		if not self.checkCollision(p) and p.alive:
		# 			massList[i] = p.mass
		# 			posList[i] = p.pos.elements
		# 			self.calcAcc(p)


	def checkOutOfBounds(self, camera): #bounds=[turtle.window_width()/2, turtle.window_height()/2]):
		if self.immune or ALL_IMMUNE or TestMode or camera == None: return False
		out = False
		if abs(self.pos.subtract(camera.pos)) > voidRadius:
			out = True
		# print("Checking")
		if out and not self.inbound:
			if self._respawn:
				self.respawn()
			else:
				self.die()
		elif not out and self.inbound:
			self.inbound = False


	def respawn(self):
		# print("Name:", self.name)
		# newMass --> determines the mass of the particle after respawning
		# bounds = [turtle.window_width()/2, turtle.window_height()/2]
		radius = voidRadius #sqrt(bounds[0] ** 2 + bounds[1] ** 2) # radius of circle encompassing corners of canvas
		self.pos = randomVector(3, radius * 0.99)
		self.vel = randomVector(3, 5, 15).subtract(self.pos.getClone().setMag(30))
		if not self.newMass: self.mass = random.random() * 2000 + 500
		if self.newMass: self.mass = self.newMass
		self.setRadius()
		# self.inbound = True
		# print("Respawning to: {}".format([self.pos.elements[0], self.pos.elements[1], self.pos.elements[2]]))

	def die(self, killer=None):
		# print("%s dying to %s" % (self.name, killer.name))
		global particleList
		if self._respawn:
			# if CAMERA_UNTRACK_IF_DIE and camera.panTrack == self:
			# 	camera.panTrackSet(killer)
			self.respawn()
		else:
			# self.respawn()
			# if killer:
				# print("{} dying from {}".format(self.idx(), killer.idx()))
			# else:
				# print("{} dying from no one.".format(self.idx()))
			try:
				if camera.panTrack: camera.panTrackSet()
				if buffer != 0:
					BUFFER[self].append(False)
			except NameError:
				pass
			self.delete()
			# if self in particleList:
			# 	particleList.remove(self)
			# if self in nonStaticList: nonStaticList.remove(self)
			# if self in staticList: staticList.remove(self)
			# self.alive = False

	def contest(self, other):
		CoM = (other.pos * other.mass + self.pos * self.mass) / (self.mass + other.mass)
		if self.mass >= other.mass:
			self.vel = (self.vel.multiply(self.mass).add(other.vel.multiply(other.mass))).multiply(1/(self.mass + other.mass))
			self.mass += other.mass
			# Using (mv)_1 + (mv)_2 = (m_1 + m_2)v:
			self.setRadius()
			self.pos = CoM
			other.die(self)
		else:
			other.vel = (self.vel.multiply(self.mass).add(other.vel.multiply(other.mass))).multiply(1/(self.mass + other.mass))
			other.mass += self.mass
			other.setRadius()
			other.pos = CoM
			self.die(other)

	def step(self, delta, camera=None):
		global particlePosList
		global particleMassList
		global particleRadiusList
		if self.static:
			self.pos += self.vel * delta# + self.acc * (delta**2 / 2)
			return False

		# oldAcc = self.acc.getClone()
		oldmass = self.mass
		oldradius = self.radius
		self.acc = vector([0, 0, 0])
		self.runLoop()
		if abs(self.radius) > radiusLimit and self.limitRadius:
			self.die()
			return False

		self.vel += self.acc * delta
		self.pos += self.vel * delta
		idx = self.idx()
		# print(particlePosList)
		particlePosList[idx] = self.pos.elements
		if self.mass != oldmass:
			particleMassList[idx] = self.mass
		if self.radius != oldradius:
			particleRadiusList[idx] = self.radius



		self.checkOutOfBounds(camera)

		return True

	def circularise(self, other, plane = None, axis=None, binary=False):
		# If axis is supplied, the resulting orbit is in the direction of the
		#   cross product of the displacement vector from the body to parent and the axis
		# If binary is true, then each body will be placed in an orbit around the centre of mass
		#   and the final velocity of the pair will be equal to the velocity of self
		if other == self:
			return False
		if binary:
			reducedMass = self.mass * other.mass / (self.mass + other.mass)
			fullMass = self.mass + other.mass
		# 	centreOfMass = (self.pos + other.pos) / (self.mass + other.mass)
		# 	oldOther = other
		# 	other = [self.mass + other.mass, centreOfMass, self.vel.getClone()]
		if type(other) == list:
			# Can specify a mass at a position instead of a particle
			# Parse as [mass, position, vel=(0-vector)]
			mass = other[0]
			position = other[1]
			if (len(other) > 2):
				otherVel = other[2]
			else:
				otherVel = vector([0, 0, 0])
		else:
			mass = other.mass
			position = other.pos
			otherVel = other.vel.getClone()

		# if inclination == "r":
		#     inclination = random.random() * 360 - 180
		fullDist = abs(self.pos - position)
		if binary:
			# speed = speed * (self.mass / reducedMass)
			speed = mass * sqrt(G / (fullDist * fullMass))
		else:
			speed = sqrt(G * mass / fullDist)
		vel = randomVector(3, 1)
		if (axis == None):
			vel.makeOrthogonal(position - self.pos)
			if plane: vel = vel.lock(plane)#[vel.elements[i] * plane[i] for i in range(len(vel.elements))]
		else:
			vel = axis.cross(position - self.pos)
		self.vel = vel.mag(speed) + otherVel
		if binary:
			# altSpeed = (mass / reducedMass) * sqrt(G / (self.mass * fullDist))
			altSpeed = self.mass * sqrt(G / (fullDist * fullMass))
			other.vel = -vel.mag(altSpeed) + otherVel
		return True

		# if type(other) == particle:


class marker(particle):
	def __init__(self, position, colour, radius = 20):
		self.pos = position
		self.colour = colour
		self.radius = radius
		self.static = True
		staticList.append(self)
		markerList.append(self)
	def set_colour(self, colour):
		self.colour = colour

	def step(self, delta):
		pass
