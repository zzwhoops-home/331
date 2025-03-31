import sys
from helpers import Node
import math
import random

# get command line args
args = sys.argv
data = args[1]

examples = []
ex_count = {}
total_count = 0

with open("data.dat", "r") as f:
    lines = f.readlines()

    for line in lines:
        line_list = line.strip().split(" ")
        attribs = line_list[:-1]
        result = line_list[-1]

        examples.append({
            result: attribs
        })

        if (result not in ex_count):
            ex_count[result] = 1
        else:
            ex_count[result] += 1

    total_count = sum([i for i in ex_count.values()])

def build_dt(exs, attribs, parent_exs):
    res = check_classification(exs)
    
    if (len(exs) == 0):
        return majority(parent_exs)
    elif (res):
        return res
    elif (len(attribs) == 0):
        return majority(exs)
    # else:
    #     A = importance(attribs, examples)

def check_classification(exs: list):
    """This function checks if every example in a list is the same classification

    Args:
        exs (list): The list of examples to check

    Returns:
        str: the classification if every example is the same classification
        None: one or more classifications differ
    """
    keys = exs.keys()
    check = keys[0]

    for key in keys:
        if (key != check):
            return None
        
    return check

def majority(exs: list):
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

if __name__ == "__main__":
    print(majority(examples))
    print(ex_count)
