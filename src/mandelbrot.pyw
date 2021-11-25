from OpenGL.GL import glColor3ub, glVertex2f, glBegin, glEnd, glClearColor, GL_QUADS, glClear, GL_COLOR_BUFFER_BIT
from OpenGL.GLU import gluOrtho2D
from OpenGL.GLUT import *
from OpenGL.WGL.EXT import swap_control
from glhelperfuncs import *
from shaders import *
from time import time
from functools import partial

WINDOW_SIZE_HEIGHT = 1000
WINDOW_SIZE_WIDTH = int(WINDOW_SIZE_HEIGHT/(2.0/3.0))
WINDOW_TITLE = "PyMandelbrot Test"

PERFORMANCE_TESTING = False
ZOOM_INCREMENT = 0.3
PAN_PCT_INCREMENT = 0.25
ITERATION_INCREMENT = 20





from collections import namedtuple

class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

class WindowCoordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MandelbrotView:
    def __init__(self):
        self.lasttime = time()
        self.shadermanager = ShaderManager()
        self.ASPECT_RATIO = 3.0/2.0 #Will change for bifurcation mode
        self.currentColorMode = 0
        self.currentZoomLevel = 1.0
        self.currentZoomLevelDisplay = 1
        self.maxTestIterations = 1000 #Just a starting value, can change later
        self.startHeight = 2.0
        self.BOUNDS = {"TOP": 1.0, "BOTTOM": -1.0, "LEFT": -2.0, "RIGHT": 1.0}
        self.currentCoordinates = ComplexNumber(-0.5, 0.0) # (Real, Imag) coords
        self.BIFMODE = False
        self.specialKeys = {"SHIFT": False, "CTL": False, "ALT": False}
        self.controlsLocked = False
        self.initview()

    def initview(self):
        self.shadermanager.activateShader(MANDELBROT_64)
        self.updateShaderUniforms()

    def specialToggle(self, state, keycode, _, __):
        sv = {"PRESS": True, "RELEASE": False}
        if keycode == 112: #shift
            self.specialKeys["SHIFT"] = sv[state]
        elif keycode == 114: #shift
            self.specialKeys["CTL"] = sv[state]
        elif keycode == 116: #shift
            self.specialKeys["ALT"] = sv[state]
        elif state == "PRESS" and keycode in [GLUT_KEY_UP, GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_INSERT]: # Passthrough certain special keys
            self.keypress_callback_GLUT(keycode, _, __)

    def mouse_callback_GLUT(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == 1: #State 1 is mouse up
            #reverse the Y coord
            y = WINDOW_SIZE_HEIGHT - y
            clickcoords = WindowCoordinates(x, y)
            complexcoords = self.getComplexCoordsFromWindowCoords(clickcoords)
            self.currentCoordinates.real, self.currentCoordinates.imag = complexcoords
            print("Setting coordinates to (%s, %s)" % (self.currentCoordinates.real, self.currentCoordinates.imag))
            self.updateView()

    #kind of wish I had the new match/case thingy now...
    def keypress_callback_GLUT(self, keycode, _, __):
        moveamount = self.currentZoomLevel*self.startHeight/2.0*PAN_PCT_INCREMENT
        if keycode == b"P":
            self.shadermanager.activateShader(CHECKERBOARD_TEST)
        elif keycode == b"M":
            self.shadermanager.activateShader(MANDELBROT_64)

        elif keycode == GLUT_KEY_UP: self.currentCoordinates.imag += moveamount
        elif keycode == GLUT_KEY_DOWN: self.currentCoordinates.imag -= moveamount
        elif keycode == GLUT_KEY_LEFT: self.currentCoordinates.real -= moveamount
        elif keycode == GLUT_KEY_RIGHT: self.currentCoordinates.real += moveamount
        elif keycode == b"+":
            self.currentZoomLevelDisplay -= 1
            self.setZoomLevelFromInt(self.currentZoomLevelDisplay)
        elif keycode == b"-":
            self.currentZoomLevelDisplay += 1
            self.setZoomLevelFromInt(self.currentZoomLevelDisplay)
        elif keycode in b"[{":
            if keycode == b"{":
                self.maxTestIterations -= ITERATION_INCREMENT*10
            self.maxTestIterations -= ITERATION_INCREMENT
            if self.maxTestIterations < 0: self.maxTestIterations = 0
        elif keycode in b"}]":
            if keycode == b"}":
                self.maxTestIterations += ITERATION_INCREMENT*10
            self.maxTestIterations += ITERATION_INCREMENT
        elif keycode == GLUT_KEY_INSERT: # Shift + 0 keypad
            self.resetAll()
        else:
            print("OTHER KEYCODE: %s" % keycode)

        self.updateView()

    def updateView(self):
        height = self.currentZoomLevel * self.startHeight
        width = height * self.ASPECT_RATIO
        self.BOUNDS["LEFT"] = self.currentCoordinates.real - (width/2)
        self.BOUNDS["TOP"] = self.currentCoordinates.imag + (height/2)
        self.BOUNDS["BOTTOM"] = self.BOUNDS["TOP"] - height
        self.BOUNDS["RIGHT"] = self.BOUNDS["LEFT"] + width
        #self.updateTitle()
        self.redrawView()

    def setZoomLevelFromInt(self, zoomLevelInt):
        self.currentZoomLevel = pow(1.0 - ZOOM_INCREMENT, zoomLevelInt - 1)
        self.currentZoomLevelDisplay = zoomLevelInt

    def getComplexHeight(self): return self.currentZoomLevel * self.startHeight
    def getComplexWidth(self): return self.getComplexHeight() * self.ASPECT_RATIO

    def getComplexCoordsFromWindowCoords(self, windowcoords):
        real = ((windowcoords.x/WINDOW_SIZE_WIDTH) * self.getComplexWidth()) +self.BOUNDS["LEFT"]
        imag = ((windowcoords.y/WINDOW_SIZE_HEIGHT) * self.getComplexHeight()) + self.BOUNDS["BOTTOM"]
        return real, imag


    def resetAll(self):
        print("View reset")
        self.ASPECT_RATIO = 3.0/2.0
        self.currentColorMode = 0
        self.currentZoomLevel = 1.0
        self.currentZoomLevelDisplay = 1
        self.maxTestIterations = 1000
        self.startHeight = 2.0
        self.BOUNDS = {"TOP": 1.0, "BOTTOM": -1.0, "LEFT": -2.0, "RIGHT": 1.0}
        self.currentCoordinates = ComplexNumber(-0.5, 0.0)
        self.BIFMODE = False
        self.updateShaderUniforms()
        resetDisplay()
        self.updateView()

    def timerfunc(self, _):
        self.updateShaderUniforms()
        self.redrawView()
        glutPostRedisplay()
        #Technically we dont need to do this, we only need to redraw the view after a control input
        glutTimerFunc(100, self.timerfunc, 0)

    def updateShaderUniforms(self):
        self.shadermanager.updateShaderUniforms(self.generateShaderUniformData())

    def generateShaderUniformData(self):
        uniformdata = {}
        uniformdata["WINDOW_SIZE_WIDTH"] = WINDOW_SIZE_WIDTH
        uniformdata["WINDOW_SIZE_HEIGHT"] = WINDOW_SIZE_HEIGHT
        uniformdata["CURRENT_COLOR_MODE"] = self.currentColorMode
        uniformdata["ESCAPE_VELOCITY_TEST_ITERATIONS"] = self.maxTestIterations
        uniformdata["ORTHO_WIDTH"] = self.getComplexWidth()
        uniformdata["ORTHO_HEIGHT"] = self.getComplexHeight()
        uniformdata["BOUND_LEFT"] = self.BOUNDS["LEFT"]
        uniformdata["BOUND_BOTTOM"] = self.BOUNDS["BOTTOM"]
        return uniformdata



    def redrawView(self):
        self.updateShaderUniforms()
        glClear(GL_COLOR_BUFFER_BIT)
        glBegin(GL_QUADS)
        glVertex2f(0, 1)
        glVertex2f(1, 1)
        glVertex2f(1, 0)
        glVertex2f(0, 0)
        glEnd()
        glutSwapBuffers()

def LOCK_SIZE_FUNC(*_, **__): glutReshapeWindow(WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT)

def main():
    glinit(WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT, WINDOW_TITLE)
    viewcontrol = MandelbrotView()
    viewcontrol.redrawView()

    press = partial(viewcontrol.specialToggle, "PRESS")
    release = partial(viewcontrol.specialToggle, "RELEASE")
    glutIgnoreKeyRepeat(False)
    glutSpecialFunc(press)
    glutSpecialUpFunc(release)
    glutKeyboardFunc(viewcontrol.keypress_callback_GLUT)
    glutMouseFunc(viewcontrol.mouse_callback_GLUT)
    glutDisplayFunc(viewcontrol.redrawView)
    glutReshapeFunc(LOCK_SIZE_FUNC)
    #swap_control.wglSwapIntervalEXT(True)
    glutMainLoop()

if __name__ == "__main__":
    main()