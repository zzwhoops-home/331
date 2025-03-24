import sys

# get command line args
args = sys.argv
data = args[1]

with open("data.dat", "r") as f:
    print(f.readlines())