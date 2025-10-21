import glfw

def processInput(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        print("Escape pressed - closing window")
        glfw.set_window_should_close(window, True)
