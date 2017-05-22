## Orbits 3
## Written by Leo Carnovale
## whilst on a train to uni
## 7/3/2017
## an N-body simulator in 3D(!!!)

# W, A, S, D, R, F --> Pan
# Up, Down, Left, Right --> Rotate
# Space, Esc --> Pause, stop
# '[', ']' --> decrease, increase delta
# K, L --> decrease, increase particleCount
# '<', '>' --> decrease, increase screenDepth
# (;), (') --> decrease, increase voidRadius (Max distance from origin before particle respawns)
# H --> Toggle on screen data
# Left Click --> Follow particle (if one is clicked on) or stop following particle (if nothing is clicked)
# Shift_L + Left Click --> Kill particle if one is clicked on
# Right Click --> zero all particles velocity on clicked particle

import time
from tkinter import *
import sys
import turtle
from math import *
import random


def setup(): # Will be run just before the loop starts
    global camera
    camera.setTrack(particleList[-1])
    print(vector([0,-2,0]).getHeading(0, trueBearing=True)/pi)
    print(vector([-4,-2,3]).lock([0, 1]).elements)
    # Exit() # Don't forget about this !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return


class ptr:
    def __init__(self, obj):
        self.obj = obj
    def set(self, obj):
        self.obj = obj
    def get(self):
        return self.obj

testMode = False

window = turtle.Screen()
window.setup(width = 1.0, height = 1.0)

LINUX = False # If true, then non alphanumeric key controls will be replaced with numbers

INITIAL_WINDOW_WIDTH = 500
INITIAL_WINDOW_HEIGHT = 600

master = Tk()
w = Canvas(master, width = INITIAL_WINDOW_WIDTH, height = INITIAL_WINDOW_HEIGHT)
w.pack()
canvas_width = INITIAL_WINDOW_WIDTH
canvas_height = INITIAL_WINDOW_HEIGHT
w.create_line(canvas_width/4, canvas_height/2, 3 * canvas_width/4, canvas_height/2)
ratio = 0.9
w.create_rectangle(canvas_width * (1 - ratio), canvas_height * (1 - ratio), canvas_width * ratio, canvas_height * ratio)


particleCount = 25
radiusLimit = 20
anaglyph = False
colourful = True
limit = 50000
delta = 0.00005
voidRadius = 1000
defaultDensity = 10
screenDepth = 600
SMOOTH_FOLLOW = 0.6
SMOOTH_ROTATE = 1

randomSpawn = False # Spawn a 'cloud' of particles
SUN_MASS = 300000
sunSpawn = True

autoAbort = True

CAMERA_UNTRACK_IF_DIE = True # Stop tracking a particle if it dies
EYE_WIDTH = 5 # A parameter needed to apply anaglyph depth perception to particles. Should be the width between the left and right eye,
PAN_RATE = 1.5 # Max speed of pan

START_PAUSED = True

PRESET_2_RADIUS = 200 # Radius of particles from centre
PRESET_2_RADIUS_OFFSET = 0
PRESET_2_MASS = 150
PRESET_2_PARTICLE_COUNT = particleCount
PRESET_2_NEWMASS = 30

PRESET_3_PARTICLE_COUNT = particleCount
PRESET_3_MASS = 150
PRESET_3_MIN_RADIUS = 40
PRESET_3_MAX_RADIUS = 200
PRESET_3_NEWMASS = 30
PRESET_3_SAME_DIRECTION = True
PRESET_3_PLANE = [1,0,1] # Plane in which the ring of particles will be made in

PRESET_4_PARTICLE_COUNT = 6
PRESET_4_START_MASS = 300000
PRESET_4_MASS_RATIO = 50 # Mass of parent/mass of body
PRESET_4_START_RADIUS = 700
PRESET_4_RADIUS_RATIO = 10
PRESET_4_DENSITY = 500
PRESET_4_RANDOM_PLANES = True
PRESET_4_SAME_DIRECTION = True # Only applies if random_planes is false


preset = ptr(3)
# Presets:
# 1: Earth, Moon, Apollo
# 2: Circle of particles around circularised around sun or the center of mass
# 3: Line of planets circularised around sun (sun will spawn regardless of sunSpawn)
# 4: 'Endless' fractal of planets orbiting another (sun will not spawn)


if len(sys.argv) > 1:
    arguments = {"-t": [0, testMode, True], #--> Enables test mode (times the simulation)
"-l": [1, limit, int], # --> number of iterations to run
"-c": [1, particleCount, int],# --> number of particles
"-p": [1, preset, int],# --> preset
"-d": [1, delta, float], # --> delta
"-sp": [1, START_PAUSED, int]
}
    argsParsed = sys.argv
    for a in range(1, len(argsParsed)):
        if argsParsed[a] in arguments:
            arg = argsParsed[a] # Will be -t, -l etc.
            if arguments[arg][0]:
                try:
                    nextArg = argsParsed[a + 1] # Should be a parameter for an arg
                    if nextArg in arguments: raise IndexError # If the next arg is another argument then the parameter is missing
                    nextArg = arguments[arg][2](nextArg)
                except ValueError:
                    print("incorrect usage of {}, should be:".format(arg), end = " ")
                    print(arguments[arg][2])
                    continue
                except IndexError:
                    print("Missing argument for {}".format(arg))
                    continue
                else:
                    arguments[arg][1].set(nextArg)
                    print(arg, nextArg)
            else:
                arguments[arg][1] = arguments[arg][2] # This doesn't work :( i need a pointer a variable rather than the actual variable
                print(arg, arguments[arg][2]) # For debugging
    print(preset)

preset = 3

G = 500 # Gravitational Constant
turtle.bgcolor("black")

turtle.tracer(0, 0) # Makes the turtle's speed instantaneous
turtle.hideturtle() #

def roundList(list, places):
    return [round(x, places) for x in list]

def radtodeg(things):
    thing = [x for x in things]
    if type(thing) == list:
        for i, t in enumerate(thing):
            thing[i] = t * 180/pi
    else:
        thing = thing * 180/pi
    return thing


def drawDot(x, y, r, Fill=True, colour = [0, 0, 0], actualRadius = 0):
    # Draws a dot on the canvas
    if not actualRadius:
        actualRadius = r
    if Fill:
        turtle.up()
        turtle.goto(x, y)
        if actualRadius > radiusLimit:
            return
        if colourful:
            turtle.pencolor([actualRadius/radiusLimit, 0, (radiusLimit - actualRadius)/radiusLimit])
        else:
            turtle.pencolor(colour)

        turtle.dot(2 * r)


    else:
        turtle.up()
        turtle.goto(x, y - r)
        turtle.down()
        turtle.circle(r)
        turtle.up()

def drawIntersect(x, offset , y, radius, colour = [0,0,0]):
    # This is used to draw the intersect between two dots when anaglyph is enabled. It doesn't work very well.
    # Note: doesn't account for dots with different y values
    if abs(offset) > abs(radius):
        return
    height = sqrt(radius ** 2 - offset ** 2)
    angle = asin(height/radius)
    angle = angle * 180/pi
    turtle.up()
    turtle.goto(x, y + height)
    turtle.pencolor(colour)
    turtle.begin_fill()
    turtle.fillcolor(colour)
    turtle.setheading(angle - 90)
    turtle.down()
    turtle.circle(-1 * radius, angle * 2)
    turtle.setheading(angle + 90)
    turtle.circle(-1 * radius, angle * 2)
    turtle.end_fill()


def drawLine(x2, y2, x1 = 0, y1 = 0):
    # Draws a line from one point to another (starts at origin by default)
    turtle.up()
    turtle.goto(x1, y1)
    turtle.down()
    turtle.goto(x2, y2)
    turtle.up()

def drawPoly(points, fill=None, depthPerception=True, lineColour=None, forceFill=True):
    global screenDepth
    try:
        x, y = points[0]
    except ValueError:
        depthPerception = True
    except TypeError:
        depthPerception = True
    if fill and not lineColour: lineColour = fill
    if not fill and not lineColour: lineColour = [0, 0, 0]

    if depthPerception:
        oldPoints = points
        points = []
        for point in oldPoints:
            if point.elements[2] > -screenDepth:
                posX, posY, posZ = point.elements[0:3]
                newX = posX * screenDepth / (posZ + screenDepth)
                newY = posY * screenDepth / (posZ + screenDepth)
                points.append([newX, newY])

    turtle.up()
    turtle.pencolor(lineColour)
    turtle.goto(points[0])
    turtle.down()
    if fill:
        # print("Filling..")
        turtle.fillcolor(fill)
        turtle.begin_fill()

    for point in points[1:]:
        turtle.goto(point) #point must be of length 2
    turtle.goto(points[0])
    if fill:
        turtle.end_fill()
    turtle.up()
    return True

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
        angles = [self.getHeading(i, False) for i in range(self.dim)] # a list of the cos of the angles between the vector and each axis
        self.elements = [mag * angles[k] for k in range(self.dim)] # trig
        return self

    # For most of the following functions (add, subtract etc.) there is a respective 'functionToMe',
    # The only difference is that the original function returns a new vector without changing any other vector.
    # functionToMe will change the original vector.
    # eg. a.add(b) --> c = (a + b), a.addToMe(b) --> a = (a + b)
    # There might be a better way to do this?

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

class angleVector(vector):
    def __init__(self, elements, wrap=True, lowerBound=-pi, radius=1):
        super().__init__(elements)
        self.wrap = wrap
        self.lowerBound = lowerBound # upper bound is always lowerBound + 2pi
        self.wrapAngles()
        self.radius = radius

    def wrapAngles(self):
        if not self.wrap: return
        for i, angle in enumerate(self.elements):
            if angle > (self.lowerBound + 2 * pi):
                self.elements[i] -= 2 * pi
            elif angle <= self.lowerBound:
                self.elements[i] += 2 * pi

    def transpose(self, positionVector, wrap=True, lowerBound=-pi):
        # returns an angle vector with THE SAME elements as the position vector
        return angleVector(positionVector.elements, wrap, lowerBound)

    # def convert(self, positionVector, wrap=True, lowerBound=-pi):


    def negate(self):
        return angleVector([-x for x in self.elements], self.wrap, self.lowerBound, self.radius)

    def reverse(self):
        return self.add(angleVector([pi for e in self.elements]))

    def reverseToMe(self):
        self.define(self.reverse())

    def add(self, other, element=[], addTrue=True):
        tempVec = [x for x in self.elements]
        for i, angle in enumerate(tempVec):
            if (element and i not in  element):
                next

            tempVec[i] += other.elements[i]

        return angleVector(tempVec, self.wrap, self.lowerBound)

    # def addTrue(self, other):
        #only useful for angles representing 3d vectors, as camera does
        # tanA = secX tanY


    def addToMe(self, other, element=[]):
        self.define(self.add(other, element))

    def subtract(self, other, element=[]):
        return self.add(other.negate(), element)

    def subtractToMe(self, other, element=[]):
        self.define(self.subtract(other, element))

    def multiply(self, scalar):
        return angleVector([x * scalar for x in self.elements], self.wrap, self.lowerBound)


    def multiplyToMe(self, scalar):
        self.define(self.multiply(scalar))

    def getMag(self):
        return self.radius

    def setMag(self, mag):
        self.radius = mag

    def getHeading(self):
        print("Can't do getHeading for", self)
        return False

    def setHeading(self, *args):
        print("Can't do getHeading for", self)
        return False

    # def relAngle(self, other):




class shape:
    # Uses the vector class
    def __init__(self, points, position=vector([0, 0, 0]), joins = {}, net = []):
        self.points = points # points --> array of vectors
        self.joins = joins # --> {point:[points joined to it]}
        self.net = net # --> [[point, point, point, colour], ...], a list of faces, each face is a list of points with the last value the colour of the face. colour None means no fill (see through)
        if self.joins == {}:
            for point in points:
                self.joins[point] = []
        self.position = position

    def addPoints(self, points):
        self.points += points
        for point in points:
            self.joins[point] = []

    def makeJoin(self, point, other):
        if point not in self.points: return False
        if other not in self.points: return False
        self.joins[point].append(other)
        self.joins[other].append(point)
        return True

    def makeJoins(self, points, wrap=True):
        lastPoint = points[0]
        for point in points[1:]:
            if point not in self.points:
                return False
            else:
                self.makeJoin(lastPoint, point)
                lastPoint = point
        if wrap: self.makeJoin(lastPoint, points[0])
        return True

    def isJoined(self, point, other):
        # Finds if two points are directly joined or not
        if other in self.joins[point]:
            return True
        else:
            return False

    def isJoinedLong(self, point, other, returnPath=False, currentPath=None):
        # Finds if two points are joined indirectly and finds the path that joins them.
        # W.I.P. Don't use until it actually works!
        if returnPath:
            path = []
        if currentPath == None:
            currentPath = [point]
        if other in self.joins[point]:
            if returnPath:
                return [currentPath] + [other]
            else:
                return True
        else:
            currentPath += [point]
            joined = False
            for join in self.joins[point]:
                if join not in currentPath:
                    joined = self.isJoinedLong(join, other, returnPath, currentPath)
            # Now joined should be the path of the join.
            return joined



    def makeFace(self, points, colour=None):
        # Assumes all the points are joined and in correct order
        for point in points:
            if point not in self.points: return False
        print("Making face")
        self.net.append([points] + [colour])

    def draw(self, drawPoints=False):
        global globalNet
        # Order faces in decreasing Z position;
        # orderedNet = self.net.sort(key = lambda: face: min([x.elemnts[2] for x in face[0]]))
        # orderedNet = [[min([point.elements[2]]), point for point in face[0]])]]
        orderedNet = [[min([point.elements[2] for point in face[0]]), face] for face in self.net]
        # orderedNet = sorted(orderedNet)
        # print(orderedNet)
        # print(orderedNet.sort())
        globalNet = orderedNet
        # for face in self.net:
            # print([min([point.elements[2] for point in face[0]]), face])
        try:
            orderedNet.sort(reverse = True)
        except TypeError:
            pass # Occurs if two elements have the same max z point
        orderedNet = [x[1] for x in orderedNet]
        for face in orderedNet:
            # print("Drawing poly: {}".format(face))
            drawPoly(face[0], face[1])

    def translate(self, posChange):
        # posChange --> position vector, where the shape is moving to
        for point in self.points:
            point.addToMe(posChange)


    def rotate(self, angles, centre = None):
        # rotation around an axis results in change of angles to from other axes, ie rotation of x axis means changing z and y angles and components.
        if not centre:
            centre = self.getCentre()

        for axis, angle in enumerate(angles):
            if angle != 0:
                pass


    def getCentre(self):
        # Find centre of object (technically this is really the average)

        total = vector([0 for x in self.points[0].elements])
        for point in self.points:
            total.addToMe(point)
        totalMag = total.getMag()
        total.setMag(totalMag/len(self.points))
        return total


# globalNet = []
# a = shape([vector([100,200,31]), vector([101,400,32]), vector([301, 400, 30]), vector([300, 200, 29])])
# A, B, C, D = a.points
# Z = vector([0, 0, 200])
# E, F, K, H = A.add(Z), B.add(Z), C.add(Z), D.add(Z)
#
# a.addPoints([E, F, K, H])
#
#
# a.makeJoins([A, B, C, D])
# a.makeJoins([E, F, K, H])
#
# a.makeJoin(A, E)
# a.makeJoin(B, F)
# a.makeJoin(C, K)
# a.makeJoin(D, H)
#
#
# a.makeFace([A, B, C, D], [0.5, 0.5, 1])
# a.makeFace([D, C, K, H], [1, 0, 1])
# a.makeFace([H, K, F, E], [1, 1, 0])
# a.makeFace([B, C, K, F], [1, 0, 0])
# a.makeFace([B, F, E, A], [0, 1, 0])
# a.makeFace([A, E, H, D], [0, 0, 1])



class cameraClass:
    # More specific to the particle sim, good for organising panning and rotation of the canvas and particles. Only one instance of cameraClass is necessary.
    # any more than 1 would be weird
    def __init__(self, track=None, distance=50):
        self.track = track  # Particle being tracked
        self.trackDistance = distance # Distance FROM THE 'SCREEN', a distance of 0 means right at the screen, meaning a z position of -(screenDepth)
        self.rotateTrack = None
        self.rotateLocal = [0, 0]
        self.rotorigin = angleVector([pi/2, pi/2, 0])# rotational origin, used as [XZ angle, YZ angle], in Z direction


    def matchVel(self, other=None):
        # Makes a target particle the 'centre of motion' meaning it appears stationary, essentially matches all other velocities to it
        if not other: return False
        velDifference = other.vel.getClone() # vel to subtract from other particles (Initially recalculated this every iteration in the following loop, but this creates bugs and is slow)
        for p in particleList:
            p.vel.subtractToMe(velDifference)
        return True


    def followPan(self, smooth=True):
        """A smooth value of True (ie one) will have a rate of 0.5,
        for any other rate replace smooth with (rate * 2), as it will be half of the smooth parameter.
        For a rate of one, let smooth = False. ie, movements will be instant. """
        if not self.track: return 0
        rate = 1
        if smooth: rate = smooth/2
        difference = self.track.pos.subtract(vector([0, 0, self.trackDistance - screenDepth])).multiply(rate)
        for p in particleList:
            p.pos.subtractToMe(difference)

    def autoRate(self, rate):
        found = False
        origin = vector([0,0,-screenDepth])
        # if self.track: origin = self.track.pos.add(vector([0, 0, camera.trackDistance]))
        dist = min([x.pos.subtract(origin).getMag() - x.radius for x in particleList]) # finds the particle closest to the origin (distance from surface of particle)
        A = 100 # Sorry i couldnt think of a name. Its just a coeffecient for the radius
        # I'm not sure what a varying A does to newRate exactly, but 100 works well
        newRate = dist * rate/(dist + A)
        return newRate

    def pan(self, panArray, rate=1):
        # panArray --> [x, y, z], each between -1 and 1, for direction of pan.
        if panArray[3] == False: # If false, uses the autoRate to choose a speed based on proximity to a particle
            rate = self.autoRate(rate)
        tempFlag = False
        if self.track:
            if self.trackDistance < self.track.radius * 2:
                if panArray[2] == -1:
                    panArray[2] += 1
                    tempFlag = True
            panArray[0], panArray[1] = 0, 0
            # Don't allow horizontal or vertical movement
            self.trackDistance += panArray[2] * rate

        vecAdd = vector([panArray[0], panArray[1], panArray[2]]).multiply(rate)
        # vector to add to make pan

        for p in particleList:
            p.pos.addToMe(vecAdd)
        if tempFlag: panArray[2] -= 1
        return True

    def rotate(self, rotate, rate=pi/180, following=False):
        # rotate --> [x, y], each between -1 and 1, for direction of rotation.
        if not rotate[0] and not rotate[1]: return False
        if self.track:
            ## When tracking, set target as origin, change sign of rate to reverse direction
            origin = self.track.pos
            # print("Here... following:", following, "rotateTrack:", self.rotateTrack)
            if self.rotateTrack and following == False:
                self.rotorigin.addToMe(angleVector(rotate).multiply(rate))
                return
            rate = -rate
        else:
            ## otherwise, set the centre of the screen as the origin
            origin = vector([0, 0, -screenDepth])

        for p in particleList:
            # This uses trig and triangles to find the new x, y and z elements if the angle changes.
            # Position:
            # thetaXZ = vector([(p.pos.elements[0] - origin.elements[0]), (p.pos.elements[2] - origin.elements[2])]) # vector from p to origin along XZ plane
            thetaXZ = p.pos.subtract(origin).getHeading(axis = 0, trueBearing = 2, lock = [0, 2])
            radius = p.pos.subtract(origin).lock([0, 2]).getMag()
            p.pos.elements[2] = radius * sin(thetaXZ + rotate[0] * rate) + origin.elements[2]
            p.pos.elements[0] = radius * cos(thetaXZ + rotate[0] * rate) + origin.elements[0]

            thetaYZ = p.pos.subtract(origin).getHeading(axis = 1, trueBearing = 2, lock = [1, 2])
            radius = p.pos.subtract(origin).lock([1, 2]).getMag()
            p.pos.elements[1] = radius * cos(thetaYZ + rotate[1] * rate) + origin.elements[1]
            p.pos.elements[2] = radius * sin(thetaYZ + rotate[1] * rate) + origin.elements[2]

            # Velocity:
            thetaXZ = p.vel.getHeading(axis = 0, trueBearing = 2, lock = [0, 2])
            velMagXZ = p.vel.lock([0, 2]).getMag()
            p.vel.elements[0] = velMagXZ * cos(thetaXZ + rotate[0] * rate)
            p.vel.elements[2] = velMagXZ * sin(thetaXZ + rotate[0] * rate)

            thetaYZ = p.vel.getHeading(axis = 1, trueBearing = 2, lock = [1, 2])
            velMagYZ = p.vel.lock([1, 2]).getMag()
            p.vel.elements[1] = velMagYZ * cos(thetaYZ + rotate[1] * rate)
            p.vel.elements[2] = velMagYZ * sin(thetaYZ + rotate[1] * rate)

        # print(velMagXZ)

        return True

    def followRotate(self, smooth=1):
        if not self.rotateTrack or not self.track: return False
        # print("Follow Rotating")
        origin = vector([0, 0, -screenDepth])
        relativePosition = self.rotateTrack.pos.subtract(self.track.pos)
        trackAngle = [0, 0]
        print("relativePosition: {}".format(roundList(relativePosition.elements, 4)), end = "\t")
        trackAngle[0] = relativePosition.getHeading(axis = 0, trueBearing = 2)#, lock = [0, 2])
        trackAngle[1] = relativePosition.getHeading(axis = 1, trueBearing = 2)#, lock = [1, 2])
        if relativePosition.elements[2]  < 0:
            trackAngle[1] = pi - trackAngle[1]
        print("trackAngle: {}".format(roundList(radtodeg(trackAngle), 5)), end = "\t")
        trackAngle = angleVector(trackAngle)
        relAngle = self.rotorigin - trackAngle
        print("rotorigin~: {},\t XZbearing, YZbearing~: {}".format(roundList(radtodeg(self.rotorigin.elements), 5), roundList(radtodeg(relAngle.elements), 5)), end = "")
        print()
        self.rotate(relAngle.negate().elements, rate = smooth, following = True)


    def setTrack(self, target=None):
        self.track = target
        if target: self.trackDistance = max(self.trackDistance, target.radius * 2)
        if self.rotateTrack == target: self.setRotateTrack()

    def setRotateTrack(self, target=None):
        if self.rotateTrack == target: target=None
        self.rotateTrack = target

    def doAll(self, pan, rotate, smoothFollow=True, panRate=PAN_RATE, rotateRate=pi/180, smoothRotate=1):
        self.followPan(smoothFollow)
        self.pan(pan, panRate)
        self.rotate(rotate, rotateRate)#, smoothRotate = smoothRotate)
        self.followRotate(smoothRotate)

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


camera = cameraClass()

particleList = []

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

    def calcAccList(self, ListOfParticles):
        for p in ListOfParticles:
            if p != self:
                self.calcAcc(p)

    def draw(self, getDrawCoords=False, velVec=False):
        eyeWidth = EYE_WIDTH
        if self.pos.elements[2] > -screenDepth:
            posX, posY, posZ = self.pos.elements[0:3]
            apparentRadius = self.radius * screenDepth/(posZ + screenDepth)
            apparentX = posX * screenDepth/(posZ + screenDepth)
            apparentY = posY * screenDepth/(posZ + screenDepth)
            if velVec:
                velX, velY, velZ = self.vel.elements[0:3]
                if (velZ + posZ + screenDepth) > 0:
                    apparentVelX = (velX + posX) * screenDepth / ((velZ + posZ) + screenDepth)
                    apparentVelY = (velY + posY) * screenDepth / ((velZ + posZ) + screenDepth)
                else:
                    apparentVelX = (velX + posX) * screenDepth / (0.0001)
                    apparentVelY = (velY + posY) * screenDepth / (0.0001)

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



    def checkCollision(self, other):
        if other.alive and (self.pos.subtract(other.pos).getMag() < self.radius + other.radius):
            self.contest(other)
            return True
        else:
            return False

    def checkCollisionList(self, ListOfParticles):
        for p in ListOfParticles:
            if p != self:
                self.checkCollision(p)

    def checkOutOfBounds(self, bounds=[turtle.window_width()/2, turtle.window_height()/2]):
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

    def step(self, delta, draw=True, drawVel=False, onlyDraw = False):
        if onlyDraw:
            self.draw(velVec = drawVel)
            return True
        if self.radius > radiusLimit:
            self.die()
        if draw:
            self.draw(velVec = drawVel)

        self.checkCollisionList(particleList)
        self.calcAccList(particleList)
        self.vel.addToMe(self.acc.multiply(delta))
        self.pos.addToMe(self.vel.multiply(delta))
        self.checkOutOfBounds()
        self.acc.multiplyToMe(0)
        return True

    def circularise(self, other, plane = [1,1,1], inclination = 0):
        if inclination == "r":
            inclination = random.random() * 360 - 180
        speed = sqrt(G * other.mass/(self.pos.subtract(other.pos).getMag()))
        vel = randomVector(3, 1)
        vel.makeOrthogonal(other.pos.subtract(self.pos))
        vel.elements = [vel.elements[i] * plane[i] for i in range(len(vel.elements))]
        vel.setMag(speed)
        vel.addToMe(other.vel)
        self.vel = vel
        return True


        # self.vel.elements[2] = speed + other.vel.elements[2]


if randomSpawn: particleList = [particle(random.random() * 100 + 500, randomVector(3, 100 + i/particleCount * 300), randomVector(3, 30, 100)) for i in range(particleCount)]

def spawnSun():
    global particle
    global Sun
    global SUN_MASS
    Sun = particle(SUN_MASS, vector([0, 0, 0]))
    Sun.immune = True
    return True

if sunSpawn: spawnSun()

if preset == 1:
    Earth = particle(10000, vector([400, 0, 0]))
    Earth.immune = True
    Moon = particle(400, vector([450, 0, 0]))
    Moon.immune = True
    Apollo = particle(0.5, vector([456, 0, 0]))
    Apollo.immune = True

    Earth.circularise(Sun)
    Moon.circularise(Earth)
    Apollo.circularise(Moon)

elif preset == 2:
    tempParticleList = [particle(PRESET_2_MASS, vector([0,0,0])) for i in range(PRESET_2_PARTICLE_COUNT)]
    killIt = False # If there is a sun, leave it there. If not, create a temporary centre of mass
                   # then 'kill' it
    if sunSpawn:
        centre = Sun
        killIt = False
    else:
        centre = particle(PRESET_2_MASS * (PRESET_2_PARTICLE_COUNT / 2), vector([0,0,0]))
        killIt = True
    for i in range(PRESET_2_PARTICLE_COUNT):
        angle = i/PRESET_2_PARTICLE_COUNT * 2 * pi
        tempParticleList[i].pos.elements[0] = cos(angle) * (PRESET_2_RADIUS + (random.random() - 0.5) * PRESET_2_RADIUS_OFFSET)
        tempParticleList[i].pos.elements[2] = sin(angle) * (PRESET_2_RADIUS + (random.random() - 0.5) * PRESET_2_RADIUS_OFFSET)
        tempParticleList[i].circularise(centre, plane = [1,0,1])
        tempParticleList[i].newMass = PRESET_2_NEWMASS
        if i > 0:
            # if particleList[i].vel.subtract(particleList[i - 1].vel).getMag() < particleList[i].vel.getMag():
            if tempParticleList[i].vel.add(tempParticleList[i - 1].vel).getMag() < tempParticleList[i].vel.getMag():
                tempParticleList[i].vel.reverseToMe()
    if killIt:
        centre.respawn = False
        centre.die()

elif preset == 3:
    if not sunSpawn: spawnSun()
    for i in range(PRESET_3_PARTICLE_COUNT):
        radius = i / (PRESET_3_PARTICLE_COUNT - 1) * (PRESET_3_MAX_RADIUS - PRESET_3_MIN_RADIUS) + PRESET_3_MIN_RADIUS
        particle(PRESET_3_MASS, vector([radius, 0, 0]))
        particleList[-1].circularise(Sun, plane = PRESET_3_PLANE)
        if PRESET_3_SAME_DIRECTION: particleList[-1].vel.elements[2] = abs(particleList[-1].vel.elements[2])


elif preset == 4:
    if sunSpawn:
        Sun.respawn = False
        Sun.die()

    particle(PRESET_4_START_MASS, vector([0, 0, 0]))
    for i in range(1, PRESET_4_PARTICLE_COUNT):
        radius = PRESET_4_START_RADIUS / (PRESET_4_RADIUS_RATIO ** (i - 1))
        mass = PRESET_4_START_MASS / (PRESET_4_MASS_RATIO ** (i - 1))
        if PRESET_4_RANDOM_PLANES:
            posAdd = randomVector(3, radius)
        else:
            posAdd = vector([radius, 0, 0])
        particle(mass, particleList[i-1].pos.add(posAdd))
        particleList[i].density = PRESET_4_DENSITY
        particleList[i].setRadius()
        particleList[i].circularise(particleList[i-1])

        if PRESET_4_SAME_DIRECTION and not PRESET_4_RANDOM_PLANES:
            particleList[i].vel.elements[2] = abs(particleList[i].vel.elements[2])


    # particleList = particleList + tempParticleList


# for p in particleList:
#     if p != Earth and p != Moon and p != Sun and p != Apollo:
#         p.circularise(Sun)


# A = particle(10000, vector([100, 0, 0]))
# B = particle(10000, vector([-100, 0, 0]))
# A.circularise(B)
# A.vel.multiplyToMe(2 ** (-1))
# A.vel.multiplyToMe(0.5)
# B.circularise(A)





running = True
particleListSort = particleList

# shift = 10 ** 0
pan = [0, 0, 0, False]
shiftL = False

# rotShift = pi/360
rotate = [0, 0]

tempDelta = 0 # Used to restore delta after unpausing

def panLeft():
    if pan[0] < 1:
        pan[0] += 1

def panRight():
    if pan[0] > - 1:
        pan[0] -= 1

def panForward():
    if pan[2] > - 1:
        pan[2] -= 1

def panBack():
    if pan[2] < 1:
        pan[2] += 1

def panUp():
    if pan[1] > - 1:
        pan[1] -= 1

def panDown():
    if pan[1] < 1:
        pan[1] += 1

def panFast():
    global shiftL
    shiftL = True
    pan[3] = True

def panSlow():
    global shiftL
    shiftL = False
    pan[3] = False

def rotRight():
    if rotate[0] < 1:
        rotate[0] = rotate[0] + 1

def rotLeft():
    if rotate[0] > -1:
        rotate[0] = rotate[0] - 1

def rotUp():
    if rotate[1] < 1:
        rotate[1] += 1

def rotDown():
    if rotate[1] > -1:
        rotate[1] -= 1


def changeScreenDepthUp():
    global screenDepth
    screenDepth += 10

def changeScreenDepthDown():
    global screenDepth
    if screenDepth > 10: screenDepth -= 10

def upDelta():
    global delta
    delta = delta * 2

def downDelta():
    global delta
    delta = delta / 2

def addParticle():
    global particleList
    global particleCount
    x = particle(random.random() * 5000 + 500, vector([0, 0, 0]))
    particleList[-1].respawn()
    particleCount += 1

def removeParticle():
    global particleList
    global particleCount
    particleList.pop(-1)
    particleCount -= 1


paused = False
def pause():
    global paused
    global delta
    if paused:
        paused = False
    else:
        paused = True

def Exit():
    global kill
    global running
    kill = True
    running = False


# centreParticle = None
# zDistance = None



def clickScreen(x, y):
    # print(x, y)
    global particleList
    global vector
    global screenDepth
    mouseVec = vector([x, y])
    for p in particleList:
        if p.draw(True): # Gets the coordinates of where it is drawn
            drawValues = p.draw(True)
            if mouseVec.subtract(vector([drawValues[0], drawValues[1]])).getMag() < drawValues[2]:
                return p
    return False

def leftClick(x, y):
    global shiftL
    global camera
    global clickScreen
    if not shiftL: camera.setTrack()
    p = clickScreen(x, y)
    if p:
        if shiftL:
            p.die()
        else:
            camera.setTrack(p)
    print("click!")

def rightClick(x, y):
    global camera
    global clickScreen
    p = clickScreen(x, y)
    if shiftL: camera.setRotateTrack()
    if p:
        if shiftL:
            camera.setRotateTrack(p)
            print("Setting")
        else:
            camera.matchVel(p)

def upVoid():
    global voidRadius
    voidRadius += 10

def downVoid():
    global voidRadius
    voidRadius -= 10

def toggleData():
    global showData
    showData = showData * -1

showData = 1
turtle.onkeypress(panLeft, "a")
turtle.onkeyrelease(panRight , "a")

turtle.onkeypress(panRight, "d")
turtle.onkeyrelease(panLeft , "d")

turtle.onkeypress(panForward, "w")
turtle.onkeyrelease(panBack , "w")

turtle.onkeypress(panBack, "s")
turtle.onkeyrelease(panForward , "s")

turtle.onkeypress(panUp, "r")
turtle.onkeyrelease(panDown , "r")

turtle.onkeypress(panDown, "f")
turtle.onkeyrelease(panUp , "f")

turtle.onkeypress(panFast, "Shift_L")
turtle.onkeyrelease(panSlow, "Shift_L")

turtle.onkeypress(rotRight, "Right")
turtle.onkeyrelease(rotLeft, "Right")

turtle.onkeypress(rotLeft, "Left")
turtle.onkeyrelease(rotRight, "Left")

turtle.onkeypress(rotUp, "Up")
turtle.onkeyrelease(rotDown, "Up")

turtle.onkeypress(rotDown, "Down")
turtle.onkeyrelease(rotUp, "Down")

turtle.onkey(pause, "space")
turtle.onkey(Exit, "Escape")

turtle.onkey(addParticle, "l")
turtle.onkey(removeParticle, "k")

turtle.onkey(toggleData, "h")
if LINUX:
    turtle.onkey(changeScreenDepthUp, "2")
    turtle.onkey(changeScreenDepthDown, "1")

    turtle.onkey(upDelta, "4")
    turtle.onkey(downDelta, "3")

    turtle.onkey(upVoid, "6")
    turtle.onkey(downVoid, "5")
else:
    turtle.onkey(changeScreenDepthUp, ".")
    turtle.onkey(changeScreenDepthDown, ",")

    turtle.onkey(upDelta, "]")
    turtle.onkey(downDelta, "[")

    turtle.onkey(upVoid, "'")
    turtle.onkey(downVoid, ";")

turtle.onscreenclick(leftClick, 1)
turtle.onscreenclick(rightClick, 3)



turtle.listen()



if testMode:
    limit = testLimit
    print("\nRunning %i iterations with timer." %(limit))

def writeText(text, x=None, y=None, colour=[1, 1, 1]):
    if x and y: turtle.goto(x, y)
    turtle.pencolor(colour)
    turtle.write(text, True)

def makeData():
    global screenDepth
    global particleList
    global G
    global delta
    global paused
    global pan
    global rotate
    global camera
    global frameRate
    global frameCount
    global longFrameRate
    global voidRadius
    data = """Screen depth: {}  Particle Count: {}   Gravitational constant: {}   delta: {} (Paused: {})
Pan: {}   Rotation: {}   trackDistance: {}   FPS:  {}
Auto Rate (Speed): {}   Frame Number: {}   Long frame rate: {}
Void Radius: {}  Local Rotate: {}  rotorigin: {}""".format(
screenDepth,
len(particleList),
G,
delta,
paused,
pan,
rotate,
camera.trackDistance,
int(frameRate),
round(camera.autoRate(PAN_RATE), 5),
frameCount,
longFrameRate,
voidRadius,
camera.rotateLocal,
camera.rotorigin.elements
)
    return data


kill = False
frameRate = 1
longFrameRate = 1
frameCount = 0
# for i in range(limit):
frameStart = time.time()
longFrameStart = frameStart
warning = False
if START_PAUSED: pause()

if testMode: middleTime = time.time()

setup()

A = angleVector([5 * pi/6, 0])
B = angleVector([7 * pi/6, 0])
I = angleVector([0, 0])
J = angleVector([pi/2, 0])
K = angleVector([pi, 0])
L = angleVector([3 * pi/ 2,0])



while running:
    if kill:
        turtle.exit()
        break
    # side = side * -1
    particleList = [[x.pos.elements[2], x] for x in particleList] # Order the particles by Z position so they are drawn in the right forward/backward arrangement
    try:
        particleList.sort(reverse=True)
    except TypeError:
        # print("Not sorted")
        pass # Occurs when two particles have the same z value, python doesn't know how to order them.

    particleList = [x[1] for x in particleList]

    camera.doAll(pan, rotate, smoothFollow = SMOOTH_FOLLOW, smoothRotate = SMOOTH_ROTATE)


    turtle.clear()
    for p in particleList:
        p.step(delta, onlyDraw = paused)

    # aPos = a.getCentre()
    # a.translate(vector([-1, -1, 1]))#aPos.subtract(vector([0, 0, 200])).setMag(1).reverse())
    # a.draw()

    frameEnd = time.time()
    frameLength = frameEnd - frameStart
    frameStart = time.time()
    if frameLength !=0 : frameRate = 1/frameLength


    if frameRate < 1 and autoAbort:
        # This algorithm will stop the simulation if the frame rate is less than
        # 1 fps for 2 consecutive frames. This is sometimes a problem if the camera
        # is very close to particles, strange things happen for some reason.
        if warning:
            if frameCount - warningFrame < 2:
                print("Abort!!!")
                running = False
            else:
                warningFrame = frameCount
        else:
            print("Warning!")
            warningFrame = frameCount
            warning = True
    else:
        warning = False

    if frameCount >= 30:
        frameCount = 0
        longFrameEnd = frameEnd
        longFrameRate = int(30/(longFrameEnd - longFrameStart))
        longFrameStart = frameStart
    frameCount += 1

    # particles = ""
    # for p in particleListSort:
    #     particles += "Pos: " + str([int(p.pos.elements[0]), int(p.pos.elements[1]), int(p.pos.elements[2])]) + ", Vel: " + str([int(p.vel.elements[0]), int(p.vel.elements[1]), int(p.vel.elements[2])]) + ", Acc: " + str([p.acc.elements[0], p.acc.elements[1], p.acc.elements[2]])
    #     if camera.track == p:
    #         particles += str(int(p.vel.getMag())) + " <----------"
    #     particles += "\n"
    #
    # print(particles)


    data = makeData()
    if showData == 1: writeText(data, - turtle.window_width()/2 + 10, turtle.window_height()/2 - 60, colour=[min(1, 10/frameRate), min(1, max((frameRate-10)/10, 0)), 0])
    turtle.update()

if testMode:
    programEnd = time.time()
    elapsed = programEnd - programStart
    first, second = middleTime- programStart, programEnd - middleTime

    print("Total time elapsed:         %s" %(elapsed))
    print("Prior to loop/During loop:  %s/\t%s" %(first, second))
    print("Average time per iteration: %s" %(second/testLimit))
