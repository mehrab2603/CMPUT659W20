import re
import random
from players.scripts.DSL import DSL

class SingleIf:
    def __init__(self, dsl=None):
        if dsl is None:
            dsl = DSL()
        
        self._dsl = DSL()
        self._non_terminal_symbols = self._dsl._grammar.keys()
        self._rules = set()
        self.generate_rules()

    def __eq__(self, other):
        if isinstance(other, SingleIf):
            return self._rules == other._rules
        return False
    
    def get_next_unreduced_symbol(self, rule):
        for non_terminal_symbol in self._non_terminal_symbols:
            pattern = re.compile(r"\b"+non_terminal_symbol+r"\b", 0)
            result = pattern.search(rule)

            if result is not None:
                return non_terminal_symbol, result.span()

        return None

    def get_rule_string(self, generate_new=False):
        if generate_new:
            self.generate_rules()

        return " and ".join(self._rules)

    def generate_rules(self, dsl=None):
        if dsl is not None:
            self._dsl = dsl
            self._non_terminal_symbols = self._dsl._grammar.keys()
        
        valid_rule_found = False

        while not valid_rule_found:
            rule_string = self._dsl.start

            unreduced_symbol_status = self.get_next_unreduced_symbol(rule_string)

            while unreduced_symbol_status is not None:
                unreduced_symbol, location = unreduced_symbol_status
                replacement_symbol = random.choice(self._dsl._grammar[unreduced_symbol])

                rule_string = rule_string[:location[0]] + replacement_symbol + rule_string[location[1]:]

                unreduced_symbol_status = self.get_next_unreduced_symbol(rule_string)

            if len(re.findall(r"\bif\b", rule_string)) == 1:
                valid_rule_found = True
                self._rules = set([rule.strip() for rule in rule_string.replace("if ", "").split(" and ")])

