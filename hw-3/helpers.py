class Node:
    def __init__(self, attribute, children: list):
        self.attribute = attribute
        self.children = children

    def add_child(self, node):
        self.children.append(node)