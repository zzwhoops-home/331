class Predicate:
    def __init__(self, name: str, negated: bool, args: list):
        self.name = name
        self.negated = negated
        self.args = args
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, value):
        return self.name == value.name
    
    def matches(self, predicate):
        """Custom function comparing two predicates. Used to check if two predicates match

        Args:
            predicate (Predicate): Predicate to compare to

        Returns:
            bool: True if the two predicates have the same identifier
        """
        return self.name == predicate.name

class Clause:
    def __init__(self, predicates: list[Predicate]):
        self.predicates = predicates

    def __hash__(self):
        return hash(self.str_clause)
    
    def __str__(self):
        return self.str_clause

class Constant:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, value):
        return self.name == value

    def __hash__(self):
        return hash("c" + self.name)
    
class Variable:
    def __init__(self, name: str):
        self.name = name

class Function:
    def __init__(self, name: str):
        # needs to include independent term since funcs depend on vars
        self.name = name