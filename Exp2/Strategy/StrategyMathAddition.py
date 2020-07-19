from StrategyBaseClass import StrategyBaseClass

class StrategyMathAddition(StrategyBaseClass):
    def __init__(self):
        pass

    def fit_to_dataset(self, context) -> bool:
        return "calc" in context and context["calc"] == "add" and "param1" in context and "param2" in context

    def execute(self, context):
        return context["param1"] "+" context["param2"]