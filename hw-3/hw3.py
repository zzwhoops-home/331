import sys
from helpers import Node
import math
import random

# get command line args
args = sys.argv
data = args[1]

examples = []
attributes = []
unique_attrib_vals = {}
ex_count = {}
total_count = 0

POS_EX = "A"
NEG_EX = "B"

def read_file(filename: str):
    """Helper function to read in file and load attributes

    Args:
        filename (str): Path to file
    """
    global examples
    global total_count
    global attributes

    with open(filename, "r") as f:
        lines = f.readlines()

        # for each example, format as {classification: [attributes]}
        for line in lines:
            line_list = line.strip().split(" ")
            attribs = line_list[:-1]
            result = line_list[-1]

            examples.append({
                result: attribs
            })

            # count up classifications
            if (result not in ex_count):
                ex_count[result] = 1
            else:
                ex_count[result] += 1

        # get total count
        total_count = sum([i for i in ex_count.values()])

        # attributes can be numbered from 0 to # attributes - 1
        attribute_count = len(list(examples[0].values())[0])
        attributes = [i for i in range(attribute_count)]

def build_dt(exs, attribs, parent_exs = None):
    """Builds a decision tree from a list of examples, attributes, and parent examples

    Args:
        exs (_type_): _description_
        attribs (_type_): _description_
        parent_exs (_type_): _description_

    Returns:
        _type_: _description_
    """
    res = check_classification(exs)
    
    if (len(exs) == 0):
        print("a")
        return majority(parent_exs)
    elif (res):
        print("b")
        return res
    elif (len(attribs) == 0):
        print("c")
        return majority(exs)
    else:
        # find attribute of max importance
        A = max_importance(attribs, examples)
        
        # create tree node
        tree = Node(attribute=A, examples=exs, children=[])

        # get unique values of A
        values = unique_attrib_vals[A]

        # iterate through values, recursively build subtrees
        for v in values:
            split_exs = [ex for ex in exs if list(ex.values())[0][A] == v]
            split_attributes = attributes[:].remove(A)
            subtree = build_dt(exs=split_exs, attribs=split_attributes, parent_exs=examples)
            # print([list(ex.values())[0][A] for ex in split_exs])

        return tree


def max_importance(attribs, exs):
    max_attrib = None
    max_attrib_importance = float("-inf")
    
    for attrib in attribs:
        val = importance(attrib, exs)
        if (val > max_attrib_importance):
            max_attrib_importance = val
            max_attrib = attrib
    
    return max_attrib

def importance(a, exs):
    pos, neg = importance_counter(exs)
    # find subsets
    subsets = {}

    # count current set pos/neg examples
    for ex in exs:
        # split apart into subsets
        attribute = list(ex.values())[0][a]
        if (attribute not in subsets):
            subsets[attribute] = [ex]
        else:
            subsets[attribute].append(ex)

    # get entropy to subtract from
    importance_entropy = entropy(pos, neg)

    remainder_entropy = 0
    # count positive/negative in subsets to find remainder
    for values in subsets.values():
        pos_k, neg_k = importance_counter(values)
        remainder_entropy += remainder(pk=pos_k, nk=neg_k, p=pos, n=neg)

    gain = importance_entropy - remainder_entropy
    return gain

def importance_counter(exs):
    pos = 0
    neg = 0

    for ex in exs:
        classification = list(ex.keys())[0]
        if (classification == POS_EX):
            pos += 1
        elif (classification == NEG_EX):
            neg += 1
        else:
            print("Make sure you change the pos/neg examples!!")
    
    # returns (pos, neg) tuple for access
    return (pos, neg)

def check_classification(exs: list):
    """This function checks if every example in a list is the same classification

    Args:
        exs (list): The list of examples to check

    Returns:
        str: the classification if every example is the same classification
        None: one or more classifications differ
    """
    check = list(exs[0].keys())[0]

    for ex in exs:
        if (list(ex.keys())[0] != check):
            return None
        
    return check

def majority(exs: list):
    """This function takes in a list of examples and returns
    the most common output value from a set of examples,
    breaking ties randomly.

    Args:
        exs (list): A list of examples to check majority

    Returns:
        type of elements in exs: The output value in the examples provided which appears the most 
    """
    # count total of each item
    count = {}
    for ex in exs:
        classification = list(ex.keys())[0]
        if (classification not in count):
            count[classification] = 1
        else:
            count[classification] += 1

    # keep track of majority count and classification 
    majority_count = 0
    majority_classes = []
    for key, value in count.items():
        # if the count is greater or equal, replace
        if (value >= majority_count):
            majority_count = value
            majority_classes.append(key)

    choice = random.choice(majority_classes)
    return choice

def remainder(pk: int, nk: int, p: int, n: int):
    """Calculates Remainder(A)
    Importance(A) = Entropy(p / p + n) - Remainder(A)

    Args:
        pk (int): The number of positive / "Case A" examples in the current subset caused by division by A
        nk (int): The number of negative / "Case B" examples in the current subset caused by division by A
        p (int): Total positive / "Case A" examples which attribute A considers
        n (int): Total negative / "Case B" examples which attribute A considers

    Returns:
        float: the expected entropy after asking about attribute A
    """
    subset_total = pk + nk
    attrib_total = p + n

    # (pk + nk) / (p + n)
    left = subset_total / attrib_total
    
    # B(pk / (pk + nk))
    right = entropy(p=pk, n=nk)

    # remainder(A)
    remainder = left * right
    return remainder

def entropy(p: int, n: int):
    """Helper function which calculates entropy of a Boolean rv
    which is true with probability p / p + n
    p = positive examples
    n = negative examples

    Args:
        p (int): # of positive examples, or "case A" examples
        n (int): # of negative examples, or "case B" examples
    """
    total = p + n
    ratio = p / total # r = p / (p + n)
    # 0 ratio or 1 ratio = complete certainty = 0 entropy
    if (ratio == 0 or ratio == 1):
        return 0

    # r * log_2(r)
    left = ratio * math.log2(ratio)

    # (1 - r) * log_2(1 - r)
    right = (1 - ratio) * math.log2(1 - ratio)

    # -(r * log_2(r) + (1 - r) * log_2(1 - r))
    result = -(left + right)
    return result

def get_unique_attrib_vals(exs: list):
    """Gets a list of unique attribute values for each attribute
    based on the examples provided

    Args:
        exs (list): The examples to go through
    """
    for attrib in attributes:
        values = set([list(ex.values())[0][attrib] for ex in exs])
        unique_attrib_vals[attrib] = values

if __name__ == "__main__":
    # read input file and extract attributes / outputs
    read_file(filename="data.dat")

    # get unique values for each attribute (should be just T / F)
    get_unique_attrib_vals(exs=examples)

    print(build_dt(exs=examples, attribs=attributes))
