import sys
from PIL import Image
from grid import Tile
import math
from queue import PriorityQueue 

# DISTANCE CONSTANTS (in meters)
PX_WIDTH = 10.29
PX_HEIGHT = 7.55

# TERRAIN SPEEDS
SPEEDS = {
    "OPEN": 5,
    "MEADOW": 0.5,
    "EASY_FOREST": 4,
    "JOG_FOREST": 3,
    "WALK_FOREST": 2,
    "IMPASSIBLE": 0.01,
    "SWAMP": 0.25,
    "PAVED_ROAD": 6,
    "FOOTPATH": 6,
    "OUT_OF_BOUNDS": 0
}
# COLOR CONSTANTS
COLORS = {
    "OPEN": (248, 148, 18),
    "MEADOW": (255, 192, 0),
    "EASY_FOREST": (255, 255, 255),
    "JOG_FOREST": (2, 208, 60),
    "WALK_FOREST": (2, 136, 40),
    "IMPASSIBLE": (5, 73, 24),
    "SWAMP": (0, 0, 255),
    "PAVED_ROAD": (71, 51, 3),
    "FOOTPATH": (0, 0, 0),
    "OUT_OF_BOUNDS": (205, 0, 101),
    "OPTIMAL_PATH": (161, 70, 221)
}

# REFERENCE FOR O(1) SEARCH
COLOR_REF = {
    (248, 148, 18): "OPEN",
    (255, 192, 0): "MEADOW",
    (255, 255, 255): "EASY_FOREST",
    (2, 208, 60): "JOG_FOREST",
    (2, 136, 40): "WALK_FOREST",
    (5, 73, 24): "IMPASSIBLE",
    (0, 0, 255): "SWAMP",
    (71, 51, 3): "PAVED_ROAD",
    (0, 0, 0): "FOOTPATH",
    (205, 0, 101): "OUT_OF_BOUNDS"
}

# get command line args
args = sys.argv
img_path = args[1]
elev_path = args[2]
path_path = args[3]
output_path = args[4]

def process_elev():
    with open(elev_path, "r") as f:
        arr = f.readlines()
        result = [line.split()[:-5] for line in arr]
        return result

def process_path():
    with open(path_path, "r") as f:
        arr = f.readlines()
        result = [[int(num) for num in line.split()] for line in arr]
        return result

def process_img():
    img = Image.open(img_path, "r")
    pixels = img.load()
    width, height = img.size
    
    map = [[None for i in range(width)] for i in range(height)]

    for x in range(width):
        for y in range(height):
            pixel = pixels[x, y]
            colors = (pixel[0], pixel[1], pixel[2])
            if (colors in COLOR_REF):
                # get type value
                type = COLOR_REF[colors]

                # create tile object
                tile = Tile(x, y, type)

                # assign to array
                map[y][x] = tile

    return map

def build_from(map):
    width = len(map[0])
    height = len(map)
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for x in range(width):
        for y in range(height):
            color = COLORS[map[y][x]]
            pixels[x, y] = color

    img.save(output_path)

def get_neighbors(map, point):
    x, y = point
    width = len(map[0])
    height = len(map)

    tile = map[y][x]

    # Get N neighbor
    if (y - 1 >= 0):
        neighbor = map[y - 1][x]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get S neighbor
    if (y + 1 < height):
        neighbor = map[y + 1][x]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get W neighbor
    if (x - 1 >= 0):
        neighbor = map[y][x - 1]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get E neighbor
    if (x + 1 < width):
        neighbor = map[y][x + 1]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get NW neighbor
    if (y - 1 >= 0 and x - 1 >= 0):
        neighbor = map[y - 1][x - 1]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get NE neighbor
    if (y - 1 >= 0 and x + 1 < width):
        neighbor = map[y - 1][x + 1]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get SW neighbor
    if (y + 1 < height and x - 1 >= 0):
        neighbor = map[y + 1][x - 1]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

    # Get SE neighbor
    if (y + 1 < height and x + 1 < width):
        neighbor = map[y + 1][x + 1]
        if (neighbor.type != "OUT_OF_BOUNDS" and not neighbor.visited):
            tile.neighbors.append(neighbor)

# we pretend that the coordinate 0 meters, 0 meters at (0, 0)
# is located in the center of the 0, 0 pixel, not the top-left
def get_coords(self):
    real_x = PX_WIDTH * self.x
    real_y = PX_HEIGHT * self.y
    return [real_x, real_y]

def get_distance(map, elev, pt_a, pt_b):
    pt_a_x = pt_a[0]
    pt_a_y = pt_a[1]

    pt_b_x = pt_b[0]
    pt_b_y = pt_b[1]

    elev_a = float(elev[pt_a_y][pt_a_x])
    elev_b = float(elev[pt_b_y][pt_b_x])

    x_a = pt_a_x * PX_WIDTH
    y_a = pt_a_y * PX_HEIGHT
    x_b = pt_b_x * PX_WIDTH
    y_b = pt_b_y * PX_HEIGHT

    vec_a = [x_a, y_a, elev_a]
    vec_b = [x_b, y_b, elev_b]

    distance = math.dist(vec_a, vec_b)
    return distance

def get_cost(map, point_to_travel, dist_f, dist_g):
    x = point_to_travel[0]
    y = point_to_travel[1]
    
    multiplier = SPEEDS[map[y][x].type]
    print(map[y][x].type)

    return (dist_f + dist_g) * multiplier


# perform A* search
def search(map, point, next_point):
    x = point[0]
    y = point[1]

    # get start Tile
    start_tile = map[y][x]

    # populate Tile neighbors
    get_neighbors(map, point)
    adjacent = start_tile.neighbors

    
    pass

def compare():
    source = Image.open(img_path)
    generated = Image.open(output_path)

    source_px = source.load()
    gen_px = generated.load()

    width, height = source.size
    for x in range(width):
        for y in range(height):
            s = source_px[x, y]
            s = (s[0], s[1], s[2])
            g = gen_px[x, y]
            g = (g[0], g[1], g[2])

            if (s != g):
                print(f"{x} {y} {s} {g}")
                return False
            
    return True

if __name__ == "__main__":
    # process elevation file
    elev_map = process_elev()
    path_points = process_path()
    # print(path_points)
    map = process_img()
    # print(map)
    # build = build_from(map)

    start_pt = path_points[0]
    for path_pt in path_points:
        # search(map, path_pt)
        get_neighbors(map, path_pt)
        break
    
    tiles = map[start_pt[1]][start_pt[0]].neighbors
    for tile in tiles:
        next_pt = [tile.x, tile.y]
        g_dist = get_distance(map, elev_map, start_pt, next_pt)
        h_dist = get_distance(map, elev_map, next_pt, path_points[1])
        cost = get_cost(map, next_pt, g_dist, h_dist)
        print(f"{tile.x} {tile.y}: g dist: {g_dist}, h dist = {h_dist}, f(x) (cost) = {cost}")
        print()