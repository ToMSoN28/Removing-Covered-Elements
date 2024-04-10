import random

import numpy as np
import pygame as pg

from line import Line
from point import Point


class Wall:
    
    def __init__(self, wall_id, screen, path, if_in):
        self.id = wall_id
        self.screen = screen
        self.path = path
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        self.color = (r,g,b)
        self.if_in = if_in
        lines = []
        points = []
        self.read_wall_from_file()
        
        
    def read_wall_from_file(self):
        lines = []
        points = []
        sx, sy = self.screen.get_size()
        with open(self.path, 'r') as file:
            for line in file:
                x,y,z = line.split()
                point = Point(int(x), int(sy - int(y)), int(z))
                points.append(point)
            
            for i in range(len(points)-1):
                line = Line(self.screen, points[i], points[i+1], self.id)
                lines.append(line)
            line = Line(self.screen, points[len(points)-1], points[0], self.id)
            lines.append(line)
            
        self.points = points
        self. lines = lines
        
    def plane_equation_3points(self, p1, p2, p3):
        v1 = p2 - p1
        v2 = p3 - p1
        cp = np.cross(v1, v2)
        A, B, C = cp
        D = -np.dot(cp, p1)
        
        return A, B, C, D
    
    def plane_equation_n_points(self, points): # points is a Nx3 matrix
        centroid = np.mean(points, axis=0)
        normalized_points = points - centroid
        U, S, Vt = np.linalg.svd(normalized_points)
        normal_vector = Vt[2, :]
        A, B, C = normal_vector
        D = -np.dot(normal_vector, centroid)
        
        return A, B, C, D

    def find_z_of_plane(self, x, y):
        if len(self.point_list) == 3:
            point1 = np.array([self.point_list[0].x, self.point_list[0].y, self.point_list[0].z])
            point2 = np.array([self.point_list[1].x, self.point_list[1].y, self.point_list[1].z])
            point3 = np.array([self.point_list[2].x, self.point_list[2].y, self.point_list[2].z])
            A, B, C, D = self.plane_equation_3points(point1, point2, point3)
        else:
            points = np.zeros((len(self.point_list), 3))
            for i in range(len(self.point_list)):
                points[i] = [self.point_list[i].x, self.point_list[i].y, self.point_list[i].z]
            A, B, C, D = self.plane_equation_n_points(points)
            
        return (-A * x - B * y - D) / C
    
    def draw_wall_with_fill(self):
        points_to_fill = []
        for point in self.points:
            points_to_fill.append(point.cordinate_to_print())
            
        pg.draw.polygon(self.screen, self.color, points_to_fill)
            
    def points_transformation(self, tranfromation_matrix):
        for point in self.points:
            point.get_transformation(tranfromation_matrix)

            
    def zoom_transformation(self, value):
        for point in self.points:
            point.zoom_transformation(value)
            
    def print_polygon_structure(self):
        self.points_to_print = []
        self.line_to_print = []
        
        for point in self.points:
            self.points_to_print.append(point.cordinate_to_print())
        for i in range(len(self.points_to_print)-1):
            self.line_to_print.append((self.points_to_print[i], self.points_to_print[i+1]))
        self.line_to_print.append((self.points_to_print[0], self.points_to_print[len(self.points_to_print)-1]))
        
    def point_inside_polygon(self, x, y):
        crossings = 0
        for line in self.line_to_print:
            if (line[0][1] > y and line[1][1] <= y) or (line[0][1] <= y and line[1][1] > y):
                if line[0][0] + (y - line[0][1]) / (line[1][1] - line[0][1]) * (line[1][0] - line[0][0]) <= x:
                    crossings += 1
        return crossings % 2 == 1
    
    def points_in_triangle(self):
            # Obliczamy wektory boczne trójkąta
            v1 = np.array((self.points[1].x, self.points[1].y, self.points[1].z)) - np.array((self.points[0].x, self.points[0].y, self.points[0].z))
            v2 = np.array((self.points[2].x, self.points[2].y, self.points[2].z)) - np.array((self.points[0].x, self.points[0].y, self.points[0].z))
            
            # Obliczamy normalną do płaszczyzny trójkąta
            normal = np.cross(v1, v2)
            
            # Obliczamy równanie płaszczyzny trójkąta w postaci Ax + By + Cz + D = 0
            A, B, C = normal
            D = np.dot(normal, np.array((self.points[0].x, self.points[0].y, self.points[0].z)))
            
            # Wyznaczamy minimalną i maksymalną wartość dla każdego wymiaru (x, y, z)
            min_x = min(self.points[0].x, self.points[1].x, self.points[2].x)
            max_x = max(self.points[0].x, self.points[1].x, self.points[2].x)
            min_y = min(self.points[0].y, self.points[1].y, self.points[2].y)
            max_y = max(self.points[0].y, self.points[1].y, self.points[2].y)
            min_z = min(self.points[0].z, self.points[1].z, self.points[2].z)
            max_z = max(self.points[0].z, self.points[1].z, self.points[2].z)
            
            self.punkty_wewnatrz = []
            # Sprawdzamy wszystkie punkty wewnątrz obszaru ograniczonego przez trójkąt
            for x in range(int(min_x), int(max_x) + 1):
                for y in range(int(min_y), int(max_y) + 1):
                    for z in range(int(min_z), int(max_z) + 1):
                        try:
                            # Obliczamy wartość równania płaszczyzny dla aktualnego punktu
                            wartosc = A * x + B * y + C * z - D
                            # Jeśli wartość jest bliska zeru, punkt należy do płaszczyzny trójkąta
                            if abs(wartosc) < 0.001:
                                v0 = v2
                                v2 = np.array([x,y,z,])-np.array((self.points[0].x, self.points[0].y, self.points[0].z))
                                
                                # Obliczamy współczynniki barycentryczne
                                dot00 = np.dot(v0, v0)
                                dot01 = np.dot(v0, v1)
                                dot02 = np.dot(v0, v2)
                                dot11 = np.dot(v1, v1)
                                dot12 = np.dot(v1, v2)
                                
                                # Obliczamy współczynniki barycentryczne
                                invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
                                u = (dot11 * dot02 - dot01 * dot12) * invDenom
                                v = (dot00 * dot12 - dot01 * dot02) * invDenom
                                
                                # Sprawdzamy czy punkt jest wewnątrz trójkąta
                                if (u >= 0) and (v >= 0) and (u + v <= 1):
                                    point = Point(x, y, z)
                                    # point.to_string()
                                    self.punkty_wewnatrz.append(point)
                        except ZeroDivisionError:
                            continue
                        except OverflowError:
                            continue
            

        
            
            
            