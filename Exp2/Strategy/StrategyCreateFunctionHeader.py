from StrategyBaseClass import StrategyBaseClass

class StrategyCreateFunctionHeader(StrategyBaseClass):
    def __init__(self):
        pass

    def fit_to_dataset(self, context) -> bool:
        return "function_name" in context

    def execute(self, context):
        return "def {}:".format(context["function_name"])