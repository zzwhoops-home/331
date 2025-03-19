import sys
from helpers import Clause, Predicate, Constant, Variable, Function
import re

# get command line args
args = sys.argv
KB_PATH = args[1]

kb = []
terms = {
    'vars': set(),
    'consts': set(),
    'funcs': set()
}


def process_file():
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

        return clauses

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
        negated = True if p[0] == '!' else False

        # get predicate name
        if (negated):
            pred = p[1:p.index("(")]
        else:
            pred = p[:p.index("(")]

        # get result between parentheses (terms)
        result = re.search(r"\((.*)\)", p).group(1)
        str_terms = result.split(",")

        processed_terms = process_terms(str_terms=str_terms)

        pred_obj = Predicate(name=pred, negated=negated, args=processed_terms)
        predicates.append(pred_obj)

    return predicates

def resolution():
    global kb

    length = len(kb)

    # if we're already done
    if (length == 0 or length == 1):
        return
    
    # check all pairs
    for i in range(0, length - 1):
        for j in range(i + 1, length):
            # get current pair c_i and c_j
            clause_i = kb[i]
            clause_j = kb[j]
            resolve_clauses(clause_i, clause_j)

def resolve_clauses(clause_i: Clause, clause_j: Clause):
    """Resolves two clauses and returns the result

    Args:
        clause_i (Clause): Clause i in the pair
        clause_j (Clause): Clause j in the pair

    Returns:
        Clause: the resolved clauses
    """
    for predicate_i in clause_i.predicates:
        if predicate_i in clause_j.predicates:
            args_i = predicate_i.args
            args_j = predicate_i.args
            if (arg_matches(args_i, args_j)):
                print("yes")
            pass

    return False

def arg_matches(args_i, args_j):
    args_i = list(args_i)
    args_j = list(args_j)
    if (len(args_i) != len(args_j)):
        return False
    for i in range(len(args_i)):
        if (args_i[i] != args_j[i]):
            return False
        
    return True

if __name__ == "__main__":
    clauses = process_file()

    for clause in clauses:
        preds = process_clause(clause)

        clause_obj = Clause(preds, clause)
        kb.append(clause_obj)

    # print([str(x) for x in kb])

    # resolve KB
    resolution()

    # print(preds[0])
    # print(next(iter(preds[0].args)))
    # print(preds[1])
    # print(next(iter(preds[1].args)))