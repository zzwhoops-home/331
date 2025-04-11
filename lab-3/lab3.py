import sys
from helpers import Node
import math
import random
from graphviz import Digraph
import pickle

# FOR DEBUGGING USE:
# lab-3/train.dat lab-3/features.txt lab-3/models/best.model dt
# get command line args
args = sys.argv
examples_path = args[1] # path to training/test set
features_path = args[2] # path to set of features
out_path = args[3] # the path the trained model should be output to
learning_type = args[4] # 'dt' or 'ada'

examples = []
attributes_names = None
attributes_key = None
unique_attrib_vals = {}
ex_count = {}
total_count = 0

POS_EX = "en"
NEG_EX = "nl"

def read_file():
    """Helper function to read in file and load attributes
    """
    global examples
    global total_count
    global attributes_names
    global attributes_key

    # get attributes
    with open(features_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        # attributes can be numbered from 0 to # attributes - 1
        attributes = [i for i in range(len(lines))]

        # add actual attribute names for later reference
        attributes_names = [line.replace("\n", "") for line in lines]

        # create dictionary from two arrays
        attributes_key = dict(zip(attributes_names, attributes))

    with open(examples_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        # for each example, format as {classification: [attributes]}
        for line in lines:
            line_list = line.strip().split("|")
            result = line_list[0]
            words = line_list[1]

            attribs = []
            # append to attributes based on true or false (detection of substring)
            for name in attributes_names:
                if name in words:
                    attribs.append(True)
                else:
                    attribs.append(False)

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


def build_dt(exs, attribs, parent_exs=None, depth=0, max_depth=None):
    """Builds a decision tree from a list of examples, attributes, and parent examples

    Args:
        exs (_type_): _description_
        attribs (_type_): _description_
        parent_exs (_type_): _description_

    Returns:
        _type_: _description_
    """
    res = check_classification(exs)
    
    # base case: if no examples left, return majority value of parent examples
    if (len(exs) == 0):
        maj = majority(parent_exs)
        return Node(attribute=None, examples=[], children=[], label=maj)
    
    # base case: if all examples of the same classification, return the classification
    elif (res):
        return Node(attribute=None, examples=exs, children=[], label=res)
    
    # base case: if there are no more attributes to split on, return majority value of examples
    elif (len(attribs) == 0):
        maj = majority(exs)
        return Node(attribute=None, examples=exs, children=[], label=maj)
    
    # base case: max depth reached
    if (max_depth is not None and depth >= max_depth):
        maj = majority(exs)
        return Node(attribute=None, examples=exs, children=[], label=maj)

    # otherwise, find best attribute to split on
    # find attribute of max importance
    A = max_importance(attribs, exs=exs)
    
    # create tree node
    tree = Node(attribute=A, examples=exs, children=[])

    # get unique values of A
    values = unique_attrib_vals[A]

    # next tree should not consider attribute A
    split_attributes = attribs[:]
    split_attributes.remove(A)

    # iterate through values, recursively build subtrees
    for v in values:
        split_exs = [ex for ex in exs if list(ex.values())[0][attributes_key[A]] == v]
        subtree = build_dt(exs=split_exs, attribs=split_attributes, parent_exs=examples, depth=depth + 1, max_depth=max_depth)
        if (subtree.value is None):
            subtree.value = v
        tree.add_child(subtree)

    return tree

def visualize_dt(node, graph=None, parent_name=None, edge_label=None):
    if graph is None:
        graph = Digraph(format='png')
        graph.attr(size='96')

    node_name = str(id(node))

    if (node.attribute is not None):
        label = f"{node.attribute}: {len(node.examples)}"
    else:
        # count # of each class for label
        classes = {}
        for ex in node.examples:
            check = list(ex.keys())[0]
            if (check not in classes):
                classes[check] = 1
            else:
                classes[check] += 1

        classes_str = "("
        for key, value in classes.items():
            classes_str += f"{key}: {value}, "
        classes_str += f"#k: {len(node.examples)})"
        label = f"Leaf: {node.label} {classes_str}"

    graph.node(name=node_name, label=label)

    if (parent_name):
        graph.edge(tail_name=parent_name, head_name=node_name, label=edge_label)

    if (node.children):
        for child in node.children:
            visualize_dt(node=child, graph=graph, parent_name=node_name, edge_label=str(child.value))

    return graph

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
        attribute = list(ex.values())[0][attributes_key[a]]
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
    if (not exs):
        return None
    
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
        if (value > majority_count):
            majority_count = value
            majority_classes = [key]
        elif (value == majority_count):
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

    Probably unnecessary, since we are working always with True or False

    Args:
        exs (list): The examples to go through
    """
    for attrib in attributes_names:
        values = set([list(ex.values())[0][attributes_key[attrib]] for ex in exs])
        unique_attrib_vals[attrib] = values
    
if __name__ == "__main__":
    # read input file and extract attributes / outputs
    read_file()

    # print(majority(exs=examples))
    # get unique values for each attribute (should be just T / F)
    get_unique_attrib_vals(exs=examples)

    max_depth = 6
    dt = build_dt(exs=examples, attribs=attributes_names, max_depth=max_depth)

    dt_graph = visualize_dt(dt)
    dt_graph.render(f'{max_depth + 1}-layer Decision Tree', view=True)