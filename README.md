# Orbits
A 3D n-body simulator in Python.

The latest version of Orbits (Orbits4) attempts to take particles in 3-dimensional space, and project them on to a plane in a separate location,
representing the screen. The correct shape of a sphere projected onto a plane would be an ellipse, as it is a conic section, and that's 
what I'm trying to create. It requires some nifty mathematics to work out the shape of the ellipse, aswell as the position of the ellipse on the screen. 
Benefits to this method include:
  -  Being able to easily rotate and move the camera throughout space
  -  Being able to easily create a 'buffer', storing the locations of particles for a period of time before drawing them, giving much 
     faster performance for large simulations (but with the cost of waiting to buffer)
  -  As well as buffering, while playing back the buffer the camera will be able to move through the recorded particles in space. This was      impossible in earlier versions as each movement changed the position of the particle in space, and so a change in the buffer would 
     need a change in every following recorded position.
  -  More complex movement of the camera, ie panning and rotational tracking, special modifications to both etc.
  
For a more in depth and mathematical explanation of the task at hand, Projection.pdf describes how I am trying to go about working out the maths to create this program. 
Keep in mind at the time of writing this, the program doesn't work correctly, and the maths is based off what I talk about in that document, so there are probably mistakes there too.

Description of the files:

  - *Orbits3.9.py*: A 'finished' product that does almost everything I want in the final version but uses much simpler mathematics, and thus has significant restrictions on the capabilities visually, but is also a bit sloppy and no where near optimised. Nevertheless, it works and looks good, despite not drawing particles as ellipses (which is really a minor detail anyway).
  - *Orbits4.py*: A miserable failure at trying to use tkinter to draw the projections instead of turtle. I thought it would be a faster alternative, but it turns out that what I'm trying to do just isn't feasable in tkinter (as far as I know).
  - *Orbits4T.py*: An example of a quick retreat from tkinter, I decided to go back to turtle and try to work out the mathematical parts before I worry about the technical bits.
