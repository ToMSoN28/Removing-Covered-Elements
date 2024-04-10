import pygame as pg
import numpy as np
from wall import Wall
from line import Line
from point import Point

class LineScaner:
    def __init__(self, screen, walls, lines):
        self.screen = screen
        self.sx, self.sy = screen.get_size()
        self.walls = walls
        
    def find_wall_of_id(self, wall_id):
        for wall in self.walls:
            if wall.id == wall_id:
                return wall
        return None
            
    def sizing_scan(self):
        min_x = None
        max_x = None
        min_y = None
        max_y = None
        for wall in self.walls:
            for point in wall.points:
                x, y = point.cordinate_to_print()
                x, y = int(x), int(y)
                if min_x == None or x < min_x:
                    min_x = x
                if min_y == None or y < min_y:
                    min_y = y
                if max_x == None or x > max_x:
                    max_x = x
                if max_y == None or y > max_y:
                    max_y = y
                if min_x < 0:
                    min_x = 0
                if min_y < 0:
                    min_y = 0
                if max_x > 800:
                    max_x = 800
                if max_y > 600:
                    maxy = 600
        return min_x, max_x, min_y, max_y
            
            
    def scren_scann(self):
        values_matrix = np.empty((800, 600), dtype=np.float64)
        values_matrix.fill(np.inf)
        colors_matrix = np.full((800, 600, 3), (255, 255, 255), dtype=np.uint8)
        # min_x, max_x, min_y, max_y = self.sizing_scan()
        for wall in self.walls:
            # wall.print_polygon_structure()
            # for i in range(min_x, max_x-1):
            #     for j in range(min_y, max_y-1):
            #         if wall.point_inside_polygon(i,j):
            #             x, y, z = wall.points[0].print_to_coordinate(i, j)
            #             if values_matrix[i][j] > z and z < 0:
            #                 values_matrix[i][j] = z
            #                 colors_matrix[i][j] = wall.color
            # wall.points_in_triangle()
            for point in wall.punkty_wewnatrz:
                x, y = point.cordinate_to_print()
                x, y = int(x), int(y)
                if values_matrix[x][y] > point.z:
                    values_matrix[x][y] = point.z
                    colors_matrix[x][y] = wall.color
                            
        pg.surfarray.blit_array(self.screen, colors_matrix)  
        
    def z_buffering(self):
        width = 800
        height = 600

        # Inicjalizacja bufora Z oraz kolorów
        z_buffer = np.full((width, height), float('inf'))
        image = np.zeros((width, height, 3), dtype=np.uint8)

        for wall in self.walls:
            v0, v1, v2 = (wall.points[i].to_h_matrix() for i in range(3))
            print(v0, v1, v2)

            # Ustalanie współrzędnych trójkąta
            x_min, x_max = int(min(v0[0], v1[0], v2[0])), int(max(v0[0], v1[0], v2[0]))
            y_min, y_max = int(min(v0[1], v1[1], v2[1])), int(max(v0[1], v1[1], v2[1]))

            for x in range(x_min, x_max + 1):
                for y in range(y_min, y_max + 1):
                    barycentric_coords = self.barycentric_coordinates((x, y), v0[:2], v1[:2], v2[:2])
                    if barycentric_coords is not None and all(coord >= 0 for coord in barycentric_coords):
                        z_interpolated = self.interpolate_depth(barycentric_coords, v0[2], v1[2], v2[2])

                        if z_interpolated < z_buffer[x, y]:
                            z_buffer[x, y] = z_interpolated
                            # Tutaj można dodać kolorowanie trójkąta w zależności od danych w wierzchołkach
                            image[x, y] = wall.color # Biały kolor

        pg.surfarray.blit_array(self.screen, image) 

    def barycentric_coordinates(self, point, v0, v1, v2):
        x, y = point
        x0, y0 = v0
        x1, y1 = v1
        x2, y2 = v2

        denominator = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if denominator == 0:
            return None

        w0 = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / denominator
        w1 = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / denominator
        w2 = 1 - w0 - w1

        return np.array([w0, w1, w2])

    def interpolate_depth(self, barycentric_coords, z0, z1, z2):
        w0, w1, w2 = barycentric_coords
        return z0 * w0 + z1 * w1 + z2 * w2    
        