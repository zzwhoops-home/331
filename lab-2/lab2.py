import sys

# get command line args
args = sys.argv
KB_PATH = args[1]

def process_file():
    with open(KB_PATH, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        print(lines)

if __name__ == "__main__":
    process_file()