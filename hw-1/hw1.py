import sys
from collections import deque

# get command line args
args = sys.argv
dir = args[1]
start = args[2]
target = args[3]

# get length of string
start_len = len(start)

def find_neighbors(word, lines):
    # create result list
    result = []

    # iterate through # of letters
    for i in range(start_len):
        # replace one character at a time
        for l in "abcedfghijklmnopqrstuvwxyz":
            # ensure we are not replacing with the same character
            if (l != word[i]):
                # replace character at index i
                test = word[:i] + l + word[i + 1:]

                # if the word is valid, append word
                if (test in lines):
                    result.append(test)

    return result

def build_parents(lines):
    # create hashmap
    parents = {}
    visited = set([start])

    # get initial neighbors and add to queue
    queue = deque([start])
    while (queue):
        # pop from queue
        cur = queue.popleft()

        # find adjacency list
        adj = find_neighbors(cur, lines)

        # in adjacency list, add to visited and queue if not already visited
        for word in adj:
            if (word not in visited):
                visited.add(word)
                queue.append(word)
                parents[word] = cur

        # if we find the target, return
        if (target in visited):
            return parents

    # otherwise, print no solution
    print("No solution")

def print_path(parents):
    # get current word and also create path list
    cur = target
    path = [cur]

    # while we haven't reached the start, append the path
    while (cur != start):
        cur = parents[cur]
        path.append(cur)

    # print out path backwards
    for i in range(len(path) - 1, -1, -1):
        print(path[i])

if __name__ == "__main__":
    # get lines
    with open(dir, "r") as f:
        # get all lines that are the same # of characters
        lines = set([line.rstrip() for line in f if len(line) - 1 == start_len])

        # build parent matrix with BFS solution
        parents = build_parents(lines)

        # print final path if parents are found
        if (parents):
            print_path(parents)