import json
import numpy as np

class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = None

        self.vertices = []
        self.edges = []  
        self.faces = [] 
        
        self.nodes = []
        self.beams = []
        self.triangles = []
        
        self.load()
    
    def load(self):
        with open(self.path, "r") as f:
            self.data = json.load(f)
        
        self.extract_vertices()
        self.extract_edges()
        self.extract_faces()
        self.discretise_crease_pattern()
        self.create_objects()
        self.print_data()

    def extract_vertices(self):
        vertices_coords = self.data["vertices_coords"]
        self.vertices = np.array([[x, y, 0.0] for x, y, *_ in vertices_coords], dtype = np.float32)
    
    def extract_edges(self):
        self.edges = np.array(self.data.get("edges_vertices", []), dtype=int)
        self.edges_sorted = np.array([tuple(edge) for edge in np.sort(self.edges, axis=1)])
        self.edge_assignments = self.data.get("edges_assignment", [])
        self.edge_fold_angles = self.data.get("edges_foldAngle", [])
    
    def extract_faces(self):
        self.faces = self.data.get("faces_vertices", [])
        
    def discretise_crease_pattern(self):
        for face in self.faces:
            if len(face) == 3:
                self.triangles.append(face)
            elif len(face) == 4:
                face.sort()
                vd = self.find_diagonal(face[0], face[1:])
                self.create_facet_edge(face[0], vd)
                for v in face[1:]:
                    if v != vd:
                        self.triangles.append([face[0], v, vd])
            elif len(face) > 4:
                print('WORK ON LATER')
                #triangulate_faces(face)
        self.triangles = np.array(self.triangles)
   
    def find_diagonal(self, v, rest):
        for r in rest:
            matches = np.all(self.edges_sorted == [v, r], axis=1)
            if not np.any(matches):
                return r

    def create_facet_edge(self, v , vd):
        self.edges = np.vstack([self.edges, [v, vd]])
        self.edge_assignments.append('F')
        self.edge_fold_angles.append(0.0)

   # FIX: FINISH LATER
    #def triangulate_faces(self):
    #    print()

    def find_connected_beams(self, id):
        return np.where((self.edges[:, 0] == id) |
                        (self.edges[:, 1] == id))[0]

    def find_connected_triangles(self, id):
        return np.where((self.triangles[:, 0] == id) |
                        (self.triangles[:, 1] == id) |
                        (self.triangles[:, 2] == id))[0]

    def calculate_beam_length(self, id):
        return np.linalg.norm(self.vertices[self.edges[id, 0]] - self.vertices[self.edges[id, 1]])

    def find_adjacent_triangles(self, id):
        for t in self.triangles:
            adjacent = []
            e1 = [t[0], t[1]]
            e2 = [t[0], t[2]]
            e3 = [t[1], t[2]]
            if (id == e1) | (id == e2) | (id == e3):
                np.append(adjacent, id) 

    def create_objects(self):
        self.nodes = [Node(id, self) for id in range(len(self.vertices))]
        self.beams = [Beam(id, self) for id in range(len(self.edges))]

    def print_data(self):
        print('Vertices:\n', self.vertices)
        print('Edges:\n', self.edges)
        print('Edges Sorted:\n', self.edges_sorted)
        print('Edge Assignments:\n', self.edge_assignments)
        print('Edge Angles:\n', self.edge_fold_angles)
        print('Face:\n', self.faces)
        print('Triangles:\n', self.triangles)
        print()
        for node in self.nodes:
            print(node)
        for beam in self.beams:
            print(beam)

class Node:
    def __init__(self, id, parser):
        self.id = id
        self.mass = 1.0
        self.damping = 0.01

        self.position = parser.vertices[id]
        self.velocity = np.zeros(3)
        self.force = np.zeros(3)

        self.beams_connected = parser.find_connected_beams(id)
        self.triangles_incident = parser.find_connected_triangles(id)
        self.creases_affecting = []
        
        for t in self.triangles_incident:
            for b in parser.triangles[t]:
                if b not in self.creases_affecting:
                    self.creases_affecting.append(b)

        self.creases_affecting = np.array(self.creases_affecting)
        self.creases_affecting = np.setdiff1d(self.creases_affecting, self.beams_connected)

    def __str__(self):
        return (
                f"Node {self.id}\n"
                f"Position {self.position}\n"
                f"Beams {self.beams_connected}\n"
                f"Triangles {self.triangles_incident}\n"
                f"Creases Affecting {self.creases_affecting}\n"
            )

class Beam:
    def __init__(self, id , parser):
        self.id = id
        self.direction = np.zeros(3)

        self.length_original = parser.calculate_beam_length(id)
        self.length_current = self.length_original
        self.type = parser.edge_assignments[id]
        self.k_axial = 100.0
        self.k_crease = 10.0
        self.fold_angle_target = parser.edge_fold_angles[id]
        self.fold_angle_current = 0.0

        self.node_endpoints = [parser.edges[id, 0], parser.edges[id, 1]]
        self.triangle_adjacent = parser.find_adjacent_triangles(id)

    def __str__(self):
        return (
                f"Beam {self.id}\n"
                f"Length {self.length_original}\n"
                f"Type {self.type}\n"
            )

class Triangle:
    def __init__():
        self.normal
        self.angles_interior_current

        self.angles_interior_original
        self.k_face
        self.area

        self.triangle_nodes
        self.triangle_beams
        self.triangle_adjacent
