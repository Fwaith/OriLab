import sys
import re
import glfw
import glm
import math
import numpy as np
from OpenGL.GL import *

import display
import render
import input
import parser

def main():
    window = display.window()
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    glfw.set_cursor_pos_callback(window, input.mouse_callback)
    glfw.set_mouse_button_callback(window, input.mouse_button_callback)
    glfw.set_scroll_callback(window, input.scroll_callback)
    render.object()

    model_loc = glGetUniformLocation(render.shaderProgram, "model")
    view_loc = glGetUniformLocation(render.shaderProgram, "view") 
    projection_loc = glGetUniformLocation(render.shaderProgram, "projection")

    glEnable(GL_DEPTH_TEST)
    while not glfw.window_should_close(window):
        input.processInput(window)
       
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        parser.validate()

        glUseProgram(render.shaderProgram)

        model = glm.mat4(1.0)
        model = glm.rotate(model, glm.radians(input.modelRotY), glm.vec3(0.0, 1.0, 0.0))
        model = glm.rotate(model, glm.radians(input.modelRotX), glm.vec3(1.0, 0.0, 0.0))
        cameraUp = glm.vec3(0.0, 1.0, 0.0)
        view = glm.lookAt(input.cameraPos, input.cameraPos + input.cameraFront, cameraUp)
        projection = glm.perspective(glm.radians(input.fov), 600.0 / 600.0, 0.1, 100.0)
        glUseProgram(render.shaderProgram)

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection))
        
        glBindVertexArray(render.VAO)
        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        glfw.swap_buffers(window)
        glfw.swap_interval(1)
        glfw.poll_events()

    glfw.terminate()
    return

if __name__ == "__main__":
    main()
