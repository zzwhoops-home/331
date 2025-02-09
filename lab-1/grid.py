class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.visited = False
        self.parent = None
        self.cost = float('inf')
        self.neighbors = []