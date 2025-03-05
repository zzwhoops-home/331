import sys
from helpers import Clause, Predicate, Constant, Variable, Function
import re

# get command line args
args = sys.argv
KB_PATH = args[1]

kb = set()
terms = {
    'vars': set(),
    'consts': set(),
    'funcs': set()
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
            terms['vars'] = set(vars[1].split(" "))

        if (len(consts) > 1):
            terms['consts'] = set(consts[1].split(" "))
            
        if (len(funcs) > 1):
            terms['funcs'] = set(funcs[1].split(" "))

def process_terms(str_terms: list[str]):
    """Processes a list of string terms into their correct forms, either a:
        - constant
        - variable
        - function    

    Args:
        terms (list[str]): a list of string terms

    Returns:
        set[Constant | Variable | Function]: A set of processed terms into objects
    """
    global terms

    processed_terms = set()

    for term in str_terms:
        if (term in terms["consts"]):
            const = Constant(name=term)
            processed_terms.add(const)
        elif (term in terms["vars"]):
            var = Variable(name=term)
            processed_terms.add(var)
        elif (term in terms["funcs"]):
            func = Function(name=term)
            processed_terms.add(func)

    return processed_terms

def process_clause(clause: str):
    """Processes a clause, generating required Clauses, Predicates, and Terms

    Args:
        clause (str): the string clause representation
    
    Returns:
        list[Predicate]: a list of processed predicates
    """
    # predicate array
    predicates = []

    # split multiple clauses into array
    str_preds = clause.split(" ")

    # for each predicate, find constants
    for p in str_preds:
        # get negation
        negated = True if clause[0] == '!' else False

        # get predicate name
        pred = clause[:clause.index("(")]

        # get result between parentheses (terms)
        result = re.search("\((.*)\)", p).group(1)
        str_terms = result.split(",")

        processed_terms = process_terms(str_terms=str_terms)

        pred_obj = Predicate(name=pred, negated=negated, args=processed_terms)
        predicates.append(pred_obj)

    return predicates

if __name__ == "__main__":
    process_file()

    process_clause(clauses[0])

    print(kb)