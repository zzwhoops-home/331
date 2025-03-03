class Predicate:
    def __init__(self, pred_name, sign, const):
        self.pred_name = pred_name
        self.sign = sign
        self.const = const
    
    def __str__(self):
        return self.pred_name