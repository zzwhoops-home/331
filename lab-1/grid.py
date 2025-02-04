class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        visited = False
        cost = float('inf')
        neighbors = []