import sys
from helpers import Clause, Predicate, Constant, Variable, Function
import re
import copy

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
        list[Constant | Variable | Function]: A list of processed terms into objects
    """
    global terms

    processed_terms = []

    for term in str_terms:
        # check for function (has parentheses)
        func_check = term.index("(") if '(' in term else None
        if (func_check and term[:func_check] in terms["funcs"]):
            # get result between parentheses, if it exists (terms)
            result = re.search(r"\((.*)\)", term).group(1)
            func_var = Variable(name=result)

            # create function
            func = Function(name=term[:func_check], var=func_var)
            processed_terms.append(func)
        elif (term in terms["consts"]):
            const = Constant(name=term)
            processed_terms.append(const)
        elif (term in terms["vars"]):
            var = Variable(name=term)
            processed_terms.append(var)

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
            # get predicate name
            pred = p[1:] if negated else p

            # create predicate and add the object
            pred_obj = Predicate(name=pred, negated=negated, args=[])
            predicates.append(pred_obj)
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

def resolution(kb):
    length = len(kb)

    # if we're already done
    if (length <= 1):
        return True
    
    # set to keep track of new clauses
    clauses = set(kb)

    while (True):
        new = set()
        
        for clause_i in clauses:
            for clause_j in clauses:
                if (clause_i != clause_j):
                    resolvents, empty = resolve_clauses(clause_i=clause_i, clause_j=clause_j)

                    if (not resolvents and empty):
                        return False
                    elif (resolvents and empty):
                        continue
                    elif (resolvents and not empty):
                        resolved_clause = Clause(resolvents)
                        new.add(resolved_clause)
        
        # if new is a subset of clauses return True
        new_str = set([str(clause) for clause in new])
        clauses_str = set([str(clause) for clause in clauses])
        if (new_str.issubset(clauses_str)):
            return True

        clauses.update(new)

def resolve_clauses(clause_i: Clause, clause_j: Clause):
    """Resolves two clauses and returns the result

    Args:
        clause_i (Clause): Clause i in the pair
        clause_j (Clause): Clause j in the pair

    Returns:
        Clause: the resolved clauses
    """
    resolved_pred = None
    new_predicates_i = copy.deepcopy(clause_i.predicates)
    new_predicates_j = copy.deepcopy(clause_j.predicates)
    
    # keep track of current substitutions
    theta = {}

    for predicate_i in new_predicates_i:
        for predicate_j in new_predicates_j:
            # ensure the two predicates have the same name and are not exactly the same
            if (predicate_i.name == predicate_j.name and str(predicate_i) != str(predicate_j)):
                # check if the two clauses are opposites of each other
                if (predicate_i.negated != predicate_j.negated):
                    # if the arguments match, no unification is needed
                    if (arg_matches(predicate_i.args, predicate_j.args)):
                        # create tuple to remove instances as they have been resolved by unifying
                        resolved_pred = (predicate_i, predicate_j)
                        break
                    # if the two clauses are the same and opposites only, see if they unify
                    else:
                        # new arguments
                        new_args_i = predicate_i.args[:]
                        new_args_j = predicate_j.args[:]

                        uni_res = unify(new_args_i, new_args_j, t=theta)
                        
                        if (uni_res):
                            theta.update(uni_res)

                            # create tuple to remove instances as they have been resolved by unifying
                            resolved_pred = (predicate_i, predicate_j)
                            break
        if (resolved_pred):
            break

    if (not resolved_pred):
        # no resolvents, but not empty
        return ([], False)

    if (theta):
        for pred_i in new_predicates_i:
            args = pred_i.args
            for i in range(len(args)):
                if (args[i] in theta):
                    args[i] = theta[args[i]]

        for pred_j in new_predicates_j:
            args = pred_j.args
            for i in range(len(args)):
                if (args[i] in theta):
                    args[i] = theta[args[i]]

    new_i, new_j = resolved_pred
    new_predicates_i.remove(new_i)
    new_predicates_j.remove(new_j)
    # return the two sets of predicates resolved
    resolvents = new_predicates_i + new_predicates_j

    # check for tautologies, don't return resolvents in that case
    literals = set()
    for pred in resolvents:
        if (f"!{str(pred)}" in literals or str(pred).replace("!", "") in literals):
            return ([], False)
        literals.add(str(pred))

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

def unify(x, y, t={}):
    if (t is None):
        return None
    elif (x == y):
        return t
    elif (type(x) == Variable):
        return unify_var(x, y, t)
    elif (type(y) == Variable):
        return unify_var(y, x, t)
    elif (type(x) == Function and type(y) == Function):
        arg_x = x.var
        arg_y = y.var
        # recursively unify if we have functions
        return unify(arg_x, arg_y, unify(x.name, y.name, t)) # nested
    elif(type(x) == list and type(y) == list):
        # recursively unify if in a list
        return unify(x[1:], y[1:], unify(x[0], y[0], t)) # nested
    else:
        return None

def unify_var(var, x, t):
    """Attempts to unify the variable and given x with the provided substitution set

    Args:
        var (_type_): _description_
        x (_type_): _description_
        t (_type_): _description_

    Returns:
        _type_: _description_
    """
    if (var in t):
        # if the variable is in the substitution set, attempt to unify it with the value
        val = t[var]
        return unify(val, x, t)
    elif (x in t):
        val = t[x]
        return unify(var, val, t)
    else:
        t[var] = x
        return t

if __name__ == "__main__":
    clauses = process_file()

    for clause in clauses:
        preds = process_clause(clause)

        clause_obj = Clause(preds)
        kb.append(clause_obj)

    # resolve KB, if we find empty clause, resolution() returns False
    # and we can return "no", otherwise we say "yes"
    print("yes" if resolution(kb) else "no")