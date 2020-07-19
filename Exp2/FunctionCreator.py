from RequirementBaseClass import RequirementBaseClass
from Strategy.StrategyBaseClass import StrategyBaseClass
import StructuredMask

class FunctionCreator(RequirementBaseClass, StrategyBaseClass):
    masks: list

    def __init__(self, function_name):
        RequirementBaseClass.__init__(self)
        # Syntax
        # <Keyword> Object (z.B. <Detail>)
        # [] Optional (z.B. [ein]) 
        # | alternativ (muss auch ans Ende der Alternative z.B. ein/eine/einer/)
        # {} Kann sich beliebig oft wiederholen (z.B. {})
        self.masks = []
        self.masks.append(("Schreibe {<Detail>} auf die Konsole", lambda library: " ".join(library["Detail"])))
        self.StructuredMaskInstance = StructuredMask.StructuredMask(self.masks)
        self.function_name = function_name