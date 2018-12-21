import os
import matplotlib.pyplot as plt

from plyfile import PlyData


cur_dir = os.getcwd() + "\\"
data_dir = str(os.path.abspath(os.path.join(cur_dir, os.pardir))) + "\\Dataset\\Zu Blatt 3\\"


plydata1 = PlyData.read(data_dir + 'simplePolygonTriangulated_1.ply')
plydata2 = PlyData.read(data_dir + 'simplePolygonTriangulated_2.ply')

used_dataset = plydata2

all_points = list(used_dataset.elements[0])
all_faces = [list(elem[0]) for elem in list(used_dataset.elements[1])]



print(all_points)
print(all_faces)


# Konvertiere Face Liste in Adjazenzliste
def converter(faces):
    max_vertex =  max([max(elem) for elem in faces])
    print(max_vertex)

    adj_list = dict()
    for i in range(max_vertex):
        adj_list[i] = list(set([entry for elem in faces if i in elem for entry in elem if entry > i]))

    print("adj_list =", adj_list)

converter(all_faces)



"""
def coloring(faces, colors, next_face, used_faces):
    print(colors)
    print("~~~~~~~~~next_face =", next_face)
    print("~~~~~~~~~next_face =", faces[next_face])

    if faces != []:
        p1 = faces[next_face][0]
        p2 = faces[next_face][1]
        p3 = faces[next_face][2]

        used_faces[next_face] = 1

        # print("len(faces) =", len(faces))
        # faces.remove(faces[next_face])
        # print("len(faces) =", len(faces))

        print("p1 =", p1)
        print("p2 =", p2)
        print("p3 =", p3)


        if colors[p1] == -1 and colors[p2] == -1 and colors[p3] == -1:
            colors[p1] = 0
            colors[p2] = 1
            colors[p3] = 2

            p1_p2_faces = [i for i in range(len(faces)) if p1 in faces[i] and p2 in faces[i] and not p3 in faces[i]]
            p1_p3_faces = [i for i in range(len(faces)) if p1 in faces[i] and p3 in faces[i] and not p2 in faces[i]]
            p2_p3_faces = [i for i in range(len(faces)) if p2 in faces[i] and p3 in faces[i] and not p1 in faces[i]]

            print("p1_p2_faces =", p1_p2_faces)
            print("p1_p3_faces =", p1_p3_faces)
            print("p2_p3_faces =", p2_p3_faces)

            children = p1_p2_faces + p1_p3_faces + p2_p3_faces
            print("children =", children)

            for face in children:
                if used_faces[face] != -1:
                    children.remove(face)


            for child in children:
                coloring(faces, colors, child, used_faces)


        else:

            if colors[p1] == -1 and colors[p2] != -1 and colors[p3] != -1:
                all_possible_colors = [0,1,2]
                all_possible_colors.remove(colors[p2])
                all_possible_colors.remove(colors[p3])
                colors[p1] = all_possible_colors[0]

            if colors[p2] == -1 and colors[p1] != -1 and colors[p3] != -1:
                all_possible_colors = [0,1,2]
                all_possible_colors.remove(colors[p1])
                all_possible_colors.remove(colors[p3])
                colors[p2] = all_possible_colors[0]

            if colors[p3] == -1 and colors[p1] != -1 and colors[p2] != -1:
                all_possible_colors = [0,1,2]
                all_possible_colors.remove(colors[p1])
                all_possible_colors.remove(colors[p2])
                colors[p3] = all_possible_colors[0]

            p1_p2_faces = [i for i in range(len(faces)) if p1 in faces[i] and p2 in faces[i] and not p3 in faces[i]]
            p1_p3_faces = [i for i in range(len(faces)) if p1 in faces[i] and p3 in faces[i] and not p2 in faces[i]]
            p2_p3_faces = [i for i in range(len(faces)) if p2 in faces[i] and p3 in faces[i] and not p1 in faces[i]]

            print("p1_p2_faces =", p1_p2_faces)
            print("p1_p3_faces =", p1_p3_faces)
            print("p2_p3_faces =", p2_p3_faces)

            children = p1_p2_faces + p1_p3_faces + p2_p3_faces

            for face in children:
                if used_faces[face] != -1:
                    children.remove(face)

            print("children =", children)

            for child in children:
                coloring(faces, colors, child, used_faces)

    else:
        if min(colors) == -1:
            coloring(faces, colors, 0, used_faces)

    return colors

"""

import numpy as np

def coloring(tri, colors, next_triangle, used_triangle):
    print(colors)
    print("~~~~~~~~~next_face =", next_triangle)
    print("~~~~~~~~~next_face =", tri[next_triangle])

    if tri != []:
        p1 = tri[next_triangle][0]
        p2 = tri[next_triangle][1]
        p3 = tri[next_triangle][2]

        used_triangle[next_triangle] = 1

        # print("len(faces) =", len(faces))
        # faces.remove(faces[next_face])
        # print("len(faces) =", len(faces))

        print("p1 =", p1)
        print("p2 =", p2)
        print("p3 =", p3)

        if max(colors) == -1:
            colors[p1] = 0
            colors[p2] = 1


        if colors[p1] == -1 and colors[p2] != -1 and colors[p3] != -1:
            all_possible_colors = [0,1,2]
            all_possible_colors.remove(colors[p2])
            all_possible_colors.remove(colors[p3])
            colors[p1] = all_possible_colors[0]

        if colors[p2] == -1 and colors[p1] != -1 and colors[p3] != -1:
            all_possible_colors = [0,1,2]
            all_possible_colors.remove(colors[p1])
            all_possible_colors.remove(colors[p3])
            colors[p2] = all_possible_colors[0]

        if colors[p3] == -1 and colors[p1] != -1 and colors[p2] != -1:
            all_possible_colors = [0,1,2]
            all_possible_colors.remove(colors[p1])
            all_possible_colors.remove(colors[p2])
            colors[p3] = all_possible_colors[0]

        # For each line, we have a runtime of O(n/3)
        p1_p2_triangles = [i for i in range(len(tri)) if p1 in tri[i] and p2 in tri[i] and not p3 in tri[i]]
        p1_p3_triangles = [i for i in range(len(tri)) if p1 in tri[i] and p3 in tri[i] and not p2 in tri[i]]
        p2_p3_triangles = [i for i in range(len(tri)) if p2 in tri[i] and p3 in tri[i] and not p1 in tri[i]]

        print("p1_p2_faces =", p1_p2_triangles)
        print("p1_p3_faces =", p1_p3_triangles)
        print("p2_p3_faces =", p2_p3_triangles)

        children = p1_p2_triangles + p1_p3_triangles + p2_p3_triangles

        for face in children:
            if used_triangle[face] != -1:
                children.remove(face)

        print("children =", children)

        for child in children:
            coloring(tri, colors, child, used_triangle)

    else:
        if min(colors) == -1:
            coloring(tri, colors, 0, used_triangle)

    return colors



def draw_convex_hull(all_points, faces, colors, title):
    px_values = list()
    py_values = list()
    faces_x_values = list()
    faces_y_values = list()

    for p in all_points:
        px_values.append(p[0])
        py_values.append(p[1])

    for face in faces:
        faces_x_values.append([all_points[face[0]][0], all_points[face[1]][0], all_points[face[2]][0], all_points[face[0]][0]])
        faces_y_values.append([all_points[face[0]][1], all_points[face[1]][1], all_points[face[2]][1], all_points[face[0]][1]])

    print("conv_hull_x_values =", faces_x_values)
    print("conv_hull_y_values =", faces_y_values)

    # c takes the colors, s takes the point sizes and zorder says whether the lines are over or below the points:
    plt.scatter(px_values, py_values, c=colors, s=80, zorder=10)
    for i in range(len(faces_x_values)):
        plt.plot(faces_x_values[i], faces_y_values[i], 'gray')
    plt.suptitle(title)
    plt.show()



def main_coloring(points, faces):
    colors = [-1] * len(points)
    used_faces = [-1] * len(faces)
    colors = coloring(faces, colors, 0, used_faces)

    print("final colors =", colors)
    renamed_colors = []
    for color in colors:
        if color == 0:
            renamed_colors.append('red')
        if color == 1:
            renamed_colors.append('limegreen')           # green, lime
        if color == 2:
            renamed_colors.append('dodgerblue')       # blue, cornflowerblue, dodgerblue

    print("len(points) =", len(points))
    print("len(renamed_colors) =", len(renamed_colors))
    print(renamed_colors)

    draw_convex_hull(points, faces, renamed_colors, "Task 5")

main_coloring(all_points, all_faces)

