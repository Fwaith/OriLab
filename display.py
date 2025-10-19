import glfw
import numpy as np
from OpenGL.GL import *
import OpenGL.GL.shaders as shader

def window():
    if not glfw.init():
        return
   
    window=set_window()
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)

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
    
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    while not glfw.window_should_close(window):
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            print("Escape pressed - closing window")
            glfw.set_window_should_close(window, True)
       
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 3)
         
        glfw.swap_buffers(window)
        glfw.swap_interval(1)
        glfw.poll_events()

    print("Closing")
    glfw.terminate()

def set_window():
    glfw.window_hint(glfw.SCALE_FRAMEBUFFER, glfw.FALSE)
    window = glfw.create_window(640, 640, "OriLab", None, None)
    return window

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)
