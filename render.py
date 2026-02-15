import numpy as np
from OpenGL.GL import *
import glm

class Renderer:
    def __init__(self, parser):
        self.beam_vertices = self.create_beam_array(parser)
        self.beam_colours = self.create_beam_colour_array(parser)
        self.beam_vertex_count = len(self.beam_vertices) // 3

        self.setup_buffers_beam()
        self.setup_shaders_beam()
        
        self.triangle_vertices = self.create_triangle_array(parser)
        self.triangle_count = len(self.triangle_vertices) // 3

        self.setup_buffers_triangle()
        self.setup_shaders_triangle()

    def create_beam_array(self, parser):
        vertices = []

        for beam in parser.beams:
            v1, v2 = beam.node_endpoints
            p1 = parser.vertices[v1]
            p2 = parser.vertices[v2]
            vertices.extend(p1)
            vertices.extend(p2)

        return np.array(vertices, dtype=np.float32)

    def create_beam_colour_array(self, parser):
        beam_colours = []
        
        for beam in parser.beams:
            if beam.type == 'M':
                colour = [1.0, 0.0, 0.0, 1.0]
            elif beam.type == 'V':
                colour = [0.0, 0.0, 1.0, 1.0]
            elif beam.type == 'F':
                colour = [1.0, 1.0, 0.0, 1.0]
            else:
                colour = [0.0, 0.0, 0.0, 1.0]
            
            beam_colours.extend(colour)
            beam_colours.extend(colour)
        
        return np.array(beam_colours, dtype=np.float32)

    def setup_buffers_beam(self):
        self.beam_vao = glGenVertexArrays(1)
        glBindVertexArray(self.beam_vao)

        self.beam_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.beam_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.beam_vertices.nbytes,  self.beam_vertices, GL_DYNAMIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        self.beam_colour_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.beam_colour_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.beam_colours.nbytes, self.beam_colours, GL_STATIC_DRAW)
        
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def setup_shaders_beam(self):
        vertex_shader_source = """
            #version 330 core
            layout (location = 0) in vec3 aPos;
            layout (location = 1) in vec4 aColor;
            
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            
            out vec4 Color;
            
            void main() {
                gl_Position = projection * view * model * vec4(aPos, 1.0);
                Color = aColor;
            }
        """
        
        fragment_shader_source = """
            #version 330 core
            in vec4 Color;
            out vec4 FragColor;
            
            void main() {
                FragColor = Color;
            }
        """

        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)
        
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)
        
        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, vertex_shader)
        glAttachShader(self.shader_program, fragment_shader)
        glLinkProgram(self.shader_program)
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        
        self.model_loc = glGetUniformLocation(self.shader_program, "model")
        self.view_loc = glGetUniformLocation(self.shader_program, "view")
        self.projection_loc = glGetUniformLocation(self.shader_program, "projection")

        self.beam_shader = self.shader_program
        self.beam_model_loc = self.model_loc
        self.beam_view_loc = self.view_loc
        self.beam_projection_loc = self.projection_loc
     
    def render_beams(self, model, view, projection):
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(3.0)

        glUseProgram(self.beam_shader)
        
        glUniformMatrix4fv(self.beam_model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(self.beam_view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(self.beam_projection_loc, 1, GL_FALSE, glm.value_ptr(projection))
        
        glBindVertexArray(self.beam_vao)
        glDrawArrays(GL_LINES, 0, self.beam_vertex_count)
        glBindVertexArray(0)
        
        glUseProgram(0)

    def create_triangle_array(self, parser):
        vertices = []

        for triangle in parser.triangles:
            v1, v2, v3 = triangle.triangle_nodes
            p1 = parser.vertices[v1]
            p2 = parser.vertices[v2]
            p3 = parser.vertices[v3]
            vertices.extend(p1)
            vertices.extend(p2)
            vertices.extend(p3)
        
        return np.array(vertices, dtype=np.float32)

    def setup_buffers_triangle(self):
        self.triangle_vao = glGenVertexArrays(1)
        glBindVertexArray(self.triangle_vao)

        self.triangle_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.triangle_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.triangle_vertices.nbytes, self.triangle_vertices, GL_DYNAMIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def setup_shaders_triangle(self):
        vertex_shader_source = """
            #version 330 core
            layout (location = 0) in vec3 aPos;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main() {
                gl_Position = projection * view * model * vec4(aPos, 1.0);
            }
        """

        fragment_shader_source = """
            #version 330 core
            out vec4 FragColour;

            void main() {
                FragColour = vec4(1.0, 1.0, 1.0, 1.0);
            }
        """

        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)
        
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)
        
        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, vertex_shader)
        glAttachShader(self.shader_program, fragment_shader)
        glLinkProgram(self.shader_program)
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        
        self.model_loc = glGetUniformLocation(self.shader_program, "model")
        self.view_loc = glGetUniformLocation(self.shader_program, "view")
        self.projection_loc = glGetUniformLocation(self.shader_program, "projection")

        self.triangle_shader = self.shader_program
        self.triangle_model_loc = self.model_loc
        self.triangle_view_loc = self.view_loc
        self.triangle_projection_loc = self.projection_loc

    def render_triangles(self, model, view, projection):
        glUseProgram(self.shader_program)
        
        glUniformMatrix4fv(self.triangle_model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(self.triangle_view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(self.triangle_projection_loc, 1, GL_FALSE, glm.value_ptr(projection))
        
        glBindVertexArray(self.triangle_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.triangle_count)
        glBindVertexArray(0)
