import glfw
import glm
import math
import numpy as np
from OpenGL.GL import *
from PIL import Image

VAO = None
shaderProgram = None

def object():
    global VAO, shaderProgram    
    
    vertices = np.array([
        -0.5, 0.5, 0.5,  1.0, 0.0, 0.0  ,0.0, 1.0, #top left
        0.5, 0.5, 0.5,  0.0, 1.0, 0.0  ,1.0, 1.0, #top right
        -0.5, -0.5, 0.5,  0.0, 0.0, 1.0  ,0.0, 0.0, #bottom left
        0.5, -0.5, 0.5,  1.0, 1.0, 0.0  ,1.0, 0.0, #bottom right

        -0.5, 0.5, -0.5,  1.0, 0.0, 0.0  ,0.0, 1.0, #top left back
        0.5, 0.5, -0.5,  0.0, 1.0, 0.0  ,1.0, 1.0, #top right back
        -0.5, -0.5, -0.5,  0.0, 0.0, 1.0  ,0.0, 0.0, #bottom left back
        0.5, -0.5, -0.5,  1.0, 1.0, 0.0  ,1.0, 0.0 #bottom right back
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2,  2, 1, 3, #front
        4, 5, 6,  5, 6, 7, #back
        0, 4, 6,  0, 6, 2, #left
        1, 5, 3,  5, 3, 7, #right
        0, 4, 5,  5, 0, 1, #top
        2, 7, 6,  7, 2, 3  #bottom
    ], dtype=np.uint32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    stride = 8 * 4
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    image = Image.open("metal.jpg")
    width, height = image.size
    """nrChannels = len(image.getbands())"""
    data = np.array(image)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
    glGenerateMipmap(GL_TEXTURE_2D)

    vertexShaderSource = """
        #version 460 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec3 aColor;
        layout (location = 2) in vec2 aTexCoord;

        out vec2 TexCoord;
        out vec3 Pos;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main() {
            gl_Position = projection * view * model * vec4(aPos.x, aPos.y, aPos.z, 1.0);
            Pos = aPos;
            TexCoord = aTexCoord;
        } """

    fragmentShaderSource = """
        #version 460 core
        out vec4 FragColor;

        in vec2 TexCoord;
        in vec3 Pos;

        uniform vec4 ourColor;
        uniform sampler2D ourTexture;

        void main() {
            FragColor = texture(ourTexture, TexCoord) * vec4(Pos.x, ourColor.g, Pos.z, 1.0);
        } """

    vertexShader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShader,vertexShaderSource)
    glCompileShader(vertexShader)

    if not glGetShaderiv(vertexShader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(vertexShader).decode()
        print("Vertex shader error:", error)
        raise RuntimeError("Vertex shader compilation failed")

    fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragmentShader, fragmentShaderSource)
    glCompileShader(fragmentShader)

    if not glGetShaderiv(fragmentShader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(fragmentShader).decode()
        print("Fragment shader error:", error)
        raise RuntimeError("Fragment shader compilation failed")

    shaderProgram = glCreateProgram()
    glAttachShader(shaderProgram, vertexShader)
    glAttachShader(shaderProgram, fragmentShader)
    glLinkProgram(shaderProgram)
    
    if not glGetProgramiv(shaderProgram, GL_LINK_STATUS):
        error = glGetProgramInfoLog(shaderProgram).decode()
        print("Program linking error:", error)
        raise RuntimeError("Shader program linking failed")

    glDeleteShader(vertexShader)
    glDeleteShader(fragmentShader)
