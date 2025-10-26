import glfw
import numpy as np
from OpenGL.GL import *

def object():
    program = glCreateProgram()
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

    vertex_shader_source = """
        attribute vec2 position;
        attribute vec4 color;
        varying vec4 v_color;
        void main() { 
            gl_Position = vec4(position, 0.0, 1.0);
            v_color = color;
        } """

    fragment_shader_source = """
        varying vec4 v_color;
        void main() { 
            gl_FragColor = v_color;
        } """

    glShaderSource(vertex_shader, vertex_shader_source)
    glShaderSource(fragment_shader, fragment_shader_source)

    glCompileShader(vertex_shader)
    if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(vertex_shader).decode()
        print(error)
        raise RuntimeError("Vertex shader compilation error")
    
    glCompileShader(fragment_shader)
    if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(fragment_shader).decode()
        print(error)
        raise RuntimeError("Fragment shader compilation error")

    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    glDetachShader(program, vertex_shader)
    glDetachShader(program, fragment_shader)

    glUseProgram(program)

    data = np.zeros(4, [("position", np.float32, 2),
                        ("color", np.float32, 4)])
    data['position'] = [(-1,+1), (+1,+1), (-1,-1), (+1,-1)]
    data['color'] = [(0,1,0,1), (1,1,0,1), (1,0,0,1), (0,0,1,1)]

    buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)

    stride = data.strides[0]
    offset = ctypes.c_void_p(0)
    location = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(location)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glVertexAttribPointer(location, 2, GL_FLOAT, False, stride, offset)

    offset = ctypes.c_void_p(data.dtype["position"].itemsize)
    location = glGetAttribLocation(program, "color")
    glEnableVertexAttribArray(location)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glVertexAttribPointer(location, 4, GL_FLOAT, False, stride, offset)

    location = glGetUniformLocation(program, "color")
    glUniform4f(location, 0.0, 0.0, 1.0, 1.0)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
