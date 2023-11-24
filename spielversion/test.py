import random
from open_spiel.python.algorithms import cfr
import itertools as it
from cluedo_game import CluedoGame,CluedoParams
from matplotlib import pyplot as plt
from open_spiel.python.algorithms import external_sampling_mccfr as external_mccfr
from pyspiel import TabularPolicy, State, PlayerId, Game
from open_spiel.python.algorithms import exploitability


def print_policy(policy: TabularPolicy) -> None:
    for state, probs in zip(it.chain(*policy.states_per_player),
                            policy.action_probability_array):
        print(f'{state:6}   p={probs}')


eval_steps = []
eval_nash_conv = []


def get_mccfr_policy(game: CluedoGame, n: int):
    cfr_solver = external_mccfr.ExternalSamplingSolver(
        game, external_mccfr.AverageType.SIMPLE)
    for i in range(n):
        cfr_solver.iteration()
        average_policy = cfr_solver.average_policy()
        if i & (i - 1) == 0:
            conv = exploitability.nash_conv(game, cfr_solver.average_policy())
            eval_steps.append(i)
            print("Iteration {} exploitability {}".format(i, conv))
    print_policy(average_policy)
    return average_policy


params = CluedoParams(2)
game = CluedoGame(game_params=params)

if __name__ == '__main__':
    get_mccfr_policy(game, 1)
