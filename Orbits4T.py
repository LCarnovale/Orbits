# Author: Leo Carnovale (leo.carnovale@gmail.com / l.carnovale@student.unsw.edu.au)
# Date  : April to May ish?
# Orbits 4T

# On surface tablet, 71.1mm = 400 pixels.
# --> 5.63 pixels / mm

# This could help find radii for the stars: https://www.physicsforums.com/threads/star-radius-mass-from-spectral-class-b-v-luminosity.868047/

from tkinter import *
from math import *
import turtle
import random
import time
import vector
import loadSystem
import particle as Pmodule
import copy

randomVector = vector.randomVector
vector = vector.vector

particleList  = Pmodule.particleList
staticList    = Pmodule.staticList
nonStaticList = Pmodule.nonStaticList

markerList   = Pmodule.markerList

marker   = Pmodule.marker
particle = Pmodule.particle

print("Starting Orbits4T")
PROGRAM_START = time.time()

LINUX = False # If true, then non alphanumeric key controls will be replaced with numbers

#############################################################################################################################
# args:                                                                                                                     #
# <key> : [<type>, <default value>, <requires parameter>, [<second default value>], [changed]]                              #
# second default value is only necessary if <requires parameter> is true.                                                   #
# if true, then the algorithm looks for a value after the key.                                                              #
# if false, the algorithm still looks for a value after the key but if no value is given the second default value is used.  #
# The final value indicates if the argument has been supplied, to know if the user has specified a value                    #
# 	 (Useful if the default varies depending on other arguments)                                                            #
# NOTE: THIS LAST VALUE WILL BE ADDED AUTOMATICALLY, DO NOT INCLUDE IT IN THE CODE                                          #
# ANOTHER NOTE: A key is defined as anything starting with a dash '-' then a letter. A dash followed by a number would be   #
#    read as a negative number.                                                                                                     #
#                                                                                                                           #
########### PUT DEFAULTS HERE ###############################################################################################
args = {#   [<type>   \/	 <Req.Pmtr>  <Def.Pmtr>
"-?"  :  [None], # Help.
"-d"  :     [float,	0.025,	True], # Delta time per step
"-n"  :     [int,   20,		True], # Particle count
"-p"  :     [str,   "1",	True], # preset
"-rt" :     [str,   False,  False,  True], # Run in real time
"-sp" :     [str,   False,	False,  True], # start paused
"-ss" :     [str,   False,	False,  True], # staggered simulation
"-G"  :     [float, 20,		True], # Gravitational constant
"-pd" :     [str,   False,	False,  True], # Print data
"-sd" :     [float, 2500,	True], # Default screen depth
"-ps" :     [float, 0.01,	True], # Maximum pan speed
"-rs" :     [float, 0.01,	True], # Rotational speed
"-ip" :     [str,   "Earth",True], # Initial pan track
"-ir" :     [str,   "Sun",  True], # Initial rot track
"-ae" :     [str,   True,   False,  True], # Auto "exposure"
"-rel":     [str,   False,  False,  True], # Visualise special relativity effects (Experimental)
"-mk" :     [str,   False,	False,  True], # Show marker points
"-ep" :     [int,   360,	True], # Number of points on each ellipse (Irrelevant if SMART_DRAW is on)
"-sf" :     [float, 0.5,	True], # Rate at which the camera follows its target
"-ad" :     [str,   False,	False,  True], # Always draw. Attempts to draw particles even if they are thought not to be on screen
"-vm" :     [float, 150,	True], # Variable mass. Will be used in various places for each preset.
"-vv" :     [float, False,	False,  1], # Draw velocity vectors
"-ds" :     [str,	False,	False,  True], # Draw stars, ie, make the minimum size 1 pixel, regardless of distance.
"-sdp":     [int,   5,		True], # Smart draw parameter, equivalent to the number of pixels per edge on a shape
"-me" :     [int,   400,	True], # Max number of edges drawn
"-ab" :     [int,   False,	False,  20], # Make asteroid belt (Wouldn't recommend on presets other than 3..)
"-es" :     [int,	False,	False,  5], # Make earth satellites
"-WB" :     [str,   False,	False,	True], # Write buffer to file
"-rp" :     [float, False,  False,  0.6], # Make random planets
"-cf" :     [str,	True,  False,  True], # Use complex flares
"-sr" :     [int,   False,  True], # Make rings (really just a thin asteroid belt) around Saturn
"-rg" :     [str,   False,  False,  True], # Record gif shots
"-tn" :     [str,   False,  False,  True], # True n-body simulation. When off program makes some sacrifices for performance boost.
"-asb" :    [int,   4,      True], # Number of bodies in the auto-systems.
"-flim":    [float, False,  True], # Frame limit
"-demo":    [str,   False,  False,  True], # Run demo
"-dfs":     [int,   0,      True], # Draw diffraction spikes (Experimental)
"-df" :     [str, "SolSystem.txt", True], # Path of the data file
"-test":    [str,   False,  False, True], # Test mode
"-getStars":[float, False,  False, 4], # Get stars from the datafile.
"-PM":      [str,   False,  False, True],  # Enter the preset maker
"-dbg":     [str,   False,  False, True],  # Enter debug mode. (Frame by frame with command line options)
"-P?":      [str,   False,  False, True],  # Show available presets and quit
"-AA_OFF":  [str,   True,   False, False]   # Turn off AutoAbort.
}

originalG = args["-G"][1]

if len(sys.argv) > 1:
	if ("-?" in sys.argv):
		# Enter help mode
		print("Welcome to Orbits4T!")

		print("""
This version contains the following presets:
1)  Centre body with '-n' number of planets orbiting in random places. (Default 10)
2)  'Galaxy' kinda thing (Miserable failure, don't waste your time with this one)
3)  THE WHOLE UNIVERSE
4)  Another small test. Large body with a line of small bodies orbiting in a circle.
5)  Repulsive particles on the surface of a sphere, that eventually sort themselves into an even spread. Just cool to watch.
The third one is way better, don't even bother with the others. They were just practice.

Arguments:
Key|Parameter type|Description
   | (if needed)  |
-d :    float       Delta time per step.
-n :    int         Particle count, where applicable.
-p :    string      Preset.
-sp:                Start paused.
-rt:                Start in real time. (Can be toggled during the simulation)
-ss:                Staggered simulation (Hit enter in the terminal to trigger each step)
-G :    float       Gravitational constant.
-pd:                Print debugging data.
-sd:    float       Default screen depth.
-ps:    float       Maximum pan speed.
-rs:    float       Rotational speed.
-ip:    string      Starts the simulation with pan track at a body with the given name. (ONLY PRESET 3)
                        The body is found by using the search function, so a HIP id will work too.
-ir:    string      Starts the simulation with rot track at a body with the given name, like -ip. (ONLY PRESET 3)
-mk:                Show marker points (static X, Y, Z and Origin coloured particles)
-ep:    int         Number of points on each ellipse (Irrelevant if SMART_DRAW is on (which it is))
-sf:    float       Rate at which the camera follows its target.
-ad:                (Debug tool) Always draw. Attempts to draw particles even if they are thought not to be on screen
-vm:    float       Variable mass. To be used in relevant places for some presets.
-vv:                Draw velocity and acceleration vectors. Note that while velocity vectors are to scale,
                        acceleration vectors are multiplied by 5 when being drawn. (Otherwise they are too short)
                        Give a number parameter to scale each vector.
-ds  :              Draw stars, ie, make the minimum size 1 pixel, regardless of distance.
-sdp :  int         Smart draw parameter, equivalent to the number of pixels per edge on a shape.
-me  :  int         Maximum edges, max number of edges drawn on each shape.
-ab  :  int         Make asteroid belt (Wouldn't recommend on presets other than 3..)
-es  :  int         Make earth satellites.
-WB  :              Write buffer to file.
-sr  :  int         Make rings around Saturn, the given number represents how many objects to make.
-dfs :  int         Draw diffraction spikes around stars. Enter the number of spikes after -dfs. *Experimental*
-rp  :  float       Make random planets, give a percentage of stars to have systems.
                        (only for preset 3, if stars are also made)
-tn  : (True/False) Runs the simulation in True N-body mode, making calculations of acceleration due the
                        gravity of all bodies to all bodies. Much slower but usually much more accurate
                        (Really not worth turning on for presets like the solar system)
                        If left on, (ie the argument is not used) then the most influencial bodies at the
                        start are the only ones that affect that body for the rest of the simulation.
                        But, for some presets this is ON by default.
-asb :  int         Number of bodies in auto generated systems.
-demo:              Runs a demo. Only usable in preset 3, goes through bodies looking around them
                        then moving onto the next body.
-flim:  float       Frame limit.
-df  :  string      Path of the data file. (Not implemented)
-test:              Enter test mode.* (See below)
-getStars: float	Loads stars from a database of almost 120,000 stars in the night sky. The value
                        given with this parameter will be used as the maximum apparent magnitude from
                        Earth of the stars loaded. The default is 4.5, which loads about 510 stars.
-PM  :              Enters the preset maker, allowing you to design a preset.
-P?  :              Shows the available presets then exits.
-AA_OFF:            Turn off AutoAbort. (AutoAbort will kill the simulation if two consecutive frames
                        last longer than a second, it's only trying to help you not bring your
                        computer to a standstill, be careful if you choose to abandon it)
-? : Enter this help screen then exit

Using the program:
  - Use W, A, S, D to move forwards, left, backwards, and right respectively.
  - Use R, F to move up and down respectively.
  - Use the arrow keys to rotate the camera.
  - '[', ']' to decrease and increase delta time.
  - ',', '.' to decrease and increase the screen depth.
  - 'n', 'm' to start recording and playing the buffer. The simulation will be paused while recording.
  - Space to pause the simulation. (Movement is still allowed)
  - 'I' will set the simulation to run at real time (ish).
  - '\\' will reverse time.
  - Click any particle to set the camera to track that particle.
  - Right click any particle to fix the camera's rotation on that particle.
  - Cycle through targeted particles with Tab/shift-Tab. (Available only in preset 3)
        Once a particle is targeted, pressing T and Y will toggle pan and rotational
        tracking respectively.
  - Press 'G' to go to a selected target.
  - To stop tracking, click (and/or right click) on empty space or another particle.
  - To clear the target selection, press C
  - End the simulation with Esc.

*Test mode: There are some hard coded time, position and velocity snapshots for various
bodies in the simulation, with data taken from the same source as the start positions, but
anywhere between 92 minutes and a month later, and so show the correct positions and velocities
that those bodies should have. Test mode will use the delta time step given by the command line
argument (or the default) and nothing else. No graphics will be drawn, instead the program will
simply step its way through to each relevant time until each of the bodies with test data can
have their correct position and velocity compared with the correct values.""")
		exit()
	argv = sys.argv
	for arg in args:
		args[arg].append(False) # This last value keeps track of whether or not the argument has been specified by the user
	for i, arg in enumerate(argv):
		if arg in args:
			if (args[arg][-1]):
				print("%s supplied multiple times." % (arg))
			try:
				if args[arg][2]:
					if argv[i + 1] in args:
						raise IndexError # If the next arg is an arg keyword (eg -p, -d) then the parameter is missing
					args[arg][1] = args[arg][0](argv[i + 1])
				else: # No parameter needed, set it to args[arg][3]
					if (len(argv) > i + 1 and (argv[i + 1] not in args)):
						if (argv[i + 1] == "False"):
							args[arg][1] = False
						elif (argv[i + 1] == "True"):
							args[arg][1] = True
						else:
							args[arg][1] = args[arg][0](argv[i + 1])
					else:
						args[arg][1] = args[arg][3]
				args[arg][-1] = True
			except ValueError:
				print("Wrong usage of {}".format(arg))
			except IndexError:
				print("Missing parameter for {}.".format(argv[i]))

		else:
			if (arg[0] == "-" and arg[1].isalpha()):
				print("Unrecognised argument: '%s'" % (arg))

else:
	print("You haven't used any arguments.")
	print("Either you're being lazy or don't know how to use them.")
	print("For help, run '%s -?'" % (sys.argv[0]))
	time.sleep(1)
	print("Now onto a very lame default simulation...")
	time.sleep(1)

Delta			        = args["-d"][1]
PARTICLE_COUNT	        = args["-n"][1]
preset			        = args["-p"][1]
STAGGERED_SIM	        = args["-ss"][1]
START_PAUSED	        = args["-sp"][1]
Pmodule.G		        = args["-G"][1]
PRINT_DATA		        = args["-pd"][1]
defaultScreenDepth	    = args["-sd"][1]
maxPan			        = args["-ps"][1]
rotSpeed		        = args["-rs"][1]
showMarkers		        = args["-mk"][1]
ellipsePoints	        = args["-ep"][1]
smoothFollow	        = args["-sf"][1]
DRAW_VEL_VECS	        = args["-vv"][1]
ALWAYS_DRAW		        = args["-ad"][1]
variableMass	        = args["-vm"][1]
DATA_FILE		        = args["-df"][1]
drawStars		        = args["-ds"][1]
makeAsteroids 	        = args["-ab"][1]
makeSatellites	        = args["-es"][1]
writeBuffer		        = args["-WB"][1]
FRAME_LIMIT 	        = args["-flim"][1]
getStars 		        = args["-getStars"][1]
DEMO                    = args["-demo"][1]

presetMaker             = args["-PM"][1]
presetShow              = args["-P?"][1]

TestMode 				= args["-test"][1]
AUTO_ABORT              = args["-AA_OFF"][1]      # I wouldn't change this unless you know the programs good to go

SMART_DRAW_PARAMETER = args["-sdp"][1]     # Approx number of pixels between each point

MAX_POINTS = args["-me"][1]  # Lazy way of limiting the number of points drawn to stop the program
                             # grinding to a halt everytime you get too close to a particle

particle.TestMode = TestMode



# Time lengths constants
MINUTE  = 60
HOUR    = 60 *	MINUTE
DAY     = 24 *	HOUR
YEAR    = 365 * DAY

# Distance constants
LIGHT_SPEED = 299792458
LIGHT_YEAR  = LIGHT_SPEED * YEAR
AU      = 149597870700
PARSEC  = 3.085677581e+16

# Preset 3
AsteroidsStart 	 = 249.23 * 10**9 # Places the belt roughly between Mars and Jupiter.
AsteroidsEnd 	 = 740.52 * 10**9 # Couldn't find the actual boundaries (They're probably pretty fuzzy)
AsteroidsMinMass = 0.0001 * 10**15
AsteroidsMaxMass = 1	  * 10**23
AsteroidsDensity = 1500
  # Saturn ring constants
STRN_RING_MIN_MASS    = 10
STRN_RING_MAX_MASS    = 1000
STRN_RING_DENSITY     = 1000
STRN_RING_MIN_RADIUS  = 7e6
STRN_RING_MAX_RADIUS  = 50e6
STRN_RING_THICKNESS   = 1e5
  # Random planets settings
randomPlanets         = args["-rp"][1]
DEFAULT_SYSTEM_SIZE   = args["-asb"][1] # Default number of bodies to add to a system
TRUE_NBODY            = args["-tn"][1]

# Preset 4
PRESET_4_MIN_RADIUS = 40
PRESET_4_MAX_RADIUS = 400

# Physical constants
REAL_G       = 6.67408e-11
EARTH_MASS   = 5.97e24   # These are all the actual values, not simulated.
EARTH_RADIUS = 6.371e6
SUN_MASS     = 1.989e30
SUN_RADIUS   = 695.7e6

# Random Planet Settings
MIN_PERIOD = 20  * DAY
MAX_PERIOD = 150 * YEAR
MAX_PLANET_COUNT = 12
MIN_PLANET_COUNT = 1


# Simulation settings
particle.ALL_IMMUNE = False
REAL_TIME           = args["-rt"][1]
particle.defaultDensity  = 1
particle.radiusLimit     = 1e+10       # Maximum size of particle
voidRadius               = 5000      # Maximum distance of particle from camera
CAMERA_UNTRACK_IF_DIE = True # If the tracked particle dies, the camera stops tracking it
SMART_DRAW = True               # Changes the number of points on each ellipse depeding on distance
FPS_AVG_COUNT = 10        # Frames used to calculate long average. Less->current fps, more->average fps
RECORD_SCREEN = args["-rg"][1]
DRAW_MARKERS = args["-mk"][1]
RELATIVITY_EFFECTS = args["-rel"][1]
RELATIVITY_SPEED = 0

SCREEN_SETUP = False            # True when the screen is made, to avoid setting it up multiple times

MAX_VISIBILE_MAG = 15
# Camera constants
DEFAULT_ROTATE_FOLLOW_RATE = 0.04
GOTO_DURATION       = 6     # Approximately the number of seconds taken to travel to an object using pan track toggling
AUTO_RATE_CONSTANT  = 10    # A mysterious constant which determines the autoRate speed, 100 works well.
FOLLOW_RATE_COEFF   = 0.4
FOLLOW_RATE_BASE    = 1.1
TRAVEL_STEPS_MIN	= 100   # Number of steps to spend flying to a target (at full speed, doesn't include speeding up or slowing down)
MAX_DRAW_DIST       = 3 * LIGHT_YEAR  # Maximum distance to draw bodies that don't have a given magnitude (ie planets, stars are not affected)

DEFAULT_ZERO_VEC = [0, 0, 0]
DEFAULT_UNIT_VEC = [1, 0, 0]

# Drawing/Visual constants
MAG_SHIFT  = -1              # All apparent magnitudes are shifted by this amount before being drawn
MIN_CLICK_RESPONSE_SIZE = 10 # Radius of area (in pixels) around centre of object that can be clicked
                             # depending on its size
MIN_BOX_WIDTH = 50
COMPLEX_FLARE = args["-cf"][1]
SHOW_SCREENDEPTH = True


# Exposure options
EXPOSURE = 1                 # The width of the flares are multiplied by this
EXP_COEFF = 400
MAX_EXPOSURE = 1e20
AUTO_EXPOSURE = args["-ae"][1]
AUTO_EXPOSURE_STEP_UP = 0.8      # Coeffecient of the log of the current exposure to step up and down
AUTO_EXPOSURE_STEP_DN = 0.9     # When decreasing exposure, mimic a 'shock' reaction
#                               # By going faster down in exposure. (This is close the human eye's behaviour i think)

# AUTO_EXP_BASE = 2             # Increasing this will make the auto exposure 'stronger' (Must be > 1)
REFERENCE_INTENSITY = 1E-65     # 'R', The intensity of a zero magnitude object. Theoretically in units of W/m^2
INTENSITY_BASE = 10**(5/2)      # 'C', Intensity of a body = R*C^( - apparent magnitude)
MIN_VISIBLE_INTENSITY = 4E-70   # Only compared with the intensity after exposure has been applied.
  # Auto Exposure Profile:
REFERENCE_EXPOSURE = 3e6        # Exposure when looking at a zero-mag object
EXPOSURE_POWER = 1.3            # AutoExposure = REF_EXP * e^(EXP_PWR*Magnitude)
AUTO_EXP_BASE = e**EXPOSURE_POWER

# Flare options
FLARE_RAD_EXP = 1.5
FLARE_BASE = 1e6             # Scales the size of the flares
FLARE_POLY_POINTS = 20
FLARE_POLY_MAX_POINTS = 100
MIN_RMAG = 0.02             # min 'brightness' of the rings in a flare. Might need to differ across machines.
  # Diffraction variables
DIFF_SPIKES = args["-dfs"][1]
PRIMARY_WAVELENGTH = 600E-9  # Average wavelength of light from stars. in m.
FOCAL_LENGTH = 2E-2          # Focal length of the 'eyeball' in the camera
PUPIL_WIDTH_FACTOR = 0.01   # This multiplied by the exposure gives the width of the pupil in calculations
AIRY_RATIO = 1/50            # The ratio of the intensity between successive maximums in an airy disk
  # Not user defined, don't change these. Computed now to save time later
AIRY_COEFF = 1 / log(AIRY_RATIO)
DIFFRACTION_RADIUS = 2.4 * FLARE_BASE * FOCAL_LENGTH * PRIMARY_WAVELENGTH / ( PUPIL_WIDTH_FACTOR )

currentDisplay = ""          # Holds the last data shown on screen incase of an auto-abort
lowestApparentMag = None     # The lowest apparent mag of an object on screen, used for auto exposure

## Load presets
inBuiltPresets = ["1", "2", "3", "4", "5"]
if (preset not in inBuiltPresets or presetShow):
	pass


if TestMode:
	if preset == "3":
		# Test data:
		testData = [# [[<Name>, <Time>, <Pos>, <vel>], ...]
			["ISS",
			(2017 * YEAR + 92 * MINUTE), # 2017 years, 1 hour 32 minutes, ie 1 hour 32 mins after start, should be one orbit.
			vector([-2.652741416195131E+07,  1.451863591737731E+08, -2.246871177630126E+04]) * 1000, # Both given in km/s, convert to m/s
			vector([-2.268856357268088E+01, -8.202616782054283E+00, -1.309397555344641E+00]) * 1000],
			["Earth",
			(2017 * YEAR + 92 * MINUTE),
			vector([-2.652775232714054E+07,  1.451886523109221E+08, -2.883530398781598E+04]) * 1000,
			vector([-2.977993074888063E+01, -5.581820507958473E+00,  1.472498187503835E-03]) * 1000],
			["Moon",
			(2017 * YEAR + 31 * DAY),
			vector([-9.791943397595288E+07,  1.100350864508356E+08, -4.271377345877886E+04]) * 1000,
			vector([-2.265069523685520E+01, -1.903695183547426E+01, -8.119286303272855E-02]) * 1000],
			["Mercury",
			(2017 * YEAR + 31 * DAY),
			vector([-3.491563712116394E+07, -5.847758798545337E+07, -1.603576528303239E+06]) * 1000,
			vector([3.195297711109924E+01, -2.269718543834500E+01, -4.787363119651942E+00]) * 1000],
			["Voyager2",
			(2017 * YEAR + 31 * DAY),
			vector([4.678084657944870E+09, -1.291984823213759E+10, -9.959551510991798E+09]) * 1000,
			vector([4.245078194430032E+00, -9.418854886561272E+00, -1.138382248152680E+01]) * 1000]
		]
		testData = sorted(testData, key=lambda x:x[1])
		if (not testData):
			print("No test data given to test with. Aborting.")
			exit()
		else:
			print("Testing positions and velocities for:", ", ".join([x[0] for x in testData]))

	else:
		print("Testing not available for preset %s." %(preset))
elif presetShow:
	print("Function not available (since my lazy ass hasn't written it)")
	pass

if not AUTO_ABORT:
	print("Auto abort is off!")
	print("This should only be done on large simulations where a low frame is expected.")
	print("If you don't need it off, don't turn it off.")
	time.sleep(3)


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

# Credit to 'Spektre' and 'paddyg' on StackOverflow for this function,
# Source: 'https://stackoverflow.com/questions/21977786/star-b-v-color-index-to-apparent-rgb-color'
# Author: 'https://stackoverflow.com/users/2521214/spektre' (paddyg converted it to python)
def bv2rgb(bv):
    if bv < -0.40: bv = -0.40
    if bv > 2.00: bv = 2.00

    r = 0.0
    g = 0.0
    b = 0.0

    if  -0.40 <= bv<0.00:
        t=(bv+0.40)/(0.00+0.40)
        r=0.61+(0.11*t)+(0.1*t*t)
    elif 0.00 <= bv<0.40:
        t=(bv-0.00)/(0.40-0.00)
        r=0.83+(0.17*t)
    elif 0.40 <= bv<2.10:
        t=(bv-0.40)/(2.10-0.40)
        r=1.00
    if  -0.40 <= bv<0.00:
        t=(bv+0.40)/(0.00+0.40)
        g=0.70+(0.07*t)+(0.1*t*t)
    elif 0.00 <= bv<0.40:
        t=(bv-0.00)/(0.40-0.00)
        g=0.87+(0.11*t)
    elif 0.40 <= bv<1.60:
        t=(bv-0.40)/(1.60-0.40)
        g=0.98-(0.16*t)
    elif 1.60 <= bv<2.00:
        t=(bv-1.60)/(2.00-1.60)
        g=0.82-(0.5*t*t)
    if  -0.40 <= bv<0.40:
        t=(bv+0.40)/(0.40+0.40)
        b=1.00
    elif 0.40 <= bv<1.50:
        t=(bv-0.40)/(1.50-0.40)
        b=1.00-(0.47*t)+(0.1*t*t)
    elif 1.50 <= bv<1.94:
        t=(bv-1.50)/(1.94-1.50)
        b=0.63-(0.6*t*t)

    return (r, g, b)


def screenWidth():
	return turtle.window_width()

def screenHeight():
	return turtle.window_height()

def polyDot(radius, fill=None, x=None, y=None):
	if SMART_DRAW:
		numPoints = int(
		max(radius / SMART_DRAW_PARAMETER,
		    FLARE_POLY_MAX_POINTS))
	else:
		numPoints = FLARE_POLY_POINTS

	turtle.up()
	if (x != None and y != None):
		turtle.goto(x, y)
	else:
		x, y = turtle.position()
	angleSep = 2*pi / numPoints
	if (fill != None):
		turtle.pencolor(fill)
		turtle.fillcolor(fill)
	turtle.goto(x, y + radius)
	turtle.down()
	turtle.begin_fill()
	for i in range(1, numPoints):
		angle = i * angleSep
		if DIFF_SPIKES: rad = radius * (1 + sin(angle * DIFF_SPIKES/2) ** 100)
		else: rad = radius
		turtle.goto(x + rad*sin(angle),
		            y + rad*cos(angle))
	turtle.end_fill()
	turtle.up()
	turtle.goto(x, y)

# I = R * B^(-m)
def getIntensity(apparentMag):
	# global REFERENCE_INTENSITY
	return REFERENCE_INTENSITY * INTENSITY_BASE**(-apparentMag)

# m = log_B(R / I)
def intensityToMag(intensity, exposure=1):
	# global REFERENCE_INTENSITY
	return log(REFERENCE_INTENSITY / (intensity / exposure)) / log(INTENSITY_BASE)

def drawOval(x, y, major, minor, angle, fill = [0, 0, 0], box = False, mag = None):
	global ellipsePoints
	global drawStars
	global lowestApparentMag
	global FLARE_POLY_POINTS
	if SMART_DRAW:
		perimApprox = 2*pi*sqrt((major**2 + minor**2) / 2)
		points = int(perimApprox / SMART_DRAW_PARAMETER)
	else:
		points = ellipsePoints
	points = min(points, MAX_POINTS)
	localX = major/2
	localY = 0
	screenX = localX * cos(angle) - localY * sin(angle)
	screenY = localY * cos(angle) + localX * sin(angle)

	flareWidth = 0
	if (mag != None): mag += MAG_SHIFT
	if (mag != None):
		# This uses Rayleigh Criterion to determine the width of the diffraction 'flare'
		# ie, an 'Airy disk'. Using this it is then sufficient to set the intensity
		# of the centre to 100%, and the edge of the disk to 0%, and then have a linear
		# slope through the radius.

		# Generally the middle ring about x = 0 will be the only one visible, however when
		# the camera is close to very bright lights further maximums will be visible and overlap
		# (since we wouldn't be working with a point source).
		# Assume that each sucessive maximum is 1/50th (AIRY_RATIO) the intensity of
		# the previous
		intensity = EXPOSURE * getIntensity(mag)
		tempDiffRadius = DIFFRACTION_RADIUS
		flareWidth = (AIRY_COEFF * log(MIN_VISIBLE_INTENSITY / intensity)) * tempDiffRadius

		if (lowestApparentMag == None):
			lowestApparentMag = mag
		elif (lowestApparentMag and mag < lowestApparentMag):
			lowestApparentMag = mag
	elif (points <= 2 and mag == None):
		fill = [1, 1, 1]

	if box:
		boxRadius = max(MIN_BOX_WIDTH, major * 1.4 + flareWidth) / 2
		turtle.up()
		turtle.pencolor([1, 1, 1])
		turtle.goto(x - boxRadius, y - boxRadius)
		turtle.down()
		turtle.goto(x - boxRadius, y + boxRadius)
		turtle.goto(x + boxRadius, y + boxRadius)
		turtle.goto(x + boxRadius, y - boxRadius)
		turtle.goto(x - boxRadius, y - boxRadius)
		turtle.up()
	if (points > 2):
		turtle.up()
		turtle.goto(x + screenX, y + screenY)
		turtle.begin_fill()
		turtle.fillcolor(fill)
		onScreen = True
		Drawn = False
		screenRadius = camera.screenRadius
		centreRadius = (x**2 + y**2)**(1/2)
		start = 0
		end = points
		for i in range(start, end):
			localX = major/2 * cos(2 * pi * i / points)
			localY = minor/2 * sin(2 * pi * i / points)
			screenX = localX * cos(angle) - localY * sin(angle)
			screenY = localY * cos(angle) + localX * sin(angle)
			turtle.goto(x + screenX, y + screenY)
		turtle.end_fill()

	if (drawStars):
		turtle.up()
		turtle.goto(x, y)
		turtle.pencolor(fill)
		if (mag == None):
			if (points < 2):
				turtle.dot(2)
			return True

		# Scale up fill:
		if type(fill) == list:
			M = max(fill)
			fill = [x * 1/M for x in fill]

		for r in range(int(flareWidth), 0, -1):
			# Ir: Intensity at radius 'r' (Scaled so that 0 is the minimum threshold)
			# Ir = intensity * (1 - r / flareWidth)
			scale = (1 - r / flareWidth) ** 2
			if (scale < MIN_RMAG): continue
			turtle.pencolor([x * scale for x in fill])
			if not DIFF_SPIKES: turtle.dot((r) + minor)
			else: polyDot(r + minor, fill = [x * scale for x in fill])
	# else:
	# 	return False
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

# These must be in descending order
# A '!' indicates that the unit symbol is not shown, if the unit symbol
# matches one of the symbols in the respective list
prefixes = [
	["! Parsecs",PARSEC],
	["! light years",LIGHT_YEAR],
	["P",1e15],
	["! AU", AU],
	["T",1e12],
	["G",1e9],
	["M",1e6],
	["k",1e3],
	["" ,1e0],
	["m",1e-3],
	[u"\u03BC",1e-6]
] # 149,597,870,700
# Returns a string of num reduced with the appropriate prefix
def numPrefix(num, unit, rounding=3, standardOnly=False):
	# unit is a string, ie 'm', 'g'
	# if standardOnly is False, then
	# the function will replace m with parsec/lightyear etc. in units like m/s or m.
	# That won't happpen if standardOnly is True
	global prefixes
	for p in prefixes:
		if (num > p[1]*0.8):
			if (p[0] and p[0][0] == "!" and not standardOnly):
				result = str(round(num / p[1], rounding)) + p[0][1:] + unit[1:]
			else:
				result = str(round(num / p[1], rounding)) + p[0] + unit
			return result
	return str(num) + unit

def massTerm(mass):
	global EARTH_MASS
	global SUN_MASS
	if (mass > 0.8 * SUN_MASS):
		return ("%.5e Solar masses" % (mass / SUN_MASS))
	else:
		return ("%.5e Earth masses" % (mass / EARTH_MASS))

def radiusTerm(radius):
	global EARTH_RADIUS
	global SUN_RADIUS
	if (radius > 0.8 * SUN_RADIUS):
		return ("%.5e Solar radii" % (radius / SUN_RADIUS))
	else:
		return ("%.5e Earth radii" % (radius / EARTH_RADIUS))

# Fill's a nested dictionary. Really designed only for use with
# the planet-child tree
def fillDict(particle):
	if (not particle.child): return None

	result = {}
	for c in particle.child:
		result[c] = fillDict(c)
	return result

# Finds the next object after current in a planet tree
def findNext(tree, current, avoidChild = False, previous=False):
	global orderedParticleList
	if (not tree):
		return None
	elif (current not in tree):
		for p in tree:
			temp = findNext(tree[p], current, avoidChild, previous)
			if temp: return temp
			if temp == False:
				# False is only returned when there are no next particles in next tree level,
				# but the particle has a parent. The parent will be in this level.
				# If the previous isn't found then it will immediately return the parent,
				# so if previous is true then this line won't ever be read.
				return findNext(tree, current.parent, True)
		return None
	else:
		if current.child and not (avoidChild or previous): return current.child[0]
		globalIndex = orderedParticleList.index(current)
		best = (len(orderedParticleList) if not previous else 0)
		found = False

		if previous:
			for p in tree:
				tempIndex = orderedParticleList.index(p)
				if ((tempIndex < globalIndex) and (tempIndex > best)):
					found = True
					best = tempIndex
		else:
			for p in tree:
				tempIndex = orderedParticleList.index(p)
				if ((tempIndex > globalIndex) and (tempIndex < best)):
					found = True
					best = tempIndex
		if found:
			foundParticle = orderedParticleList[best]
			return foundParticle
		elif current.parent:
			if previous: return current.parent
			return False
		else:
			return None

# Just for debugging.
def printTree(tree, indent=0):
	for t in tree:
		if not tree[t]:
			print("\t" * indent + t.name)
		else:
			print("\t" * indent + t.name + ":")
			printTree(tree[t], indent+1)


def timeString(seconds, rounding=3):
	if seconds < 60:
		return ("{}s".format(round(seconds, rounding)))

	minutes = seconds / 60
	minutes = int(minutes)
	if minutes < 60:
		return ("{}:{}s".format(("%02d"%(int(minutes))), round(seconds % 60, rounding)))

	hours = minutes / 60
	if hours < 24:
		return ("{}:{}:{}s".format(int(hours), ("%02d"%(int(minutes % 60))), round(seconds % 60, rounding)))

	days = hours / 24
	if days < 365:
		return ("{} days, {}:{}:{}s".format(int(days), int(hours % 24), ("%02d"%(int(minutes % 60))), round(seconds % 60, rounding)))

	years = days / 365
	return ("{} years, {} days, {}:{}:{}s".format(int(years), int(days % 365), int(hours % 24), ("%02d"%(int(minutes % 60))), round(seconds % 60, rounding)))

class buffer:
	def __init__(self):
		self.buffer = {}
		self.bufferMode = 0 # 0: Normal. 1: Recording, sim paused. 2: Playing.
		self.bufferLength = 0
		self.emptyBuffers = len(particleList)
		self.bufferCount = self.emptyBuffers


	def initialise(self):
		self.buffer = {}
		for p in particleList:
			self.buffer[p] = []


	def bufferModeString(self):
		if (self.bufferMode == 0):
			return "Normal"
		elif (self.bufferMode == 1):
			return "Recording"
		elif (self.bufferMode == 2):
			return "Playing"

	# Takes a particle and if needed stores its position.
	# Can be called on a particle regardless of whether or not
	# the buffer is buffering.
	def storeBuffer(self, particle):
		if (self.bufferMode == 1):
			# Store the position.
			print("Storing", particle)
			self.buffer[p].append(
				[p.pos.getClone(), p.radius, p.colour]
			)
			print(self.buffer[p])
			# else:
				# self.buffer[p].append(None)
		else:
			# No use for the particle.
			return


	def buildBuffer(self, particle):
		pos = particle.pos.getClone()
		rad = particle.radius
		colour = particle.colour
		vel = particle.vel.getClone()
		acc = particle.acc.getClone()
		if (DRAW_VEL_VECS):
			self.buffer[particle].append([pos, rad, colour, vel, acc])
		else:
			self.buffer[particle].append([pos, rad, colour])
		if len(self.buffer[particle]) == 1: self.emptyBuffers -= 1



	def playBuffer(self, particle, index = 0):
		if (index > len(self.buffer[particle])):
			print("Attempting to access non-existant buffer.")
			exit()
		elif not self.buffer[particle]: return False
		if len(self.buffer[particle]) == 1: self.emptyBuffers += 1
		return self.buffer[particle].pop(index)


	def processPosition(self, particle, playIndex = 0, playRemove = True):
		# A kind of autopilot, takes in a position and returns basically what the camera should see.
		if self.bufferMode == 2:
			if (self.emptyBuffers == self.bufferCount):
				# All buffers are empty.
				self.bufferMode = 0
				return False
			# playing
			play = self.playBuffer(particle, playIndex)
			return play

		elif self.bufferMode == 1:
			# recording. Don't let the particle move.
			# print("recording")
			self.buildBuffer(particle)
			# print(self.buffer[particle])
			# print(particle)
			# print(self.buffer)
			return self.buffer[particle][0]
		else:
			return False

def warpedDistance(particle):
	if particle == None:
		return None
	dist = (abs(particle.pos - camera.pos) - particle.radius)*(1 + tan(1/2 * camera.rot.relAngle(particle.pos - camera.pos)))
	return abs(dist)

class MainLoop:
	def __init__(self):
		# Records the movements to all particles
		self.Time = 0
		self.commonShiftPos = DEFAULT_ZERO_VEC
		self.commonShiftVel = DEFAULT_ZERO_VEC
		self.closestParticle = None

		self.pause = -1         # 1 for pause, -1 for not paused.
		self.Delta = 0

		self.clickTarget = []
		self.target = None
		self.FPS = 1
		self.frameWarning = False
		self.displayData = True
		self.DataDisplay = [
		#  	Title		 [<is a function>, object]
		]
		self.smoothAcc = 0 # Used mainly for relativity stuff

	def Zero(self):
		self.commonShiftPos = DEFAULT_ZERO_VEC
		self.commonShiftVel = DEFAULT_ZERO_VEC
		self.commonRotate = DEFAULT_ZERO_VEC

	def setDelta(self, delta):
		for p in particleList:
			p.runLoop()
			p.vel -= self.Delta / 2 * p.acc
			p.vel += delta / 2 * p.acc
			p.acc *= 0
		self.Delta = delta

	def addData(self, name, data, isExpression=False, default=None):
		self.DataDisplay.append([name, isExpression, data, default])

	def addDataLine(self):
		self.DataDisplay.append("NL")

	def showData(self):
		if not self.displayData: return False
		global currentDisplay
		global planets
		# delta = self.Delta
		pauseString = "True"
		if self.Time != 0:
			time = ("-" if self.Time < 0 else "") + timeString(abs(self.Time))
		else:
			time = "00:00"
		if self.pause == -1: pauseString = "False"
		if (not self.closestParticle):
			distString = "---"
		else:
			distString = numPrefix(abs(camera.pos - self.closestParticle.pos), "m")
		text = """Frame Rate: %s
Buffermode: %s (%d) \tScreenDepth: %f
Particle Count: %d  \tDelta: %f
Paused: %s          \tTime:  %s
Distance to closest particle: %s
		""" % (
			(("%.2f"%self.FPS) if self.FPS != 999 else "INFINITY!!"),
			Buffer.bufferModeString(),
			(0 if Buffer.bufferCount == 0 else Buffer.bufferLength / Buffer.bufferCount),
			camera.screenDepth, len(particleList),
			self.Delta,
			pauseString,
			time,
			distString)
			#("---" if not self.closestParticle else numPrefix(abs(camera.pos - self.closestParticle.pos), "m"))


		if self.DataDisplay: maxLen = max([len(x[0]) for x in self.DataDisplay])

		for data in self.DataDisplay:
			text += "\n"
			if data == "NL":
				continue
			text += data[0] + (maxLen - len(data[0]))*"  " + ("\t: " if data[1] else "")
			if (data[1]):
				try:
					value = eval(data[2])
				# except KeyError:
				# 	value = "KEY_ERROR"
				# except NameError:
				# 	value = "NAME_ERROR"
				# except ValueError:
				# 	value = "VALERROR"
				except Exception:
					value = data[3]
			else:
				value = data[2]
			text += str(value)

		currentDisplay = text
		width = screenWidth()
		height = screenHeight()
		textX = -width / 2 + 10
		textY = height / 2 - 15 * (len(text.split("\n")) - 1) # Origin of the text box is bottom left corner
		if (text[-1] != "\n"): textY -= 15
		turtle.goto(textX, textY)
		turtle.down()
		turtle.pencolor([1, 1, 1])
		turtle.write(text)

	def abort(self):
		global Running
		global currentDisplay
		Running = False

		print("Current screen data:")
		print(currentDisplay)
		print()


		print("Auto Aborting!!!")

	def STEP(self, camera, draw = True):
		global FRAME_LIMIT
		global particleList
		global DRAW_VEL_VECS
		global panRate
		global lowestApparentMag
		global MAX_VISIBILE_MAG
		global EXPOSURE

		delta = self.Delta
		if pan[0:-1]: self.smoothAcc += 0.01
		else: self.smoothAcc -= 0.01
		if (self.closestParticle != None) and not RELATIVITY_EFFECTS:
			panAmount = (abs(self.closestParticle.pos - camera.pos) - self.closestParticle.radius) * maxPan#maxPan/(AUTO_RATE_CONSTANT)
			if (pan[-1]):
				panAmount *= 15
		elif RELATIVITY_EFFECTS:
			panAmount = RELATIVITY_SPEED * LIGHT_SPEED * delta * self.smoothAcc
		else:
			panAmount = maxPan
		panRate = panAmount

		if (rotate != [0, 0, 0]):
			camera.rotate(rotate, rotSpeed)
		frameStart = time.time()
		if self.pause == -1 and Buffer.bufferMode != 2: self.Time += delta

		doStep = (self.pause == -1 and Buffer.bufferMode != 2)

		if (abs(camera.pos) > 1e5):
			self.commonShiftPos = -camera.pos
		if DRAW_MARKERS:
			for m in sorted(markerList, key = lambda x: abs(x.pos - camera.pos), reverse = True):
				camera.drawParticle(m)
		clickTarget = None
		if (self.clickTarget):
			clickTarget = self.clickTarget.pop(0)       # Puts the earliest click position in clickTarget
			if (clickTarget[2] == 0):
				# camera.panTrackSet()                  # Left click
				pass
			elif (clickTarget[2] == 1):
				camera.rotTrackSet()                    # Right click
		self.closestParticle = None

		camera.step((delta if doStep else 0), pan, panAmount)
		if doStep:
			if camera.panTrack:
				camera.panTrack.step(delta, camera)
			if camera.rotTrack and camera.rotTrack != camera.panTrack:
				camera.rotTrack.step(delta, camera)
		if camera.panTrack:
			camera.panFollow()
		if camera.rotTrack:
			camera.rotFollow()
		for I, p  in enumerate(particleList):
			if (I > 0 and (abs(p.pos - camera.pos) > abs(particleList[I - 1].pos - camera.pos))):
				# Swap the previous one with the current one
				particleList = particleList[:I - 1] + [particleList[I], particleList[I-1]] + particleList[I + 1:]

			pWarp = warpedDistance(p)
			if (self.closestParticle == None):
				self.closestParticle = p
			elif (pWarp and pWarp < warpedDistance(self.closestParticle)):
				self.closestParticle = p

			if doStep and not (p == camera.panTrack or p == camera.rotTrack):
				p.step(delta, camera)
				# This bit is for preset 5, shouldn't be used otherwise
				if p.mass < 0:
					p.pos = p.pos.mag(100)

			buff = Buffer.processPosition(p) # Returns something if it wants anything other than the actual particle to be drawn
			if not buff:
				drawResult = camera.drawParticle(p, box = (self.target == p and self.displayData))
			else:
				# Buff returned something, which means it wants the camera
				# to draw something other than the particle's actual position
				drawResult = camera.drawAt(buff[0], buff[1], buff[2], box = (self.target == p and self.displayData))

			if DRAW_VEL_VECS and drawResult and buff:
				vecResult = camera.drawParticle([buff[0] + buff[3] * DRAW_VEL_VECS, 1, [0, 1, 0]], drawAt=True, point=True)
				accResult = camera.drawParticle([buff[0] + buff[4] * DRAW_VEL_VECS * 5, 1, [1, 0, 0]], drawAt=True, point=True)
				if vecResult:
					drawLine((vecResult[0], vecResult[1]), (drawResult[0], drawResult[1]), fill = [0, 1, 0])
				if accResult:
					drawLine((accResult[0], accResult[1]), (drawResult[0], drawResult[1]), fill = [1, 0, 0])

			if (clickTarget):
				if (drawResult):
					clickX   = clickTarget[0]
					clickY   = clickTarget[1]
					clickBut = clickTarget[2]
					drawX   = drawResult[0]
					drawY   = drawResult[1]
					drawRad = drawResult[2]
					if (abs(vector([clickX, clickY]) - vector([drawX, drawY])) < max(drawRad, MIN_CLICK_RESPONSE_SIZE)):
						if (clickBut == 0):
							# Left click
							MainLoop.target = p
						elif (clickBut == 1):
							# Right click
							camera.rotTrackSet(p)

		if AUTO_EXPOSURE and drawStars:
			# print("LAM:", lowestApparentMag, "Exposure:", EXPOSURE, end="")
			# GreatestIntensity = getIntensity(lowestApparentMag)
			if lowestApparentMag != None: targetExp = REFERENCE_EXPOSURE * AUTO_EXP_BASE ** lowestApparentMag
			else: targetExp = min(1.1 * EXPOSURE, MAX_EXPOSURE)

			# if targetExp < EXPOSURE_MIN: targetExp = EXPOSURE_MIN
			# elif targetExp > MAX_EXPOSURE: targetExp = MAX_EXPOSURE
			expStep = (targetExp - EXPOSURE)
			if    (expStep > 0): expStep = EXPOSURE / (1 - AUTO_EXPOSURE_STEP_UP)
			elif  (expStep < 0): expStep = -EXPOSURE * (AUTO_EXPOSURE_STEP_DN)
			if (abs(EXPOSURE - targetExp) <= abs(expStep)):
				EXPOSURE = targetExp
			else:
				EXPOSURE += expStep
			lowestApparentMag = None
			MAX_VISIBILE_MAG = intensityToMag(MIN_VISIBLE_INTENSITY, EXPOSURE)
			# print(" ->", EXPOSURE, "Target:", targetExp)


		frameEnd = time.time()
		frameLength = frameEnd - frameStart
		if (frameLength == 0):
			FPS = 999
		else:
			FPS = 1 / frameLength
		if FRAME_LIMIT:
			if (FPS > FRAME_LIMIT):
				time.sleep(1/FRAME_LIMIT - 1/FPS)
				frameEnd = time.time()
				frameLength = frameEnd - frameStart
				if (frameLength == 0):
					FPS = 999
				else:
					FPS = 1 / frameLength
			elif (FPS == 999):
				time.sleep(1/FRAME_LIMIT)
				frameEnd = time.time()
				frameLength = frameEnd - frameStart
				if (frameLength == 0):
					FPS = 999
				else:
					FPS = 1 / frameLength
		self.FPS -= self.FPS / FPS_AVG_COUNT
		self.FPS += FPS / FPS_AVG_COUNT

		if (AUTO_ABORT):
			if (FPS < 1):
				if (self.frameWarning):
					self.abort()
				else:
					self.frameWarning = True
			else:
				self.frameWarning = False
		if self.displayData: self.showData()
		self.Zero()
#
# class Matrix:
# 	def __init__(self, array):
# 		"""Array should be 2 dimensional, ie: [[Column], ..., [Column]] etc."""
# 		self.array = array
#
# 	def vecFromColumn(self, colIndex):
# 		return vector(self.array[colIndex])
#
# 	def vecFromRow(self, rowIndex):
# 		return vector([x[rowIndex] for x in self.array])
#
# 	def vecMultiply(self, vec):
# 		return vector([self.vecFromRow(x).dot(vec) for x in range(len(self.array))])

class camera:
	# Main job: work out where a dot should go on the screen given the cameras position and rotation and the objects position.
	def __init__(self, pos = vector(DEFAULT_ZERO_VEC), rot = vector(DEFAULT_UNIT_VEC), vel = vector(DEFAULT_ZERO_VEC), screenDepth = defaultScreenDepth):
		self.pos = pos
		self.rot = rot.setMag(1)
		self.vel = vel
		# self.trackSeparate = vector([100, 0, 0])
		self.rotTrackOrigin = DEFAULT_UNIT_VEC
		self.screenDepth = screenDepth
		self.screenXaxis = vector([-self.rot[2], 0, self.rot[0]], unit=True)
		self.screenYaxis = vector([
			 -self.rot[0]    * self.rot[1],
			 (self.rot[0]**2 + self.rot[2]**2),
			 -self.rot[2]    * self.rot[1]
		], unit=True)
		self.panStart = self.pos # When flying to a position, the speed is based on the progress from start to finish.
		self.rotStart = self.rot # Similar to above but for rotation
		self.speedParameter = 1 # sqrt(1 - v^2/c^2), not the traditional v/c
		# self.TransformMatrix = Matrix([[0, 0], [0, 0], [0, 0]])
	# total distance, maxSpeed, destination, at speed(0, 1 or 2), stopping distance, position of closest particle at start.
	# Stored so they aren't calculated each step.
	panInfo = [0, 0, vector([0, 0, 0]),
	 			0, 0, vector([0, 0, 0])]
	screenRadius = 0 #(screenWidth()**2 + screenHeight()**2)**(1/2)
	panTrack = None
	rotTrack = None
	panTrackLock = False # Once the pan or rotation tracking has sufficiently closed in on the target,
	rotTrackLock = False # don't allow any 'slippage', ie lock on firmly to the target
	moving = False # To go to a particle, just activate pan and rotational
				   # tracking on the target until they both have locked on
	absolutePan = vector([0, 0, 0])

	def setScreenDepth(self, value, increment=False):
		if (-value >= self.screenDepth):
			print("Screen depth already at {}, can't decrement by {}.".format(self.screenDepth, -value))
			return False
		if increment:
			self.screenDepth += value
			difference = value
		else:
			difference = value - self.screenDepth
			self.screenDepth = value

		# self.pos -= self.rot * difference

	#   Checks if the camera is still moving to the particle or if it has arrived
	def checkMoving(self):
		if (self.moving):
			if not (self.panTrack or self.rotTrack):
				self.moving = False

	def goTo(self, particle, lock=False):
		self.moving = True
		if lock: self.moving = 2 # Allows an option to lock the rot track to an object after going to it
		self.rotTrackSet(particle)
		# self.panTrackSet(particle)

	def rotate(self, direction, rate):
		# direction as a 2 element list [x, y]
		self.screenXaxis = self.screenXaxis.rotateAbout(self.screenYaxis, direction[0] * rate)
		self.screenYaxis = self.screenYaxis.rotateAbout(self.screenXaxis, direction[1] * rate)
		self.rot =         self.screenYaxis.cross(self.screenXaxis)
		self.screenXaxis = self.screenXaxis.rotateAbout(self.rot,         direction[2] * rate)
		self.screenYaxis = self.screenYaxis.rotateAbout(self.rot,         direction[2] * rate)
		self.rot.setMag(1)

	# This executes a step for the camera, applying it's velocity to get a new position.
	# NB: The cameras velocity is in m/step, not m/s. To follow a target the velocity must be
	# 	converted from the particles m/s to m/step for the camera, simply by
	# 	multiplying the velocity in m/s by the time step (delta)
	def step(self, delta, pan=[0, 0, 0], panRate=1):
		if (self.screenRadius == 0): self.screenRadius = (screenWidth()**2 + screenHeight()**2)**(1/2)
		panShift = (pan[0] * self.screenXaxis +
					pan[1] * self.screenYaxis +
					pan[2] * self.rot) * panRate
		if (panShift and self.panTrack and not self.panTrackLock):
			self.panTrackSet()

		self.vel = panShift
		if self.panTrack:
			self.vel += self.panTrack.vel * delta + self.panTrack.acc * delta**2
			# self.trackSeparate += panShift
		self.vel += self.absolutePan
		# if abs(self.vel) > 0.99 * LIGHT_SPEED * delta:
			# self.vel.setMag(0.99 * LIGHT_SPEED * delta)

		self.absolutePan *= 0
		# self.absolutePan = panShift
		if RELATIVITY_EFFECTS:
			# if delta:
			self.speedParameter = sqrt( 1 - RELATIVITY_SPEED**2 )
			self.vel *= 1 / (self.speedParameter) * panRate
			# time travelled will be a bit more as observed by a stationary observer
		self.pos += self.vel
		# if (self.vel):
		#
		# 	self.TransformMatrix = Matrix([[]])

	# Moves the camera to a particle if its too far away,
	# then locks the camera's movement to that object
	def panTrackSet(self, target = None):
		# panInfo: [total distance, maxSpeed, destination, atSpeed (0, 1 or 2), stopping distance]. Stored so they aren't calculated each step.
		self.panTrack = target
		self.panTrackLock = False
		if target:
			minDist = target.pos
			for p in particleList:
				if (p == target): continue
				if (abs(p.pos - self.pos) < abs(minDist - self.pos)):
					minDist = p.pos
			self.panInfo[5] = minDist
			self.panStart = self.pos.getClone()
			if ((20 * target.radius) < abs(self.pos - target.pos)):
				if (self.rotTrack and self.rotTrack != target):
					destination = (target.pos - self.rotTrack.pos).mag(20 * target.radius) # Aligns the new destination so that we will see the object after rotating
				else:
					destination = self.rot.mag(-20 * target.radius)
			else:
				destination = self.pos - target.pos
			self.panInfo[0] = abs(target.pos + destination - self.pos)
			travelSteps = max(GOTO_DURATION * MainLoop.FPS, TRAVEL_STEPS_MIN) # No less than 100 steps
			self.panInfo[1] = self.panInfo[0] / travelSteps
			self.panInfo[2] = destination
			self.panInfo[3] = 0 # at speed: 0 for accelerating, 1 for at speed, 2 for slowing down.
			self.panInfo[4] = (self.panInfo[1] / FOLLOW_RATE_COEFF)
		# print("Setting panTrack to %s from %s, mag %s" % (self.trackSeparate.string(2), "none" if not target else target.name, numPrefix(abs(self.trackSeparate), "m", 2)))
			# print("Travel steps: {}, Total distance: {}, maxSpeed: {}, stopping distance: {}".format(travelSteps, self.panInfo[0], self.panInfo[1], self.panInfo[4]))
		return target

	def rotTrackSet(self, target = None):
		# print("Setting rot")
		self.rotTrack = target
		# self.moving = False
		if target:
			self.rotTrackLock = False
			self.rotStart = self.rot.getClone()
		return target

	# Not used, this can be removed
	def autoRate(self, rate, distance):
		newRate = dist * 0.5# * rate/(AUTO_RATE_CONSTANT)
		return newRate

	def zeroCameraPosVel(self):
		MainLoop.commonShiftPos = self.pos.negate()
		# MainLoop.commonShiftVel = self.vel.negate()

	# Returns values for use in drawParticle or False if particle not on screen
	def onScreen(self, particle):
		relPosition = particle.pos - self.pos
		if (relPosition.dot(self.rot) <= 0):
			return False
		if (particle.radius >= abs(relPosition)):
			return False
		if ("absmag" in particle.info):
			appMag = particle.info["absmag"] + 5 * log(abs(particle.pos - self.pos) / (10 * PARSEC), 10)
			if (appMag > MAX_VISIBILE_MAG):
				return False

		offset = atan(particle.radius/abs(relPosition))
		# centreAngle = atan()
		# if (abs(X) - majorAxis > screenWidth()/2 or abs(Y) - majorAxis > screenHeight()/2):
		# 	return False
		return True




	def drawParticle(self, particle, drawAt = False, point=False, box=False):
		# drawAt: if the desired particle isn't actually where we want to draw it, parse [pos, radius [, colour]] and set drawAt = True
		# if not self.onScreen(particle): return False
		self.rot.setMag(1)
		global MAX_VISIBILE_MAG

		newLow = False
		if drawAt:
			pos = particle[0]
			radius = particle[1]
			colour = particle[2]
		else:
			appMag = particle.absmag
			if (appMag != None):
				appMag += 5 * log(abs(particle.pos - self.pos) / (10 * PARSEC), 10)
				particle.info["appmag"] = appMag
				if (lowestApparentMag == None or appMag < lowestApparentMag):
					newLow = True
				if (appMag - 1 > MAX_VISIBILE_MAG):
					return False
			pos = particle.pos
			radius = particle.radius
			colour = particle.colour
		# Get relative position to camera's position.
		relPosition = pos - self.pos

		# Make object's distance to camera in the direction of motion
		# smaller based on speed parameter.
		if RELATIVITY_EFFECTS and self.vel:
			vDistance = relPosition.dot(self.vel) / abs(self.vel)
			# else: vDistance = 0
			vDistWarped = vDistance * self.speedParameter
			vDiff = vDistance - vDistWarped
			relPosition -= self.vel.mag(1) * vDiff #/ abs(self.vel)
		distance = abs(relPosition)

		if (relPosition.dot(self.rot) <= 0):
			# Only condition to exit draw if ALWAYS_DRAW is True
			return False
		if (distance < radius):
			# and this one
			return False
		elif (distance > MAX_DRAW_DIST and appMag == None):
			return False

		ScreenParticleDistance = self.screenDepth * abs(relPosition) * abs(self.rot) / (relPosition.dot(self.rot))
		# ScreenParticleDistance *= sqrt( 1 - self.speedParameter )
		relPosOnScreen = relPosition * ScreenParticleDistance / abs(relPosition)

		X = relPosOnScreen.dot(self.screenXaxis) / abs(self.screenXaxis)
		Y = relPosOnScreen.dot(self.screenYaxis) / abs(self.screenYaxis)

		offset = asin(radius/distance)
		centreAngle = acos(min(1, self.screenDepth / ScreenParticleDistance))
		minAngle = centreAngle - offset
		screenAngle = atan(self.screenRadius / self.screenDepth)
		if (minAngle > screenAngle):
			return False
		if (radius >= distance and not point):
			return False
		if point:
			majorAxis, minorAxis = 1, 1
		else:
			majorAxis = 2 * (sqrt(X ** 2 + Y ** 2) - self.screenDepth * tan( atan(sqrt(X ** 2 + Y ** 2) / self.screenDepth ) - offset))
			minorAxis = 2 * self.screenDepth * tan(offset)
		if (not point and not ALWAYS_DRAW and (abs(X) - majorAxis > screenWidth()/2 or abs(Y) - majorAxis > screenHeight()/2)):
			# prin = prin + ("Outside of screen, x: " + str(X) + ", y: " + str(Y) + ", major axis: " + str(majorAxis))
			return False
		if X != 0:
			angle = atan(Y / X)
		elif X == 0 and Y == 0:
			angle = 0
		else:
			angle = pi/2
		drawOval(X, Y, majorAxis, minorAxis, angle, colour, box, mag=(appMag if not drawAt else None))
		return [X, Y, majorAxis, minorAxis]

	def drawAt(self, posVector, radius, colour = None, box=False):
		return self.drawParticle([posVector, radius, colour], True, box=box)

	def panFollow(self):
		if self.panTrack == None: return False
		if self.panTrackLock: return True
		# Choose the follow rate so that the approach takes approx
		# 5 seconds whilst at max speed, dont worry about time accelerating
		panDest = self.panInfo[2]
		relPos = (self.panTrack.pos + panDest - self.pos)
		distTravelled = abs(self.pos - self.panStart)
		remDist = abs(relPos)
		if (self.panInfo[3]):
			# At speed, get ready to slow down.
			speed = self.panInfo[1]
			if (self.panInfo[3] == 2 or remDist <= self.panInfo[4]):
				# CLose enough to start slowing down.
				speed = FOLLOW_RATE_COEFF * remDist
				self.panInfo[3] = 2
		else:
			# Accelerating to max speed.
			speed = max(FOLLOW_RATE_COEFF * distTravelled**FOLLOW_RATE_BASE, 0.0001*abs(self.panInfo[5] - self.pos))
			if (speed >= self.panInfo[1]):
				self.panInfo[3] = 1
				speed = self.panInfo[1]

		if (self.panInfo[3] == 2 and speed <= 0.0001*abs(self.panTrack.pos - self.pos)):
			# Close enough to lock on
			speed = abs(relPos)
			self.panTrackLock = True
		vel = relPos.mag(speed)
		self.absolutePan = vel
		return True

	def rotFollow(self, followRate=DEFAULT_ROTATE_FOLLOW_RATE):
		if self.rotTrack == None: return False
		relPos   = (self.rotTrack.pos - self.pos).mag(1)
		if self.rotTrackLock:
			self.rot = relPos
		else:
			relAngle = relPos.relAngle(self.rot)
				# 'shift' is equivalent to a portion of the arc from the current rotation to the end rotation.
			shift    = followRate * ((relAngle + 0.02) if (relAngle > 0.001 and followRate != 1) else relAngle)
				# shiftMag is a modified 'shift' so that adding it to rot results in a rotation of 'shift' through that arc
			shiftMag = sin(shift) / (cos(relAngle/2 - shift))
				# rotShift is simply a vector from the current rotation to the desired rotation of magnitude shiftMag
			rotShift = (relPos - self.rot).mag(shiftMag)

			self.rot += rotShift

			if (relAngle <= 0.001):
				self.lockRot()


		self.screenXaxis = self.rot.cross(self.screenYaxis).mag(1)
		self.screenYaxis = self.screenXaxis.cross(self.rot).mag(1)
		# self.screenXaxis.setMag(1)
		# self.screenYaxis.setMag(1)
		self.rot.setMag(1)
		return True

	def lockPan(self):
		self.panTrackLock = True
		self.moving = False

	def lockRot(self):
		if (self.moving):
			self.panTrackSet(self.rotTrack)
			if (self.moving != 2):
				self.rotTrackSet()
			else:
				self.rotTrackLock = True
		else:
			self.rotTrackLock = True
		self.moving = False
markerList = []

autoRateValue = maxPan
pan = [0, 0, 0, False]
shiftL = False
rotate = [0, 0, 0]

def panRight():
	if pan[0] < 1:
		pan[0] += 1

def panLeft():
	if pan[0] > - 1:
		pan[0] -= 1

def panBack():
	if pan[2] > - 1:
		pan[2] -= 1

def panForward():
	if pan[2] < 1:
		pan[2] += 1

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

def rotRight():
	if rotate[0] < 1:
		rotate[0] = rotate[0] + 1

def rotLeft():
	if rotate[0] > -1:
		rotate[0] = rotate[0] - 1

def rotDown():
	if rotate[1] < 1:
		rotate[1] += 1

def rotUp():
	if rotate[1] > -1:
		rotate[1] -= 1

def rotAntiClock():
	if rotate[2] < 1:
		rotate[2] += 1

def rotClockWise():
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
	MainLoop.clickTarget.append([x, y, 0])    # 0 for left click, 1 for right

def rightClick(x, y):
	MainLoop.clickTarget.append([x, y, 1])    # 0 for left click, 1 for right

def upScreenDepth():
	camera.setScreenDepth(1.05 * camera.screenDepth)

def downScreenDepth():
	camera.setScreenDepth((1/1.05) * camera.screenDepth)
	# camera.setScreenDepth(-10, True)

def upMaxMag():
	global REFERENCE_EXPOSURE
	global EXPOSURE
	# global MAX_VISIBILE_MAG
	# MAX_VISIBILE_MAG += 0.1
	REFERENCE_EXPOSURE *= 1.1
	EXPOSURE *= 1.1

def downMaxMag():
	global REFERENCE_EXPOSURE
	global EXPOSURE
	# global MAX_VISIBILE_MAG
	# MAX_VISIBILE_MAG -= 0.1
	REFERENCE_EXPOSURE /= 1.1
	EXPOSURE /= 1.1

def upDelta():
	# global Delta
	# global FLARE_BASE
	# FLARE_BASE += 0.01
	# print(FLARE_BASE)
	MainLoop.setDelta(MainLoop.Delta * 1.2)

def downDelta():
	# global Delta
	# global FLARE_BASE
	# FLARE_BASE -= 0.01
	# print(FLARE_BASE)
	MainLoop.setDelta(MainLoop.Delta * 1 / 1.2)

def revDelta():
	# global Delta
	MainLoop.setDelta(MainLoop.Delta * -1)

def toggleRealTime():
	global REAL_TIME
	REAL_TIME = False if REAL_TIME else True

def bufferRecord():
	Buffer.bufferMode = 1

def bufferPlay():
	if MainLoop.pause == 1:
		pause()
	Buffer.bufferMode = 2

def togglePanTrack():
	global shiftL
	if camera.panTrack or not MainLoop.target:
		camera.panTrackSet()
	else:
		camera.panTrackSet(MainLoop.target)
		if shiftL: camera.panTrackLock()

def toggleRotTrack():
	if MainLoop.target:
		if camera.rotTrack:
			camera.rotTrackSet()
		else:
			camera.rotTrackSet(MainLoop.target)
	else:
		camera.rotTrackSet()

def goToTarget(lock=False):
	if MainLoop.target:
		camera.goTo(MainLoop.target, lock=lock)

def toggleScreenData():
	# MainLoop.target = None
	MainLoop.displayData = False if MainLoop.displayData else True

def cycleTargets():
	global planetTree
	global shiftL
	try:
		if not shiftL:
			if MainLoop.target:
				MainLoop.target = findNext(planetTree, MainLoop.target)
			if not MainLoop.target:
				MainLoop.target = planetList[0]
		else:
			if MainLoop.target:
				MainLoop.target = findNext(planetTree, MainLoop.target, previous=True)
			if not MainLoop.target:
				MainLoop.target = planetList[-1]
	except NameError:
		return

def clearTarget():
	MainLoop.target = None



# Searches the list of particles for a particle with a matching name
# 'listen' determines if the function hands back focus to the turtle screen.
def search(term=None, listen=True):
	global TestMode
	global particleList
	if TestMode: return False
	if term == None: term = turtle.textinput("Search for a body", "Enter a search term:")
	if not term:
		if listen: turtle.listen()
		return False
	bestBody = None
	for body in particleList:
		if term == str(body.HIPid):
			bestBody = body
			break
		if not body.name: continue
		if term == body.name:
			MainLoop.target = body
			break
		else:
			if term.lower() in body.name.lower():
				if bestBody:
					if bestBody.name > body.name:
						bestBody = body
				else:
					bestBody = body
			# match = (sum([(1 if term[i].lower() == body.name[i].lower() else 0) for i in range(minLength)]) / minLength)
			# if (match > bestMatch):
			# 	bestMatch = match
			# 	bestBody = body
	# if bestMatch:
	# 	MainLoop.target = bestBody
	if bestBody:
		MainLoop.target = bestBody
		if listen: turtle.listen()
		return True
	else:
		if listen: turtle.listen()
		return False



DEFAULT_ZERO_VEC = vector(DEFAULT_ZERO_VEC)
DEFAULT_UNIT_VEC = vector(DEFAULT_UNIT_VEC)
MainLoop = MainLoop()

panRate = 0 # Will be used to store the pan rate of each step


camera = camera(pos = vector([0, 0, 0]))

setup()
Running = True

if preset == "1":
	if (not args["-tn"][-1]):
		TRUE_NBODY = True

	# for i in range(10):
	# 	particle(50 + i*20, vector([50, 100 - 10*i, 0]))
	# Cloud of particles orbiting a big thing
	MainLoop.addData("Pan speed", "round(panRate, 2)", True)
	MainLoop.addData("Camera pan lock", "camera.panTrackLock", True)
	MainLoop.addData("Camera rot lock", "camera.rotTrackLock", True)
	particle(25000, vector([150+defaultScreenDepth, 0, 0]))
	for i in range(PARTICLE_COUNT):
		particle(variableMass, vector([150 + defaultScreenDepth, 0, 0]) + randomVector(3, 50, 400).makeOrthogonal(vector([random.random()*0.2, 1, random.random()*0.2])),
                         colour = [random.random(), random.random(), random.random()], autoColour=False).circularise(particleList[0], axis=vector([0, 1, 0]))
elif preset == "2":
	# Galaxy kinda thing
	MainLoop.addData("Pan speed", "round(panRate, 2)", True)
	MainLoop.addData("Camera pan lock", "camera.panTrackLock", True)
	MainLoop.addData("Camera rot lock", "camera.rotTrackLock", True)

	minDist, maxDist = 25, 250
	COM = vector([0, 0, 0])     # Centre of mass
	particleMass = variableMass
	centreVec = vector([defaultScreenDepth, 0, 0])
	for i in range(PARTICLE_COUNT):
		randomVec = randomVector(3, minDist, maxDist, [1, 0, 1])
		randomVec = randomVec.setMag(maxDist * (abs(randomVec) / maxDist)**2)
		particle(particleMass, centreVec + randomVec + randomVector(3, 25))
		COM += particleList[-1].pos

	COM = COM / PARTICLE_COUNT
	# totalMass = PARTICLE_COUNT * particleMass
	for p in particleList:
		forceVec = vector([0, 0, 0])
		for p2 in particleList:
			if p2 == p: continue
			forceVec += (p.pos - p2.pos).setMag(Pmodule.G * p.mass * p2.mass / (abs(p.pos - p2.pos)**2))
		velVec = forceVec.cross(vector([0, 1, 0]))
		velVec.setMag(sqrt(abs(forceVec.dot(p.pos - COM) / p.mass)))
		p.vel = velVec
		# p.circularise([totalMass / 2, COM], axis = vector([0, 1, 0]))
elif preset == "3":
	#############################
	# Loading this preset will load planets from SolSystem.txt
	# And, if the relevant argument is used, starts from StarsData.txt
	# Additional notes:
	#   - Random planets will create random planets on a certain percentage of stars
	#     given by the -rp argument.
	#   - All randomly created bodies (except asteroid/ring objects) will have the relevant parent assigned
	#     to their info attribute.
	#   - All solar system bodies (except the sun) have the relevant parent given
	#     in the text file. Stars don't get parents. :(
	#   - Parents are stored as objects! under:
	#         Particle.info["parent"] = <particle object>
	if (not args["-G"][-1]): Pmodule.G = REAL_G

	if (not args["-sf"][-1]): smoothFollow = 0.04

	MainLoop.addData("Pan speed", "numPrefix(panRate, 'm/step', 2)", True)
	MainLoop.addData("Camera pan lock", "camera.panTrackLock and (camera.panTrack.name or 'True')", True)
	MainLoop.addData("Camera rot lock", "camera.rotTrackLock and (camera.rotTrack.name or 'True')", True)

	planetTree = {}
	AUTO_RATE_CONSTANT = 1.0e9
	Pmodule.ALL_IMMUNE = True
	planetList = []
	planets = {}
	colours = {
		"Moon"		: [1,	1, 	 1],  # Photo realistic moon white
		"Earth"		: [0,   0.5, 1],  # Photo realistic ocean blue
		"Sun"		: [1,   1,   0],
		"Mercury"	: [1,   0.5, 0],
		"Venus"		: [1,   0.3, 0],
		"Mars"		: [1,   0,   0],
		"Jupiter"	: [1,   0.6, 0.2],
		"Saturn" 	: [1,   0.8, 0.5],
		"Uranus"	: [0.5, 0.5, 1],
		"Neptune"	: [0.2, 0.2, 1]
	}
	print("Loading planets...")
	Data = loadSystem.loadFile(DATA_FILE)
	MainLoop.addDataLine()
	if drawStars:
		MainLoop.addData("Exposure", "round(EXPOSURE, 4)", True)
		MainLoop.addDataLine()
	MainLoop.addData("Selected target", "MainLoop.target.name", True, "None")
	MainLoop.addData("Mass", "'%.5e'%(MainLoop.target.mass) + 'kg \t(' + massTerm(MainLoop.target.mass) + ')'", True, "---")
	MainLoop.addData("Radius", "numPrefix(round(MainLoop.target.radius, 2), 'm') + '   \t(' + radiusTerm(MainLoop.target.radius) + ')'", True, "---")
	MainLoop.addData("Velocity", "numPrefix(abs(MainLoop.target.vel), 'm/s', 5)", True, "---")
	MainLoop.addData("Surface gravity", "numPrefix( MainLoop.target.mass*Pmodule.G/MainLoop.target.radius**2 , 'm/s^2', 5)", True, "---")
	MainLoop.addDataLine()
	MainLoop.addData("Distance to Target", "")
	MainLoop.addData("Centre", "numPrefix( round( abs( MainLoop.target.pos - camera.pos ), 3 ), 'm' )", True, "---")
	MainLoop.addData("Surface", "numPrefix( round( abs( MainLoop.target.pos - camera.pos ) - MainLoop.target.radius, 3 ), 'm' )", True, "---")
	MainLoop.addData("Light time", "timeString(abs(MainLoop.target.pos - camera.pos)/LIGHT_SPEED)", True, "---")
	MainLoop.addDataLine()
	MainLoop.addData("Speed of camera", "numPrefix(abs(camera.vel), 'm/step', 2)", True, "---")
	if RELATIVITY_EFFECTS: MainLoop.addData("Speed Parameter", "'{} *c*dt'.format(RELATIVITY_SPEED)", True, "---")
	MainLoop.addData("Target speed relative to camera", "(numPrefix(abs(MainLoop.target.vel - camera.vel / MainLoop.Delta), 'm/s') if abs(MainLoop.target.vel - camera.vel / MainLoop.Delta) > 0.0001 else 0)", True, "---")
	MainLoop.addDataLine()


	bigVec = vector([0, 0, 0])
	for planet in Data:
		data = Data[planet]
		if (planet == "$VAR"):
			if ("TIME" in data): MainLoop.Time = data["TIME"]
			continue

		if data["$valid"]:
			pos = vector([data["X"], data["Y"], data["Z"]]) * 1000
			vel = vector([data["VX"], data["VY"], data["VZ"]]) * 1000
			mass = data["MASS"]
			density = data["DENSITY"]
			planetName = data["NAME"]
			new = particle(mass, pos, vel, density=density, autoColour=False,
						colour=(colours[planetName] if planetName in colours else [0.5, 0.5, 0.5]),
						limitRadius=False, name=planetName)
			new.info["appmag"] = 0
			if data["ABSMAG"]: new.info["absmag"] = data["ABSMAG"]
			if data["PARENT"]: new.info["parent"] = data["PARENT"]

			planetList.append(new)
			planets[planetName] = new

			bigVec += new.pos

	camera.pos = bigVec.cross(planets["Mercury"].pos.mag(1))
	# camera.rotTrackSet(planets["Sun"])
	# camera.lockRot()
	# MainLoop.target = planets["Earth"]
	if "Phobos" in planets:
		planets["Phobos"].immune = False # Screw you phobos
	MainLoop.addData("Absolute Magnitude", "MainLoop.target.info['absmag']", True, "---")
	MainLoop.addData("Apparent Magnitude", "round(MainLoop.target.info['appmag'],2)", True, "---")

	if args["-sr"][1]:
		# Make saturnian rings
		objectCount = args["-sr"][1]
		STRN_RING_MIN_RADIUS = planets["Saturn"].radius + STRN_RING_MIN_RADIUS
		STRN_RING_MAX_RADIUS = planets["Saturn"].radius + STRN_RING_MAX_RADIUS
		ringWidth = STRN_RING_MAX_RADIUS - STRN_RING_MIN_RADIUS
		saturnPos = planets["Saturn"].pos
		saturnVel = planets["Saturn"].vel
		# Make axis from average axis of other moons
		ringAxis = vector([0, 0, 0])
		for moon in [m for m in particleList if (m.parent == "Saturn")]:
			# if (moon.name in ["Cassini", "Phoebe"]): continue
			ringAxis += (moon.pos - saturnPos).cross(moon.vel - saturnVel).mag(1)
		# ringAxis = ringAxis.makeOrthogonal(planets["Titan"].pos - planets["Saturn"].pos)
		ringAxis.setMag(1)
		for i in range(objectCount):
			# objectRadius = random.random() * ringWidth + STRN_RING_MIN_RADIUS
			objectMass = random.random() * (
				STRN_RING_MAX_MASS - STRN_RING_MIN_MASS
			) + STRN_RING_MIN_MASS
			objectPos = randomVector(3, STRN_RING_MIN_RADIUS, STRN_RING_MAX_RADIUS).makeOrthogonal(ringAxis)
			offset = randomVector(3, 0, STRN_RING_THICKNESS)
			objectPos += offset
			new = particle(objectMass, objectPos + saturnPos, autoColour = False,
			        colour = "white", limitRadius=False, immune=False)
			new.circularise(planets["Saturn"], axis = ringAxis)

	if makeAsteroids:
		beltRadius = (AsteroidsEnd - AsteroidsStart) / 2
		beltCentre = (AsteroidsEnd + AsteroidsStart) / 2
		for i in range(makeAsteroids):
			pos = randomVector(3, beltCentre, fixComponents=[1, 1, 0])
			offset = randomVector(3, 0, beltRadius)
			offset *= (abs(offset) / beltRadius) ** 2
			offset.elements[2] *= 1/5
			density = AsteroidsDensity
			mass = random.random() * (AsteroidsMaxMass - AsteroidsMinMass) + AsteroidsMinMass
			new = particle(mass, planets["Sun"].pos + pos + offset, autoColour=False, colour = "grey", limitRadius=False)
			new.circularise(planets["Sun"], axis = vector([0, 0, -1]))
			planetList.append(new)

	earthVec = planets["Earth"].pos
	radius   = planets["Earth"].radius + 150000

	if makeSatellites:
		for i in range(makeSatellites):
			offset = randomVector(3, radius)
			particle(10000, earthVec + offset, autoColour = False, colour = "grey", immune=True).circularise(planets["Earth"])

	if getStars:
		print("Loading stars...")
		if not args["-ds"][-1]: drawStars = True
		MainLoop.addData("Maximum visible magnitude", "round(MAX_VISIBILE_MAG,2)", True)
		# MainLoop.addData("Min intensity", "MIN_VISIBLE_INTENSITY", True)
		MainLoop.addData("Earth magnitude", "MainLoop.target.mag", True, "---")
		MainLoop.addData("Surface temperature", "MainLoop.target.temp", True, "---")
		MainLoop.addData("Colour index", "MainLoop.target.ci", True, "---")
		MainLoop.addDataLine()
		MainLoop.addData("HYG database id", "MainLoop.target.ID", True, "---")
		MainLoop.addData("Hipparcos catalog id", "MainLoop.target.HIPid", True, "---")
		if (getStars < 10):
			STARS_DATA = loadSystem.loadFile("StarsData.txt", key=["$dist != 100000", "(\"$proper\" != \"None\") or ($mag < {})".format(getStars)], quiet=False)
			# STARS_DATA = loadSystem.loadFile("StarsData.txt", key=["$dist != 100000", "(\"$proper\" != \"None\") or ($absmag < {})".format(getStars)], quiet=False)
		else:
			# STARS_DATA = loadSystem.loadFile("StarsData.txt", getStars, True, key=["$dist!=100000"], quiet=False)
			STARS_DATA = loadSystem.loadFile("StarsData.txt", key=["$dist<={}".format(getStars)], quiet=False)
#			print("Loading named stars...")
#			STARS_DATA.update(loadSystem.loadFile("StarsData.txt", key=["\"$proper\" != 'None'", "$dist != 100000"], quiet = False))

		# Load names.txt to make random names for stars with no name.
		nameFile = open("names.txt", "r")
		names = nameFile.read()
		nameFile.close()
		things, adj = names.split("---")
		things, adj = things.split("\n"), adj.split("\n")
		def randomName():
			global things
			global adj
			return random.sample(adj, 1)[0] + " " + random.sample(things, 1)[0]


		for STAR_key in STARS_DATA:
			if STAR_key == "$VAR" or STAR_key[0] in ["~", "!"]: continue
			STAR = STARS_DATA[STAR_key]
			X = STAR["x"]
			Y = STAR["y"]
			Z = STAR["z"]
			vX = STAR["vx"]
			vY = STAR["vy"]
			vZ = STAR["vz"]
			# print("Looking at star:", STAR["proper"], end = "")
			massIndex = random.random() * 1.5 + 30
			new = particle(10**(massIndex), vector([X, Y, Z]) * PARSEC,
				vector([vX, vY, vZ]) * PARSEC / YEAR, static=True,
				name=STAR["proper"], density=1e3, immune=True, limitRadius=False)
			if (new.name == None):
				new.name = randomName()
			planetList.append(new)
			new.info["appmag"] = 0
			new.info["absmag"] = STAR["absmag"]
			new.info["mag"] = STAR["mag"]
			new.info["ID"] = STAR_key
			new.info["HIPid"] = "None" if not STAR["hip"] else int(STAR["hip"])
			new.info["ci"] = (None if not STAR["ci"] else STAR["ci"])
			if (new.info["ci"] != None):
				new.info["temp"] = 4600 * ((1 / ((0.92 * new.info["ci"]) + 1.7)) + (1 / ((0.92 * new.info["ci"]) + 0.62)) )
				new.autoColour = False
				new.colour = bv2rgb(new.info["ci"])
			else:
				new.info["temp"] = None
		if (randomPlanets):
			# systemCount = randomPlanets * len(STARS_DATA)
			print("Generating solar systems...")
			systemChoice = planetList[-len(STARS_DATA)+1::int(1/randomPlanets)]
			EarthMass = 5.97e24
			density   = 5.51e+3 # Also Earth's density
			for system in systemChoice:
				# system is a particle
				systemAxis = randomVector(3, 10)
				system.static = False
				Pmodule.nonStaticList.append(system)
				dbgCounter = 0
				maxRadius = (Pmodule.G * system.mass * MAX_PERIOD**2 / 4 * pi**2) ** (1/3)
				minRadius = (Pmodule.G * system.mass * MIN_PERIOD**2 / 4 * pi**2) ** (1/3)
				planetCount = ( int( random.random() * (MAX_PLANET_COUNT - MIN_PLANET_COUNT) ) + MIN_PLANET_COUNT)
				for i in range(planetCount):
					dbgCounter += 1
					radius = random.random()**3 * (maxRadius - minRadius) + minRadius
					newPos = randomVector(3, radius).makeOrthogonal(systemAxis + randomVector(3, 0, 3))
					newPos += system.pos
					newMass = EarthMass*10**(((random.random()-1/2)*2)**3 * 2)
					new = particle(
						newMass,
						newPos,
						system.vel,
						immune = True, colour = [random.random() for i in range(3)], autoColour=False,
						density = (random.random() + 0.5)*density, limitRadius = False,
						name = "%s - %d"%(system.name, i))
					new.circularise(system, axis = systemAxis + randomVector(3, 0, 2))
					new.info["parent"] = system
					planetList.append(new)
				print("Making system for %s. %d planets made." % (system.name, dbgCounter))
					# MainLoop.target = new

	search(args["-ir"][1], listen=False)
	camera.rotTrackSet(MainLoop.target)
	search(args["-ip"][1], listen=False)
	camera.panTrackSet(MainLoop.target)
	clearTarget()

	# Fill out tree
	print("Building parent-child tree...")
	for p in particleList:
		if p.parent:
			if (type(p.parent) == str):
				if p.parent not in planets:
					print("Error: Non existant parent (%s) referred to." % (p.parent))
					p.parent = None
					continue
				else:
					p.parent = planets[p.parent]
			if not p.parent.child:
				p.parent.info["child"] = [p]
			else:
				p.parent.child.append(p)

	# Now for the long bit...
	for p in particleList:
		if not p.parent:
			if not p.child:
				planetTree[p] = None
			else:
				planetTree[p] = fillDict(p)

	# printTree(planetTree)
	# for i in range(10):
	# 	randParticle = random.sample(particleList, 1)[0]
	# 	print("Random planet: %s" % (randParticle.name))
	# 	nextParticle = findNext(planetTree, randParticle)
	# 	print("Next planet: %s" % (nextParticle.name))
	# 	prevParticle = findNext(planetTree, randParticle, previous=True)
	# 	print("Previous particle: %s" % (prevParticle.name))
	# 	print()

	# for p in planetTree:
	# MainLoop.abort()

elif preset == "4":
	# defaultDensity = 10
	Sun = particle(300000, vector([0, 0, 0]), density=10, name="Sun",
			colour=[1,0,0], autoColour=False)
	for i in range(PARTICLE_COUNT):
		radius = i / (PARTICLE_COUNT - 1) * (PRESET_4_MAX_RADIUS - PRESET_4_MIN_RADIUS) + PRESET_4_MIN_RADIUS
		particle(variableMass, vector([radius, 0, 0]), density=10)
		particleList[-1].circularise(Sun, axis = vector([0, -1, 0]))
	camera.pos = vector([0, 0, radius])
	camera.rotTrackSet(Sun)

elif preset == "5":
	if PARTICLE_COUNT < 4:
		print("Minimum particle count for this preset is 4")
		PARTICLE_COUNT = 4
	locked = False
	def lockParticles():
		global locked
		locked = True
	print("Press 'L' to lock the particles and start the simulation.")
	time.sleep(1)
	turtle.onkey(lockParticles, "l")
	turtle.listen()
	camera.pos = vector([-400, 0, 0])
	if not SCREEN_SETUP:
		window = turtle.Screen()
		window.setup(width = 1.0, height = 1.0)
		turtle.bgcolor([0, 0, 0])
		turtle.tracer(0, 0)             # Makes the turtle's speed instantaneous
		turtle.hideturtle()
		SCREEN_SETUP = True

	for i in range(PARTICLE_COUNT):
		new = particle(-variableMass, randomVector(3, 100), autoColour=False, immune=True)
	MainLoop.setDelta(Delta)
	while (locked == False):
		turtle.clear()
		MainLoop.STEP(camera)
		# for p in particleList:
		# 	p.pos = p.pos.mag(100)
		turtle.update()
	new = particle(100, vector([0, 0, 0]), radius = 90, immune=True, limitRadius=False)
# if not TestMode:

# print("True nbody: {}, supplied: {}".format(TRUE_NBODY, args["-tn"][-1]))

Buffer = buffer()

if (TRUE_NBODY == False or TRUE_NBODY == "False"):
	print("Auto-assigning systems...")

	# forces = {}
	for p1 in particleList:
		forces = []
		# Now go through the list a second time and find the accelerations due to each particle
		for p2 in particleList:
			if (p1.pos == p2.pos): continue
			forces.append([p2, abs(p1.calcAcc(p2, True))])
		# Pick the top few particles attracting p1
		forces.sort(key=lambda x:x[1], reverse = True)
		bodies = [x[0] for x in forces[0:min(DEFAULT_SYSTEM_SIZE, len(forces))]]
		p1.system = bodies

	# print("Moon system:", ", ".join([x.name for x in planets["Moon"].system]))
	# print("ISS system:", ", ".join([x.name for x in planets["ISS"].system]))
	# print("Earth system:", ", ".join([x.name for x in planets["Earth"].system]))
	# print("Voyager1 system:", ", ".join([x.name for x in planets["Voyager1"].system]))
# else:
# 	print("TRUE_NBODY:", TRUE_NBODY, "Type:", type(TRUE_NBODY))

orderedParticleList = list(particleList)
print("Done! Starting simulation...")
PROGRAM_LOADED = time.time()
loadTime = PROGRAM_LOADED - PROGRAM_START
print("Simulation loaded in %s" % (timeString(loadTime)))

def startRecord():
	global RECORD_SCREEN
	RECORD_SCREEN = True

def stopRecord():
	global RECORD_SCREEN
	RECORD_SCREEN = False

def upRelSpeed():
	global RELATIVITY_SPEED
	RELATIVITY_SPEED += 0.02
	if RELATIVITY_SPEED >= 1: RELATIVITY_SPEED = 0.999

def dnRelSpeed():
	global RELATIVITY_SPEED
	RELATIVITY_SPEED -= 0.02
	if RELATIVITY_SPEED < 0: RELATIVITY_SPEED = 0




if not TestMode:
	if not SCREEN_SETUP:
		window = turtle.Screen()
		window.setup(width = 1.0, height = 1.0)
		turtle.bgcolor([0, 0, 0])

		turtle.tracer(0, 0)             # Makes the turtle's speed instantaneous
		turtle.hideturtle()
		SCREEN_SETUP = True

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

	turtle.onkey(cycleTargets, "Tab")
	turtle.onkeypress(togglePanTrack, "t")
	turtle.onkey(toggleRotTrack, "y")
	turtle.onkey(clearTarget,    "c")
	turtle.onkey(goToTarget,	 "g")
	turtle.onkey(toggleRealTime, "i")

	turtle.onkey(toggleScreenData, "h")
	turtle.onkey(startRecord, "j")
	turtle.onkey(stopRecord, "k")

	turtle.onkeypress(upScreenDepth, "'")
	turtle.onkeypress(downScreenDepth, ";")

	turtle.onkeypress(upMaxMag, ".")
	turtle.onkeypress(downMaxMag, ",")

	turtle.onkey(upDelta, "]")
	turtle.onkey(downDelta, "[")
	turtle.onkey(revDelta, "\\")

	turtle.onscreenclick(leftClick, 1)
	turtle.onscreenclick(rightClick, 3)

	turtle.onkey(bufferRecord, "n")
	turtle.onkey(bufferPlay, "m")

	turtle.onkey(upRelSpeed, "=")
	turtle.onkey(dnRelSpeed, "-")

	turtle.onkey(search, "/")

if TestMode:
	try:
		print("Running simulation with delta time step of %s/step" % (timeString(Delta)))
	# 	print("""	Note that with leapfrog arithmetic,
	# velocity and position are technically never both known at the same time,
	# but that shouldn't affect results significantly.""")
		Time = MainLoop.Time
		checkTimes = sorted([x[1] for x in testData])
		checkData = {}
		# Format of testdata: [[<Name>, <Time>, <Pos>, <vel>], ...]
		for t in testData:
			if (t[1] in checkData): checkData[t[1]].append(t)
			if (t[1] not in checkData): checkData[t[1]] = [t]
		# Stop the tested particles from respawning.
		names = [t[0] for t in testData]
		testList = []
		for p in particleList:
			if (p.name in names):
				p.respawn = False
				testList.append(p)
		flag = False
		# We know there is test data because otherwise the program would have exited by now
		startTime = Time
		stepCounter = 1
		startSim = time.time()
		tempDelta = False
		progressStep = 1
		progressPoint = 0
		print("Progress :..", end = "")
		while checkTimes:
			progress = 100 * (Time - startTime) / (checkTimes[0] - startTime)
			if (progress >= progressPoint):
				print("\rProgress: %d%%" % (progressPoint), end = "")
				progressPoint += progressStep
			# print("\rProgress: %.2f%%" % (100 * (Time - startTime) / (checkTimes[-1] - startTime)), end = "")
			sys.stdout.flush()

			if Time == checkTimes[0]:
				if (tempDelta):
					Delta = tempDelta
				checkNames = [x[0] for x in checkData[checkTimes[0]]]
				for p in testList:

					if (p.name in checkNames):
						# Check the data.
						targetData = checkData[checkTimes[0]][checkNames.index(p.name)]
						targetTime = targetData[1]
						targetPos  = targetData[2]
						targetVel  = targetData[3]
						if not (p.alive):
							print("\n%s is dead." % (p.name))
						else:
							print("\nAt time: %s, for %s:" %(timeString(Time), p.name))
							print("\tShould be at:    %s\twith vel: %s (mag: %s)" % (targetPos.string(2), targetVel.string(2), numPrefix(abs(targetVel), "m/s")))
							print("\tWas actually at: %s\twith vel: %s (mag: %s)" % (p.pos.string(2), p.vel.string(2), numPrefix(abs(p.vel), "m/s")))
							print("\tOffset by        %s (mag: %s) over %d steps of %lfs, average %s/step or %s" % (
								(p.pos - targetPos).string(2),
								numPrefix(abs(p.pos - targetPos), "m", 3),
								stepCounter, (Delta if not tempDelta else tempDelta),
								numPrefix(abs(p.pos - targetPos) / stepCounter, "m", 3),
								numPrefix(abs(p.pos - targetPos) / (stepCounter * Delta), "m/s", 3))
							)
						print()
						checkTimes.pop(0)
						if (not checkTimes): break
						progressPoint = 0
						# flag = len(checkTimes)
					p.step(Delta)
			else:
				if (tempDelta):
					Delta = tempDelta
					tempDelta = False

				if (Time + Delta >= checkTimes[0]):
					tempDelta = Delta
					Delta = checkTimes[0] - Time

				for p in particleList:
					p.step(Delta)

			Time += Delta
			stepCounter += 1
			if stepCounter == 100:
				interval = time.time() - startSim
				# Covered 50 * Delta in interval seconds, ie (50*Delta simSeconds / interval realSeconds)
				simSpeed = 100*Delta / interval
				remainingTimeFirst = checkTimes[0] - Time
				if (len(checkTimes) > 1 and checkTimes[0] != checkTimes[-1]):
					remainingTimeLast = checkTimes[-1] - Time
					remainingSimTimeFirst = remainingTimeFirst / simSpeed
					remainingSimTimeLast  = remainingTimeLast  / simSpeed
					print("\nEstimated remaining time for first data: %s, and for last: %s" % (timeString(round(remainingSimTimeFirst, 2)), timeString(round(remainingSimTimeLast, 2))))
				else:
					remaingSimTime = remainingTimeFirst / (simSpeed)
					print("\nEstimated remaining time: %s" % (timeString(round(remaingSimTime, 2))))
	except KeyboardInterrupt:
		print("\nStopping.")
		exit()
	exit()

turtle.listen()
Buffer.initialise()
frameStart = time.time()
# demoTimer = frameStart
MainLoop.setDelta(Delta)
if REAL_TIME:
	Delta = 0
if START_PAUSED:
	pause()
frameCount = 0

# Debug options:


def save():
	global frameCount
	turtle.getcanvas().postscript(file = "frames/frame_{0:05d}.eps".format(frameCount))
	frameCount += 1

if DEMO: # Run a nice looking screen saver type thing
	print("Running demo. Note that during the demo you may have to fight with the program")
	print("for control of the camera sometimes. The screen display can be brought back by")
	print("pressing 'H' at any time.")
	toggleScreenData()
	start_particle = particleList[0]
	demoTimer = frameStart

while Running:
	turtle.clear()
	if STAGGERED_SIM or args["-dbg"][1]:
		inp = input()
	MainLoop.STEP(camera)
	if REAL_TIME:
		MainLoop.setDelta(time.time() - frameStart)
		frameStart = time.time()
	if DEMO:
		if (int(time.time() - demoTimer) % 15 >= 14) and (camera.panTrackLock):
			# demoTimer = time.time()
			camera.panTrackLock = False
			cycleTargets()
			goToTarget(lock = True)
		if (camera.panTrackLock and camera.rotTrackLock):
			pan[0] = 0.5
		else:
			demoTimer = time.time() # Set the timer to now while its moving
			pan[0] = 0

	turtle.update()
	if (RECORD_SCREEN):
		save()
