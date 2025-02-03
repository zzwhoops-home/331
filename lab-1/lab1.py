import matplotlib
import numpy
import sys
from PIL import Image

# DISTANCE CONSTANTS (in meters)
PX_WIDTH = 10.29
PX_HEIGHT = 7.55

# TERRAIN SPEEDS
class Terrain:
    OPEN = 5
    MEADOW = 0.5
    EASY_FOREST = 4
    JOG_FOREST = 3
    WALK_FOREST = 2
    IMPASSIBLE = 0.01
    SWAMP = 0.25
    PAVED_ROAD = 6
    FOOTPATH = 5

# COLOR CONSTANTS
class Color:
    OPEN_LAND = "#F89412"
    ROUGH_MEADOW = "#FFC000"
    EASY_MOVEMENT_FOREST = "#FFFFFF"
    SLOW_RUN_FOREST = "#02D03C"
    WALK_FOREST = "#028828"
    IMPASSIBLE_VEGETATION = "#054918"
    LAKE_SWAMP_MARSH = "#0000FF"
    PAVED_ROAD = "#473303"
    FOOTPATH = "#000000"
    OUT_OF_BOUNDS = "#CD0065"
    OPTIMAL_PATH = "#A146DD" 

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
        print(result[0], len(result[0]))

if __name__ == "__main__":
    process_elev()