class Node:
    def __init__(self, attribute, examples: list, children: list, label = None):
        self.attribute = attribute
        self.examples = examples
        self.children = children
        self.label = label
        self.value = None

    def add_child(self, node):
        self.children.append(node)