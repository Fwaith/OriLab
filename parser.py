import json
import numpy as np

class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = None

        self.vertices = []
        self.edges = []
        self.faces = []
        self.tris = []
        
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
                self.tris.append(face)
            elif len(face) == 4:
                face.sort()
                vd = self.find_diagonal(face[0], face[1:])
                self.create_facet_edge(face[0], vd)
                for v in face[1:]:
                    if v != vd:
                        self.tris.append([face[0], v, vd])
            elif len(face) > 4:
                self.triangulate_faces(face)
        self.edges = np.sort(self.edges)
        self.tris = np.array(self.tris)
   
    def find_diagonal(self, v, rest):
        for r in rest:
            matches = np.all(self.edges_sorted == [v, r], axis=1)
            if not np.any(matches):
                return r

    def create_facet_edge(self, v , vd):
        self.edges = np.vstack([self.edges, [v, vd]])
        self.edge_assignments.append('F')
        self.edge_fold_angles.append(0.0)

    def triangulate_faces(self, face):
        f = face.copy()
        while len(f) > 3:
            self.tris.append([f[0], f[1], f[2]])
            f.pop(1)
        self.tris.append([f[0], f[1], f[2]])

    def find_connected_beams(self, id):
        return np.where((self.edges[:, 0] == id) |
                        (self.edges[:, 1] == id))[0]

    def find_connected_triangles(self, id):
        return np.where((self.tris[:, 0] == id) |
                        (self.tris[:, 1] == id) |
                        (self.tris[:, 2] == id))[0]

    def calculate_beam_length(self, id):
        return np.linalg.norm(self.vertices[self.edges[id, 0]] - self.vertices[self.edges[id, 1]])

    def find_adjacent_triangles(self, id):
        adjacent = []

        for i, t in enumerate(self.tris):
            e1 = np.array([t[0], t[1]])
            e2 = np.array([t[0], t[2]])
            e3 = np.array([t[1], t[2]])
            if (e1 == self.edges[id]).all():
                adjacent.append(i)
            elif (e2 == self.edges[id]).all():
                adjacent.append(i)
            elif (e3 == self.edges[id]).all():
                adjacent.append(i)
        return np.array(adjacent)

    def calculate_area(self, id):
        a, b, c = self.tris[id]

        p1 = self.vertices[a]
        p2 = self.vertices[b]
        p3 = self.vertices[c]

        v1 = p2 - p1
        v2 = p3 - p1

        cross = np.cross(v1, v2)
        return 0.5 * np.linalg.norm(cross)

    def calculate_interior_angles(self, id):
        p1 = self.vertices[self.tris[id][0]]
        p2 = self.vertices[self.tris[id][1]]
        p3 = self.vertices[self.tris[id][2]]
        a = np.linalg.norm(p3 - p2) 
        b = np.linalg.norm(p3 - p1)
        c = np.linalg.norm(p2 - p1)
        angles = np.zeros(3)
        
        if b > 1e-10 and c > 1e-10:
            cos_angle = (b**2 + c**2 - a**2) / (2 * b * c)
            angles[0] = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        if a > 1e-10 and c > 1e-10:
            cos_angle = (a**2 + c**2 - b**2) / (2 * a * c)
            angles[1] = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        if a > 1e-10 and b > 1e-10:
            cos_angle = (a**2 + b**2 - c**2) / (2 * a * b)
            angles[2] = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        return angles

    def find_triangle_beams(self,id):
        sides = []
        e1 = np.array([self.tris[id][0], self.tris[id][1]])
        e2 = np.array([self.tris[id][0], self.tris[id][2]])
        e3 = np.array([self.tris[id][1], self.tris[id][2]])
        for i, e in enumerate(self.edges):
            if np.array_equal(e, e1) | np.array_equal(e, e2) | np.array_equal(e, e3):
                sides.append(i)
        return np.array(sides)

    def create_objects(self):
        self.nodes = [Node(id, self) for id in range(len(self.vertices))]
        self.beams = [Beam(id, self) for id in range(len(self.edges))]
        self.triangles = [Triangle(id, self) for id in range(len(self.tris))]

    def print_data(self):
        print('Vertices:\n', self.vertices)
        print('Edges:\n', self.edges)
        print('Edges Sorted:\n', self.edges_sorted)
        print('Edge Assignments:\n', self.edge_assignments)
        print('Edge Angles:\n', self.edge_fold_angles)
        print('Face:\n', self.faces)
        print('Triangles:\n', self.tris)
        print()
        for node in self.nodes:
            print(node)
        for beam in self.beams:
            print(beam)
        for triangle in self.triangles:
            print(triangle)

class Node:
    def __init__(self, id, parser):
        self.id = id
        self.mass = 1.0
        self.damping = 0.01

        self.position = parser.vertices[id]
        self.velocity = np.zeros(3)
        self.force = np.zeros(3)

        self.beams_connected = parser.find_connected_beams(id)
        self.tris_incident = parser.find_connected_triangles(id)
        self.creases_affecting = []

        for t in self.tris_incident:
            for b in parser.tris[t]:
                if b not in self.creases_affecting:
                    self.creases_affecting.append(b)

        self.creases_affecting = np.array(self.creases_affecting)
        self.creases_affecting = np.setdiff1d(self.creases_affecting, self.beams_connected)

    def __str__(self):
        return (
                f"Node {self.id}\n"
                f"Position {self.position}\n"
                f"Beams {self.beams_connected}\n"
                f"Triangles {self.tris_incident}\n"
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

        self.node_endpoints = np.array([parser.edges[id, 0], parser.edges[id, 1]])
        self.triangle_adjacent = parser.find_adjacent_triangles(id)

    def __str__(self):
        return (
                f"Beam {self.id}\n"
                f"Length {self.length_original}\n"
                f"Type {self.type}\n"
                f"Endpoints {self.node_endpoints}\n"
                f"Adjacent {self.triangle_adjacent}\n"
            )

class Triangle:
    def __init__(self, id, parser):
        self.id = id
        self.normal = np.zeros(3)

        self.angles_interior_original = parser.calculate_interior_angles(id)
        self.angles_interior_current = self.angles_interior_original
        self.k_face = 100.0
        self.area = parser.calculate_area(id)

        self.triangle_nodes = parser.tris[id]
        self.triangle_beams = parser.find_triangle_beams(id)
        self.triangle_adjacent = []

        for b in self.triangle_beams:
            for i, t in enumerate(parser.tris):
                if (np.array_equal(parser.edges[b], np.array([t[0], t[1]])) |
                    np.array_equal(parser.edges[b], np.array([t[0], t[2]])) |
                    np.array_equal(parser.edges[b], np.array([t[1], t[2]]))) and not np.array_equal(t, parser.tris[id]):
                    self.triangle_adjacent.append(i)

        self.triangle_adjacent = np.array(self.triangle_adjacent)

    def __str__(self):
        return (
                f"Triangle {self.id}\n"
                f"Angles {self.angles_interior_original}\n"
                f"Area {self.area}\n"
                f"Vertices {self.triangle_nodes}\n"
                f"Sides {self.triangle_beams}\n"
                f"Neighbours {self.triangle_adjacent}\n"
        )
