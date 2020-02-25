import random
import os
from players.scripts.DSL import DSL
from src.SingleIf import SingleIf

class Script:
    def __init__(self, id, single_ifs=None, if_count = None):
        self._id = id

        if single_ifs is None:
            self._single_ifs = []

            if if_count is None:
                if_count = random.choice(range(1, 10))

            while len(self._single_ifs) < if_count:
                new_single_if = SingleIf()

                if new_single_if not in self._single_ifs:
                    self._single_ifs.append(new_single_if)
        else:
            self._single_ifs = []

            for single_if in single_ifs:
                if single_if not in self._single_ifs:
                    self._single_ifs.append(single_if)

        self._fitness = 0
        self._matches_played = 0
        self._counter_calls = [0] * len(self._single_ifs)

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_single_ifs(self):
        return self._single_ifs

    def add_fitness(self, v):
        self._fitness += v
        
    def get_fitness(self):
        return self._fitness
        
    def increment_matches_played(self):
        self._matches_played += 1

    def increment_if_call_counter(self, index, value):
        self._counter_calls[index] += value
        
    def get_matches_played(self):
        return self._matches_played

    def reset_statistics(self):
        self._fitness = 0
        self._matches_played = 0
        self._counter_calls = [0] * len(self._single_ifs)
        
    def get_script_text(self):
        text = [
            "import random",
            "from players.player import Player",
            "from players.scripts.DSL import DSL",
            "",
            "class Script{}(Player):".format(self._id),
            "",
            "    def __init__(self):",
            "        self._counter_calls = []",
            "        for i in range({}):".format(len(self._single_ifs)),
            "            self._counter_calls.append(0)",
            "",
            "    def get_counter_calls(self):",
            "        return self._counter_calls",
            "",
            "    def get_action(self, state):",
            "        actions = state.available_moves()",
            "",
            "        for a in actions:",
        ]

        for index, single_if in enumerate(self._single_ifs):
            text.append("            if " + single_if.get_rule_string() + ":")
            text.append("                self._counter_calls[{}] += 1".format(index))
            text.append("                return a")
            text.append("                        ")

        text.append("        return actions[0]\n")
        text.append("")

        text = "\n".join(text)
        exec(text)

        return text

    def get_instance(self):
        exec(self.get_script_text())
        script_instace = eval("Script{}()".format(self.get_id()))
        
        return script_instace

    def cleanup(self):
        new_single_ifs = []

        for index, single_if in enumerate(self._single_ifs):
            if self._counter_calls[index] > 0:
                new_single_ifs.append(single_if)

        if len(new_single_ifs) == 0:
            new_single_ifs.append(random.choice(self._single_ifs))

        delete_count = len(self._single_ifs) - len(new_single_ifs)

        if delete_count > 0:
            print("Deleted {} unused ifs from script {}".format(delete_count, self.get_id()))

        self._single_ifs = new_single_ifs
        self._counter_calls = [0] * len(self._single_ifs)
