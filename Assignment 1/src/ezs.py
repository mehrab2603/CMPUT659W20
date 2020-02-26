import re
import os
import time
import random
import numpy as np
from game import Board, Game
from src.SingleIf import SingleIf
from src.ScriptNew import Script

class EZS:
    def __init__(self, generations, population, rounds, elites, tournaments, mutations):
        self._generations = generations
        self._population = population
        self._rounds = rounds
        self._elites = elites
        self._tournaments = tournaments
        self._mutations = mutations

        self._scripts = []

    def generate_population(self, generation, population):
        return [Script("{}_{}".format(generation, i)) for i in range(population)]

    def evaluate(self, scripts, rounds, do_cleanup=False):
        for script in scripts:
            script.reset_statistics()

        for i in range(len(scripts)):
            for j in range(i + 1, len(scripts)):

                script_1 = scripts[i]
                script_2 = scripts[j]

                script_1_instance = script_1.get_instance()
                script_2_instance = script_2.get_instance()

                print("############################################")
                
                for k in range(rounds):
                    game = Game(n_players=2, dice_number=4, dice_value=3, column_range=[2,6], offset=2, initial_height=1)

                    player_1 = [script_1, script_1_instance] if k < (rounds / 2.0) else [script_2, script_2_instance]
                    player_2 = [script_2, script_2_instance] if k < (rounds / 2.0) else [script_1, script_1_instance]
                    
                    print("{} vs {}".format(player_1[0].get_id(), player_2[0].get_id()))

                    is_over = False
                    who_won = None
                
                    number_of_moves = 0

                    while not is_over:
                        moves = game.available_moves()
                        if game.is_player_busted(moves):
                            continue
                        else:
                            if game.player_turn == 1:
                                chosen_play = player_1[1].get_action(game)
                            else:
                                chosen_play = player_2[1].get_action(game)

                            # print('Chose: ', chosen_play)
                            # game.print_board()
                            game.play(chosen_play)
                            # game.print_board()
                            number_of_moves += 1
                            
                            # print()
                        who_won, is_over = game.is_finished()
                        
                        if number_of_moves >= 200:
                            is_over = True
                            who_won = -1
                            # print('No Winner!')
                            
                    if who_won == 1:
                        player_1[0].add_fitness(1)
                        player_2[0].add_fitness(-1)

                        print("Winner: {}".format(player_1[0].get_id()))
                    elif who_won == 2:
                        player_1[0].add_fitness(-1)
                        player_2[0].add_fitness(1)

                        print("Winner: {}".format(player_2[0].get_id()))
                    elif who_won == -1:
                        player_1[0].add_fitness(-1)
                        player_2[0].add_fitness(-1)

                        print("Nobody won!!!")

                    if is_over:
                        player_1[0].increment_matches_played()
                        player_2[0].increment_matches_played()

                        for l in range(len(player_1[0].get_single_ifs())):
                            player_1[0].increment_if_call_counter(l, player_1[1]._counter_calls[l])
                            
                        for l in range(len(player_2[0].get_single_ifs())):
                            player_2[0].increment_if_call_counter(l, player_2[1]._counter_calls[l])

                print("############################################")

        if do_cleanup:
            for script in self._scripts:
                script.cleanup()

    def get_elites(self, scripts, elites):
        return sorted(scripts, key=lambda script: script.get_fitness(), reverse=True)[:elites]

    def get_tournament_winner(self, scripts, tournaments, rounds):
        selected_scripts = [Script(id=script.get_id() + "_tourney", single_ifs=script.get_single_ifs()) for script in np.random.choice(scripts, tournaments, replace=False)]

        print("Selected tourney players: {}".format([script.get_id() for script in selected_scripts]))

        self.evaluate(scripts=selected_scripts, rounds=rounds, do_cleanup=False)
        best_player = self.get_elites(scripts=selected_scripts, elites=1)[0]

        print("Best tourney player: {}".format(best_player.get_id()))

        return best_player

    def crossover(self, p1, p2):
        split_index = random.randint(0, min(len(p1.get_single_ifs()), len(p2.get_single_ifs())))
        p1_single_ifs = p1.get_single_ifs()[0:split_index]
        p2_single_ifs = p2.get_single_ifs()[split_index:]

        return Script(id="{}_{}_child".format(p1.get_id(), p2.get_id()), single_ifs=p1_single_ifs + p2_single_ifs)

    def mutate(self, new_id, script, mutations):
        new_single_ifs = []
        
        for single_if in script.get_single_ifs():
            if random.randint(0, 100) < mutations * 100:    # Don't change
                if single_if not in new_single_ifs:
                    new_single_ifs.append(single_if)
            else:
                new_single_if = SingleIf()

                while new_single_if in new_single_ifs:
                    new_single_if = SingleIf()

                new_single_ifs.append(new_single_if)   # Change

            if random.randint(0, 100) < mutations * 100:    # Append a new one
                new_single_if = SingleIf()

                while new_single_if in new_single_ifs:
                    new_single_if = SingleIf()

                if random.randint(0, 100) < 50: # Append to left
                    new_single_ifs.insert(-1, new_single_if)
                else:   # Append to right
                    new_single_ifs.append(new_single_if)

        return Script(id=new_id, single_ifs=new_single_ifs)

    def start(self, save_directory=None):
        self._scripts = self.generate_population(generation=0, population=self._population)

        for i in range(self._generations):
            start = time.time()

            self.evaluate(scripts=self._scripts, rounds=self._rounds, do_cleanup=True)
            next_generation = self.get_elites(scripts=self._scripts, elites=self._elites)

            next_generation_script_number = 0

            while len(next_generation) < self._population:
                parent_script_1 = self.get_tournament_winner(scripts=self._scripts, tournaments=self._tournaments, rounds=self._rounds)
                parent_script_2 = self.get_tournament_winner(scripts=self._scripts, tournaments=self._tournaments, rounds=self._rounds)

                child_script = self.crossover(parent_script_1, parent_script_2)
                child_script = self.mutate(new_id="{}_{}".format(i + 1, next_generation_script_number), script=child_script, mutations=self._mutations)
                
                next_generation.append(child_script)

                next_generation_script_number += 1

            self._scripts = next_generation

            end = time.time()

            if save_directory is not None:
                self.evaluate(scripts=self._scripts, rounds=self._rounds, do_cleanup=False)
                best_in_generation = self.get_elites(scripts=self._scripts, elites=1)[0]

                configuration_specific_save_directory = os.path.join(
                    save_directory,
                    "Configuration_{}_{}_{}_{}_{}_{}".format(self._generations, self._population, self._rounds, self._elites, self._tournaments, self._mutations)
                )
                
                filename = "gen_{}.py".format(i)

                if not os.path.exists(configuration_specific_save_directory):
                    os.makedirs(configuration_specific_save_directory, exist_ok=True)
                else:
                    os.makedirs(configuration_specific_save_directory, exist_ok=True)

                with open(os.path.join(configuration_specific_save_directory, filename), "w") as f:
                    f.write("# Generated in {} seconds\n".format(end - start))
                    f.write(best_in_generation.get_script_text())

        self.evaluate(scripts=self._scripts, rounds=self._rounds, do_cleanup=False)
        best = self.get_elites(scripts=self._scripts, elites=1)[0]

        return best

        




