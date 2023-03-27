import OpenGL.raw.GL.VERSION.GL_2_0 as GL20
import OpenGL.raw.GL.VERSION.GL_4_3

CHECKERBOARD_TEST = {}
CHECKERBOARD_TEST["shaderstr"] = """#version 330

layout (std140) uniform PARAMS {
 int rowsizepixels;
};

layout(location = 0) out vec4 fragColor;

void main() {
    int fragtestx = int(gl_FragCoord.x)/rowsizepixels;
    int fragtesty = int(gl_FragCoord.y)/rowsizepixels;
    vec4 blue = vec4(0.0,0.0,1.0,1.0); //blue
    vec4 green = vec4(0.0,1.0,0.0,1.0); //green
    vec4 c1 = blue;
    vec4 c2 = green;
    if ( mod(fragtesty, 2) == 0 ) {
        c1 = blue;
        c2 = green;
    } else {
        c1 = green;
        c2 = blue;
    }
    if ( mod(fragtestx, 2) == 0 ) {
        fragColor = c1;
    }
    else {
        fragColor = c2;
    }
}
"""
CHECKERBOARD_TEST["name"] = "CHECKERBOARD_TEST"
CHECKERBOARD_TEST["shadertype"] = GL20.GL_FRAGMENT_SHADER
CHECKERBOARD_TEST_UNIFORMS = {}
CHECKERBOARD_TEST_UNIFORMS["rowsizepixels"] = int
CHECKERBOARD_TEST["uniforms"] = CHECKERBOARD_TEST_UNIFORMS


MANDELBROT_64 = {}
MANDELBROT_64["shaderstr"] = """
#version 450
#extension GL_ARB_gpu_shader_fp64 : require
#extension GL_ARB_arrays_of_arrays : require
#extension GL_NV_shader_buffer_load : require

//Didnt need to specify the offsets or alignment explicitly here since
//the values I chose are the automatic values anyway, but its easier
//to see where I got the values for the fp32 shader.
layout (std140) uniform PARAMS {
    int WINDOW_SIZE_WIDTH;
    int WINDOW_SIZE_HEIGHT;
    int CURRENT_COLOR_MODE;
    int ESCAPE_VELOCITY_TEST_ITERATIONS;
    double ORTHO_WIDTH;
    double ORTHO_HEIGHT;
    double BOUND_LEFT;
    double BOUND_BOTTOM;
};

layout(location = 0) out vec4 fragColor;
layout (binding = 0, rgba32f) uniform image2D image_in;
const int a = WINDOW_SIZE_WIDTH;
const int b = WINDOW_SIZE_HEIGHT;
const int asize = a*b;

//Borrowed from http://lolengine.net/blog/2013/07/27/rgb-to-hsv-in-glsl
vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
//Borrowed from the map() function in the open-source Processing Core development environment.
//Using this because the HSV color range both starts and ends at pure red. Id rather it begin
//around purple and end at red, that way there is a progression from "cool" to "hot" colors.
float map(float value, float valmin, float valmax, float targetmin, float targetmax) {
  return targetmin + (value - valmin) * (targetmax - targetmin) / (valmax - valmin);
}

ivec2 getWindowCoordsFromOrthoCoords(dvec2 ortho) {
    int winX = int((double(WINDOW_SIZE_WIDTH) * (BOUND_LEFT - ortho.x))/(BOUND_LEFT - ORTHO_WIDTH));
    int winY = int((double(WINDOW_SIZE_HEIGHT) * (BOUND_BOTTOM - ortho.y))/(BOUND_BOTTOM - ORTHO_HEIGHT));
    return ivec2(winX, winY);
}

void populatetexture(dvec2 c) {
    dvec2 z = dvec2(0.0, 0.0);
    int iter = 1;
    double zRealSquared = 0.0;
    double zImagSquared = 0.0;
    while (zRealSquared + zImagSquared < 4.0 && iter < ESCAPE_VELOCITY_TEST_ITERATIONS) {
        //Moved out of functions to increase speed... but it didnt.
        //I think this means the GLSL compiler was pretty smart and made these optimizations for us.
        //Z^2
        z.y = (z.x * z.y) + (z.y * z.x);
        z.x = (zRealSquared) - zImagSquared;
        //+c
        //Adding complex numbers is the same as adding two vectors.
        z = z + c;
        iter++;
        zRealSquared = z.x*z.x;
        zImagSquared = z.y*z.y;
        //Buddhabrot stuff. Track the number of times a point is traveled through by this iterating function
        //Then later we can map the intensity of the pixel to this number
        //Even if we only had a single channel, we always use vec4 to get the data.
        //Unused channels will just be 0 and can be ignored.
        ivec2 passingcoord = getWindowCoordsFromOrthoCoords(z);
        vec4 olddata = imageLoad(image_in, passingcoord);
        olddata.x += 1;
        imageStore(image_in, passingcoord, olddata);
    } 
}

float findEscapeVelocity(dvec2 c) {
    dvec2 z = dvec2(0.0, 0.0);
    int iter = 1;
    double zRealSquared = 0.0;
    double zImagSquared = 0.0;
    
    while (zRealSquared + zImagSquared < 4.0 && iter < ESCAPE_VELOCITY_TEST_ITERATIONS) {
        //Moved out of functions to increase speed... but it didnt.
        //I think this means the GLSL compiler was pretty smart and made these optimizations for us.
        //Z^2
        z.y = (z.x * z.y) + (z.y * z.x);
        z.x = (zRealSquared) - zImagSquared;
        //+c
        //Adding complex numbers is the same as adding two vectors.
        z = z + c;
        iter++;
        zRealSquared = z.x*z.x;
        zImagSquared = z.y*z.y;
    }
    if (zRealSquared + zImagSquared >= 4.0) {
        // populatetexture(c);
        return float(iter)/float(ESCAPE_VELOCITY_TEST_ITERATIONS);
    }
    return 0.0;
}
dvec2 getOrthoCoordsFromWindowCoords(double x, double y) {
    double orthoX = fma(x/double(WINDOW_SIZE_WIDTH), ORTHO_WIDTH, BOUND_LEFT);
    double orthoY = fma(y/double(WINDOW_SIZE_HEIGHT), ORTHO_HEIGHT, BOUND_BOTTOM);
    return dvec2(orthoX, orthoY);
}

vec4 getColorFromVelocity(float v) {
    if (v == 0.0) return vec4(0.0,0.0,0.0,1.0);
    vec4 retcolor = vec4(v,0.0,0.0,1.0);
    if      (CURRENT_COLOR_MODE == 0){retcolor = vec4(hsv2rgb(vec3(1-map(v, 0.0, 1.0, 0.25, 1.0), 1.0, 1.0)), 1.0); }
    else if (CURRENT_COLOR_MODE == 1){retcolor = vec4(hsv2rgb(vec3(map(v, 0.0, 1.0, 0.0, 0.8), 1.0, 1.0)), 1.0); }
    else if (CURRENT_COLOR_MODE == 2) retcolor = vec4(v,v,v,1.0);
    return retcolor;
}
void main() {
    dvec2 orthoCoords = getOrthoCoordsFromWindowCoords(double(gl_FragCoord.x), double(gl_FragCoord.y));
    float normalizedVelocity = findEscapeVelocity(orthoCoords);
	fragColor = getColorFromVelocity(normalizedVelocity);
}
"""
MANDELBROT_64["name"] = "MANDELBROT_64"
MANDELBROT_64["shadertype"] = GL20.GL_FRAGMENT_SHADER
MANDELBROT_64_UNIFORMS = {}
MANDELBROT_64_UNIFORMS["WINDOW_SIZE_WIDTH"] = int
MANDELBROT_64_UNIFORMS["WINDOW_SIZE_HEIGHT"] = int
MANDELBROT_64_UNIFORMS["CURRENT_COLOR_MODE"] = int
MANDELBROT_64_UNIFORMS["ESCAPE_VELOCITY_TEST_ITERATIONS"] = int
MANDELBROT_64_UNIFORMS["ORTHO_WIDTH"] = float
MANDELBROT_64_UNIFORMS["ORTHO_HEIGHT"] = float
MANDELBROT_64_UNIFORMS["BOUND_LEFT"] = float
MANDELBROT_64_UNIFORMS["BOUND_BOTTOM"] = float
MANDELBROT_64["uniforms"] = MANDELBROT_64_UNIFORMS

FRACTAL_COMPUTE_SHADER = {}
FRACTAL_COMPUTE_SHADER["shaderstr"] = """
#version 450
#extension GL_ARB_gpu_shader_fp64 : require
#extension GL_ARB_arrays_of_arrays : require
#extension GL_NV_shader_buffer_load : require

//Didnt need to specify the offsets or alignment explicitly here since
//the values I chose are the automatic values anyway, but its easier
//to see where I got the values for the fp32 shader.
//layout(local_size_x = 1, local_size_y = 1) in;

layout (std140) uniform PARAMS {
    int WINDOW_SIZE_WIDTH;
    int WINDOW_SIZE_HEIGHT;
    int CURRENT_COLOR_MODE;
    int ESCAPE_VELOCITY_TEST_ITERATIONS;
    double ORTHO_WIDTH;
    double ORTHO_HEIGHT;
    double BOUND_LEFT;
    double BOUND_BOTTOM;
};

void main() {
	//fragColor = vec4(1.0,0.0,0.0,1.0);
}


"""
FRACTAL_COMPUTE_SHADER["uniforms"] = MANDELBROT_64_UNIFORMS
FRACTAL_COMPUTE_SHADER["name"] = "FRACTAL_COMPUTE_SHADER"
FRACTAL_COMPUTE_SHADER["shadertype"] = OpenGL.raw.GL.VERSION.GL_4_3.GL_COMPUTE_SHADER