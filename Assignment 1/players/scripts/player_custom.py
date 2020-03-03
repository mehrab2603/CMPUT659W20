from players.player import Player
from players.scripts.DSL import DSL



class PlayerCustom(Player):

    def get_action(self, state):
        actions = state.available_moves()
        
        for a in actions:

            if DSL.isStopAction(a) and DSL.hasWonColumn(state,a):
                return a

            if DSL.containsNumber(a, 4) and DSL.isDoubles(a):
                return a

            if DSL.containsNumber(a, 2) and DSL.containsNumber(a, 6):
                return a

            if DSL.containsNumber(a, 2) and DSL.containsNumber(a, 4):
                return a

            if DSL.containsNumber(a, 6) and DSL.containsNumber(a, 4):
                return a

            if DSL.containsNumber(a, 2) and DSL.isDoubles(a):
                return a

            if DSL.containsNumber(a, 6) and DSL.isDoubles(a):
                return a

            if DSL.containsNumber(a, 4):
                return a

            if DSL.containsNumber(a, 2):
                return a

            if DSL.containsNumber(a, 6):
                return a
        
        return actions[0]