import copy
import random

class DSL:
    
    def __init__(self, column_range, extended=False):
        
        self.start = 'S'
        
        self._grammar = {}
        self._grammar[self.start] = ['if B']
        self._grammar['B'] = ['B1', 'B1 and B1']
        self._grammar['B1'] = ['DSL.isDoubles(a)', 'DSL.containsNumber(a, NUMBER )', 'DSL.actionWinsColumn(state,a)', 'DSL.hasWonColumn(state,a)', 
                               'DSL.numberPositionsProgressedThisRoundColumn(state, NUMBER ) > SMALL_NUMBER and DSL.isStopAction(a)', 'DSL.isStopAction(a)',
                               'DSL.numberPositionsConquered(state, NUMBER ) > SMALL_NUMBER and DSL.containsNumber(a, NUMBER )'] + (['DSL.hasIncentive(state, a, SMALL_NUMBER, SMALL_NUMBER)'] if extended else [])
        self._grammar['NUMBER'] = [str(i) for i in range(column_range[0], column_range[1] + 1)]
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

    @staticmethod
    def hasIncentive(state, action, small_number_1, small_number_2):
        """
        Returns true with probability proportional to the action's gathered incentive points when incentives are
        to catch up to the opponent at most small_number_1 steps away or
        to reach the top of the column if it is at most small_number_2 steps away.
        """
        copy_state = state.clone()

        player_column_positions = {}

        if isinstance(action, str): # Not sure what to do with these other than selecting randomly
            return random.randint(0, 100) < 50
        
        copy_state.play(action)

        who_won, is_over = copy_state.is_finished()

        if is_over == True and who_won != copy_state.player_turn:   # Select action if it wins the game
            return True

        for column_index in range(copy_state.board_game.column_range[0], copy_state.board_game.column_range[1] + 1):    # Current player's marker positions after this action
            player_column_positions[column_index] = copy_state.number_positions_conquered(column_index) + copy_state.number_positions_conquered_this_round(column_index)
        
        copy_state.play("n")    # End turn so that the other player becomes active and we can get the positions of its markers

        incentive_points = 0    # Gather up all the different incentives

        for column_index, _ in enumerate(copy_state.board_game.board):
            if column_index in action:
                column_size = len(copy_state.board_game.board[column_index])
                opponent_column_position = copy_state.number_positions_conquered(column_index)

                distance_from_opponent = opponent_column_position - player_column_positions[column_index]
                distance_from_top = column_size - player_column_positions[column_index]

                if opponent_column_position >= 0 and abs(distance_from_opponent) <= small_number_1:  # If opponent is within reach
                    incentive_points += 1   # Could be modified to have varying points depending on the distance
                
                if distance_from_top <= small_number_2: # If the top of the column is within reach
                    incentive_points += 1
        
        if random.randint(0, 100) <= incentive_points * 10 + 50:    # Higher the total incentive, higher the probability of selecting the action
            return True
        else:
            return False