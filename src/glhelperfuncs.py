import ctypes
import re
import OpenGL.GL.pointers
#import OpenGL.raw.GL.VERSION.GL_1_1 as GL11
#import OpenGL.raw.GL.VERSION.GL_1_5 as GL15
#import OpenGL.raw.GL.VERSION.GL_2_0 as GL20
#import OpenGL.raw.GL.VERSION.GL_3_0 as GL30
#import OpenGL.raw.GL.VERSION.GL_3_1 as GL31
import sys
import glfw.GLFW as GLFW
from OpenGL.GL import glColor3ub, glVertex2i, glBegin, glEnd, glClearColor, GL_QUADS, glClear, GL_COLOR_BUFFER_BIT, glShaderSource
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
from OpenGL.GLUT import glutTimerFunc, glutSpecialFunc, glutInit, glutInitDisplayMode, glutPostRedisplay, glutInitWindowSize, glutInitWindowPosition, glutSwapBuffers, glutCreateWindow, glutDisplayFunc, glutMainLoop, GLUT_DOUBLE, GLUT_RGB, glutSetOption, GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION
from shaders import *
from time import time

class ShaderManager:
    def __init__(self):
        self.uniforms = {}
        self.uniformIndices = []
        self.uniformOffsets = None
        self.uniformBlockIndex = None
        self.shaderProgram = None

    def activateShader(self, shaderdict):
        self.uniforms = shaderdict["uniforms"]
        shader = createShaderFromString(shaderdict["shaderstr"], shaderdict["shadertype"])
        self.shaderProgram = glCreateProgram()
        glAttachShader(self.shaderProgram, shader)
        glLinkProgram(self.shaderProgram)
        self.changeShaderProgram(self.shaderProgram)


    def updateShaderUniforms(self):
        print("UPDATE UNIFORMS")
        uniformbuffer = []
        #Just testing checkerboard for now, not sure how to handle this for arbitrary shader programs
        CHECKER_CELL_SIDE_SIZE_PX = 25
        #uniformbuffer.append(CHECKER_CELL_SIDE_SIZE_PX)
        #uniformbuffer.append(t)
        #glBufferSubData(GL_UNIFORM_BUFFER, 0, uniformbuffer)
        t1 = glGetUniformLocation(self.shaderProgram, "time")
        rsp = glGetUniformLocation(self.shaderProgram, "rowsizepixels")
        glUniform1i(rsp, CHECKER_CELL_SIDE_SIZE_PX)


    def changeShaderProgram(self, shaderprogref):
        glUseProgram(shaderprogref)
        uniformnames = tuple(self.uniforms.keys())
        print(uniformnames)
        """
        glGetUniformIndices(shaderprogref, uniformnames, self.uniformIndices)
        glGetUniformIndices()
        glGetActiveUniformsiv(shaderprogref, self.uniformIndices, GL_UNIFORM_OFFSET, self.uniformOffsets)
        uniformblockindex = glGetUniformBlockIndex(shaderprogref, "PARAMS")
        finalbuffersize = glGetActiveUniformsiv(shaderprogref, uniformblockindex, GL_UNIFORM_BLOCK_DATA_SIZE)
        uniformbufferobject = glGenBuffers()
        glBindBuffer(GL_UNIFORM_BUFFER, uniformbufferobject)
        glBindBufferBase(GL_UNIFORM_BUFFER, uniformblockindex, uniformbufferobject)
        glBufferData(GL_UNIFORM_BUFFER, finalbuffersize, GL_DYNAMIC_DRAW)
        """



def createShaderFromString(shaderstr, shadertype):
    shaderhandle = glCreateShader(shadertype)
    glShaderSource(shaderhandle, shaderstr)
    glCompileShader(shaderhandle)
    if glGetShaderiv(shaderhandle, GL_COMPILE_STATUS) == GL_FALSE:
        compileerror = glGetShaderInfoLog(shaderhandle)
        print(compileerror)
        raise(Exception("Shader compilation error:\n%s" % compileerror))

    return shaderhandle

def glinit(windowSizeW, windowSizeH, windowTitle):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB)
    glutInitWindowSize(windowSizeW, windowSizeH)
    glutInitWindowPosition(50,50)
    glutCreateWindow(windowTitle)
    gluOrtho2D(0.0, 1.0, 0.0, 1.0) #left, right, bottom, top
    glClearColor(255, 255, 255, 255) #Clear black
    glViewport(0, 0, windowSizeW, windowSizeH)
    #glMatrixMode(GL_PROJECTION)
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)


def resetDisplay():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glLoadIdentity()
    #glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
