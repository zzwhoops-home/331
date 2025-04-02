class Node:
    def __init__(self, attribute, examples: list, children: list, value = None):
        self.attribute = attribute
        self.value = value
        self.examples = examples
        self.children = children

    def add_child(self, node):
        self.children.append(node)