class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.visited = False
        self.parent = None
        self.g = 0
        self.h = float('inf')
        self.neighbors = []

    def cost(self):
        return self.g + self.h

    def __eq__(self, other):
        inst_match = isinstance(other, Tile)
        coord_match = self.x == other.x and self.y == other.y
        return inst_match and coord_match
    
    def __hash__(self):
        return hash(f"{self.x}{self.y}")