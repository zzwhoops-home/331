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

    processed_terms = []

    for term in str_terms:
        if (term in terms["consts"]):
            const = Constant(name=term)
            processed_terms.append(const)
        elif (term in terms["vars"]):
            var = Variable(name=term)
            processed_terms.append(var)
        elif (term in terms["funcs"]):
            func = Function(name=term)
            processed_terms.append(func)

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

        # if we are only dealing with prop logic, ignore this step
        pred_ind = p.index("(") if "(" in p else None
        if (not pred_ind):
            pred = p[1:] if negated else p
        else:
            # get predicate name
            pred = p[1:p.index("(")] if negated else p[:p.index("(")]

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
        return True
    
    new = []

    while (True):
        # get KB string representations for checking set subset
        kb_set = set([str(clause) for clause in kb])

        # check all pairs
        for clause_i in kb:
            for clause_j in kb:
                # get current pair c_i and c_j
                if (clause_i != clause_j):
                    resolved, empty = resolve_clauses(clause_i, clause_j)
                    # check for empty clause. if we find one, then DB is unsatisfiable
                    if (not resolved and empty):
                        return False
                    
                    # otherwise, add to "new" clause
                    new.append(Clause(resolved))
        # if no new clauses to add to KB, the KB is satisfiable
        new_set = set([str(clause) for clause in new])
        # check new_set is a subset of the KB
        if (new_set <= kb_set):
            return True
        
        # otherwise, add any new clauses to the KB
        kb += new

def resolve_clauses(clause_i: Clause, clause_j: Clause):
    """Resolves two clauses and returns the result

    Args:
        clause_i (Clause): Clause i in the pair
        clause_j (Clause): Clause j in the pair

    Returns:
        Clause: the resolved clauses
    """
    resolved_pred = None
    new_predicates_i = clause_i.predicates[:]
    new_predicates_j = clause_j.predicates[:]

    for predicate_i in clause_i.predicates:
        for predicate_j in clause_j.predicates:
            # ensure the two predicates have the same name and are not exactly the same
            if (predicate_i.name == predicate_j.name and predicate_i != predicate_j):
                # check that arguments match and
                # check if the two clauses are opposites of each other
                if (arg_matches(predicate_i.args, predicate_j.args) and predicate_i.negated != predicate_j.negated):
                    # if so, remove the instances
                    resolved_pred = (predicate_i, predicate_j)
                    break
        if (resolved_pred):
            break

    if (not resolved_pred):
        # no resolvents, but not empty
        return ([], False)

    new_i, new_j = resolved_pred
    new_predicates_i.remove(new_i)
    new_predicates_j.remove(new_j)
    # return the two sets of predicates resolved
    resolvents = new_predicates_i + new_predicates_j
    return (resolvents, len(resolvents) == 0)

def arg_matches(args_i, args_j):
    """Takes two sets of arguments (constants, variables, or functions)
    and checks if the arguments match exactly

    Args:
        args_i (_type_): list of arguments for clause i
        args_j (_type_): list of arguments for clause j

    Returns:
        bool: True if the arguments match, False if they do not
    """
    for i in range(len(args_i)):
        if (args_i[i] != args_j[i]):
            return False

    return True

if __name__ == "__main__":
    clauses = process_file()

    for clause in clauses:
        preds = process_clause(clause)

        clause_obj = Clause(preds)
        kb.append(clause_obj)

    # print([str(x) for x in kb])

    # resolve KB, if we find empty clause, resolution() returns False
    # and we can return "no", otherwise we say "yes"
    print("yes" if resolution() else "no")

    # print(preds[0])
    # print(next(iter(preds[0].args)))
    # print(preds[1])
    # print(next(iter(preds[1].args)))