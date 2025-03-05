class Predicate:
    def __init__(self, name: str, negated: bool, args: list[str]):
        self.name = name
        self.negated = negated
        self.args = args
    
    def __str__(self):
        return self.name

class Clause:
    def __init__(self, predicates: list[Predicate], str_clause: str):
        self.predicates = predicates
        self.str_clause = str_clause

    def __hash__(self):
        return self.str_clause

class Constant:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, value):
        return self.name == value