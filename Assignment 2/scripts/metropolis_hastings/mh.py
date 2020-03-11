import math
import random
import copy
from collections import Counter
from scripts.cant_stop.dsl import DSL
from scripts.metropolis_hastings.rule_tree import RuleTree

#   samples = []
# 2 samples.append(np.random.normal(10, 1, 1)[0])
# 3
# 4 for i in range(0, 20000):
# 5 x_i = samples[i]
# 6 x_cand = np.random.normal(x_i, 1, 1)[0]
# 7 accept = min(1, binomial(x_cand)/binomial(x_i))
# 8
# 9 p = random.uniform(0, 1)
# 10 if p < accept:
# 11 samples.append(x_cand)
# 12 else:
# 13 samples.append(x_i)

class MetropolisHastings:
    def __init__(self, dsl, ground_truths):
        self.rule_tree = RuleTree(dsl._grammar, dsl.start)
        self.ground_truths = copy.deepcopy(ground_truths)

    def get_script(self, id, rule=None, beta=0.5):
        if rule is None:
            rule = self.rule_tree.mutate_tree().get_rule()

        text = [
            "import random",
            "from scripts.cant_stop.player import Player",
            "from scripts.cant_stop.dsl import DSL",
            "",
            "class Script{}(Player):".format(id),
            "",
            "    def __init__(self):",
            "        pass",
            "",
            "    def get_action(self, state):",
            "        actions = state.available_moves()",
            "",
            "        for a in actions:",
            "            {}:".format(rule),
            "                return a",
            "",
            "        return actions[0]",
            ""
        ]

        text = "\n".join(text)

        exec(text)
        script_instace = eval("Script{}()".format(id))

        errors = self.evaluate_script(script_instace)
        
        return {"rule": rule, "instance": script_instace, "errors": errors, "c_value": math.exp(-beta * errors)}

    def evaluate_script(self, script):
        errors = 0

        for ground_truth in self.ground_truths:
            state, true_action = ground_truth
            predicted_action = script.get_action(state)

            if true_action != predicted_action:
                errors += 1

        return errors

    def remove_agreeing_ground_truth(self, script):
        remove_count = 0

        for ground_truth in self.ground_truths:
            state, true_action = ground_truth
            predicted_action = script["instance"].get_action(state)

            if true_action == predicted_action:
                self.ground_truths.remove(ground_truth)
                remove_count += 1

        print("Rule | {} | matched {} ground truths which were removed.".format(script["rule"] ,remove_count))

    def draw_samples(self, iterations=1000, sample_count=5):
        selected_samples = []      

        for i in range(sample_count):
            iteration_samples = [self.get_script(id="Sample{}Iteration{}".format(i, 0))]
            iteration_sampled_rules = [iteration_samples[-1]["rule"]]

            for j in range(iterations):
                previous = iteration_samples[-1]
                candidate = self.get_script(id="Sample{}Iteration{}".format(i, j + 1))

                accept = min(1, candidate["c_value"] / previous["c_value"])

                if accept > random.uniform(0, 1):
                    iteration_samples.append(candidate)
                else:
                    iteration_samples.append(previous)
                
                iteration_sampled_rules = [iteration_samples[-1]["rule"]]

            selected_samples.append(Counter(iteration_sampled_rules).most_common(1)[0][0])

            print("Sampled rule: {}".format(selected_samples[i]))
            self.remove_agreeing_ground_truth(self.get_script(id="Selected{}".format(i), rule=selected_samples[i]))

        return selected_samples

            




