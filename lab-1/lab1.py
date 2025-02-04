import sys
from PIL import Image

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
    "FOOTPATH": 5,
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
    
    map = [[0 for i in range(width)] for i in range(height)]

    for x in range(width):
        for y in range(height):
            pixel = pixels[x, y]
            colors = (pixel[0], pixel[1], pixel[2])
            if (colors in COLOR_REF):
                map[y][x] = COLOR_REF[colors]

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
    build = build_from(map)