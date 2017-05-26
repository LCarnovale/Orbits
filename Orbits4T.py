# Author: Leo Carnovale (leo.carnovale@gmail.com / l.carnovale@student.unsw.edu.au)
# Date  : April to May ish?
# Orbits 4T


from tkinter import *
from math import *
import turtle
import random
import time


LINUX = False # If true, then non alphanumeric key controls will be replaced with numbers


# args:
# <key> : [<type>, <default value>, <requires parameter>, [<second default value>]]
# second default value is only necessary if <requires parameter> is true.
# if true, then the algorithm looks for a value after the key.
# if false, the algorithm still looks for a value after the key but if no value given the second default value is used.
        #     PUT DEFAULTS HERE
args = {#       \/
"-?" :  [None],
"-d" :  [float, 0.05,   True], # Delta time per step
"-n" :  [int,   10,     True], # Particle count
"-p" :  [int,   0,      True], # preset
"-sp":  [str,   False,  False,  True], # start paused
"-ss":  [str,   False,  False,  True], # staggered simulation
"-g" :  [float, 20,     True],  # Gravitational constant
"-w" :  [float, 500,    True],  # Window width
"-h" :  [float, 600,    True],  # Window height
"-pd":  [str,   False,  False,  True], # Print data
"-sd":  [float, 1500,   True],  # Default screen depth
"-ps":  [float, 5.0,    True],  # Maximum pan speed
"-rs":  [float, 0.1,    True],  # Rotational speed
"-mk":  [str,   False,  False,  True], # Show marker points
"-ep":  [int,   360,    True],  # Number of points on each ellipse (Irrelevant if SMART_DRAW is on)
"-sf":  [float, 0.5,    True],  # Rate at which the camera follows its target
"-ad":  [str,   False,  False,  True]  # Always draw. Attempts to draw particles even if they are thought not to be on screen
}


if len(sys.argv) > 1:
    if ("-?" in sys.argv):
        # Enter help mode
        print("Welcome to Orbits4T!")

        print("""
Arguments:
-? : Enter this help screen
-d :*   float,     Delta time per step
-n :*   int,       Particle count.
-p :*   int,       Preset (Not used in this version)
-sp:    string,    Start paused
-ss:    string,    Staggered simulation (Hit enter in the terminal to trigger each frame)
-g :*   float,     Gravitational constant
-w :*   float,     Window width (Not used in thie version)
-h :*   float,     Window height (Not used in thie version)
-pd:    string,    Print debugging data
-sd:*   float,     Default screen depth
-ps:*   float,     Maximum pan speed
-rs:*   float,     Rotational speed
-mk:    string,    Show marker points (static X, Y, Z and Origin coloured particles)
-ep:*   int,       Number of points on each ellipse (Irrelevant if SMART_DRAW is on (which it is))
-sf:*   float,     Rate at which the camera follows its target
-ad:    string,    Always draw. Attempts to draw particles even if they are thought not to be on screen
(*) indicates a parameter is required after the argument

Using the program:
  - Use W, A, S, D to move forwards, left, backwards, and right respectively.
  - Use R, F to move up and down respectively.
  - Space to pause the simulation. (Movement is still allowed)
  - Click any particle to set the camera to track that particle.
  - To stop tracking, click empty space or another particle.

""")

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

        else:
            if (arg[0] == "-"):
                print("Unrecognised argument: '%s'" % (arg))
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
rotSpeed                = args["-rs"][1]
showMarkers             = args["-mk"][1]
ellipsePoints           = args["-ep"][1]
SMOOTH_FOLLOW           = args["-sf"][1]
ALWAYS_DRAW             = args["-ad"][1]

AUTO_RATE_CONSTANT  = 100       # A mysterious constant which determines the autoRate speed, 100 works well.

defaultDensity      = 1
radiusLimit         = 50        # Maximum size of particle
voidRadius          = 5000      # Maximum distance of particle from camera

AUTO_ABORT          = True      # I wouldn't change this unless you know the programs good to go

particleList = [ ]


DEFAULT_ZERO_VEC = [0, 0, 0]
DEFAULT_UNIT_VEC = [1, 0, 0]

CAMERA_UNTRACK_IF_DIE = True

def setup():
    # a = particle(1, vector([25, 1, 0]))
    # camera.drawParticle(a)
    if showMarkers:
        O = marker(vector([0,   0, 0]), [1, 1, 1])
        X = marker(vector([100, 0, 0]), [1, 0, 0])
        Y = marker(vector([0, 100, 0]), [0, 1, 0])
        Z = marker(vector([0, 0, 100]), [0, 0, 1])

def roundList(list, places):
    return [round(x, places) for x in list]

window = turtle.Screen()
window.setup(width = 1.0, height = 1.0)
turtle.bgcolor("black")

turtle.tracer(0, 0)             # Makes the turtle's speed instantaneous
turtle.hideturtle()

SMART_DRAW = True               # Changes the number of points on each ellipse
                                # depending on its size
SMART_DRAW_PARAMETER = 5        # Approx number of pixels between each point

MAX_POINTS = 800                # Lazy way of limiting the number of points drawn to stop the program
                                # grinding to a halt everytime you get too close to a particle

def drawOval(x, y, major, minor, angle, fill = "black"):
    global ellipsePoints
    if SMART_DRAW:
        perimApprox = 2*pi*sqrt((major**2 + minor**2) / 2)
        points = int(perimApprox / SMART_DRAW_PARAMETER)
    else:
        points = ellipsePoints
    points = min(points, MAX_POINTS)
    turtle.up()
    localX = major/2
    localY = 0
    screenX = localX * cos(angle) - localY * sin(angle)
    screenY = localY * cos(angle) + localX * sin(angle)
    turtle.goto(x + screenX, y + screenY)
    turtle.begin_fill()
    turtle.fillcolor(fill)
    onScreen = True
    Drawn = False
    for i in range(points):
        localX = major/2 * cos(2 * pi * i / points)
        localY = minor/2 * sin(2 * pi * i / points)
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
        self.minDistance = None
        self.pause = -1 # 1 for pause, -1 for not paused.

        self.clickTarget = None

        self.frameWarning = False

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

    def abort(self):
        print("Auto Aborting!!!")

        exit()

    def STEP(self, delta, camera, draw = True):
        # I think it would be slightly more effecient to only do an if comparison once,
        # even if means a few lines are duplicated.

        # drawLine((-500, 0), (500, 0), fill = [1, 1, 1])
        global particleList

        camera.panFollow()

        if (pan[-1] == False and self.minDistance != None):
            panAmount = self.minDistance * maxPan/(self.minDistance + AUTO_RATE_CONSTANT)
        else:
            panAmount = maxPan

        if ([0, 0, 0] not in pan):
            camera.pan(pan, panAmount)
        if (rotate != [0, 0]):
            camera.rotate(rotate, rotSpeed)

        frameStart = time.time()
        if draw:
            self.minDistance = None
            for m in sorted(markerList, key = lambda x: abs(x.pos - camera.pos), reverse = True):
                camera.drawParticle(m)
            # if not particleList:
            #     return None
            if (self.clickTarget):
                camera.panTrackSet()

            for I in range(len(particleList)):
                # print("I: %d" % (I))
                p = particleList[I]
                if (I > 0 and (abs(p.pos - camera.pos) > abs(particleList[I - 1].pos - camera.pos))):
                    # Swap the previous one with the current one
                    particleList = particleList[:I - 1] + [particleList[I], particleList[I-1]] + particleList[I + 1:]

                if (self.minDistance == None):
                    self.minDistance = abs(p.pos - camera.pos) - p.radius
                elif ((abs(p.pos - camera.pos) - p.radius) < self.minDistance):
                    self.minDistance = abs(p.pos - camera.pos) - p.radius
                if (self.pause == -1):
                    p.step(delta)
                if (abs(self.commonShiftPos != 0) or abs(self.commonShiftVel) != 0):
                    p.pos.addToMe(self.commonShiftPos)
                    p.pos.addToMe(self.commonShiftVel.multiply(delta))
                buff = Buffer.processPosition(p)
                if not buff:
                    drawResult = camera.drawParticle(p)
                    if (self.clickTarget):
                        # print("clicked")
                        if (drawResult):
                            # print("%s, drawResult[2, 3]: %lf, %lf. |p - click| = %lf" % (str(vector(self.clickTarget[:-1]) - vector(drawResult[0:2])),
                            #                                         drawResult[2], drawResult[3], abs(vector(self.clickTarget[:-1]) - vector(drawResult[0:2]))
                            #                                         ))
                            if (abs(vector(self.clickTarget[:-1]) - vector(drawResult[0:2])) < drawResult[2]):
                                if (self.clickTarget[2] == 0):
                                    # Left click
                                    camera.panTrackSet(p)
                else:
                    camera.drawAt(buff)
        else:
            for p in particleList:
                p.step(delta)

        frameEnd = time.time()
        frameLength = frameEnd - frameStart
        if (frameLength == 0):
            FPS = -1
        else:
            FPS = 1 / frameLength

        # print("FPS:", FPS)
        if (AUTO_ABORT):
            if (FPS < 1 and FPS != -1):
                if (self.frameWarning):
                    self.abort()
                else:
                    self.frameWarning = True
            else:
                self.frameWarning = False


        self.clickTarget = None
        self.Zero()


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

    def __iadd__(self, other):
        self.addToMe(other)
        return self

    def __isub__(self, other):
        self.subtractToMe(other)
        return self

    def __neg__(self):
        return self.reverse()

    def __str__(self):
        return ("<" + ", ".join([str(x) for x in self.elements]) + ">")

    def __repr__(self):
        return self.elements

    def __getitem__(self, value):
        return self.elements[value]

    def __mul__(self, value):
        if (type(value) in [int, float]):
            return self.multiply(value)
        else:
            return 0
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
            cosTheta = self.dot(other) / (self.getMag() * other.getMag())
            return acos(cosTheta)
        else:
            angleSelf = self.lock(plane).getHeading(plane[0], trueBearing = plane[1])
            angleOther = other.lock(plane).getHeading(plane[0], trueBearing = plane[1])
            angle = angleSelf - angleOther
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


class camera:
    # Main job: work out where a dot should go on the screen given the cameras position and rotation and the objects position.
    def __init__(self, pos = vector(DEFAULT_ZERO_VEC), rot = vector(DEFAULT_UNIT_VEC), vel = vector(DEFAULT_ZERO_VEC), screenDepth = DEFAULT_SCREEN_DEPTH):
        self.pos = pos
        self.rot = rot.setMag(1)
        self.vel = vel
        self.panTrack = None
        self.rotTrack = None
        self.trackDistance = 100
        self.rotTrackOrigin = DEFAULT_UNIT_VEC
        self.screenDepth = screenDepth
        self.screenXaxis = vector([-self.rot[2], 0, self.rot[0]]).setMag(1)
        self.screenYaxis = vector([self.rot[0] * self.rot[1], -(self.rot[0]**2 + self.rot[2]**2), self.rot[2] * self.rot[1]]).setMag(1)

        print(self.pos)
        print(atan((turtle.window_width()/2) / self.screenDepth))
        print(atan((turtle.window_height()/2) / self.screenDepth))

    def pan(self, direction, rate):
        # Direction as a vector
        if PRINT_DATA: print("direction[0] = {}, rate = {}, self.rot[0] = {}".format(direction[0], rate, self.rot[0]))
        screenZaxis = self.rot.setMag(1)
        if self.panTrack == None:
            self.pos += ((self.screenXaxis * direction[2]) + (self.screenYaxis * -direction[1]) + (screenZaxis * direction[0])) * -rate
        else:
            self.trackDistance += direction[0] * rate
    def rotate(self, direction, rate):
        # direction as a 2 element list [x, y]
        self.screenXaxis = self.screenXaxis.rotateAbout(self.screenYaxis, direction[0] * rate)
        self.screenYaxis = self.screenYaxis.rotateAbout(self.screenXaxis, direction[1] * rate)
        self.rot = self.screenXaxis.cross(self.screenYaxis)
        self.rot.setMag(1)
        if (self.panTrack):     # Makes the rotation appear to be about the centre of the tracked particle
            self.panFollow(1)   # There is probably a better way to do this, this way is a bit shifty


    def panTrackSet(self, target = None):
        self.panTrack = target
        return target

    def rotTrackSet(self, target = None):
        self.rotTrack = target
        return target

    def autoRate(self, rate, distance):
        newRate = dist * rate/(dist + AUTO_RATE_CONSTANT)
        return newRate

    def zeroCameraPosVel(self):
        MainLoop.commonShiftPos = self.pos.negate()
        MainLoop.commonShiftVel = self.vel.negate()

    def drawParticle(self, particle, drawAt = False):
        # drawAt: if the desired particle isn't actually where we want to draw it, parse [pos, radius [, colour]] and set drawAt = True
        # self.rot.setMag(1)
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
        if (relPosition.dot(self.rot) <= 0):
            # Only condition to exit draw if ALWAYS_DRAW is True
            return False
        ScreenParticleDistance = sd * abs(relPosition) * abs(self.rot) / (relPosition.dot(self.rot)) #self.screenDepth * relPosition.getMag() / self.rot.dot(relPosition) # A factor to multiply the relPosition vector by to get a vector on a plane on the screen.
        relPosOnScreen = relPosition.multiply(ScreenParticleDistance/abs(relPosition))
        relPosUnit = relPosition.multiply(1 / abs(relPosition))
        relRotation = relPosUnit - self.rot

        rp = particle.radius
        SD = self.screenDepth
        CP = pos - self.pos


        x_r, y_r, z_r = self.rot.elements
        x_CSP, y_CSP, z_CSP = relPosOnScreen.elements
        x_CSC, y_CSC, z_CSC = scrCent.elements

        X = relPosOnScreen.dot(self.screenXaxis) / abs(self.screenXaxis)
        Y = relPosOnScreen.dot(self.screenYaxis) / abs(self.screenYaxis)

        # X = (-(x_CSP - x_CSC) * z_r + (z_CSP - z_CSC) * x_r) * (x_r ** 2 + z_r ** 2) ** (-1 / 2)
        # Y = -((x_CSP - x_CSC) * x_r * y_r + (y_CSP - y_CSC) * (-x_r ** 2 - z_r ** 2) + (z_CSP - z_CSC) * z_r * y_r) * (x_r ** 2 * y_r ** 2 + (-x_r ** 2 - z_r ** 2) ** 2 + z_r ** 2 * y_r ** 2) ** (-1 / 2)


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
        if (not ALWAYS_DRAW and ((abs(centreAngleX) - abs(offset)) > screenAngleX or (abs(centreAngleY) - abs(offset)) > screenAngleY)):
            prin = prin + ("Outside of screen, x angle: " + str(centreAngleX) + ", y angle: " + str(centreAngleY) + ", offset: " + str(offset))
            return False

        majorAxis = 2 * (sqrt(X ** 2 + Y ** 2) - self.screenDepth * tan(atan(sqrt(X ** 2 + Y ** 2)/self.screenDepth) - offset))
        minorAxis = 2 * self.screenDepth * tan(offset)
        if X != 0:
            angle = atan(Y / X)
        elif X == 0 and Y == 0:
            angle = 0
        elif ALWAYS_DRAW:
            angle = pi/2
        else:
            # angle is +- pi/2, which wouldn't appear on the screen.
            prin += "CentreX = 0 != centreY, particle is perpendicular to camera. This shouldn't be possible?"
            if PRINT_DATA: print(prin)
            return False
        drawOval(X, Y, majorAxis, minorAxis, angle, colour)
        prin = prin + ("X: " + str(round(X, 5)) + ", Y: " + str(round(Y, 5)))
        if PRINT_DATA: print(prin)
        return [X, Y, majorAxis, minorAxis]

    def drawAt(self, posVector, radius, colour = None):
        return self.drawParticle([posVector, radius, colour], True)

    def panFollow(self, followRate=None):
        global SMOOTH_FOLLOW
        if (followRate == None):
            followRate = SMOOTH_FOLLOW
        if self.panTrack == None: return False
        self.pos += ((self.panTrack.pos - (self.rot * self.trackDistance)) - self.pos) * followRate



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
            if p != self and type(p) != marker:
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
        self.pos = randomVector(3, radius * 0.99) + camera.pos
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
                camera.panTrackSet(killer)
            self.respawn()
        else:
            if self in particleList:
                if camera.panTrack: camera.panTrackSet()
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

markerList = []

class marker(particle):
    def __init__(self, position, colour, radius = 20):
        self.pos = position
        self.colour = colour
        self.radius = radius
        markerList.append(self)
    def set_colour(self, colour):
        self.colour = colour

    def step(self, delta):
        pass


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



autoRateValue = maxPan
pan = [0, 0, 0, False]
shiftL = False
rotate = [0, 0]
def panLeft():
    if pan[2] < 1:
        pan[2] += 1

def panRight():
    if pan[2] > - 1:
        pan[2] -= 1

def panForward():
    if pan[0] > - 1:
        pan[0] -= 1

def panBack():
    if pan[0] < 1:
        pan[0] += 1

def panDown():
    if pan[1] > - 1:
        pan[1] -= 1

def panUp():
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

def rotLeft():
    if rotate[0] < 1:
        rotate[0] = rotate[0] + 1

def rotRight():
    if rotate[0] > -1:
        rotate[0] = rotate[0] - 1

def rotDown():
    if rotate[1] < 1:
        rotate[1] += 1

def rotUp():
    if rotate[1] > -1:
        rotate[1] -= 1

def escape():
    global Running
    Running = False

def pause():
    MainLoop.pause *= -1

def leftClick(x, y):
    MainLoop.clickTarget = [x, y, 0]    # 0 for left click, 1 for right

def rightClick(x, y):
    MainLoop.clickTarget = [x, y, 1]    # 0 for left click, 1 for right


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

turtle.onkey(escape, "Escape")
turtle.onkey(pause,  "space")

turtle.onscreenclick(leftClick, 1)
turtle.onscreenclick(rightClick, 3)

turtle.listen()

DEFAULT_ZERO_VEC = vector(DEFAULT_ZERO_VEC)
DEFAULT_UNIT_VEC = vector(DEFAULT_UNIT_VEC)
Buffer = buffer()
MainLoop = MainLoop()
# camera = camera(rot = vector([0.60275, 0.72042, 0.34307]))
camera = camera()

setup()
Running = True
particle(25000, vector([150 + DEFAULT_SCREEN_DEPTH, 0, 0]))
for i in range(PARTICLE_COUNT):
    particle(150, vector([150 + DEFAULT_SCREEN_DEPTH, 0, 0]) + randomVector(3, 50, 400)).circularise(particleList[0])
# particle(150, vector([223.43434, 266.12801, 157.37214]), vector([0, 0, 0]))

while Running:
    turtle.clear()
    if STAGGERED_SIM: input()
    MainLoop.STEP(Delta, camera)
    # for p in particleList:
    #     print(p, p.pos.elements, p.vel.elements, p.acc.elements)
    # print("step")
    if PRINT_DATA: print(particleList[0], particleList[0].pos.elements, particleList[0].vel.elements)
    # camera.rot.setHeading(pi/360, plane = [0,2], increment = True)
    turtle.update()






        # self.vel.elements[2] = speed + other.vel.elements[2]
