import sys
from helpers import Node
import math

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
    # print(examples)'
    gain = 1
    gain -= remainder(0, 2, 6, 6)
    gain -= remainder(4, 0, 6, 6)
    gain -= remainder(2, 4, 6, 6)

    print(gain)
    print(ex_count)
    print(total_count)
