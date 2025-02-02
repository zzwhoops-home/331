import sys

# get command line args
args = sys.argv
dir = args[1]
start = args[2]
target = args[3]

# get lines
with open(dir, "r") as f:
    lines = [line.rstrip() for line in f]
