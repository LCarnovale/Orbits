# Author: Leo Carnovale (leo.carnovale@gmail.com / l.carnovale@student.unsw.edu.au)
# Date  : April to May ish?
# Orbits 4T


from tkinter import *
from math import *
import turtle
import random
import time
import vector

vector = vector.vector
# import sys

# print(sys.path)
# sys.path.append(sys.path.cur)


LINUX = False # If true, then non alphanumeric key controls will be replaced with numbers


# args:
# <key> : [<type>, <default value>, <requires parameter>, [<second default value>]]
# second default value is only necessary if <requires parameter> is true.
# if true, then the algorithm looks for a value after the key.
# if false, the algorithm still looks for a value after the key but if no value given the second default value is used.
        #     PUT DEFAULTS HERE
args = {#       \/
"-?" :  [None],
"-d" :  [float, 0.025,   True], # Delta time per step
"-n" :  [int,   20,     True], # Particle count
"-p" :  [int,   1,      True], # preset
"-sp":  [str,   False,  False,  True], # start paused
"-ss":  [str,   False,  False,  True], # staggered simulation
"-g" :  [float, 20,     True],  # Gravitational constant
"-w" :  [float, 500,    True],  # Window width
"-h" :  [float, 600,    True],  # Window height
"-pd":  [str,   False,  False,  True], # Print data
"-sd":  [float, 2000,   True],  # Default screen depth
"-ps":  [float, 5.0,    True],  # Maximum pan speed
"-rs":  [float, 0.01,    True],  # Rotational speed
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
-p :*   int,       Preset
-sp:    bool,      Start paused
-ss:    bool,      Staggered simulation (Hit enter in the terminal to trigger each frame)
-g :*   float,     Gravitational constant
-w :*   float,     Window width (Not used in thie version)
-h :*   float,     Window height (Not used in thie version)
-pd:    bool,      Print debugging data
-sd:*   float,     Default screen depth
-ps:*   float,     Maximum pan speed
-rs:*   float,     Rotational speed
-mk:    bool,      Show marker points (static X, Y, Z and Origin coloured particles)
-ep:*   int,       Number of points on each ellipse (Irrelevant if SMART_DRAW is on (which it is))
-sf:*   float,     Rate at which the camera follows its target
-ad:    bool,      Always draw. Attempts to draw particles even if they are thought not to be on screen
(*) indicates a parameter is required after the argument

Using the program:
  - Use W, A, S, D to move forwards, left, backwards, and right respectively.
  - Use R, F to move up and down respectively.
  - '[', ']' to decrease and increase delta time.
  - ',', '.' to decrease and increase the screen depth.
  - Space to pause the simulation. (Movement is still allowed)
  - Click any particle to set the camera to track that particle.
  - To stop tracking, click empty space or another particle.

Presets:
1)  Centre body with -n number of planets orbiting in random places. (Default 10)
2)  Galaxy (?)

""")
        exit()

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
        # self.allshift = DEFAULT_ZERO_VEC
        # self.allrotate = DEFAULT_ZERO_VEC
        self.buffer = {}
        self.bufferMode = 0 # 0: Normal. 1: Recording, sim paused. 2: Playing.
        self.bufferLength = 0
        for p in particleList:
            self.buffer[p] = []

    def bufferModeString(self):
        if (self.bufferMode == 0):
            return "Normal"
        elif (self.bufferMode == 1):
            return "Recording"
        elif (self.bufferMode == 2):
            return "Playing"

    def getBuffer(self, particle, index = -1, remove = None):
        if self.bufferLength > 0:
            result = self.buffer[particle][index]
            if remove != None: self.buffer[particle].pop(remove)
            return result
        else:
            return False

    def addBuffer(self, particle):#, colour = None):
        pos = particle.pos.getClone()
        rad = particle.radius
        colour = particle.colour
        self.buffer[particle].append([pos, rad, colour])

    def playBuffer(self, particle, index = 0, remove = True):
        if (not self.buffer[particle]):
            self.bufferMode = 0
            return False
        buff = self.buffer[particle][index]
        if remove:
            self.buffer[particle].pop(index)
        return buff

    def processPosition(self, particle, defaultIndex = 0, playIndex = 0, playRemove = True):
        # A kind of autopilot, takes in a position and returns basically what the camera should see.
        if self.bufferMode == 2:
            # playing
            # print("Playing particle")
            play = self.playBuffer(particle, playIndex, playRemove)
            # if (play):
            return play

        elif self.bufferMode == 1:
            # recording. Don't let the particle move.
            # print("Recording. Keeping particle frozen.")
            self.addBuffer(particle)
            return self.buffer[particle][0]
        else:
            return False

        # if default == 0:


class MainLoop:
    def __init__(self):
        # Records the movements to all particles
        self.commonShiftPos = DEFAULT_ZERO_VEC
        self.commonShiftVel = DEFAULT_ZERO_VEC
        # self.commonRotate = DEFAULT_ZERO_VEC
        self.minDistance = None
        self.pause = -1         # 1 for pause, -1 for not paused.

        self.clickTarget = None

        self.FPS = 1
        self.frameWarning = False

    def Zero(self):
        self.commonShiftPos = DEFAULT_ZERO_VEC
        self.commonShiftVel = DEFAULT_ZERO_VEC
        self.commonRotate = DEFAULT_ZERO_VEC

    def changeCommonShift(self, vectorShift):
        self.commonShift.addToMe(vectorShift)
        return self.commonShift

    def showData(self, delta):
        pauseString = "True"
        if self.pause == -1: pauseString = "False"

        text = """
Buffermode: %s \t Frame Rate: %d
Particle Count: %d Delta: %lf
Paused: %s
        """ % (
            Buffer.bufferModeString(),
            self.FPS, delta, len(particleList),
            pauseString
        )
        turtle.goto(-500, 350)
        turtle.down()
        turtle.pencolor([1, 1, 1])
        turtle.write(text)

    # def changeCommonRotate(self, vectorRotate):
    #     self.commonRotate.addToMe(vectorRotate)
    #     return self.commonRotate

    def abort(self):
        global Running
        Running = False
        print("Auto Aborting!!!")
        # exit()

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
        if (rotate != [0, 0, 0]):
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

            # print("---")
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
                if (self.pause == -1 and Buffer.bufferMode != 2):
                    p.step(delta)
                if (abs(self.commonShiftPos != 0) or abs(self.commonShiftVel) != 0):
                    p.pos.addToMe(self.commonShiftPos)
                    p.pos.addToMe(self.commonShiftVel.multiply(delta))
                buff = Buffer.processPosition(p)
                if not buff:
                    drawResult = camera.drawParticle(p)
                    if (self.clickTarget):
                        if (drawResult):
                            if (abs(vector(self.clickTarget[:-1]) - vector(drawResult[0:2])) < drawResult[2]):
                                if (self.clickTarget[2] == 0):
                                    # Left click
                                    camera.panTrackSet(p)
                                elif (self.clickTarget[2] == 1):
                                    # Right click
                                    pass
                else:
                    # print("buff returned, drawing somewhere different.")
                    camera.drawAt(buff[0], buff[1], buff[2])
        else:
            # print("Got here somehow?")
            for p in particleList:
                p.step(delta)



        frameEnd = time.time()
        frameLength = frameEnd - frameStart
        if (frameLength == 0):
            FPS = -1
        else:
            FPS = 1 / frameLength
        self.FPS = FPS
        # print("FPS:", FPS)
        if (AUTO_ABORT):
            if (FPS < 1 and FPS != -1):
                if (self.frameWarning):
                    self.abort()
                else:
                    self.frameWarning = True
            else:
                self.frameWarning = False

        self.showData(delta)
        self.clickTarget = None
        self.Zero()


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

    def setScreenDepth(self, value, increment=False):
        if increment:
            self.screenDepth += value
            difference = value
        else:
            difference = value - self.screenDepth
            self.screenDepth = value
        self.pos -= self.rot * difference

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
        self.screenXaxis = self.screenXaxis.rotateAbout(self.rot,         direction[2] * rate)
        self.screenYaxis = self.screenYaxis.rotateAbout(self.rot,         direction[2] * rate)

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

        # rp = particle.radius
        # SD = self.screenDepth
        # CP = pos - self.pos

        x_r, y_r, z_r = self.rot.elements
        x_CSP, y_CSP, z_CSP = relPosOnScreen.elements
        x_CSC, y_CSC, z_CSC = scrCent.elements

        X = relPosOnScreen.dot(self.screenXaxis) / abs(self.screenXaxis)
        Y = relPosOnScreen.dot(self.screenYaxis) / abs(self.screenYaxis)

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

    def circularise(self, other, plane = None, axis=None):
        # If axis is supplied, the resulting orbit is in the direction of the
        # cross product of the displacement vector from the body to parent and the axis
        if type(other) == list:
            # Can specify a mass at a position instead of a particle
            # Parse as [mass, position, vel=0]
            mass = other[0]
            position = other[1]
            if (len(other) > 2):
                otherVel = other[2]
            else:
                otherVel = vector([0, 0, 0])
        else:
            mass = other.mass
            position = other.pos
            otherVel = other.vel

        # if inclination == "r":
        #     inclination = random.random() * 360 - 180
        speed = sqrt(G * mass/abs(self.pos - position))
        vel = randomVector(3, 1)
        if (axis == None):
            vel.makeOrthogonal(position - self.pos)
            if plane: vel = vel.lock(plane)#[vel.elements[i] * plane[i] for i in range(len(vel.elements))]
        else:
            vel = axis.cross(position - self.pos)
        vel.setMag(speed)
        self.vel = vel + otherVel
        return True

        # if type(other) == particle:
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
rotate = [0, 0, 0]
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

def rotUp():
    if rotate[1] < 1:
        rotate[1] += 1

def rotDown():
    if rotate[1] > -1:
        rotate[1] -= 1

def rotClockWise():
    if rotate[2] < 1:
        rotate[2] += 1

def rotAntiClock():
    if rotate[2] > -1:
        rotate[2] -= 1

def escape():
    global Running
    Running = False

def pause():
    MainLoop.pause *= -1
    if Buffer.bufferMode == 1:
        bufferPlay()

def leftClick(x, y):
    MainLoop.clickTarget = [x, y, 0]    # 0 for left click, 1 for right

def rightClick(x, y):
    MainLoop.clickTarget = [x, y, 1]    # 0 for left click, 1 for right

def upScreenDepth():
    camera.setScreenDepth(10, True)

def downScreenDepth():
    camera.setScreenDepth(-10, True)

def upDelta():
    global Delta
    Delta *= 1.2

def downDelta():
    global Delta
    Delta *= 1 / 1.2

def bufferRecord():
    Buffer.bufferMode = 1

def bufferPlay():
    if MainLoop.pause == 1:
        pause()
    Buffer.bufferMode = 2



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

turtle.onkeypress(rotClockWise, "e")
turtle.onkeyrelease(rotAntiClock, "e")

turtle.onkeypress(rotAntiClock, "q")
turtle.onkeyrelease(rotClockWise, "q")

turtle.onkey(escape, "Escape")
turtle.onkey(pause,  "space")

turtle.onkeypress(upScreenDepth, ".")
turtle.onkeypress(downScreenDepth, ",")

turtle.onkey(upDelta, "]")
turtle.onkey(downDelta, "[")

turtle.onscreenclick(leftClick, 1)
turtle.onscreenclick(rightClick, 3)

turtle.onkey(bufferRecord, "n")
turtle.onkey(bufferPlay, "m")

turtle.listen()

DEFAULT_ZERO_VEC = vector(DEFAULT_ZERO_VEC)
DEFAULT_UNIT_VEC = vector(DEFAULT_UNIT_VEC)
MainLoop = MainLoop()
camera = camera()

setup()
Running = True

if preset == 1:
    particle(25000, vector([150 + DEFAULT_SCREEN_DEPTH, 0, 0]))
    for i in range(PARTICLE_COUNT):
        particle(150, vector([150 + DEFAULT_SCREEN_DEPTH, 0, 0]) + randomVector(3, 50, 400)).circularise(particleList[0])
elif preset == 2:
    COM = vector([0, 0, 0])     # Centre of mass
    particleMass = 100
    for i in range(PARTICLE_COUNT):
        particle(particleMass, vector([DEFAULT_SCREEN_DEPTH, 0, 0]) + randomVector(3, 50, 500, [1, 0, 1]))
        COM += particleList[-1].pos

    COM = COM / PARTICLE_COUNT
    totalMass = PARTICLE_COUNT * particleMass
    for p in particleList:
        p.circularise([totalMass / 2, COM], axis = vector([0, 1, 0]))




Buffer = buffer()
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
