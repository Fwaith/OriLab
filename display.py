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
    
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    return window

def set_window():
    glfw.window_hint(glfw.SCALE_FRAMEBUFFER, glfw.FALSE)
    window = glfw.create_window(600, 600, "OriLab", None, None)
    return window

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)
