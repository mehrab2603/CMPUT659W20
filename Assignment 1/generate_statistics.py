import os
import re
from game import Board, Game

def calculate_fitness(script):
    return sum(script["victories_as_player_1"]) + sum(script["victories_as_player_2"]) - sum(script["defeats_as_player_1"]) - sum(script["defeats_as_player_2"])

def get_script_statistics_string(script):
    strings = [
        "Path: {}".format(script["path"]),
        "Class: {}".format(script["original_class_name"]),
        "Fitness: {}".format(script["fitness"]),
        "Rounds Played: {}".format(script["rounds_played"]),
        "Opponents: {}".format(script["opponent"]),
        "Victories 1: {}".format(script["victories_as_player_1"]),
        "Victories 2: {}".format(script["victories_as_player_2"]),
        "Defeats 1: {}".format(script["defeats_as_player_1"]),
        "Defeats 2: {}".format(script["defeats_as_player_2"]),
        "===================================",
        script["action_code"],
        "==================================="
    ]

    return "\n".join(strings)

def battle_royale(initial_height, scripts, decompose=False):
    if decompose:
        scripts = [script_tuple[0] for script_tuple in scripts]

    for script in scripts:
        script["fitness"] = 0
        script["victories_as_player_1"] = []
        script["victories_as_player_2"] = []
        script["defeats_as_player_1"] = []
        script["defeats_as_player_2"] = []
        script["opponent"] = []
        script["rounds_played"] = 0
    
    best_fitness = -1000000
    best_scripts = []

    for i in range(len(scripts)):
        for j in range(i + 1, len(scripts)):
            script_1 = eval("{}()".format(scripts[i]["modified_class_name"]))
            script_2 = eval("{}()".format(scripts[j]["modified_class_name"]))

            print("############################################")

            scripts[i]["opponent"].append(scripts[j]["original_class_name"])
            scripts[i]["victories_as_player_1"].append(0)
            scripts[i]["victories_as_player_2"].append(0)
            scripts[i]["defeats_as_player_1"].append(0)
            scripts[i]["defeats_as_player_2"].append(0)

            scripts[j]["opponent"].append(scripts[i]["original_class_name"])
            scripts[j]["victories_as_player_1"].append(0)
            scripts[j]["victories_as_player_2"].append(0)
            scripts[j]["defeats_as_player_1"].append(0)
            scripts[j]["defeats_as_player_2"].append(0)
                
            for k in range(rounds):
                game = Game(n_players=2, dice_number=4, dice_value=3, column_range=[2,6], offset=2, initial_height=initial_height)

                player_1 = [scripts[i], script_1] if k < (rounds / 2.0) else [scripts[j], script_2]
                player_2 = [scripts[j], script_2] if k < (rounds / 2.0) else [scripts[i], script_1]
                
                print("{} vs {}".format(player_1[0]["original_class_name"], player_2[0]["original_class_name"]))

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

                        game.play(chosen_play)
                        number_of_moves += 1

                    who_won, is_over = game.is_finished()
                    
                    if number_of_moves >= 200:
                        is_over = True
                        who_won = -1
                        
                if who_won == 1:
                    player_1[0]["victories_as_player_1" if k < (rounds / 2.0) else "victories_as_player_2"][-1] += 1
                    player_2[0]["defeats_as_player_2" if k < (rounds / 2.0) else "defeats_as_player_1"][-1] += 1

                    print("Winner: {} ({})".format(player_1[0]["original_class_name"], calculate_fitness(player_1[0])))
                elif who_won == 2:
                    player_2[0]["victories_as_player_2" if k < (rounds / 2.0) else "victories_as_player_1"][-1] += 1
                    player_1[0]["defeats_as_player_1" if k < (rounds / 2.0) else "defeats_as_player_2"][-1] += 1

                    print("Winner: {} ({})".format(player_2[0]["original_class_name"], calculate_fitness(player_2[0])))
                elif who_won == -1:
                    player_1[0]["defeats_as_player_1" if k < (rounds / 2.0) else "defeats_as_player_2"][-1] += 1
                    player_2[0]["defeats_as_player_2" if k < (rounds / 2.0) else "defeats_as_player_1"][-1] += 1

                    print("Nobody won!!!")

                if is_over:
                    player_1[0]["rounds_played"] += 1
                    player_2[0]["rounds_played"] += 1

            print("############################################")

        fitness = calculate_fitness(scripts[i])
        scripts[i]["fitness"] = fitness

        # Select the scripts that have the highest fitness value as the best scripts of this experiment 
        if fitness >= best_fitness:
            if fitness == best_fitness:
                best_scripts.append(scripts[i])
            else:
                best_scripts = [scripts[i]]
            
            best_fitness = fitness

    return best_fitness, best_scripts


if __name__ == "__main__":
    data_path = "arena"
    initial_height = 1
    experiments = 10
    rounds = 50

    configurations = {}
    script_count = 0

    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r") as f:
                    lines = f.readlines()

                    if len(lines) > 5 and lines[5].startswith("class ") and lines[5].endswith("(Player):\n"):
                        class_name = lines[5][len("class "):-len("(Player):\n")]
                        lines[5] = lines[5][:len("class ")] + "Script{}".format(script_count) + lines[5][-len("(Player):\n"):]
                    

                        configuration = os.path.basename(root)

                        if configuration not in configurations.keys():
                            configurations[configuration] = []

                        configurations[configuration].append({
                            "path": os.path.join(root, file),
                            "original_class_name": class_name,
                            "modified_class_name": "Script{}".format(script_count),
                            "code": "\n".join(lines),
                            "action_code": "\n".join(lines[18:]),
                            "fitness": 0,
                            "victories_as_player_1": [],
                            "victories_as_player_2": [],
                            "defeats_as_player_1": [],
                            "defeats_as_player_2": [],
                            "opponent": [],
                            "rounds_played": 0
                        })

                        script_count += 1

    for configuration, scripts in configurations.items():
        for script in scripts:
            exec(script["code"])

    print("Found {} configurations containing a total of {} scripts. Beginning evaluation...".format(len(configurations), script_count))

    best_fitness_across_configurations = -1000000
    best_scripts_across_configurations = []

    for configuration, scripts in configurations.items():
        scripts_with_best_fitness_in_configuration = []

        for experiment_number in range(experiments):
            print("Executing experiment {}...".format(experiment_number))

            best_fitness_in_experiment, best_scripts_in_experiment = battle_royale(initial_height, scripts, False)

            player_1_wins = 0
            player_2_wins = 0
            player_1_losses = 0
            player_2_losses = 0

            for script in scripts:
                player_1_wins += sum(script["victories_as_player_1"])
                player_2_wins += sum(script["victories_as_player_2"])

                player_1_losses += sum(script["defeats_as_player_1"])
                player_2_losses += sum(script["defeats_as_player_2"])

            # Write experiment statistics
            with open(os.path.join(os.path.dirname(scripts[0]["path"]), "{}_result_{}.txt".format(configuration, experiment_number)), "w") as f:
                f.write("Results of configuration {} experiment {}\n####################################\n".format(configuration, experiment_number))
                f.write("Best scripts are {}\n".format([(script["path"], "fitness: {}".format(script["fitness"])) for script in best_scripts_in_experiment]))
                f.write("Wins as player 1 / 2: {} / {}\n".format(player_1_wins, player_2_wins))
                f.write("Losses as player 1 / 2: {} / {}\n".format(player_1_losses, player_2_losses))
                f.write("####################################\n")

                for script in best_scripts_in_experiment:
                    f.write("===================================\n")
                    f.write(script["action_code"])
                    f.write("\n")
                    
                for script in scripts:
                    f.write("####################################\n")
                    f.write(get_script_statistics_string(script))
                    f.write("\n")

            scripts_with_best_fitness_in_configuration += [(script, experiment_number) for script in best_scripts_in_experiment]    # Gather up scripts with best fitness values across experiments
            
            print("Experiment {} done!!!".format(experiment_number))

        # Select the scripts that have won the most number of experiments as the best scripts of this configuration 
        best_codes = {}
        best_scripts_in_configuration = []
        best_script_info_in_configuration = []
        max_count = 0

        for script, experiment_number in scripts_with_best_fitness_in_configuration:
            if script["action_code"] not in best_codes.keys():
                best_codes[script["action_code"]] = {
                    "count": 0,
                    "source": [(script, experiment_number)]
                }
            else:
                best_codes[script["action_code"]]["count"] += 1
                best_codes[script["action_code"]]["source"].append((script, experiment_number))

                max_count = max(max_count, best_codes[script["action_code"]]["count"])

        for val in best_codes.values():
            if val["count"] == max_count:
                
                for script, experiment_number in val["source"]:
                    already_selected = False

                    for script_experiment in best_scripts_in_configuration:
                        if script_experiment[0]["action_code"] == script["action_code"]:
                            already_selected = True
                            break
                    
                    if not already_selected:
                        best_scripts_in_configuration.append((script, experiment_number))

                    best_script_info_in_configuration.append("{}/{}/{}".format(script["path"], script["original_class_name"], experiment_number))
                    
        # Write configuration statistics
        with open(os.path.join(os.path.dirname(scripts[0]["path"]), "{}_result_all.txt".format(configuration)), "w") as f:
            f.write("Overall results of configuration {}\n####################################\n".format(configuration))
            f.write("Best scripts are {}\n".format([info_string for info_string in best_script_info_in_configuration]))
            f.write("####################################\n")

            for script in best_scripts_in_configuration:
                f.write("===================================\n")
                f.write(script[0]["action_code"])
                f.write("\n\n")

        best_scripts_across_configurations += [(script, experiment_number, configuration) for script, experiment_number in best_scripts_in_configuration]
        print("Done with configuration {}!!!".format(configuration))

    if len(configurations.keys()) > 1:
        best_fitness_across_configurations, best_scripts_across_configurations = battle_royale(initial_height, best_scripts_in_configuration, decompose=True)

        with open(os.path.join(os.path.dirname(os.path.dirname(best_scripts_across_configurations[0]["path"])), "result_all.txt"), "w") as f:
            f.write("Best scripts are {}\n".format(["path: {}, fitness: {}".format(script["path"], script["fitness"]) for script in best_scripts_across_configurations]))
            f.write("####################################\n")

            for script in best_scripts_across_configurations:
                f.write("===================================\n")
                f.write(script["action_code"])
                f.write("\n\n")

    print("Done!!!")