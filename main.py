import sys
import glfw
import numpy as np
from OpenGL.GL import *

import display
import render
import input

def main():
    window=display.window()
    render.object()
    while not glfw.window_should_close(window):
        input.processInput(window)
       
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glfw.swap_buffers(window)
        glfw.swap_interval(1)
        glfw.poll_events()

    glfw.terminate()
    return

if __name__ == "__main__":
    main()
