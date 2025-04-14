import sys
from helpers import Node
import math
import random
import pickle
# from graphviz import Digraph

# FOR DEBUGGING USE:
# train lab-3/train.dat lab-3/features.txt lab-3/models/best.model dt
# train lab-3/train.dat lab-3/features.txt lab-3/models/best.model ada
# predict lab-3/datasets/test_en.txt lab-3/features.txt lab-3/models/best.model
# predict lab-3/datasets/test_nl.txt lab-3/features.txt lab-3/models/best.model
# get command line args
args = sys.argv
run_type = args[1] # either 'train' to train on dt or ada, or 'predict' to predict on examples

# check different params based on type
if (run_type == "train"):
    examples_path = args[2] # path to training set
    features_path = args[3] # path to set of features
    out_path = args[4] # the path the trained model should be output to
    learning_type = args[5] # 'dt' or 'ada'
    arg_6 = None
    if (len(args) == 7):
        arg_6 = int(args[6]) # max depth or # of stumps
elif (run_type == "predict"):
    examples_path = args[2] # path to test set
    features_path = args[3] # path to set of features
    hypo_path = args[4]

# global variables
examples = []
example_weights = None
attributes_names = None
attributes_key = None
unique_attrib_vals = {}
total_count = 0
ex_count = {}
hypotheses = []
hypotheses_weights = []

POS_EX = "en"
NEG_EX = "nl"

def read_features_file():
    """Helper function to read in file and load attributes
    """
    global attributes_names, attributes_key

    # get attributes
    with open(features_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        # attributes can be numbered from 0 to # attributes - 1
        attributes = [i for i in range(len(lines))]

        # add actual attribute names for later reference
        attributes_names = [line.replace("\n", "") for line in lines]

        # create dictionary from two arrays
        attributes_key = dict(zip(attributes_names, attributes))

def read_train_examples_file():
    """Helper function to read in file and load examples
    """
    global examples, total_count, attributes_names

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

def read_test_examples_file(type, dt=None, hypotheses=None, hypotheses_weights=None):
    """Helper function to read in file, load test examples, and print predictions for normal decision tree
    """
    with open(examples_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        if (type == "dt"):
            nl = 0
            en = 0
            for line in lines:
                classification = process_and_classify(dt, line)
                print(classification)
                if (classification == "nl"):
                    nl += 1
                elif (classification == "en"):
                    en += 1

            # print(f"\nEN: {en}, NL: {nl}")
        elif (type == "ada"):
            nl = 0
            en = 0
            for line in lines:
                classification = process_and_classify_ada(hypotheses, hypotheses_weights, line)
                print(classification)
                if (classification == "nl"):
                    nl += 1
                elif (classification == "en"):
                    en += 1

            # print(f"\nEN: {en}, NL: {nl} ada")

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

# def visualize_dt(node, graph=None, parent_name=None, edge_label=None):
#     if graph is None:
#         graph = Digraph(format='png')
#         graph.attr(size='96')

#     node_name = str(id(node))

#     if (node.attribute is not None):
#         label = f"{node.attribute}: {len(node.examples)}"
#     else:
#         # count # of each class for label
#         classes = {}
#         for ex in node.examples:
#             check = list(ex.keys())[0]
#             if (check not in classes):
#                 classes[check] = 1
#             else:
#                 classes[check] += 1

#         classes_str = "("
#         for key, value in classes.items():
#             classes_str += f"{key}: {value}, "
#         classes_str += f"#k: {len(node.examples)})"
#         label = f"Leaf: {node.label} {classes_str}"

#     graph.node(name=node_name, label=label)

#     if (parent_name):
#         graph.edge(tail_name=parent_name, head_name=node_name, label=edge_label)

#     if (node.children):
#         for child in node.children:
#             visualize_dt(node=child, graph=graph, parent_name=node_name, edge_label=str(child.value))

#     return graph

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

    for i in range(len(exs)):
        classification = list(exs[i].keys())[0]
        if (classification == POS_EX):
            pos += example_weights[i]
        elif (classification == NEG_EX):
            neg += example_weights[i]
        else:
            print(f"Make sure you change the pos/neg examples for training on differently-labeled items! Current: pos: {POS_EX}, neg: {NEG_EX}")
    
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
    global example_weights

    # count total of each item
    count = {}
    for i in range(len(exs)):
        # get classification
        classification = list(exs[i].keys())[0]

        # add example weight
        if (classification not in count):
            count[classification] = example_weights[i]
        else:
            count[classification] += example_weights[i]

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

def process_and_classify(node: Node, example: str):
    """Processes data and calls recursive function to classify the set of data

    Args:
        node (Node): a Node in the decision tree
        example (str): the example string to classify 
    """
    # iterate through features, get True or False classification
    attribs = []
    for feature in attributes_names:
        if (feature in example):
            attribs.append(True)
        else:
            attribs.append(False)

    # call recursive classify function and return result
    return classify(node, attribs)

def process_and_classify_ada(hypotheses: list[Node], hypotheses_weights: list[float], example: str):
    votes = dict()

    # get all classifications
    for k in range(len(hypotheses)):
        classification = process_and_classify(hypotheses[k], example)

        # add weighted vote to votes
        if (classification not in votes):
            votes[classification] = hypotheses_weights[k]
        else:
            votes[classification] += hypotheses_weights[k]

    # get highest weighted vote sum
    majority_vote = float("-inf")
    majority_class = None
    for key, value in votes.items():
        if (value > majority_vote):
            majority_class = key
            majority_vote = value

    return majority_class

def classify(node: Node, attribs: list[bool]):
    """Does the actual classification steps recursively
    Goes through decision tree until it reaches a leaf node

    Args:
        node (Node): a Node in the decision tree
        attribs (list[bool]): a list of true/false values corresponding with whether or not features were present in a given string
    """
    # base case: return leaf node classification
    if (node.label is not None):
        return node.label
    
    # get the attribute of the node and find its index
    node_attrib_index = attributes_key[node.attribute]
    # get True or False in the parameter list of attribute values
    attrib_val = attribs[node_attrib_index]
    
    # find the child node
    for child in node.children:
        if (child.value == attrib_val):
            return classify(child, attribs)

    # fallback, throw an error
    raise Exception("Warning: could not classify example!")

def ada(exs, stumps=50, ensemble_depth=1):
    global example_weights, hypotheses, hypotheses_weights

    # smallest possible # to prevent division-by-zero
    epsilon = sys.float_info.epsilon
    # track classification
    classification = None

    for k in range(stumps):
        # build decision tree with given depth
        hypotheses.append(None)
        hypotheses_weights.append(None)
        hypotheses[k] = build_dt(exs=exs, attribs=attributes_names, max_depth=ensemble_depth)
        # initial error is 0
        error = 0

        # compute total error for hypotheses[k]
        for j in range(len(exs)):
            # if the hypothesis predicts wrongly, add to error
            ex_answer = list(exs[j].keys())[0]
            ex_vals = list(exs[j].values())[0]

            classification = classify(hypotheses[k], ex_vals)
            # we skip "process" and classify because our train set has already been processed
            if (classification != ex_answer):
                error += example_weights[j]
            
        # break from loop if error > 1/2 (error too high for hypothesis)
        if (error > 1 / 2):
            hypotheses[k] = None
            break
        # error is min(err, 1 - epsilon)
        error = min(error, 1 - epsilon)

        # give more weight for examples h[k] got wrong
        for j in range(len(exs)):
            ex_answer = list(exs[j].keys())[0]
            ex_vals = list(exs[j].values())[0]

            classification = classify(hypotheses[k], ex_vals)
            if (classification == ex_answer):
                # w[j] = w[j] * (error / (1 - error))
                example_weights[j] = example_weights[j] * (error / (1 - error))
        
        # normalize weights to sum to 1
        normalize_weights()

        # give more weight to accurate h[k]: hypothesis_weights[k] = (1/2) * log((1 - error) / error)
        hypotheses_weights[k] = (1 / 2) * math.log((1 - error) / error)

    hypotheses = [h for h in hypotheses if h is not None]
    hypotheses_weights = [h_wt for h_wt in hypotheses_weights if h_wt is not None]

def normalize_weights():
    """Normalizes the weights (global vars) of the examples when AdaBoosting
    """
    global example_weights
    total = sum(example_weights)

    new_weights = [wt / total for wt in example_weights]
    example_weights = new_weights

if __name__ == "__main__":
    # read in attributes from features file
    read_features_file()

    # if we are training, run training model
    if (run_type == "train"):
        # read input file and extract attributes / outputs
        read_train_examples_file()

        # get unique values for each attribute (should be just POS and NEG example defined at the beginning of the file)
        get_unique_attrib_vals(exs=examples)

        # initialize all weights to 1 / total examples (will remain this value if normal dt, otherwise they will be updated with adaboost)
        if (example_weights == None):
            example_weights = [1 / total_count for i in range(total_count)]
        
        if (learning_type == "dt"):
            MAX_DEPTH = arg_6 if arg_6 else 6 # get user max depth, otherwise depth 6 
            dt = build_dt(exs=examples, attribs=attributes_names, max_depth=MAX_DEPTH)
        if (learning_type == "ada"):
            ADA_TREES = arg_6 if arg_6 else 50 # get user # stumps, otherwise 50 stumps
            
            ada(exs=examples, stumps=ADA_TREES)
        # dt_graph = visualize_dt(dt)
        # dt_graph.render(f'{MAX_DEPTH + 1}-layer Decision Tree', view=False)

        # serialize for later use
        to_save = None

        if (learning_type == "dt"):
            to_save = {
                "type": "dt",
                "dt": dt
            }
        elif (learning_type == "ada"):
            to_save = {
                "type": "ada",
                "hypotheses": hypotheses,
                "hypotheses_weights": hypotheses_weights
            }

        with open(out_path, "wb") as f:
            pickle.dump(to_save, f)
    elif (run_type == "predict"):
        # load serialized model
        with open(hypo_path, "rb") as f:
            data = pickle.load(f)
            dt_type = data["type"]

        # differentiate by learning type
        if (dt_type == "dt"):
            # get dt node
            dt = data["dt"]

            # print out classifications with normal dt
            read_test_examples_file(type=dt_type, dt=dt)
        elif (dt_type == "ada"):
            # get hypotheses and their weights
            hypotheses = data["hypotheses"]
            hypotheses_weights = data["hypotheses_weights"]

            # print out classifications with adaboosted ensemble model
            read_test_examples_file(type=dt_type, hypotheses=hypotheses, hypotheses_weights=hypotheses_weights)

        # string = "De kat liep rustig door de tuin terwijl de vogels zongen in de hoge bomen."
        # string = "This is a string that I'm using to test this function. Does it work? idk."
        # print(process_and_classify(dt, string))