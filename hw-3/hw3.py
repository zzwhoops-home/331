import sys

# get command line args
args = sys.argv
data = args[1]

attributes = {}

with open("data.dat", "r") as f:
    lines = f.readlines()

    for line in lines:
        line_list = line.strip().split(" ")
        attribs = line_list[:-1]
        result = line_list[-1]

        if (result not in attributes):
            attributes[result] = []
        attributes[result].append(attribs)

if __name__ == "__main__":
    print(attributes)
