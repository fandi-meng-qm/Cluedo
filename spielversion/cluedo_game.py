from __future__ import annotations

import copy
import itertools
import math
import random
from typing import List, NamedTuple

import pyspiel

import numpy as np

import enum

_MAX_NUM_PLAYERS = 6
_MIN_NUM_PLAYERS = 3
_GAME_TYPE = pyspiel.GameType(
    short_name="python_cluedo",
    long_name="Python cluedo",
    dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
    chance_mode=pyspiel.GameType.ChanceMode.EXPLICIT_STOCHASTIC,
    information=pyspiel.GameType.Information.IMPERFECT_INFORMATION,
    utility=pyspiel.GameType.Utility,
    reward_model=pyspiel.GameType.RewardModel.TERMINAL,
    max_num_players=_MAX_NUM_PLAYERS,
    min_num_players=_MIN_NUM_PLAYERS,
    provides_information_state_string=True,
    provides_information_state_tensor=True,
    provides_observation_string=True,
    provides_observation_tensor=False,
    provides_factored_observation_string=False)


class CluedoGame(pyspiel.Game):
    def __init__(self, n_players) -> None:
        game_params = n_players
        self.game_params = game_params
        n_actions = math.comb(n_players * 3 + 3, 3)
        game_info = pyspiel.GameInfo(
            num_distinct_actions=n_actions,
            max_chance_outcomes=math.comb(game_params.m_grid * game_params.n_grid, game_params.n_people) *
                                game_params.n_people,
            num_players=n_players,
            min_utility=0,
            max_utility=1,
            utility_sum=1.0,
            max_game_length=1000
        )
        super().__init__(_GAME_TYPE, game_info, n_players or dict())

    def new_initial_state(self, game_params=None) -> CluedoState:
        """Returns a state corresponding to the start of a game."""
        return CluedoState(self, self.game_params)

def get_cards(n_players):


def get_init_states(n_players):





class CluedoState(pyspiel.State):
    """A python version of the state."""

    def __init__(self, game, n_players):
        """Constructor; should only be called by Game.new_initial_state."""
        super().__init__(game)
        self.params = n_players
        self.players = list(range(n_players))
        self.cards = set()
        self.cards_dice = dict()
        self.accusation = dict()
        self.information_state = dict()
        self.step = 0
        self.player = int

    def current_player(self):
        """Returns id of the next player to move, or TERMINAL if game is over."""
        if self.is_terminal():
            return pyspiel.PlayerId.TERMINAL
        # in the current version only the first move is a chance move - the one which decides who is the killer
        elif self.step == 0:
            return pyspiel.PlayerId.CHANCE
        elif self.step == 1:
            self.player = random.choice(self.players)
            return self.player
        else:
            self.player = self.next_play(self.player)
            return self.player

    def next_player(self, player) ->int:
        if player + 1 > self.n_players:
            next_player = (player + 1) % self.n_players
        else:
            next_player = player + 1
        return next_player

    def _legal_actions(self, player) -> List[set] or None:
        """Returns a list of legal actions"""
        # check this is not the chance player, for some reason that is handled separately
        assert player >= 0

        set1=self.cards & {0, 1, 2, 3, 4, 5}
        set2=self.cards&{6,7,8,9,10,11}
        set3=self.cards&{12,13,14,15,16,17,18,19,20}
        actions = [set(item) for item in list(itertools.product(set1,set2,set3))]

        # print(actions)
        return actions

    def is_chance_node(self):
        if self.step == 0:
            return True




    def chance_outcomes(self):
        assert self.step == 0
        initial_states = get_init_states(self.params)
        chance_outcomes = [(i, 1 / len(initial_states)) for i in range(len(initial_states))]
        return chance_outcomes

    def _kill_action(self, victim: Person) -> None:
        assert self.current_player() == MurderPlayer.KILLER
        self.alive.remove(victim)
        self.dead.append(victim)
        self.points -= self.cost_list[self.people.index(victim)]

    def _accuse_action(self, suspect: Person) -> None:
        assert self.current_player() == MurderPlayer.DETECTIVE
        self.accused.append(suspect)

    def _apply_action(self, action: int) -> None:
        if self.is_chance_node():
            assert self.step == 0
            initial_states = get_init_states(self.params)
            state = initial_states[action]
            self.people = state.people
            self.alive = state.alive
            self.dead = state.dead
            self.accused = state.accused
            self.killer = state.killer
            self.cost_list = state.cost_list
            self.points = math.ceil(sum(self.cost_list) / 2) + 3
            self.step = 1

        else:
            if self.current_player() == MurderPlayer.KILLER:
                if action is None:
                    pass
                else:
                    self._kill_action(self.people[action])
            else:
                self._accuse_action(self.people[action])
            self.step += 1

    def n_actions(self) -> int:
        if self.step == 0:
            return len(get_init_states(self.params))
        else:
            return len(self._legal_actions(self.current_player()))

    def clone(self):
        cp = super().clone()
        return cp

    def is_terminal(self):
        if self.step > 0:
            people, victims, points, cost_list = KillerInterface.get_actions(ObservationForKiller.from_game_state(self))
            if victims is None or victims == []:
                return True
            elif self.killer in set(self.accused):
                return True
            else:
                return False
        else:
            return False

    def score(self) -> float:
        if not self.is_terminal():
            return 0
        else:
            return len(self.alive) / len(self.people)

    def returns(self):
        """Total reward for each player over the course of the game so far."""
        if not self.is_terminal():
            return [0, 0]
        else:
            score = self.score()
            return [-score, score]

    def __str__(self):
        """String for debug purposes. No particular semantics are required."""
        return f"m_grid={self.params.m_grid},n_grid={self.params.n_grid},n_people={self.params.n_people}," \
               f"people={self.people},alive={self.alive},accused={self.accused},killer={self.killer}," \
               f"cost_list={self.cost_list},points={self.points},step={self.step}"
