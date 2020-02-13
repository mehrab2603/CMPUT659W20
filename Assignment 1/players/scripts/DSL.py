import copy
import random
from players.scripts.Script import Script

class DSL:
    
    def __init__(self):
        
        self.start = 'S'
        
        self._grammar = {}
        self._grammar[self.start] = ['if B S', '']
        self._grammar['B'] = ['B1', 'B1 and B1']
        self._grammar['B1'] = ['DSL.isDoubles(a)', 'DSL.containsNumber(a, NUMBER )', 'DSL.actionWinsColumn(state,a)', 'DSL.hasWonColumn(state,a)', 
                               'DSL.numberPositionsProgressedThisRoundColumn(state, NUMBER ) > SMALL_NUMBER and DSL.isStopAction(a)', 'DSL.isStopAction(a)',
                               'DSL.numberPositionsConquered(state, NUMBER ) > SMALL_NUMBER and DSL.containsNumber(a, NUMBER )']
        self._grammar['NUMBER'] = ['2', '3', '4', '5', '6']
        self._grammar['SMALL_NUMBER'] = ['0', '1', '2'] 
    
    @staticmethod
    def isDoubles(action):
        """
        Returns true if the action is a double. 
        
        Examples of doubles: (2, 2), (3, 3), (4, ,4)
        """
        if len(action) > 1 and action[0] == action[1]:
            return True
        else:
            return False
        
    @staticmethod
    def containsNumber(action, number):
        """
        Returns true if the action contains the number
        
        Example: returns true for action (2, 3) and number 3
                 returns true for action (2, 6) and number 4
        """
        if not isinstance(action, str):
            if number in action:
                return True
        return False
    
    @staticmethod
    def actionWinsColumn(state, action):
        """
        Returns true if the action completes a column for the player
        """
        copy_state = copy.deepcopy(state)
        copy_state.play(action)
        columns_won = copy_state.columns_won_current_round()
        columns_won_previously = state.columns_won_current_round()
        if len(columns_won) > 0 and columns_won != columns_won_previously:
            return True
        return False
    
    @staticmethod
    def numberPositionsProgressedThisRoundColumn(state, column):
        """
        Returns the number of positions progressed in a given column in the current round.
        A round finishes once the player chooses to stop, which is action n in this implementation. 
        """
        return state.number_positions_conquered_this_round(column)
    
    @staticmethod
    def numberPositionsConquered(state, column):
        """
        Returns the number of positions conquered in a given column. A position is
        conquered once the player progresses in the column and decides to stop. By stopping, the
        temporary markers are replaced by permanent markers and the positions are conquered. 
        """
        return state.number_positions_conquered(column)

    @staticmethod
    def hasWonColumn(state, action):
        """
        Returns true if the player has won a column, i.e., if the player progressed all the way
        to the top of a given column. 
        """
        return len(state.columns_won_current_round()) > 0
    
    @staticmethod
    def isStopAction(action):
        """
        Returns true if the action is a stop action, i.e., action n in this implementation.
        """
        if isinstance(action, str) and action == 'n':
            return True
        return False