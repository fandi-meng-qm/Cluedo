import copy
import itertools as it
from cluedo_game import CluedoGame,CluedoParams
import numpy
from matplotlib import pyplot as plt
import numpy as np
import logging
import pyspiel
from open_spiel.python.algorithms import exploitability
from open_spiel.python import policy as policy_lib


params = CluedoParams(2)
game = CluedoGame(game_params=params)

fixed_policy = policy_lib.TabularPolicy(game)

policy = policy_lib.TabularPolicy(game)


# print(exploitability.nash_conv(game, policy))

def print_policy(policy):
    for state, probs in zip(it.chain(*policy.states_per_player),
                            policy.action_probability_array):
        print(f'{state:6}   p={probs}')
        # print(probs)


# print_policy(fixed_policy)
print_policy(policy)