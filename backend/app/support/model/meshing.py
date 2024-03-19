# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import numpy as np
import pygalmesh


def parse_obj_file(file_path):
    vertices = []
    faces = []

    with open(file_path, "r") as obj_file:
        for line in obj_file:
            if line.startswith("v "):
                vertices.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith("f "):
                face_indices = [int(index) for index in line.strip().split()[1:]]
                faces.append(face_indices)

    return vertices, faces


def remove_unused_vertices(vertices, faces):
    used_vertices = {index for face in faces for index in face}
    used_vertices = sorted(list(used_vertices))

    new_vertex_indices = {old_index: new_index for new_index, old_index in enumerate(used_vertices, start=1)}

    new_vertices = [vertices[index - 1] for index in used_vertices]
    new_faces = [[new_vertex_indices[index] for index in face] for face in faces]

    return new_vertices, new_faces


def write_obj_file(file_path, vertices, faces):
    with open(file_path, "w") as obj_file:
        for vertex in vertices:
            obj_file.write("v " + " ".join(map(str, vertex)) + "\n")

        for face in faces:
            obj_file.write("f " + " ".join(map(str, face)) + "\n")


model_file = sys.argv[sys.argv.index("--model_file") + 1]
discretization = float(sys.argv[sys.argv.index("--discretization") + 1])
localpath = sys.argv[sys.argv.index("--localpath") + 1]
model_name = sys.argv[sys.argv.index("--model_name") + 1]

print(model_file)
with open(model_file, "r") as file:
    lines = file.readlines()

# Initialize a variable to keep track of the current material index
current_material_index = 0

obj_files = []
blocks = []
# Iterate through the lines to split the file based on usemtl lines
for i, line in enumerate(lines):
    # Check if the line starts with "usemtl"
    if line.startswith("usemtl"):
        # Increment the material index
        current_material_index += 1
        blocks.append(current_material_index)

        # Create a new OBJ file for the current material
        output_obj_file = f"{localpath}/mesh{current_material_index}.obj"
        obj_files.append(output_obj_file)
        with open(output_obj_file, "w") as mesh_file:
            # Write the vertices to the current OBJ file
            mesh_file.writelines([line for line in lines[:i] if not line.startswith("f")])

    # Check if the line starts with "f" (face)
    elif line.startswith("f"):
        # Append the face to the current OBJ file for the current material
        with open(output_obj_file, "a") as mesh_file:
            mesh_file.write(line)

all_volume_elements = []
all_nodes = []
block_id = []

# Iterate over each STEP file
for index, obj_file in enumerate(obj_files):
    vertices, faces = parse_obj_file(obj_file)
    new_vertices, new_faces = remove_unused_vertices(vertices, faces)
    write_obj_file(obj_file, new_vertices, new_faces)

    # Create a mesh from the STEP file
    mesh = pygalmesh.generate_volume_mesh_from_surface_mesh(
        obj_file,
        lloyd=True,
        odt=False,
        perturb=True,
        exude=True,
        max_edge_size_at_feature_edges=1.0,
        min_facet_angle=25,
        max_radius_surface_delaunay_ball=discretization,  # Adjusted for better volume meshing
        max_facet_distance=5,
        max_circumradius_edge_ratio=3,
        max_cell_circumradius=discretization,
        exude_sliver_bound=0.0,
        exude_time_limit=0.0,
        verbose=False,
        reorient=False,
        seed=0,
    )

    mesh.write(obj_file.replace(".obj", ".vtk"))
    # Get volume elements and their nodes
    volume_elements = mesh.get_cells_type("tetra")
    nodes = mesh.points

    # Append the volume elements and nodes to the lists
    all_volume_elements.append(volume_elements)
    block_id.append(np.full(len(volume_elements), index + 1))
    all_nodes.append(nodes)


# Calculate volumes of tetrahedral elements
def tetrahedron_volume(p1, p2, p3, p4):
    return np.abs(np.dot((p2 - p1), np.cross((p3 - p1), (p4 - p1)))) / 6


txt_file = os.path.join(localpath, model_name + ".txt")
with open(txt_file, "w") as file:
    file.write("#header: x y z block_id volume\n")
    for index, _ in enumerate(all_volume_elements):
        for sub_index, element in enumerate(all_volume_elements[index]):
            p1, p2, p3, p4 = [all_nodes[index][i] for i in element]
            # print(p1, p2, p3, p4)
            volume = tetrahedron_volume(p1, p2, p3, p4)
            centroid = np.mean([p1, p2, p3, p4], axis=0)
            file.write(f"{centroid[0]} {centroid[1]} {centroid[2]} {block_id[index][sub_index]} {volume}\n")

id = 1
for block in blocks:
    ns_file = os.path.join(localpath, f"ns_{model_name}_{block}.txt")
    with open(ns_file, "w") as file:
        file.write("#header: global_id\n")
        for index, _ in enumerate(all_volume_elements):
            for sub_index, element in enumerate(all_volume_elements[index]):
                if block == block_id[index][sub_index]:
                    file.write(f"{id}\n")
                    id += 1
