import OpenGL.raw.GL.VERSION.GL_2_0 as GL20
import OpenGL.raw.GL.VERSION.GL_1_1 as GL11
from OpenGL.GL import glColor3ub, glVertex2f, glBegin, glEnd, glClearColor, GL_QUADS, glClear, GL_COLOR_BUFFER_BIT
from OpenGL.GLU import gluOrtho2D
from OpenGL.GLUT import glutTimerFunc, glutSpecialFunc, glutInit, glutInitDisplayMode, glutPostRedisplay, glutInitWindowSize, glutInitWindowPosition, glutSwapBuffers, glutCreateWindow, glutDisplayFunc, glutMainLoop, GLUT_DOUBLE, GLUT_RGB, glutSetOption, GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION
from OpenGL.WGL.EXT import swap_control
from glhelperfuncs import *
from shaders import *
from time import time

WINDOW_SIZE_WIDTH = 1500
WINDOW_SIZE_HEIGHT = 1000
WINDOW_TITLE = "PyMandelbrot Test"

class MandelbrotView:
    def __init__(self):
        self.lasttime = time()
        self.shadermanager = ShaderManager()
        self.initview()

    def initview(self):
        #self.shadermanager.activateShader(CHECKERBOARD_TEST)
        #self.shadermanager.activeShader = "CHECKERBOARD_TEST"
        self.shadermanager.activateShader(MANDELBROT_64)
        self.shadermanager.activeShader = "MANDELBROT_64"
        self.shadermanager.updateShaderUniforms()
        pass

    def keypress_callback_GLUT(self, keycode, xcoord, ycoord):
        print(keycode)
        print(str((xcoord,ycoord)))

    def updateView(self):
        self.redrawView()

    def timerfunc(self, _):
        self.shadermanager.updateShaderUniforms()
        self.redrawView()
        glutPostRedisplay()
        #Technically we dont need to do this, we only need to redraw the view after a control input
        glutTimerFunc(100, self.timerfunc, 0)

    def redrawView(self):
        self.shadermanager.updateShaderUniforms()
        glClear(GL11.GL_COLOR_BUFFER_BIT)
        glBegin(GL11.GL_QUADS)
        glVertex2f(0, 1)
        glVertex2f(1, 1)
        glVertex2f(1, 0)
        glVertex2f(0, 0)
        glEnd()
        glutSwapBuffers()



def main():
    glinit(WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT, WINDOW_TITLE)
    viewcontrol = MandelbrotView()
    viewcontrol.redrawView()
    glutSpecialFunc(viewcontrol.keypress_callback_GLUT)
    glutDisplayFunc(viewcontrol.redrawView)
    glutTimerFunc(100, viewcontrol.timerfunc, 0)
    #swap_control.wglSwapIntervalEXT(True)
    glutMainLoop()

if __name__ == "__main__":
    main()