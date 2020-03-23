import random
import re

class RuleTree:
    def __init__(self, grammar, root):
        self.grammar = grammar
        self.root = root
        self.unreduced_replacement = random.choice(self.grammar[self.root])
        self.create_subtrees()
        

    def create_subtrees(self):
        self.subtrees = []

        for non_terminal_symbol in self.grammar.keys():
            pattern = re.compile(r"\b"+non_terminal_symbol+r"\b", 0)
            result = pattern.search(self.unreduced_replacement)

            while result is not None:
                non_terminal_symbol_location = result.span()

                self.subtrees.append({
                    "original": non_terminal_symbol,
                    "location": non_terminal_symbol_location,
                })

                child = RuleTree(self.grammar, self.subtrees[-1]["original"])
                self.subtrees[-1]["child"] = child

                result = pattern.search(self.unreduced_replacement, pos=non_terminal_symbol_location[1])

        self.subtrees = sorted(self.subtrees, key=lambda tree: tree["location"][0], reverse=True)

    def get_rule(self):
        rule = self.unreduced_replacement

        for subtree in self.subtrees:
            rule = rule[0:subtree["location"][0]] + subtree["child"].get_rule() + rule[subtree["location"][1]:]

        return rule

    def get_all_nodes(self):
        all_nodes = [self]

        for subtree in self.subtrees:
            all_nodes += subtree["child"].get_all_nodes()

        return all_nodes

    def mutate_tree(self):
        all_nodes = self.get_all_nodes()
        node_to_mutate = random.choice(all_nodes)

        while len(node_to_mutate.grammar[node_to_mutate.root]) < 2:
            node_to_mutate = random.choice(all_nodes)

        old_unreduced_replacement = node_to_mutate.unreduced_replacement
        node_to_mutate.unreduced_replacement = random.choice(node_to_mutate.grammar[node_to_mutate.root])

        while node_to_mutate.unreduced_replacement == old_unreduced_replacement:
            node_to_mutate.unreduced_replacement = random.choice(node_to_mutate.grammar[node_to_mutate.root])

        node_to_mutate.create_subtrees()

        return self
