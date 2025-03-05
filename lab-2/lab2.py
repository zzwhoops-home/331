import sys
from helpers import Clause, Predicate, Constant
import re

# get command line args
args = sys.argv
KB_PATH = args[1]

kb = set()
terms = {
    'vars': [],
    'consts': [],
    'funcs': []
}

clauses = []

def process_file():
    global clauses
    global terms

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
            terms['vars'] = vars[1].split(" ")
        else:
            terms['vars'] = []

        if (len(consts) > 1):
            terms['consts'] = consts[1].split(" ")
        else:
            terms['consts'] = []
            
        if (len(funcs) > 1):
            terms['funcs'] = funcs[1].split(" ")
        else:
            terms['funcs'] = []

def process_clause(clause: str):
    """Processes a clause, generating required Clauses, Predicates, and Terms

    Args:
        clause (str): the string clause representation
    """
    # predicate array
    predicates = []

    # split multiple clauses into array
    str_preds = clause.split(" ")

    # for each predicate, find constants
    for p in str_preds:
        # get result between parentheses (terms)
        result = re.search("\((.*)\)", p).group(1)
        terms = result.split(",")

        pred_obj = Predicate()
        predicates.append(pred_obj)


if __name__ == "__main__":
    process_file()

    print(kb)

    pred = Predicate("dog", "-", "Kim")
    clause = Clause(clauses[0])
    print(clause.__hash__())
    things = [pred]
    for thing in things:
        print(thing)