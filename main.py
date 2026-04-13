import sys
import glfw
import glm
from OpenGL.GL import *
import numpy as np

import display
from render import Renderer
import input
from parser import Parser
from simulator import Simulator

def main():
    window = display.window()
    if not window:
        return
    
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    glfw.set_cursor_pos_callback(window, input.mouse_callback)
    glfw.set_mouse_button_callback(window, input.mouse_button_callback)
    glfw.set_scroll_callback(window, input.scroll_callback)
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <fold_file>")
        return
    
    parser = Parser(sys.argv[1])
    renderer = Renderer(parser)
    simulator = Simulator(parser)

    beam = simulator.beams[0]
    node_a = simulator.nodes[beam.node_endpoints[0]]
    node_b = simulator.nodes[beam.node_endpoints[1]]

    node_a.mass = 1e10
    node_a.velocity = np.zeros(3)
    node_b.mass = 1e10
    node_b.velocity = np.zeros(3)

    for node in simulator.nodes:
        node.position[2] += np.random.uniform(-0.01, 0.01)

    # In main.py after creating simulator
    fold_percentage = 0.5
    for beam in simulator.beams:
        if beam.type in ('M', 'V'):
            beam.fold_angle_target *= fold_percentage

    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        input.processInput(window)

        simulator.step()
        renderer.update(simulator.nodes)
       
        glClearColor(0.15625, 0.15625, 0.15625, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        model = glm.mat4(1.0)
        model = glm.rotate(model, glm.radians(input.modelRotY), glm.vec3(0.0, 1.0, 0.0))
        model = glm.rotate(model, glm.radians(input.modelRotX), glm.vec3(1.0, 0.0, 0.0))
       
        model = glm.translate(model, glm.vec3(-0.5, -0.5, 0.0))
        
        cameraUp = glm.vec3(0.0, 1.0, 0.0)
        view = glm.lookAt(input.cameraPos, input.cameraPos + input.cameraFront, cameraUp)
        
        width, height = glfw.get_window_size(window)
        aspect_ratio = width / height if height > 0 else 1.0
        projection = glm.perspective(glm.radians(input.fov), aspect_ratio, 0.1, 100.0)
        
        renderer.render_triangles(model, view, projection)
        renderer.render_beams(model, view, projection)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()
