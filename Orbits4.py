from tkinter import *
from math import *

LINUX = False # If true, then non alphanumeric key controls will be replaced with numbers


defaultDensity = 1

particleList = []

INITIAL_WINDOW_WIDTH = 500
INITIAL_WINDOW_HEIGHT = 600

DEFAULT_ZERO_VEC = [0, 0, 0]
DEFAULT_UNIT_VEC = [1, 0, 0]

master = Tk()
screen = Canvas(master, width = INITIAL_WINDOW_WIDTH, height = INITIAL_WINDOW_HEIGHT)
screen.pack()
canvas_width = INITIAL_WINDOW_WIDTH
canvas_height = INITIAL_WINDOW_HEIGHT

def setup():
    a = particle(1, vector([25, 1, 0]))
    camera.drawParticle(a)

def drawDot(x, y, r, fill = "black"):
    screenWidth = screen.winfo_width()
    screenHeight = screen.winfo_height()
    x += screenWidth/2
    y = screenHeight/2 - y
    id = screen.create_oval(x - r, y - r, x + r, y + r, fill = fill, outline = fill)
    return id

def drawOval(x1, y1, x2, y2, fill = "black"):
    screenWidth = screen.winfo_width()
    screenHeight = screen.winfo_height()
    x1, x2 = x1 + screenWidth/2, x2 + screenWidth/2
    y1, y2 = screenHeight/2 - y1, screenHeight/2 - y2

    id = screen.create_oval(x1, y1, x2, y2, fill = fill, outline = fill)
    return id

def drawLine(x2, y2 = (0, 0), x1 = 0, y1 = 0, fill = "black", width = 1):
    if type(x2) == tuple or type(x2) == list:
        # 1 or 2 points should have been provided
        screen.create_line(x2[0], x2[1], y2[0], y2[1], fill = fill, width = width)
    else:
        # x and y should be numbers.
        screen.create_line(x1, y1, x2, y2)

BUFFER = {}

class buffer:
    def __init__(self):
        self.allshift = DEFAULT_ZERO_VEC
        self.allrotate = DEFAULT_ZERO_VEC
        self.buffer = {}
        self.bufferMode = 0 # 0: Normal. 1: Recording, sim paused. 2: Playing.
        self.bufferLength = 0
        for p in particleList:
            self.buffer[p] = []

        def getBuffer(self, particle, index = -1, remove = None):
            if self.bufferLength > 0:
                result = self.buffer[particle][index]
                if remove != None: self.buffer[particle].pop(remove)
                return result
            else:
                return False

        def addBuffer(self, particle, position, radius, colour = None):
            self.buffer[particle].append([position, radius])



class MainLoop:
    def __init__(self):
        # Records the movements to all particles
        self.commonShift = DEFAULT_ZERO_VEC
        self.commonRotate = DEFAULT_ZERO_VEC

    def changeCommonShift(self, vectorShift):
        self.commonShift.addToMe(vectorShift)
        return self.commonShift

    def changeCommonRotate(self, vectorRotate):
        self.commonRotate.addToMe(vectorRotate)
        return self.commonRotate


    def STEP(self, delta, draw = True):
        # I think it would be slightly more effecient to only do an if comparison once,
        # even if means a few lines are duplicated.
        if self.bufferMode == 2:
            # Playing from buffer
            for p in particleList:
                pass
        if draw:
            if self.bufferMode == 0:
                # normal, and draw
                for p in particleList:
                    p.step(delta)
                    p.pos.addToMe(self.commonShift)
            else:
                # recording
                for p in particleList:
                    p.step(delta)


        else:
            for p in particleList:
                p.step(delta)


class vector:
    def __init__(self, elements):
        self.elements = elements
        self.dim = len(elements)
        # self.type = "c" #,'c' --> cartesian, 'p' --> polar

    def __abs__(self):
        return self.getMag()

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.subtract(other)

    def __iadd__(self, other):
        self.addToMe(other)
        return self

    def __isub__(self, other):
        self.subtractToMe(other)
        return self

    def __neg__(self):
        return self.reverse()

    def define(self, other):
        self.elements = other.elements
        self.dim = len(other.elements)
        return True

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

        initialAngle = self.getHeading(axis = plane[0], trueBearing = plane[1], lock = plane)
        # print(initialAngle)
        radius = self.lock(plane).getMag()
        # print(radius)
        if increment:
            self.elements[plane[0]] = radius * cos(angle + initialAngle)
            self.elements[plane[1]] = radius * sin(angle + initialAngle)
        else:
            self.elements[plane[0]] = radius * cos(initialAngle)
            self.elements[plane[1]] = radius * sin(initialAngle)


    def getClone(self):
        # This is pretty useless
        return vector(self.elements)

    def setMag(self, mag):
        #angles = [self.getHeading(i, False) for i in range(self.dim)] # a list of the cos of the angles between the vector and each axis
        #self.elements = [mag * angles[k] for k in range(self.dim)] # trig
        self.multiplyToMe(mag / self.getMag())
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

    def addToMe(self, other, element=None):
        self.define(self.add(other, element))
        return True

    def add(self, other, element=None):
        if (not element and (self.dim != other.dim)): return False
        tempVec = [x for x in self.elements]
        if element:
            tempVec[element] += other
        else:
            for i in range(self.dim):
                tempVec[i] = tempVec[i] + other.elements[i]
        return vector(tempVec)

    def subtractToMe(self, other):
        self.define(self.subtract(other))
        return True

    def subtract(self, other, element=None):
        # tempV = other.reverse()
        return self.add(other.reverse())

    def multiplyToMe(self, scalar):
        self.define(self.multiply(scalar))
        return True

    def multiply(self, scalar):
        return vector([x * scalar for x in self.elements])

    def dot(self, other):
        product = 0
        if self.dim != other.dim: return False
        for i in range(self.dim):
            product += self.elements[i] * other.elements[i]
        return product

    def relAngle(self, other, plane=None):
        # plane = None or the plane [axis1, axis2]
        if not plane:
            cosTheta = self.dot(other) / (self.getMag() * other.getMag())
            return acos(cosTheta)
        else:
            angleSelf = self.lock(plane).getHeading(plane[0], trueBearing = plane[1])
            angleOther = other.lock(plane).getHeading(plane[0], trueBearing = plane[1])
            angle = angleSelf - angleOther
            return angle

    def lock(self, elements):
        if elements == None:
            return self
        tempVec = vector([0 for x in self.elements])
        for x in enumerate(self.elements):
            if x[0] in elements:
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

DEFAULT_ZERO_VEC = vector(DEFAULT_ZERO_VEC)
DEFAULT_UNIT_VEC = vector(DEFAULT_UNIT_VEC)
class camera:
    # Main job: work out where a dot should go on the screen given the cameras position and rotation and the objects position.
    def __init__(self, pos = DEFAULT_ZERO_VEC, rot = DEFAULT_UNIT_VEC, vel = DEFAULT_ZERO_VEC, screenDepth = 500):
        self.pos = pos
        self.rot = rot
        self.vel = vel
        self.panTrack = None
        self.rotTrack = None
        self.trackSeparation = 0
        self.rotTrackOrigin = DEFAULT_UNIT_VEC
        self.screenDepth = screenDepth

    def panTrackSet(self, target = None):
        self.panTrack = target
        return target

    def rotTrackSet(self, target = None):
        self.rotTrack = target
        return target

    def drawParticle(self, particle):
        # if type(particle) != particle:
        #     print("Non particle type sent to drawParticle: ", particle)
        #     return False

        # Get relative position to camera's position.
        radius = particle.radius
        relPosition = particle.pos - self.pos
        # relPosUnit = relPosition.multiply(1 / relPosition.getMag())
        relRotation = relPosUnit - self.rot

        theta = self.rot.relAngle(relPosition)
        # Get angles in XZ, YZ, (XY?) planes
        # x1, y1, x2, y2 = 0, 0, 0, 0
        # centreAngleX = self.rot.relAngle(relPosUnit, [0, 2])
        # centreAngleY = self.rot.relAngle(relPosUnit, [1, 2])
        centreAngleX = acos((2 - relRotation.lock([0, 2]).getMag() ** 2) / 2)
        centreAngleY = acos((2 - relRotation.lock([1, 2]).getMag() ** 2) / 2)

        rp = particle.radius
        SD = self.screenDepth
        CP = relPosition
        a = SD * (2 * rp * (abs(CP)**2 - rp**2)**(3/2) / (abs(CP)**4 * cos(theta)**2) - sin(theta)**2 * rp**2 / abs(CP)**2)

        # offset: angle either side of centre angle which is slightly distorted due to the 3d bulge of the sphere.
        if tan(centreAngleX) * self.screenDepth > screen.winfo_width() or tan(centreAngleY) * self.screenDepth > screen.winfo_width():
            return False
        distanceX = relPosition.getMag()
        distanceY = relPosition.lock([1, 2]).getMag()
        print("Radius: {}, distanceX: {}, distanceY: {}".format(radius, distanceX, distanceY))
        if (radius >= distanceX or radius >= distanceY):
            return False
        offsetX = asin(radius/distanceX)
        offsetY = asin(radius/distanceX)

        x1 = tan(centreAngleX - offsetX) * self.screenDepth
        x2 = tan(centreAngleX + offsetX) * self.screenDepth
        y1 = tan(centreAngleY - offsetY) * self.screenDepth
        y2 = tan(centreAngleY + offsetY) * self.screenDepth

        drawOval(x1, y1, x2, y2)

        return relPosition



    def panFollow(self):
        pass
camera = camera()

class particle:
    def __init__(self, mass, position, velocity = 0, acceleration = 0):
        self.mass = mass
        self.pos = position
        self.dim = len(position.elements)
        if velocity == 0:
            self.vel = vector([0 for i in range(self.dim)])
        else:
            self.vel = velocity
        if acceleration == 0:
            self.acc = vector([0 for i in range(self.dim)])
        else:
            self.acc = acceleration
        self.setRadius()
        particleList.append(self)
        if self.pos.dim != self.vel.dim:
            print("This class is badly made! (non consistant dimensions):", self)

    alive = True
    respawn = True
    density = defaultDensity
    specialColour = False
    colour = [0, 0, 0]

    inbound = False
    immune = False

    newMass = False # the mass of the particle after it respawns

    def setRadius(self):
        self.radius = (0.75 * (self.mass/self.density) / pi) ** (1/3)

    def calcAcc(self, other):
        force = (G * self.mass * other.mass)/(self.pos.subtract(other.pos).getMag() ** 2)
        forceVector = other.pos.subtract(self.pos)
        # drawVector(forceVector.setMag(force/self.mass), self.pos)
        self.acc.addToMe(forceVector.setMag(force/self.mass))
        # print("calcAcc:", self.acc.elements)

    # def calcAccList(self, ListOfParticles):
    #     for p in ListOfParticles:
    #         if p != self:
    #             self.calcAcc(p)


    def checkCollision(self, other):
        if other.alive and (self.pos.subtract(other.pos).getMag() < self.radius + other.radius):
            self.contest(other)
            return True
        else:
            return False

    def runLoop(self):
        for p in particleList:
            if not self.checkCollision(p):
                self.calcAcc(p)


    def draw(self, getDrawCoords=False, velVec=False, buffer=None):
        eyeWidth = EYE_WIDTH
        if self.pos.elements[2] > -screenDepth:
            posX, posY, posZ = self.pos.elements[0:3]
            apparentRadius = self.radius * screenDepth/(posZ + screenDepth)
            apparentX = posX * screenDepth/(posZ + screenDepth)
            apparentY = posY * screenDepth/(posZ + screenDepth)
            # if self == particleList[-1]: print("X~: {}, Y~: {}, r~: {}".format(round(apparentX, 5), round(apparentY, 5), round(apparentRadius, 5)))
            if velVec:
                velX, velY, velZ = self.vel.elements[0:3]
                if (velZ + posZ + screenDepth) > 0:
                    apparentVelX = (velX + posX) * screenDepth / ((velZ + posZ) + screenDepth)
                    apparentVelY = (velY + posY) * screenDepth / ((velZ + posZ) + screenDepth)
                else:
                    apparentVelX = (velX + posX) * screenDepth / (0.0001)
                    apparentVelY = (velY + posY) * screenDepth / (0.0001)
                    print(velZ + posZ + screenDepth)

                    if getDrawCoords:
                        return [apparentX, apparentY, apparentRadius]
                        if not anaglyph:
                            drawDot(apparentX, apparentY, apparentRadius, actualRadius = self.radius)

                            if velVec: drawLine(apparentVelX, apparentVelY, apparentX, apparentY)
                        else:
                            apparentOffset = eyeWidth * posZ / (2 * (posZ + screenDepth))
                            drawDot(apparentX + apparentOffset, apparentY, apparentRadius, colour=[1, 0, 0])
                            drawDot(apparentX - apparentOffset, apparentY, apparentRadius, colour=[0, 0, 1])
                            drawIntersect(apparentX, apparentOffset, apparentY, apparentRadius)


    # def checkCollisionList(self, ListOfParticles):
    #     for p in ListOfParticles:
    #         if p != self:
    #             self.checkCollision(p)

    def checkOutOfBounds(self): #bounds=[turtle.window_width()/2, turtle.window_height()/2]):
        # self.vel.multiplyToMe(0)
        # return
        if self.immune: return False
        out = False
        if self.pos.subtract(vector([0, 0, -screenDepth])).getMag() > voidRadius:
            out = True
        # print("Checking")
        if out and not self.inbound:
            # print("Out")
            #if self.acc.getMag() < 1:
            if self.respawn:
                self.respawn()
            else:
                self.die()
        elif not out and self.inbound:
            self.inbound = False


    def respawn(self):
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
        # print(self,"Dying!")
        if self.respawn:
            if CAMERA_UNTRACK_IF_DIE and camera.track == self:
                camera.setTrack(killer)
            self.respawn()
        else:
            if self in particleList:
                if camera.track: camera.setTrack()
                if buffer != 0:
                    BUFFER[self].append(False)
                particleList.remove(self)
            self.alive = False

    def contest(self, other):
        if self.mass >= other.mass:
            self.vel = (self.vel.multiply(self.mass).add(other.vel.multiply(other.mass))).multiply(1/(self.mass + other.mass))
            self.mass += other.mass
            # Using (mv)_1 + (mv)_2 = (m_1 + m_2)v:
            self.setRadius()
            other.die(self)
        else:
            other.vel = (self.vel.multiply(self.mass).add(other.vel.multiply(other.mass))).multiply(1/(self.mass + other.mass))
            other.mass += self.mass
            other.setRadius()
            self.die(other)

    def step(self, delta, draw=True, drawVel=False, onlyDraw = False, bufferMode = 0):
        if onlyDraw and bufferMode == 0:
            self.draw(velVec = drawVel)
            return True

        elif bufferMode == 2:
            # Playing
            if BUFFER[self][0]:
                self.pos = BUFFER[self][0][0]
                self.radius = BUFFER[self][0][1]
                self.draw(velVec = drawVel)
                BUFFER[self] = BUFFER[self][1:]
            else:
                BUFFER.pop(self)
            return

        if bufferMode == 1 and BUFFER[self]:
            if BUFFER[self][-1]:
                self.pos = BUFFER[self][-1][0]


        # self.checkCollisionList(particleList)
        # self.calcAccList(particleList)
        self.runLoop()
        self.vel.addToMe(self.acc.multiply(delta))
        self.pos.addToMe(self.vel.multiply(delta))
        self.checkOutOfBounds()
        self.acc.multiplyToMe(0)
        if self.radius > radiusLimit:
            self.die()
            return False
        if bufferMode == 0:
            # No buffer. If paused, wouldn't make it to here. Just draw.
            self.draw(velVec = drawVel)

        elif bufferMode == 1:
            # Recording, Must be paused.
            BUFFER[self].append([self.pos.getClone(), self.radius])
            self.pos, self.radius = BUFFER[self][0]
            self.draw(velVec = drawVel)
            self.pos, self.radius = BUFFER[self][-1]
        return True

    def circularise(self, other, plane = None, inclination = 0):
        if inclination == "r":
            inclination = random.random() * 360 - 180
        speed = sqrt(G * other.mass/(self.pos.subtract(other.pos).getMag()))
        vel = randomVector(3, 1)
        vel.makeOrthogonal(other.pos.subtract(self.pos))
        if plane: vel = vel.lock(plane)#[vel.elements[i] * plane[i] for i in range(len(vel.elements))]
        vel.setMag(speed)
        vel.addToMe(other.vel)
        self.vel = vel
        return True

setup()

        # self.vel.elements[2] = speed + other.vel.elements[2]
