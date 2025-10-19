import glfw
import numpy as np
from OpenGL.GL import *
import OpenGL.GL.shaders as shader

def window():
    if not glfw.init():
        return
    
    window=set_window()
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            print("Escape pressed - closing window")
            glfw.set_window_should_close(window, True)
        
        vertices = np.array([-0.5, -0.5, 0.5, -0.5, 0.0, 0.5], dtype=np.float32) 
        
        # Create vertex buffer
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Set vertex attribute (equivalent to attribute vec2 position)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw the triangle
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 3)  # Draw 3 vertices

        glfw.swap_buffers(window)
        glfw.swap_interval(1)
        glfw.poll_events()

    print("Closing")
    glfw.terminate()

def set_window():
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(640, 360, "OriLab", None, None)
    return window
# if not window:
    #    glfw.terminate()
     #   return
