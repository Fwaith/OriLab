import glfw
import numpy as np
from OpenGL.GL import *

def object():
    vertices = np.array([
        -0.5, -0.5,
        0.5, -0.5,
        -0.5,  0.5,
        1.0,  1.0],
        dtype=np.float32)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    program = glCreateProgram()
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

    vertex_shader_source = """#version 330 core
        layout (location = 0) in vec3 aPos;
        void main()
        {
            gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
        }"""

    fragment_shader_source = """#version 330 core
        out vec4 FragColor;
        void main()
        {
            gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }"""

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
