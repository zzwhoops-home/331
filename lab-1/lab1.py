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
    "OPEN": 1.2,
    "MEADOW": 0.3,
    "EASY_FOREST": 1.1,
    "JOG_FOREST": 0.8,
    "WALK_FOREST": 0.4,
    "IMPASSIBLE": 0.001,
    "SWAMP": 0.1,
    "PAVED_ROAD": 1.3,
    "FOOTPATH": 1.3,
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
            color = COLORS[map[y][x].type]
            pixels[x, y] = color

    img.save(output_path)

def reset(map):
    width = len(map[0])
    height = len(map)

    for x in range(width):
        for y in range(height):
            tile = map[y][x]
            tile.parent = None
            tile.visited = False
            tile.cost = float('inf')
            tile.neighbors = []

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

def get_cost(map, elev, pt_a, pt_b, pt_dest):
    # get individual components
    a_x = pt_a[0]
    a_y = pt_a[1]
    b_x = pt_b[0]
    b_y = pt_b[1]
    dest_x = pt_dest[0]
    dest_y = pt_dest[1]    

    # get elevations
    elev_a = float(elev[a_y][a_x])
    elev_b = float(elev[b_y][b_x])
    elev_dest = float(elev[dest_y][dest_x])

    # get IRL coordinates based on tile-pixel ratios
    world_a_x = a_x * PX_WIDTH
    world_a_y = a_y * PX_HEIGHT
    world_b_x = b_x * PX_WIDTH
    world_b_y = b_y * PX_HEIGHT
    world_dest_x = dest_x * PX_WIDTH 
    world_dest_y = dest_y * PX_HEIGHT

    vec_a = [world_a_x, world_a_y, elev_a]
    vec_b = [world_b_x, world_b_y, elev_b]
    vec_dest = [world_dest_x, world_dest_y, elev_dest]

    # get 3D distance to next tile, then heuristic 3D distance to destination
    next_distance = math.dist(vec_a, vec_b)
    target_distance = math.dist(vec_b, vec_dest)
    travel_speed = SPEEDS[map[dest_y][dest_x].type]

    cost = (next_distance / travel_speed) + target_distance
    # store cost in node
    map[b_y][b_x].cost = cost
    return cost

def get_path(current):
    path = []
    cur = current
    while (cur is not None):
        path.append(cur)
        cur = cur.parent
    return path[::-1]

# perform A* search
def search(map, elev, point, next_point):
    open_pq = PriorityQueue()
    open_set = set()

    start_x = point[0]
    start_y = point[1]
    end_x = next_point[0]
    end_y = next_point[1]

    # get start Tile and cost
    start_tile = map[start_y][start_x]
    get_cost(map, elev, point, point, next_point)
    # add to priority queue and set
    open_pq.put((start_tile.cost, start_tile))
    open_set.add(start_tile)

    # get end tile
    end_tile = map[end_y][end_x]

    while (open_pq.qsize() > 0):
        # get next node with priority queue
        _, current = open_pq.get()

        # add current node to visited set
        current.visited = True

        # check for end condition
        if (current == end_tile):
            return get_path(current)

        # get cur point
        cur_point = [current.x, current.y]

        # populate Tile neighbors
        get_neighbors(map, cur_point)
        adjacent = current.neighbors

        # get costs
        for adj in adjacent:
            # skip over children already visited
            if (adj.visited):
                continue

            # get adj point
            adj_point = [adj.x, adj.y]
            # get cost
            get_cost(map, elev, cur_point, adj_point, next_point)

            if (adj in open_set):
                continue

            open_pq.put((adj.cost, adj))
            open_set.add(adj)

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

    for i in range(len(path_points) - 1):
        search(map, elev_map, path_points[i], path_points[i + 1])
        break
    
    # tiles = map[start_pt[1]][start_pt[0]].neighbors
    # for tile in tiles:
    #     next_pt = [tile.x, tile.y]
    #     # map[tile.y][tile.x].type = "OPTIMAL_PATH"
    #     cost = get_cost(map, elev_map, start_pt, next_pt, path_points[1])
    #     print(f"{tile.x} {tile.y}: f(x) (cost) = {cost}")
    #     print()
    build = build_from(map)