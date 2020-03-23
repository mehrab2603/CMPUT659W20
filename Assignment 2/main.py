import os
import time
import copy
import pickle
import random
from scripts.cant_stop.game import Game
from scripts.cant_stop.dsl import DSL
from scripts.uct.vanilla_uct_player import Vanilla_UCT
from scripts.metropolis_hastings.mh import MetropolisHastings
from scripts.metropolis_hastings.rule_tree import RuleTree

def generate_data(id, c, simulations, initial_height, column_range, dice_value, rounds, output_directory=None):
    uct_player1 = Vanilla_UCT(c, simulations)
    uct_player2 = Vanilla_UCT(c, simulations)

    data = []

    print("Generating data from {} rounds...".format(rounds))

    for i in range(rounds):
        game = Game(n_players=2, dice_number=4, dice_value=dice_value, column_range=column_range, offset=2, initial_height=initial_height)
        
        is_over = False
        number_of_moves = 0

        while not is_over:
            moves = game.available_moves()

            if game.is_player_busted(moves):
                continue
            else:
                if game.player_turn == 1:
                    chosen_play = uct_player1.get_action(game)
                else:
                    chosen_play = uct_player2.get_action(game)

                data.append((copy.deepcopy(game), chosen_play))

                game.play(chosen_play)
                number_of_moves += 1

            _, is_over = game.is_finished()
        
        print("Round {} finished!".format(i + 1))

    print("Data generation complete! Generated {} samples.".format(len(data)))

    if output_directory is not None:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        filename = time.strftime("%d%m%Y_%H%M%S_{}.pkl".format(id))
        filepath = os.path.join(output_directory, filename)

        with open(filepath, "wb") as f:
            pickle.dump(data, f)

            print("Saved data to {}.".format(filepath))

    return data

def get_game_configuration(size, extended):
    configuration = {}

    if size == "small":
        configuration = {
            "initial_height": 1,
            "column_range": (2, 6),
            "dice_value": 3,
            "rounds": 20,
            "dsl": DSL(column_range=(2, 6), extended=extended)
        }
    elif size == "big":
        configuration = {
            "initial_height": 3,
            "column_range": (2, 6),
            "dice_value": 3,
            "rounds": 20,
            "dsl": DSL(column_range=(2, 6), extended=extended)
        }
    elif size == "full":
        configuration = {
            "initial_height": 2,
            "column_range": (2, 12),
            "dice_value": 6,
            "rounds": 20,
            "dsl": DSL(column_range=(2, 12), extended=extended)
        }

    return configuration

if __name__ == "__main__":
    c = 1   # Exploration Constant
    uct_simulations = 1000
    mh_iterations = 5000

    experiment_configurations = [
        {"game_size": "small", "uses_extended_dsl": False, "experiments": 5},
        {"game_size": "small", "uses_extended_dsl": True, "experiments": 5},
        {"game_size": "big", "uses_extended_dsl": False, "experiments": 5},
        {"game_size": "big", "uses_extended_dsl": True, "experiments": 5},
        {"game_size": "full", "uses_extended_dsl": False, "experiments": 5},
        {"game_size": "full", "uses_extended_dsl": True, "experiments": 5}
    ]

    for experiment_configuration in experiment_configurations:
        game_size = experiment_configuration["game_size"]
        uses_extended_dsl = experiment_configuration["uses_extended_dsl"]
        game_configuration = get_game_configuration(size=game_size, extended=uses_extended_dsl)

        id = "c{}_sim{}_inh{}_rng{}_{}_dic{}_rnd{}".format(c, uct_simulations, game_configuration["initial_height"], game_configuration["column_range"][0], game_configuration["column_range"][1], game_configuration["dice_value"], game_configuration["rounds"])

        # Load data if exists else generate new data
        data_output_directory = os.path.join(os.path.dirname(__file__), "data")
        data_path = None

        result_output_directory = os.path.join(os.path.dirname(__file__), "results")
        result_output_path = os.path.join(result_output_directory, "{}_{}_results.txt".format(id, "extended_dsl" if uses_extended_dsl else "standard_dsl"))

        # Check if any generated data matches current configuration
        generated_data = []
        for root, directory, files in os.walk(data_output_directory):
            for filename in files:
                if filename.endswith("{}.pkl".format(id)):
                    generated_data.append(os.path.join(root, filename))
        
        if len(generated_data) == 0:    # Load already existing data for current configuration
            data = generate_data(id=id, c=c, simulations=uct_simulations, initial_height=game_configuration["initial_height"], column_range=game_configuration["column_range"], dice_value=game_configuration["dice_value"], rounds=game_configuration["rounds"], output_directory=data_output_directory)
        else:   # Generate new data for current configuration if does not exist already
            data_path = random.choice(generated_data)

            with open(data_path, "rb") as f:
                unpickler = pickle.Unpickler(f)
                data = unpickler.load()
                print("Loaded data with {} samples.".format(len(data)))

        # Do experiments
        for experiment_number in range(experiment_configuration["experiments"]):
            print("Conducting experiment {} for {} game with {} DSL...".format(experiment_number + 1, game_size, "extended" if uses_extended_dsl else "standard"))

            # Generate results
            mh = MetropolisHastings(game_configuration["dsl"], data)
            samples = mh.draw_samples(iterations=mh_iterations)

            # Write results
            if not os.path.exists(result_output_directory):
                os.makedirs(result_output_directory, exist_ok=True)

            with open(result_output_path, "a") as f:
                f.write(time.strftime("############################ Date: %d/%m/%Y Time: %H:%M:%S ############################\n"))

                for sample in samples:
                    f.write(sample["rule"])
                    f.write("\n")

                print("Results written to {}".format(result_output_path))

            print("Finished experiment {} for {} game with {} DSL...".format(experiment_number + 1, game_size, "extended" if uses_extended_dsl else "standard"))