import sys, struct
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
from OpenGL.GLUT import glutTimerFunc, glutSpecialFunc, glutInit, glutInitDisplayMode, glutPostRedisplay, glutInitWindowSize, glutInitWindowPosition, glutSwapBuffers, glutCreateWindow, glutDisplayFunc, glutMainLoop, GLUT_DOUBLE, GLUT_RGB, glutSetOption, GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION
from shaders import *

LP_c_char = ctypes.POINTER(ctypes.c_char)
LP_LP_c_char = ctypes.POINTER(LP_c_char)

#trying something different, ctype arrays are a pain to deal with
class MANDELBROT_STRUCT(ctypes.Structure):
    _fields_ = (
        ('WINDOW_SIZE_WIDTH', ctypes.c_int),
        ('WINDOW_SIZE_HEIGHT', ctypes.c_int),
        ('CURRENT_COLOR_MODE', ctypes.c_int),
        ('ESCAPE_VELOCITY_TEST_ITERATIONS', ctypes.c_int),
        ('ORTHO_WIDTH', ctypes.c_double),
        ('ORTHO_HEIGHT', ctypes.c_double),
        ('BOUND_LEFT', ctypes.c_double),
        ('BOUND_BOTTOM', ctypes.c_double)
    )

class ShaderManager:
    def __init__(self):
        self.uniforms = {}
        self.uniformIndices = []
        self.uniformOffsets = None
        self.uniformBlockIndex = None
        self.shaderProgram = None
        self.activeShader = None

    def activateShader(self, shaderdict):
        self.uniforms = shaderdict["uniforms"]
        shader = createShaderFromString(shaderdict["shaderstr"], shaderdict["shadertype"])
        self.shaderProgram = glCreateProgram()
        glAttachShader(self.shaderProgram, shader)
        glLinkProgram(self.shaderProgram)
        self.changeShaderProgram(self.shaderProgram)


    def updateShaderUniforms(self):
        if self.activeShader == "CHECKERBOARD_TEST":
            struc = struct.pack("i", 25)
        else:
            uniformbuffer = []
            #initial mandelbrot testing.
            uniformbuffer.append(1500)
            uniformbuffer.append(1000)
            uniformbuffer.append(0)
            uniformbuffer.append(500)
            uniformbuffer.append(3.0)
            uniformbuffer.append(2.0)
            uniformbuffer.append(-2.0)
            uniformbuffer.append(-1.0)
            struc = MANDELBROT_STRUCT(*uniformbuffer)
        glBufferSubData(target=GL_UNIFORM_BUFFER, offset=0, size=None, data=bytearray(struc))


    def changeShaderProgram(self, shaderprogref):
        glUseProgram(shaderprogref)
        uniformnamelist = [s.encode("utf-8") for s in self.uniforms.keys()]
        p = (LP_c_char*len(uniformnamelist))()
        uniformnames = ctypes.cast(p, LP_LP_c_char)
        for i, n in enumerate(uniformnamelist):
            uniformnames[i] = ctypes.create_string_buffer(n)
        uniformblockindex = glGetUniformBlockIndex(shaderprogref, "PARAMS")
        uniformbufferobject = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, uniformbufferobject)
        glBindBufferBase(GL_UNIFORM_BUFFER, uniformblockindex, uniformbufferobject)
        glBufferData(GL_UNIFORM_BUFFER, ctypes.sizeof(MANDELBROT_STRUCT), bytearray(), GL_DYNAMIC_DRAW) #Initialize buffer



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
