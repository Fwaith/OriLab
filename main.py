import sys
import glfw
import numpy as np
from OpenGL.GL import *

import display
import render

def main():
    window=display.window()
    render.object()
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

if __name__ == "__main__":
    main()
