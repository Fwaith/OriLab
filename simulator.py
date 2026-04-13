import numpy as np

class Simulator:
    def __init__(self, parser):
        self.nodes = parser.nodes
        self.beams = parser.beams
        self.triangles = parser.triangles
        self.step_counter = 0

        # ---- Physical parameters (tuned for a diagonal crease) ----
        # These are set in Beam and Triangle classes already, but we ensure they are correct:
        #   k_axial = 100.0
        #   k_crease = 200.0   (strong enough to overcome axial resistance)
        #   k_face = 50.0       (helps preserve triangle shape)
        #   mass = 1.0
        #   damping_ratio = 0.8

        # Compute stable time step from the highest axial frequency
        self.dt = self.compute_stable_dt()

    def compute_stable_dt(self):
        """Compute a stable time step using the highest natural frequency."""
        max_k_axial = 0.0
        min_mass = 1e9
        for beam in self.beams:
            if beam.k_axial > max_k_axial:
                max_k_axial = beam.k_axial
        for node in self.nodes:
            if node.mass < min_mass:
                min_mass = node.mass
        if max_k_axial > 0 and min_mass > 0:
            omega_max = np.sqrt(max_k_axial / min_mass)
            dt = 0.9 / (2 * np.pi * omega_max)   # 90% of stability limit
            return dt
        else:
            return 0.001   # fallback

    def step(self, dt=None):
        if dt is None:
            dt = self.dt
        # Reset forces
        for node in self.nodes:
            node.force[:] = 0.0

        self.apply_axial_forces()
        self.apply_crease_forces()
        self.apply_face_forces()
        self.apply_damping()

        # Integrate (skip pinned nodes)
        for node in self.nodes:
            if node.mass > 1e9:
                continue
            acc = node.force / node.mass
            node.velocity += acc * dt
            node.position += node.velocity * dt

        self.step_counter += 1

    def apply_axial_forces(self):
        eps = 1e-10
        for beam in self.beams:
            idx_a, idx_b = beam.node_endpoints
            node_a = self.nodes[idx_a]
            node_b = self.nodes[idx_b]
            vec = node_b.position - node_a.position
            L = np.linalg.norm(vec)
            if L < eps:
                continue
            dir_vec = vec / L
            delta = L - beam.length_original
            F_mag = -beam.k_axial * delta
            force_B = F_mag * dir_vec
            force_A = -force_B
            node_a.force += force_A
            node_b.force += force_B

    def apply_face_forces(self):
        eps = 1e-8
        for tri in self.triangles:
            i1, i2, i3 = tri.triangle_nodes
            p1 = self.nodes[i1].position
            p2 = self.nodes[i2].position
            p3 = self.nodes[i3].position

            e12 = p2 - p1
            e13 = p3 - p1
            e23 = p3 - p2

            l12 = np.linalg.norm(e12)
            l13 = np.linalg.norm(e13)
            l23 = np.linalg.norm(e23)

            if l12 < eps or l13 < eps or l23 < eps:
                continue

            cos_alpha1 = np.dot(e12, e13) / (l12 * l13)
            cos_alpha1 = np.clip(cos_alpha1, -1.0, 1.0)
            alpha1 = np.arccos(cos_alpha1)

            cos_alpha2 = np.dot(-e12, e23) / (l12 * l23)
            cos_alpha2 = np.clip(cos_alpha2, -1.0, 1.0)
            alpha2 = np.arccos(cos_alpha2)

            cos_alpha3 = np.dot(-e13, -e23) / (l13 * l23)
            cos_alpha3 = np.clip(cos_alpha3, -1.0, 1.0)
            alpha3 = np.arccos(cos_alpha3)

            alpha1_0 = tri.angles_interior_original[0]
            alpha2_0 = tri.angles_interior_original[1]
            alpha3_0 = tri.angles_interior_original[2]

            normal = np.cross(e12, e13)
            norm_n = np.linalg.norm(normal)
            if norm_n < eps:
                continue
            n = normal / norm_n

            cross_e12_n = np.cross(e12, n)
            cross_e13_n = np.cross(e13, n)
            grad1_p1 = -cross_e12_n / (l12*l12) - cross_e13_n / (l13*l13)
            grad1_p2 =  cross_e12_n / (l12*l12)
            grad1_p3 =  cross_e13_n / (l13*l13)

            delta1 = alpha1 - alpha1_0
            if abs(delta1) > eps:
                F_mag = -tri.k_face * delta1
                self.nodes[i1].force += F_mag * grad1_p1
                self.nodes[i2].force += F_mag * grad1_p2
                self.nodes[i3].force += F_mag * grad1_p3

            e21 = -e12
            cross_e21_n = np.cross(e21, n)
            cross_e23_n = np.cross(e23, n)
            grad2_p2 = -cross_e21_n / (l12*l12) - cross_e23_n / (l23*l23)
            grad2_p1 =  cross_e21_n / (l12*l12)
            grad2_p3 =  cross_e23_n / (l23*l23)

            delta2 = alpha2 - alpha2_0
            if abs(delta2) > eps:
                F_mag = -tri.k_face * delta2
                self.nodes[i2].force += F_mag * grad2_p2
                self.nodes[i1].force += F_mag * grad2_p1
                self.nodes[i3].force += F_mag * grad2_p3

            e31 = -e13
            e32 = -e23
            cross_e31_n = np.cross(e31, n)
            cross_e32_n = np.cross(e32, n)
            grad3_p3 = -cross_e31_n / (l13*l13) - cross_e32_n / (l23*l23)
            grad3_p1 =  cross_e31_n / (l13*l13)
            grad3_p2 =  cross_e32_n / (l23*l23)

            delta3 = alpha3 - alpha3_0
            if abs(delta3) > eps:
                F_mag = -tri.k_face * delta3
                self.nodes[i3].force += F_mag * grad3_p3
                self.nodes[i1].force += F_mag * grad3_p1
                self.nodes[i2].force += F_mag * grad3_p2

    def apply_crease_forces(self):
        eps = 1e-8
        max_cot = 20.0
        max_force = 100.0

        for beam in self.beams:
            if beam.k_crease == 0 or len(beam.triangle_adjacent) != 2:
                continue

            tri1 = self.triangles[beam.triangle_adjacent[0]]
            tri2 = self.triangles[beam.triangle_adjacent[1]]

            p1_idx, p2_idx = beam.node_endpoints
            tri1_nodes = set(tri1.triangle_nodes)
            p3_idx = list(tri1_nodes - {p1_idx, p2_idx})[0]
            tri2_nodes = set(tri2.triangle_nodes)
            p4_idx = list(tri2_nodes - {p1_idx, p2_idx})[0]

            p1 = self.nodes[p1_idx]
            p2 = self.nodes[p2_idx]
            p3 = self.nodes[p3_idx]
            p4 = self.nodes[p4_idx]

            pos1 = p1.position
            pos2 = p2.position
            pos3 = p3.position
            pos4 = p4.position

            e = pos2 - pos1
            le = np.linalg.norm(e)
            if le < eps:
                continue
            e_hat = e / le

            v13 = pos3 - pos1
            v23 = pos3 - pos2
            v14 = pos4 - pos1
            v24 = pos4 - pos2

            n1 = np.cross(e, v13)
            n2 = np.cross(v14, e)
            norm_n1 = np.linalg.norm(n1)
            norm_n2 = np.linalg.norm(n2)
            if norm_n1 < eps or norm_n2 < eps:
                continue
            n1 = n1 / norm_n1
            n2 = n2 / norm_n2

            cos_theta = np.dot(n1, n2)
            sin_theta = np.dot(np.cross(n1, n2), e_hat)
            theta = np.arctan2(sin_theta, cos_theta)

            beam.fold_angle_current = theta
            angle_error = beam.fold_angle_target - theta   # CRITICAL FIX
            if abs(angle_error) < 1e-8:
                continue

            F_mag = beam.k_crease * angle_error   # positive force toward target

            def safe_cot(vec, edge):
                cross_norm = np.linalg.norm(np.cross(vec, edge))
                if cross_norm < eps:
                    return 0.0
                return np.dot(vec, edge) / cross_norm

            cot_a1 = safe_cot(v13, e)
            cot_a2 = safe_cot(v23, -e)
            cot_b1 = safe_cot(v14, e)
            cot_b2 = safe_cot(v24, -e)

            cot_a1 = np.clip(cot_a1, -max_cot, max_cot)
            cot_a2 = np.clip(cot_a2, -max_cot, max_cot)
            cot_b1 = np.clip(cot_b1, -max_cot, max_cot)
            cot_b2 = np.clip(cot_b2, -max_cot, max_cot)

            grad_p1 = (cot_a1 * v13 / le + cot_b1 * v14 / le) / (2.0 * le)
            grad_p2 = (cot_a2 * v23 / le + cot_b2 * v24 / le) / (2.0 * le)
            grad_p3 = -(cot_a1 * v13 / le + cot_a2 * v23 / le) / (2.0 * le)
            grad_p4 = -(cot_b1 * v14 / le + cot_b2 * v24 / le) / (2.0 * le)

            force_p1 = F_mag * grad_p1
            force_p2 = F_mag * grad_p2
            force_p3 = F_mag * grad_p3
            force_p4 = F_mag * grad_p4

            # Clamp forces
            for f in (force_p1, force_p2, force_p3, force_p4):
                nf = np.linalg.norm(f)
                if nf > max_force:
                    f *= max_force / nf

            p1.force += force_p1
            p2.force += force_p2
            p3.force += force_p3
            p4.force += force_p4

    def apply_damping(self):
        for node in self.nodes:
            if node.mass > 1e9:
                continue
            F_damp = np.zeros(3)
            for beam_idx in node.beams_connected:
                beam = self.beams[beam_idx]
                if beam.node_endpoints[0] == node.id:
                    neighbor = self.nodes[beam.node_endpoints[1]]
                else:
                    neighbor = self.nodes[beam.node_endpoints[0]]
                rel_vel = neighbor.velocity - node.velocity
                # Damping ratio = 0.8 (critically damped)
                c = 2 * 0.8 * np.sqrt(beam.k_axial * node.mass)
                F_damp += c * rel_vel
            node.force += F_damp
