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
