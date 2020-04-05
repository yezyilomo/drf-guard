from functools import reduce


class Operator():
    @property
    def should_eval(self):
        return hasattr(self, 'left_operand') and hasattr(self, 'right_operand')


class Or(Operator):
    @property
    def should_eval(self):
        if getattr(self, 'left_operand', False):
            # Shortcircuit
            raise StopIteration(self.left_operand)
        return super().should_eval

    def eval(self):
        return self.left_operand or self.right_operand


class And(Operator):
    @property
    def should_eval(self):
        if not getattr(self, 'left_operand', True):
            # Shortcircuit
            raise StopIteration(self.left_operand)
        return super().should_eval

    def eval(self):
        return self.left_operand and self.right_operand


class Not(Operator):
    @property
    def should_eval(self):
        return hasattr(self, 'right_operand')
        
    def eval(self):
        if hasattr(self, 'left_operand') and isinstance(self.left_operand, Operator):
            # This is the case of left-And-Not-right / left-Or-Not-right
            self.left_operand.right_operand = not self.right_operand
            return self.left_operand.eval()
        return not self.right_operand
    

class Reducer():
    def __call__(self, sequence):
        return self.eval(sequence)

    def reducer(self, left_operand, right_operand):
        if isinstance(left_operand, Operator) and isinstance(right_operand, Operator):
            right_operand.left_operand = left_operand
            return right_operand
            
        if isinstance(left_operand, (list, tuple)):
            left_operand = reduce(self.reducer, left_operand)

        if isinstance(right_operand, (list, tuple)):
            right_operand = reduce(self.reducer, right_operand)
            
        if isinstance(left_operand, Operator):
            left_operand.right_operand = right_operand
            if left_operand.should_eval:
                return left_operand.eval()
            return left_operand
            
        if isinstance(right_operand, Operator):
            right_operand.left_operand = left_operand
            if right_operand.should_eval:
                return right_operand.eval()
            return right_operand
            
        return left_operand and right_operand # Default operator for ',' is `And`
    
    def eval(self, sequence):
        try:
            return reduce(self.reducer, sequence)
        except StopIteration as e:
            # Return value due to shortcircuit
            return e.args[0]

