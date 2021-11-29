import ctypes
import struct
from OpenGL.GL import *
from OpenGL.GLUT import *
from shaders import *
import numpy

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

class TextureManager:
    def __init__(self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey
        self.textureobject = GLint()
        self.initTexture()


    #For now we are only using this to create the Buddhabrot and for that we just need to
    #track the number of times a point is traveled through by the iterating function.
    #So we don't need RGBA, just single channel.
    def initTexture(self):
        glCreateTextures(GL_TEXTURE_2D, 1, self.textureobject)
        glTextureStorage2D(self.textureobject.value, 1, GL_RGBA32F, self.sizex, self.sizey)
        glBindTexture(GL_TEXTURE_2D, self.textureobject.value)
        #Set up some texture parameters. We don't want the texture to wrap
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        #Also make sure any texture filtering done is linear
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        #Zero out the texture in the GPUs memory
        glClearTexSubImage(self.textureobject.value, 0, 0, 0, 0, self.sizex, self.sizey, 1, GL_RGBA, GL_FLOAT, (ctypes.c_float * 4)(0.0))
        #glTexImage2D(GL_TEXTURE_2D, 0, GL_R, self.sizex, self.sizey, 0, GL_RED, GL_UNSIGNED_INT, 0)
        #Make the texture readable and writable
        glBindImageTexture(0, self.textureobject.value, 0, GL_FALSE, 0, GL_READ_WRITE, GL_RGBA32F)

    def getTexData(self):
        #Make sure any writing operations have finished
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        #allocate memory for the return data.
        arraysize = self.sizex * self.sizey * 4 # X size, Y size, num channels
        data = (ctypes.c_float * arraysize)(0.0) # Init to all 0.0
        glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT, ctypes.addressof(data))
        print(len([x for x in data if x != 0.0]))
        #print([x for x in data if x != 0.0])


class ShaderManager:
    def __init__(self, sizex, sizey):
        self.texman = TextureManager(sizex, sizey)
        self.uniforms = {}
        self.shaderProgram = None
        self.activeShader = None

    def printtexdata(self):
        print(self.texman.getTexData())

    def activateShader(self, shaderdict):
        self.uniforms = shaderdict["uniforms"]
        self.activeShader = shaderdict["name"]
        shader = createShaderFromString(shaderdict["shaderstr"], shaderdict["shadertype"])
        self.shaderProgram = glCreateProgram()
        glAttachShader(self.shaderProgram, shader)
        glLinkProgram(self.shaderProgram)
        self.changeShaderProgram(self.shaderProgram)


    def updateShaderUniforms(self, uniformdata={}):
        if uniformdata is None:
            raise(Exception("WAT"))
        if self.activeShader == "CHECKERBOARD_TEST":
            struc = struct.pack("i", 25)
        else:
            uniformbuffer = []
            #initial mandelbrot testing.
            uniformbuffer.append(uniformdata["WINDOW_SIZE_WIDTH"])
            uniformbuffer.append(uniformdata["WINDOW_SIZE_HEIGHT"])
            uniformbuffer.append(uniformdata["CURRENT_COLOR_MODE"])
            uniformbuffer.append(uniformdata["ESCAPE_VELOCITY_TEST_ITERATIONS"])
            uniformbuffer.append(uniformdata["ORTHO_WIDTH"])
            uniformbuffer.append(uniformdata["ORTHO_HEIGHT"])
            uniformbuffer.append(uniformdata["BOUND_LEFT"])
            uniformbuffer.append(uniformdata["BOUND_BOTTOM"])
            struc = MANDELBROT_STRUCT(*uniformbuffer)
        glBufferSubData(target=GL_UNIFORM_BUFFER, offset=0, size=None, data=bytes(struc))


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
    glClearColor(255, 255, 255, 255) #Clear black
    glViewport(0, 0, windowSizeW, windowSizeH)
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)


def resetDisplay():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glLoadIdentity()
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
