from tkinter import *
from math import *
import turtle
import random


LINUX = False # If true, then non alphanumeric key controls will be replaced with numbers

# val
mem = {}
class val:
    address = 0
    def __init__(self, value):
        mem[len(mem)] = value
        self.address = len(mem) - 1
    def set(self, value):
        mem[self.address] = value
    def __call__(self):
        return mem[self.address]




# args:
# <key> : [<type>, <default value>, <requires parameter>, [<second default value>]]
# second default value is only necessary if <requires parameter> is true.
# if true, then the algorithm looks for a value after the key.
# if false, the algorithm still looks for a value after the key but if no value given the second default value is used.
        #     PUT DEFAULTS HERE
args = {#       \/
"-d" :  [float, 0.05,   True], # Delta time per step
"-n" :  [int,   10,     True], # Particle count
"-p" :  [int,   0,      True], # preset
"-sp":  [str,   False,  False,  True], # start paused
"-ss":  [str,   False,  False,  True], # staggered simulation
"-g" :  [float, 500,    True],  # Gravitational constant
"-w" :  [float, 500,    True],  # Window width
"-h" :  [float, 600,    True],  # Window height
"-pd":  [str,   False,  False,  True], # Print data
"-sd":  [float, 500,    True],  # Default screen depth
"-ps":  [float, 1.0,    True]   # Maximum pan speed
}

# "-d":[int, None, True],
# "-p":[float, None, True],
# "-b":[str, False, False, True],
# "-w":[str, False, False, True],
# "-c":[str, False, False, True]
# }

if len(sys.argv) > 1:

    if sys.argv[1] not in args:
        mode = 0
    else:
        for i, arg in enumerate(sys.argv):
            if arg in args:
                try:
                    if args[arg][2]:
                        if sys.argv[i + 1] in args:
                            raise IndexError # If the next arg is an arg keyword (eg -p, -d) then the parameter is missing
                        args[arg][1] = args[arg][0](sys.argv[i + 1])
                    else: # No parameter needed, set it to args[arg][3]
                        args[arg][1] = args[arg][3]
                except ValueError:
                    print("Wrong usage of {}".format(arg))
                except IndexError:
                    print("Missing parameter for {}.".format(sys.argv[i]))
                # except

Delta                   = args["-d"][1]
PARTICLE_COUNT          = args["-n"][1]
preset                  = args["-p"][1]
STAGGERED_SIM           = args["-ss"][1]
G                       = args["-g"][1]
INITIAL_WINDOW_WIDTH    = args["-w"][1]
INITIAL_WINDOW_HEIGHT   = args["-h"][1]
PRINT_DATA              = args["-pd"][1]
DEFAULT_SCREEN_DEPTH    = args["-sd"][1]
maxPan                  = args["-ps"][1]


defaultDensity = 1
radiusLimit = 50
voidRadius = 1000

particleList = []


DEFAULT_ZERO_VEC = [0, 0, 0]
DEFAULT_UNIT_VEC = [1, 0, 0]

# STAGGERED_SIM = True

CAMERA_UNTRACK_IF_DIE = True
# G = 500 # Gravitational Constant

# master = Tk()
# screen = Canvas(master, width = INITIAL_WINDOW_WIDTH, height = INITIAL_WINDOW_HEIGHT)
# screen.pack()
# canvas_width = INITIAL_WINDOW_WIDTH
# canvas_height = INITIAL_WINDOW_HEIGHT

def setup():
    # a = particle(1, vector([25, 1, 0]))
    # camera.drawParticle(a)
    pass

def roundList(list, places):
    return [round(x, places) for x in list]

window = turtle.Screen()
window.setup(width = 1.0, height = 1.0)
turtle.bgcolor("black")

turtle.tracer(0, 0) # Makes the turtle's speed instantaneous
turtle.hideturtle()



# def drawDot(x, y, r, fill = "black"):
#     screenWidth = screen.winfo_width()
#     screenHeight = screen.winfo_height()
#     x += screenWidth/2
#     y = screenHeight/2 - y
#     id = screen.create_oval(x - r, y - r, x + r, y + r, fill = fill, outline = fill)
#     return id
#
#
# def drawDot(x, y, r, Fill=True, colour = [0, 0, 0], actualRadius = 0):
#     # Draws a dot on the canvas
#     # global turtle
#     if (abs(x) - abs(r) > turtle.window_width() / 2 or abs(y) - abs(r) > turtle.window_height()):
#         return False
#     if not actualRadius:
#         actualRadius = r
#     if Fill:
#         turtle.up()
#         turtle.goto(x, y)
#         if colourful:
#             turtle.pencolor([actualRadius/radiusLimit, 0, (radiusLimit - actualRadius)/radiusLimit])
#         else:
#             turtle.pencolor(colour)
#         turtle.dot(2 * r)
#     else:
#         turtle.up()
#         turtle.goto(x, y - r)
#         turtle.down()
#         turtle.circle(r)
#         turtle.up()

def drawOval(x, y, major, minor, angle, fill = "black"):
    # screenWidth = screen.winfo_width()
    # screenHeight = screen.winfo_height()
    # x1, x2 = x1 + screenWidth/2, x2 + screenWidth/2
    # y1, y2 = screenHeight/2 - y1, screenHeight/2 - y2

    # id = screen.create_oval(x1, y1, x2, y2, fill = fill, outline = fill)

    # conversion of axes: local axis x, screen axis x'
    # x' = x cos(shift) - y sin(shift)
    # y' = y cos(shift) + x sin(shift)
    turtle.up()
    localX = major/2
    localY = 0
    screenX = localX * cos(angle) - localY * sin(angle)
    screenY = localY * cos(angle) + localX * sin(angle)
    turtle.goto(x + screenX, y + screenY)
    turtle.begin_fill()
    turtle.fillcolor(fill)
    for i in range(360):
        localX = major/2 * cos(pi * i / 180)
        localY = minor/2 * sin(pi * i / 180)
        screenX = localX * cos(angle) - localY * sin(angle)
        screenY = localY * cos(angle) + localX * sin(angle)
        turtle.goto(x + screenX, y + screenY)
    turtle.end_fill()

    return True

def drawLine(pointA, pointB = None, fill = "black", width = 1):
    if (pointB == None):
        x1, y1 = (0, 0)
        x2, y2 = pointA
    else:
        x1, y1 = pointA
        x2, y2 = pointB

    turtle.pencolor(fill)
    turtle.up()
    turtle.goto(x1, y1)
    turtle.down()
    turtle.goto(x2, y2)
    turtle.up()



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

    def addBuffer(self, particle, colour = None):
        self.buffer[particle].append([particle.pos, particle.radius, particle.colour])

    def playBuffer(self, particle, index = 0, remove = True):
        buff = self.buffer[particle][index]
        if remove:
            self.buffer[particle].pop(index)
        return buff

    def processPosition(self, particle, defaultIndex = 0, playIndex = 0, playRemove = True):
        # A kind of autopilot, takes in a position and returns basically what the camera should see.
        if self.bufferMode == 2:
            # playing
            return self.playBuffer(particle, playIndex, playRemove)
        elif self.bufferMode == 1:
            # recording. Don't let the particle move.
            self.addBuffer(particle)
            return self.buffer[particle][defaultIndex]
        else:
            return False

        # if default == 0:


class MainLoop:
    def __init__(self):
        # Records the movements to all particles
        self.commonShiftPos = DEFAULT_ZERO_VEC
        self.commonShiftVel = DEFAULT_ZERO_VEC
        self.commonRotate = DEFAULT_ZERO_VEC

    def Zero(self):
        self.commonShiftPos = DEFAULT_ZERO_VEC
        self.commonShiftVel = DEFAULT_ZERO_VEC
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

        # drawLine((-500, 0), (500, 0), fill = [1, 1, 1])

        if draw:
            for p in particleList:
                p.step(delta)
                p.pos.addToMe(self.commonShiftPos)
                p.pos.addToMe(self.commonShiftVel.multiply(delta))
                buff = Buffer.processPosition(p)
                if not buff:
                    camera.drawParticle(p)
                        # print("Particle pos and vel:", roundList(p.pos.elements, 5), roundList(p.vel.elements, 5))
                else:
                    camera.drawAt(buff)
        else:
            for p in particleList:
                p.step(delta)
        self.Zero()


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

    def __str__(self):
        return str(self.elements)

    def __repr__(self):
        return self.elements

    def __getitem__(self, value):
        return self.elements[value]

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
            self.elements[plane[0]] = radius * cos(angle)
            self.elements[plane[1]] = radius * sin(angle)


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


class camera:
    # Main job: work out where a dot should go on the screen given the cameras position and rotation and the objects position.
    def __init__(self, pos = vector(DEFAULT_ZERO_VEC), rot = vector(DEFAULT_UNIT_VEC), vel = vector(DEFAULT_ZERO_VEC), screenDepth = DEFAULT_SCREEN_DEPTH):
        self.pos = pos
        self.rot = rot.setMag(1)
        self.vel = vel
        self.panTrack = None
        self.rotTrack = None
        self.trackSeparation = 0
        self.rotTrackOrigin = DEFAULT_UNIT_VEC
        self.screenDepth = screenDepth
        print(self.pos)
        print(atan((turtle.window_width()/2) / self.screenDepth))
        print(atan((turtle.window_height()/2) / self.screenDepth))

    def panTrackSet(self, target = None):
        self.panTrack = target
        return target

    def rotTrackSet(self, target = None):
        self.rotTrack = target
        return target

    def zeroCameraPosVel(self):
        MainLoop.commonShiftPos = self.pos.negate()
        MainLoop.commonShiftVel = self.vel.negate()

    def drawParticle(self, particle, drawAt = False):
        # drawAt: if the desired particle isn't actually where we want to draw it, parse [pos, radius [, colour]] and set drawAt = True
        # default max angles:
        # 0.3455555805817121
        # 0.23010109289662406
        prin = "-\n"
        screenAngleX = atan((turtle.window_width()/2) / self.screenDepth)
        screenAngleY = atan((turtle.window_height()/2) / self.screenDepth)
        if drawAt:
            pos = particle[0]
            radius = particle[1]
            colour = particle[2]
        else:
            pos = particle.pos
            radius = particle.radius
            colour = particle.colour

        # Get relative position to camera's position.
        sd = self.screenDepth
        scrCent =  self.rot.getClone().setMag(self.screenDepth)

        relPosition = pos - self.pos
        ScreenParticleDistance = sd * relPosition.getMag() * self.rot.getMag() / (relPosition.dot(self.rot)) #self.screenDepth * relPosition.getMag() / self.rot.dot(relPosition) # A factor to multiply the relPosition vector by to get a vector on a plane on the screen.
        relPosOnScreen = relPosition.multiply(ScreenParticleDistance/relPosition.getMag())
        relPosUnit = relPosition.multiply(1 / relPosition.getMag())
        relRotation = relPosUnit - self.rot

        # normal = vector([relPosOnScreen[0] - scrCent[2], relPosOnScreen[1], relPosOnScreen[2] + scrCent[0]])
        # R = scrCent - relPosOnScreen
        # X = normal.dot(R) / ScreenParticleDistance
        # PZ = normal.getClone().setMag(X)
        # CZ = relPosOnScreen + PZ
        # print("R   :", R)
        # print("X   :", X)
        # print("PZ  :", PZ)
        # print("CZ  :", CZ)
        # print("|CZ|:", CZ.getMag())
        # Y = sqrt(CZ.getMag() ** 2 - self.screenDepth ** 2)
        rp = particle.radius
        SD = self.screenDepth
        CP = pos - self.pos
        theta = acos(CP.dot(self.rot) / abs(CP))


        x_r, y_r, z_r = self.rot.elements
        # x_P, y_P, z_P = pos.elements
        # x_C, y_C, z_C = self.pos.elements
        x_CSP, y_CSP, z_CSP = relPosOnScreen.elements
        x_CSC, y_CSC, z_CSC = scrCent.elements

        X = (-(x_CSP - x_CSC) * z_r + (z_CSP - z_CSC) * x_r) * (x_r ** 2 + z_r ** 2) ** (-1 / 2)
        Y = ((x_CSP - x_CSC) * x_r * y_r + (y_CSP - y_CSC) * (-x_r ** 2 - z_r ** 2) + (z_CSP - z_CSC) * z_r * y_r) * (x_r ** 2 * y_r ** 2 + (-x_r ** 2 - z_r ** 2) ** 2 + z_r ** 2 * y_r ** 2) ** (-1 / 2)
        # X = ((SD * x_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (x_P - x_C)) * (-z_P + z_C) + (SD * z_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (z_P - z_C)) * (x_P - x_C)) * ((-z_P + z_C) ** 2 + (x_P - x_C) ** 2) ** (-1 / 2)
        # Y = sqrt((SD * x_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (x_P - x_C)) ** 2 + (SD * y_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (y_P - y_C)) ** 2 + (SD * z_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (z_P - z_C)) ** 2 - ((SD * x_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (x_P - x_C)) * (-z_P + z_C) + (SD * z_r - 1 / SD * (x_r * (x_P - x_C) + y_r * (y_P - y_C) + z_r * (z_P - z_C)) * (z_P - z_C)) * (x_P - x_C)) ** 2 / ((-z_P + z_C) ** 2 + (x_P - x_C) ** 2))



        # majorAxis = SD * (2 * rp * (abs(CP)**2 - rp**2)**(3/2) / (abs(CP)**4 * cos(theta)**2) - sin(theta)**2 * rp**2 / abs(CP)**2)
        # minorAxis = SD * 2 * rp / (abs(CP)**2 - rp**2)**(1/2)




        centreAngleX = acos((2 - relRotation.lock([0, 2]).getMag() ** 2) / 2)
        centreAngleY = acos((2 - relRotation.lock([0, 1]).getMag() ** 2) / 2)
        prin += "centreAngleX: " + str(round(centreAngleX, 5)) + ", centreAngleY: " + str(round(centreAngleY, 5)) + "\n"
        # offset: angle either side of centre angle which is slightly distorted due to the 3d bulge of the sphere.
        distance = relPosition.getMag()
        if (radius >= distance):
            prin += ("Inside particle, not drawing")
            if PRINT_DATA: print(prin)
            return False
        offset = asin(radius/distance)
        # centreX = tan(centreAngleX) * self.screenDepth
        # centreY = tan(centreAngleY) * self.screenDepth
        # print(centreAngleX, centreAngleY, centreX)
        if (abs(centreAngleX) - abs(offset)) > screenAngleX or (abs(centreAngleY) - abs(offset)) > screenAngleY:
            prin = prin + ("Outside of screen, x angle: " + str(centreAngleX) + ", y angle: " + str(centreAngleY) + ", offset: " + str(offset))
            # if PRINT_DATA: print(prin)
            return False

        # Major axis = 2 * (sqrt(x^2 + y^2) - screenDepth * tan(atan(sqrt(x^2 + y^2)/screenDepth) - offset))
        majorAxis = 2 * (sqrt(X ** 2 + Y ** 2) - self.screenDepth * tan(atan(sqrt(X ** 2 + Y ** 2)/self.screenDepth) - offset))
        minorAxis = 2 * self.screenDepth * tan(offset)
        if X != 0:
            angle = atan(Y / X)
        elif X == 0 and Y == 0:
            angle = 0
        else:
            # angle is +- pi/2, which wouldn't appear on the screen.
            prin += "CentreX = 0 != centreY, particle is perpendicular to camera. This shouldn't be possible?"
            if PRINT_DATA: print(prin)
            return False
        drawOval(X, Y, majorAxis, minorAxis, angle, colour)
        # return relPosition
        prin = prin + ("X: " + str(round(X, 5)) + ", Y: " + str(round(Y, 5)))
        if PRINT_DATA: print(prin)
        return True

    def drawAt(self, posVector, radius, colour = None):
        return self.drawParticle([posVector, radius, colour], True)

    def panFollow(self):
        pass


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
        self.colour = [self.radius/radiusLimit, 0, (radiusLimit - self.radius)/radiusLimit]

    alive = True
    respawn = True
    density = defaultDensity
    specialColour = False
    colour = [0, 0, 0]

    inbound = False
    immune = False

    newMass = False # the mass of the particle after it respawns
    def setColour(self):
        self.colour = [self.radius/radiusLimit, 0, (radiusLimit - self.radius)/radiusLimit]

    def setRadius(self):
        self.radius = (0.75 * (self.mass/self.density) / pi) ** (1/3)
        self.setColour()

    def calcAcc(self, other):
        force = (G * self.mass * other.mass)/(self.pos.subtract(other.pos).getMag() ** 2)
        forceVector = other.pos.subtract(self.pos)
        # drawVector(forceVector.setMag(force/self.mass), self.pos)
        self.acc.addToMe(forceVector.setMag(force/self.mass))
        # print("calcAcc:", self.acc.elements)

    def checkCollision(self, other):
        if other.alive and (self.pos.subtract(other.pos).getMag() < self.radius + other.radius):
            self.contest(other)
            return True
        else:
            return False

    def runLoop(self):
        for p in particleList:
            if p != self:
                if not self.checkCollision(p):
                    self.calcAcc(p)


    def checkOutOfBounds(self): #bounds=[turtle.window_width()/2, turtle.window_height()/2]):
        # self.vel.multiplyToMe(0)
        # return
        if self.immune: return False
        out = False
        if self.pos.subtract(camera.pos).getMag() > voidRadius:
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
            if CAMERA_UNTRACK_IF_DIE and camera.panTrack == self:
                camera.setTrack(killer)
            self.respawn()
        else:
            if self in particleList:
                if camera.panTrack: camera.setTrack()
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
        # self.checkCollisionList(particleList)
        # self.calcAccList(particleList)
        self.runLoop()
        if self.radius > radiusLimit:
            self.die()
            return False
        self.vel.addToMe(self.acc.multiply(delta))
        self.pos.addToMe(self.vel.multiply(delta))
        self.checkOutOfBounds()
        # if self.acc.getMag(): #print(self.acc.elements)
        self.acc.multiplyToMe(0)

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

DEFAULT_ZERO_VEC = vector(DEFAULT_ZERO_VEC)
DEFAULT_UNIT_VEC = vector(DEFAULT_UNIT_VEC)
Buffer = buffer()
MainLoop = MainLoop()
# camera = camera(rot = vector([0.60275, 0.72042, 0.34307]))
camera = camera()

setup()
Running = True
particle(500, vector([150 + DEFAULT_SCREEN_DEPTH, 0, 0]))
for i in range(-5, 5):
    particle(150, vector([150 + DEFAULT_SCREEN_DEPTH, 150 * sin(i/5 * pi), 150 * cos(i/5 * pi)])).circularise(particleList[0])
# particle(150, vector([223.43434, 266.12801, 157.37214]), vector([0, 0, 0]))

while Running:
    turtle.clear()
    if STAGGERED_SIM: input()
    MainLoop.STEP(Delta)
    # for p in particleList:
    #     print(p, p.pos.elements, p.vel.elements, p.acc.elements)
    # print("step")
    if PRINT_DATA: print(particleList[0], particleList[0].pos.elements, particleList[0].vel.elements)
    # camera.rot.setHeading(pi/360, plane = [0,2], increment = True)
    turtle.update()






        # self.vel.elements[2] = speed + other.vel.elements[2]
