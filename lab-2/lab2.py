import sys
from helpers import Predicate

# get command line args
args = sys.argv
KB_PATH = args[1]

def process_file():
    with open(KB_PATH, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        preds = lines[0].split(": ")
        vars = lines[1].split(": ")
        consts = lines[2].split(": ")
        funcs = lines[3].split(": ")
        clauses = lines[5:]

        if (len(preds) > 1):
            preds = preds[1].split(" ")
        else:
            preds = []

        if (len(vars) > 1):
            vars = vars[1].split(" ")
        else:
            vars = []

        if (len(consts) > 1):
            consts = consts[1].split(" ")
        else:
            consts = []
            
        if (len(funcs) > 1):
            funcs = funcs[1].split(" ")
        else:
            funcs = []

        print(preds)
        print(vars)
        print(consts)
        print(funcs)
        print(clauses)

if __name__ == "__main__":
    process_file()

    pred = Predicate("dog", "-", "Kim")
    things = [pred]
    for thing in things:
        print(thing)