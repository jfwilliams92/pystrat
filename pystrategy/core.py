import operator
import json

class Evaluation():
    """The simplest logical unit in an evaluation.

    Attributes:
        func_ (function): comparision operator function
        field_ (str): name of field where field_value resides in evaluation payload.
        value_ (str/float): value to compare to field_value
        op_str_ (str): string representation of comparision operator
    """

    def __init__(self, field, value, operator_str):

        operators = {
            "lt": operator.lt,
            "le": operator.le,
            "eq": operator.eq,
            "ne": operator.ne,
            "ge": operator.ge,
            "gt": operator.gt,
            "in": operator.contains
        }

        if operator_str not in operators.keys():
            raise ValueError('Operator must be a valid value.')

        self.func_ = operators[operator_str]
        self.field_ = field
        self.value_ = value
        self.op_str_ = operator_str

    def evaluate(self, payload, level=0, verbose=True):
        """Evaluate a payload against this Evaluation.

        Args:
            payload (dict): dictionary containing the data to evaluate.
            level (int): represents the level of deepness in the evaluation hierarchy
            verbose (bool): whether to print results
        
        Returns:
            result (bool): T/F of evaluation
        """
        # find the value to compare in the payload dict
        field_value_ = payload[self.field_]
        
        if verbose:
            tabs = "\t" * level
            print(tabs + f"Evaluating {field_value_} {self.op_str_} {self.value_}")
        
        # run the comparision operation based on the initialzed operator
        result = self.func_(field_value_, self.value_)
        if verbose: print(tabs + f"Evaluation Result: {result}")
        
        return result

class Composite():
    """A logical composite made of children evaluations joined by logical
    OR or AND (conjunction). Children evaluations can be Composites themselves,
    or Evaluations.

    Attributes:
        conjuction_ (str): Logical AND or OR
        children_ (list): list of logical children
    """

    def __init__(self, children, conjuction='AND'):
        
        if conjuction not in ['AND', 'OR']:
            raise ValueError('Conjuction must be a valid value.')

        if not isinstance(children, list):
            raise ValueError('Children must be a list, empty or otherwise.')
        
        self.conjuction_ = conjuction
        self.children_ = children

    def evaluate(self, payload, level=0, verbose=True):
        """Evaluate a payload against the Composite's logic

        Args:
            payload (dict): dictionary containing the data to evaluate.
            level (int): represents the level of deepness in the evaluation hierarchy
            verbose (bool): whether to print results

        Returns:
            result (bool): T/F of the composite logical evaluation
        """

        # if children are joined by AND, evaluate every child until all children
        # are evaluated or until a False breaks the loop (Need all True for AND)
        if self.conjuction_ == 'AND':
            result = True
            i = 0
            while result and (i < len(self.children_)):
                
                if verbose:
                    tabs = "\t" * level
                    if i > 0: print("\n" + tabs + f"{self.conjuction_} \n")
                    print(tabs + f"Evaluating Composite: {i + 1}, Level: {level + 1}")
                
                result = self.children_[i].evaluate(payload, level + 1, verbose=verbose)
                i += 1

        # if children are joined by OR, evaluate every child until all children
        # are evaluated or until a True breaks the loop (only need 1 True for OR)
        else:
            result = False
            i = 0
            while result == False and (i < len(self.children_)):
                
                if verbose:
                    tabs = "\t" * level
                    if i > 0: print("\n" + tabs + f"{self.conjuction_} \n")
                    print(tabs + f"Evaluating Composite: {i + 1}, Level: {level + 1}")
                
                result = self.children_[i].evaluate(payload, level + 1, verbose=verbose)
                i += 1

        if verbose: 
            tabs = "\t" * level
            print("\n" + tabs + f"Composite Result: {result}")

        return result

class JSONEvaluationEngine():
    """Engine builds the logical components from a properly formatted
    JSON backend and implements an evaluate() method.
    
    Attributes:
        composite_ (Composite): master composite of all logical components
        json_ (dict): dictionary of backend JSON
    
    """

    def __init__(self, json_path, verbose=True):
        """Initializes the engine by building the master composite.

        Args:
            json_path (str): path to JSON backend
            verbose (bool): whether to print intermediate steps of composite build.
        
        Returns:
            None
        """

        with open(json_path) as f:
            self.json_ = json.load(f)

        self.composite_ = self.build_engine(self.json_, conjunction='AND')

    def build_engine(self, children, conjunction, verbose=True):
        """Recursively joins all logical components into a master composite.

        Args:
            children (list): list of logical children, either Evaluations or Composites.
            conjuction (str): one of {'AND', 'OR'} - how to logically join children.
            verbose (bool): whether to print intermediate steps of composite build.

        Returns:
            composite (Composite): composite of logical children.
        """
        # TODO - extra recursion taking place in here somewhere
        comp_children = []
        if verbose: print(f"calling build_engine with {children}")
        for child in children:        
            if child.get('field'):
                comp_children.append(Evaluation(child['field'], child['value'], child['operator']))
                print(comp_children)
            else:
                new_children = child.get('children')
                conj = child.get('conjuction')
                comp_children.append(self.build_engine(new_children, conjunction=conj))
    
        return Composite(comp_children, conjuction=conjunction)

    def evaluate(self, payload, verbose=True):
        """Evaluate payload data against engine logical composite

        Args:
            payload (dict): dictionary of data to be evaluated.
            verbose (bool): whether to print intermediate steps of evaluation.
        
        Returns:
            result (bool): result of logical evaluation of engine against payload
        """

        return self.composite_.evaluate(payload, verbose=verbose)



