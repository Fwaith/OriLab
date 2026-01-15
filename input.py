import glfw
import glm
import math

cameraPos = glm.vec3(0.0, 0.0, 3.0)
cameraFront = glm.vec3(0.0, 0.0, -1.0)
cameraUp = glm.vec3(0.0, 1.0,  0.0)
firstMouse = True
lastX = 300.0
lastY = 300.0
fov = 45.0
deltaTime = 0.0
lastFrame = 0.0

modelRotX = 0.0
modelRotY = 0.0
mouseDragging = False

def processInput(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        print("Escape pressed - closing window")
        glfw.set_window_should_close(window, True)

    global cameraPos, cameraFront, cameraUp, deltaTime, lastFrame

    currentFrame = glfw.get_time()
    deltaTime = currentFrame - lastFrame
    lastFrame = currentFrame
    cameraSpeed = 2.5 * deltaTime

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cameraPos += cameraSpeed * cameraFront
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cameraPos -= cameraSpeed * cameraFront
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

def mouse_callback(window, xpos, ypos):

    global mouseDragging, lastX, lastY, modelRotX, modelRotY

    if not mouseDragging:
        return

    xoffset = xpos - lastX
    yoffset = ypos - lastY
    lastX = xpos
    lastY = ypos
    
    sensitivity = 0.5
    modelRotY += xoffset * sensitivity
    modelRotX += yoffset * sensitivity
    
    modelRotX %= 360.0
    modelRotY %= 360.0

def scroll_callback(window, xoffset, yoffset):
    global fov
    fov -= yoffset
    if fov < 1.0:
        fov = 1.0
    if fov > 45.0:
        fov = 45.0

def mouse_button_callback(window, button, action, mods):

    global mouseDragging, lastX, lastY

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouseDragging = True
            lastX, lastY = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            mouseDragging = False
