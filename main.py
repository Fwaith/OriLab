import sys
import glfw
import glm
import math
import numpy as np
from OpenGL.GL import *

import display
import render
import input

def main():
    window=display.window()
    render.object()

    model_loc = glGetUniformLocation(render.shaderProgram, "model")
    view_loc = glGetUniformLocation(render.shaderProgram, "view") 
    projection_loc = glGetUniformLocation(render.shaderProgram, "projection")

    glEnable(GL_DEPTH_TEST)
    while not glfw.window_should_close(window):
        input.processInput(window)
       
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(render.shaderProgram)

        timeValue = glfw.get_time()
        greenValue = (math.sin(timeValue))
        vertexColorLocation = glGetUniformLocation(render.shaderProgram, "ourColor")

        model = glm.mat4(1.0)
        model = glm.rotate(model, (glfw.get_time() * glm.radians(50.0)), glm.vec3(0.5, 1.0, 0.0))
        view = glm.lookAt(glm.vec3(1.0, 1.0, 2.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(60.0), 600.0 / 600.0, 0.1, 100.0)
        glUseProgram(render.shaderProgram)
        glUniform4f(vertexColorLocation, 0.0, greenValue, 0.0, 1.0)

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
