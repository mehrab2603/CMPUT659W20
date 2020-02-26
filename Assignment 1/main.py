import os
import time
from src.ezs import EZS

if __name__ == "__main__":
    NUM_RUNS = 3

    configurations = [
        {
            "generations": 30,
            "population": 30,
            "rounds": 20,
            "elites": 10,
            "tournaments": 10,
            "mutations": 0.5
        },
        {
            "generations": 30,
            "population": 25,
            "rounds": 20,
            "elites": 8,
            "tournaments": 8,
            "mutations": 0.5
        },
        {
            "generations": 30,
            "population": 15,
            "rounds": 20,
            "elites": 6,
            "tournaments": 6,
            "mutations": 0.5
        },
        {
            "generations": 30,
            "population": 10,
            "rounds": 20,
            "elites": 5,
            "tournaments": 5,
            "mutations": 0.5
        },
        {
            "generations": 30,
            "population": 8,
            "rounds": 20,
            "elites": 3,
            "tournaments": 3,
            "mutations": 0.5
        }
    ]

    for run_number in range(NUM_RUNS):
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")

        for configuration in configurations:
            generations = configuration["generations"]
            population = configuration["population"]
            rounds = configuration["rounds"]
            elites = configuration["elites"]
            tournaments = configuration["tournaments"]
            mutations = configuration["mutations"]

            x = EZS(generations=generations, population=population, rounds=rounds, elites=elites, tournaments=tournaments, mutations=mutations)

            start = time.time()

            x.start(save_directory=os.path.join("synthesized", "Run_{}_{}".format(run_number, timestamp)))

            end = time.time()

            print("Finished with configuration: generations {}, population {}, rounds {}, elites {}, tournaments {}, mutations {}. Time required: {} seconds.".format(generations, population, rounds, elites, tournaments, mutations, end - start))
