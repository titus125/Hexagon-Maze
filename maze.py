# -*- coding: utf-8 -*-
"""Maze.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nFHgjbb78WX0yC6XhN1bFMge5Z4aaVf0
"""

# Utils

# creates a spectrum of n colors, from https://stackoverflow.com/questions/58811499/generating-gradient-colors-in-python
def spectrum(n):
    hsv = [(h, 1, 1) for h in np.linspace(0, 240/360, n)]
    rgb = [colorsys.hsv_to_rgb(*tup) for tup in hsv]
    defloat = lambda x: tuple((int(255 * i) for i in x))
    return [defloat(x) for x in rgb]

# Code for rending the maze

# partial code from Jamis Buck's "Mazes for Programmers"
def draw_maze(maze, size):
  params = get_draw_params(size)
  a_size, b_size, width, height = params
  
  img_width = int((3 * a_size * maze.columns + a_size + 0.5))
  img_height = int((height * maze.rows + b_size + 0.5))

  background = (255, 255, 255)
  wall = (0, 0, 0)

  img = Image.new("RGB", (img_width + 1, img_height + 1), background)
  draw = ImageDraw.Draw(img)

  for mode in ["backgrounds", "walls"]:
    for cell in maze.cells.values():
      cx, cy, x_fw, x_nw, x_ne, x_fe, y_n, y_m, y_s = get_hex_coord(size, params, cell)

      if mode == "backgrounds":
        color = cell.color
        if color:
          points = [(x_fw, y_m), (x_nw, y_n), (x_ne, y_n), (x_fe, y_m), (x_ne, y_s), (x_nw, y_s)]
          draw.polygon(points, color, color)

      elif mode == "walls":
        if not cell.neighbours["SW"]:
            draw.line((x_fw, y_m, x_nw, y_s), wall, width=2)

        if not cell.neighbours["NW"]:
            draw.line((x_fw, y_m, x_nw, y_n), wall, width=2)

        if not cell.neighbours["N"]:
            draw.line((x_nw, y_n, x_ne, y_n), wall, width=2)

        if not cell.is_linked(cell.neighbours["NE"]):
            draw.line((x_ne, y_n, x_fe, y_m), wall, width=2)

        if not cell.is_linked(cell.neighbours["SE"]):
            draw.line((x_fe, y_m, x_ne, y_s), wall, width=2)

        if not cell.is_linked(cell.neighbours["S"]):
            draw.line((x_ne, y_s, x_nw, y_s), wall, width=2)

  # draw the exit
  end_cell = maze.cells[maze.end_coord]
  color = end_cell.color
  ecx, ecy, ex_fw, ex_nw, ex_ne, ex_fe, ey_n, ey_m, ey_s = get_hex_coord(size, params, end_cell)

  if not end_cell.neighbours["SW"]:
    draw.line((ex_fw, ey_m, ex_nw, ey_s), color, width=2)
    return img

  if not end_cell.neighbours["NW"]:
    draw.line((ex_fw, ey_m, ex_nw, ey_n), color, width=2)
    return img

  if not end_cell.neighbours["N"]:
    draw.line((ex_nw, ey_n, ex_ne, ey_n), color, width=2)
    return img

  if not end_cell.neighbours["NE"]:
    draw.line((ex_ne, ey_n, ex_fe, ey_m), color, width=2)
    return img

  if not end_cell.neighbours["SE"]:
    draw.line((ex_fe, ey_m, ex_ne, ey_s), color, width=2)
    return img

  if not end_cell.neighbours["SW"]:
    draw.line((ex_ne, ey_s, ex_nw, ey_s), color, width=2)
    return img   

def draw_solution(maze, size):
  img = draw_maze(maze, size)
  draw = ImageDraw.Draw(img)

  params = get_draw_params(size)
  a_size, b_size, width, height = params

  # draw out the solution path
  for i in range(len(maze.solution) - 1):
    # get centre coorindates of cell
    cell = maze.cells[maze.solution[i]]
    cx, cy, x_fw, x_nw, x_ne, x_fe, y_n, y_m, y_s = get_hex_coord(size, params, cell)

    # get centre coorindates of next cell
    next_cell = maze.cells[maze.solution[i+1]]
    ncx, ncy, nx_fw, nx_nw, nx_ne, nx_fe, ny_n, ny_m, ny_s = get_hex_coord(size, params, next_cell)

    sol_color = (0,0,0)

    # draw line to connect the centre of cell with next cell
    draw.line((cx,cy,ncx,ncy), fill=sol_color,width=2)

    if i == len(maze.solution) - 2:
      # draw the solution path for last cell 
      if not next_cell.neighbours["SW"]:
        draw.line((ncx, ncy, ncx-1.5*a_size, ncy+b_size/2), sol_color, width=2)
        return img

      if not next_cell.neighbours["NW"]:
        draw.line((ncx, ncy, ncx-1.5*a_size, ncy-b_size/2), sol_color, width=2)
        return img

      if not next_cell.neighbours["N"]:
        draw.line((ncx, ncy, ncx, ncy-b_size), sol_color, width=2)
        return img

      if not next_cell.neighbours["NE"]:
        draw.line((ncx, ncy, ncx+1.5*a_size, ncy-b_size/2), sol_color, width=2)
        return img

      if not next_cell.neighbours["SE"]:
        draw.line((ncx, ncy, ncx+1.5*a_size, ncy+b_size/2), sol_color, width=2)
        return img

      if not next_cell.neighbours["S"]:
        draw.line((ncx, ncy, ncx, ncy-b_size), sol_color, width=2)
        return img

# Helper functions
def get_draw_params(size):
  a_size = size / 2.0
  b_size = size * math.sqrt(3) / 2.0
  width = size * 2
  height = b_size * 2
  return a_size, b_size, width, height

def get_hex_coord(size, params, cell):
  a_size, b_size, width, height = params
  cx = size + 3 * cell.x * a_size
  cy = b_size + cell.y * height
  if cell.x % 2 != 0:
    cy += b_size

  # f/n = far/near
  # n/s/e/w = north/south/east/west
  x_fw = int((cx - size))
  x_nw = int((cx - a_size))
  x_ne = int((cx + a_size))
  x_fe = int((cx + size))

  # m = middle
  y_n = int((cy - b_size))
  y_m = int(cy)
  y_s = int((cy + b_size))

  return cx, cy, x_fw, x_nw, x_ne, x_fe, y_n, y_m, y_s

class HexCell:
  # x, y in offset coordinates
  def __init__(self, x, y):
    self.x = x
    self.y = y

    # Connections to other cells
    self.links = {}
    self.color = (255,255,255)
    self.cell_dist_from_start = 0
    self.path_dist_from_start = 0

    # All neighbours of a hexagon
    self.neighbours = {"N": None, "NE": None, "SE": None, "S": None, "SW": None, "NW": None}

  def link(self, cell):
    if cell not in self.links:
      self.links[cell] = True
      cell.link(self)

  def get_links(self):
    return self.links.keys()
  
  def is_linked(self, cell):
    return cell in self.links.keys()

  def get_neighbours(self):
    return list(filter(None, self.neighbours.values()))

from PIL import Image, ImageDraw
import math
import random
import numpy as np
import colorsys

class HexBoard:
  # initializes a rows x columns rectangular maze
  def init_rectangular(self, rows, columns):
    self.cells = {}
    self.rows = rows
    self.columns = columns
    for i in range(columns):
      for j in range(rows):
        self.cells[i, j] = HexCell(i, j)
    self.configure_cells()
    return

  # intializes a circular maze with radius rings using bfs. 
  def init_circular(self, radius):
    self.cells = {}

    centreX = radius 
    centreY = radius 
    self.rows = 2 * radius + 1
    self.columns = 2 * radius + 1

    frontier = [(centreX, centreY)]
    visited = np.zeros((self.columns, self.rows))
    next_frontier = []

    # In every iteration/radius, create a HexCell for every unvisited neighbours (side) of the frontier (current ring),
    # set them to visited and add them to the next_frontier 
    for r in range(radius): 
      while frontier:
        x,y = frontier.pop()
        for side in ['N','NE','SE','S','NW','SW']:
          side_x, side_y = self.get_side_coord(side, x, y)
          if visited[side_x][side_y] == 0:
            next_frontier.append((side_x, side_y))
            visited[side_x][side_y] = 1
            self.cells[side_x, side_y] = HexCell(side_x, side_y) 
      frontier = next_frontier
      next_frontier = []

    self.configure_cells()
    return

  # set cells to have the appropriate neighbours. For every cell, the adjacent coorindates are computed and if the correpsonding
  # coorindates are found in self.cells, it is added to the cell's neighbour.
  def configure_cells(self):
    for cell_key in self.cells.keys():
      x = cell_key[0]
      y = cell_key[1]

      for side in ['N','NE','SE','S','NW','SW']:
        side_coord = self.get_side_coord(side, x, y)
        if side_coord in self.cells:
          self.cells[x, y].neighbours[side] = self.cells[side_coord]
  
  # traverses the maze via dfs
  def generate_maze(self, start_coord, branch_prob):
    self.start_coord = start_coord
    self.initialize_cell_dist()

    stack = [self.cells[start_coord]]
    end = start_coord
    paths = {start_coord:[start_coord]}

    visited = np.zeros((self.columns, self.rows))
    visited[start_coord[0],start_coord[1]] = 1

    max_dist_edge = 0
    max_dist_cell = 0

    while stack:
      # peak the top of stack
      curr_cell = stack[-1]
      x = curr_cell.x
      y = curr_cell.y

      # retrieve all unexplored neighbours
      neighbours = curr_cell.get_neighbours()
      unvisited_neigh = list(filter(lambda cell: visited[cell.x][cell.y] == 0, neighbours))
      random_neigh = self.choose_neighbour(curr_cell, unvisited_neigh, branch_prob)

      # Explore neighbour specified by choose_neighbour
      if random_neigh:
        neigh_x = random_neigh.x
        neigh_y = random_neigh.y

        # link with the neighbour
        curr_cell.link(random_neigh)
        visited[neigh_x][neigh_y] = 1

        # update distance of neighbour
        random_neigh.path_dist_from_start = curr_cell.path_dist_from_start + 1

        # update the dictionary of all paths to include the new neighbour
        paths[neigh_x,neigh_y] = list(paths[x,y])
        paths[neigh_x,neigh_y].append((neigh_x, neigh_y))

        neigh_path_length = random_neigh.path_dist_from_start

        # update the maximum path length to an edge
        if neigh_path_length > max_dist_edge and self.is_edge(neigh_x, neigh_y):
          end_coord = (neigh_x, neigh_y)
          max_dist_edge = neigh_path_length

        # update the maximum path length to an cell
        if neigh_path_length > max_dist_cell:
          max_dist_cell = neigh_path_length

        # Add the neighbour to top of stack
        stack.append(random_neigh)
      else:
        # Backtrack when there are no unvisited neighbours
        stack.pop()

    # store the solution
    self.end_coord = end_coord
    self.solution = paths[end_coord]

    # store the longest path in the maze to generate the color spectrum later
    self.longest_path_dist = max_dist_cell
    
    # set the color of start and end cells
    self.cells[start_coord].color = (255,0,0)
    self.cells[end_coord].color = (0,255,0)
    
    return

  # Colors the board based on distance from start. The algorithm explores bfs from start, giving each cell a color depending on the mode.
  # 1. If mode == "cell", distance is based on (manhattan) distance (considering cell.cell_dist_from_start)
  # 2. If mode == "path", distance is based on path (considering cell.path_dist_from_start)
  def color_board(self, start, mode):
    assert mode == "cell" or mode == "path"

    start_x = self.cells[start].x
    start_y = self.cells[start].y
    frontier = [(start_x, start_y)]
    visited = np.zeros((self.columns, self.rows))
    visited[start_x][start_y] = 1

    if mode == "cell":
      color_spectrum = spectrum(self.longest_cell_dist + 1)
    else:
      color_spectrum = spectrum(self.longest_path_dist + 1)

    while True:
      if frontier == []:
        return

      x,y = frontier.pop()
      curr_cell = self.cells[x,y]

      # assign color to curr_cell depending on mode
      if mode == "cell":
        distance = curr_cell.cell_dist_from_start
      else:
        distance = curr_cell.path_dist_from_start

      curr_cell.color = color_spectrum[distance]

      for side in ['N','NE','SE','S','NW','SW']:
        side_x, side_y = self.get_side_coord(side, x, y)
        
        if self.in_bounds(side_x, side_y):
          side_cell = self.cells[side_x, side_y]

          # visit a neighbouring cell if it's 1) not visited and 2) it's not linked to curr_cell or mode is "cell" (i.e. walls are not considered)
          if not visited[side_x][side_y] and (curr_cell.is_linked(side_cell) or mode == "cell"):
            frontier.append((side_x, side_y))
            visited[side_x][side_y] = 1


  # Helper functions

  # returns the coorindates of the cells in adjecent neighbours
  def get_side_coord(self, side, x, y):

    # coorindates of neighbours differ depending on x coord, since the rows go in a zig-zag pattern:
    # when x is odd, the adjacent cells are on the south diagonal.
    # when x is even, the adjacent cells are on the north diagonal.
    if x % 2 == 0:
      north_diagonal = y-1
      south_diagonal = y
    else:
      north_diagonal = y
      south_diagonal = y+1   

    if side == 'N':
      return x, y-1
    if side == 'NE':
      return x+1, north_diagonal
    if side == 'SE':
      return x+1, south_diagonal
    if side == 'S':
      return x, y+1
    if side == 'NW':
      return x-1, north_diagonal
    if side == 'SW':
      return x-1, south_diagonal

  # check if cell coorindates exists in cells
  def in_bounds(self, x, y):
    return (x,y) in self.cells

  # check if cell is an edge
  def is_edge(self, x, y):
    neighbours = self.cells[x,y].get_neighbours()
    return len(neighbours) < 6

  # finds the distance in hex cells (manhattan distance) between all cell and start and stores the value in cell.cell_dist_from_start.
  # The algorithm expands via bfs from start one layer at the time, exploring all cells in one layer (frontier) before moving on to the next layer (next_frontier)
  def initialize_cell_dist(self):
    start_x = self.start_coord[0]
    start_y = self.start_coord[1]
    frontier = [(start_x, start_y)]
    next_frontier = []
    distance = 0
    visited = np.zeros((self.columns, self.rows))
    visited[start_x][start_y] = 1

    while True: 
      while frontier:
        x,y = frontier.pop()
        
        curr_cell = self.cells[x,y]
        curr_cell.cell_dist_from_start = distance

        for side in ['N','NE','SE','S','NW','SW']:
          side_x, side_y = self.get_side_coord(side, x, y)
          
          if self.in_bounds(side_x, side_y) and not visited[side_x][side_y]:
            next_frontier.append((side_x, side_y))
            visited[side_x][side_y] = 1

      if next_frontier == []:
        self.longest_cell_dist = distance 
        return

      frontier = next_frontier
      next_frontier = []
      distance += 1
    return

  # chooses neighbour of a cell based on the branching factor. 
  def choose_neighbour(self, curr_cell, unvisited_neigh, branch_prob):
    neigh_same_dist = list(filter(lambda cell: cell.cell_dist_from_start == curr_cell.cell_dist_from_start, unvisited_neigh))
    neigh_diff_dist = list(filter(lambda cell: cell.cell_dist_from_start != curr_cell.cell_dist_from_start, unvisited_neigh))
    if neigh_same_dist == [] and neigh_diff_dist == []:
      return None
    elif neigh_same_dist == []:
      return random.choice(neigh_diff_dist)
    elif neigh_diff_dist == []:
      return random.choice(neigh_same_dist)
    else:
      choice = np.random.choice(["branch", "stay"], 1, p=[branch_prob, 1-branch_prob])
      if choice == "branch":
        return random.choice(neigh_diff_dist)
      else:
        return random.choice(neigh_same_dist)