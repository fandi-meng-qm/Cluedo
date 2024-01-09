from __future__ import annotations

import copy
import itertools
import math
import random
from typing import List, NamedTuple

import pyspiel

import numpy as np

import enum

# SUGGESTION_ACTION = 0
# BID_ACTION_OFFSET = 1

class CluedoParams:
    def __init__(self, n_players):
        self.n_players = n_players

_MAX_NUM_PLAYERS = 6
_MIN_NUM_PLAYERS = 2
_GAME_TYPE = pyspiel.GameType(
    short_name="python_cluedo",
    long_name="Python Cluedo",
    dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
    chance_mode=pyspiel.GameType.ChanceMode.EXPLICIT_STOCHASTIC,
    information=pyspiel.GameType.Information.IMPERFECT_INFORMATION,
    utility=pyspiel.GameType.Utility.ZERO_SUM,
    reward_model=pyspiel.GameType.RewardModel.TERMINAL,
    max_num_players=_MAX_NUM_PLAYERS,
    min_num_players=_MIN_NUM_PLAYERS,
    provides_information_state_string=True,
    provides_information_state_tensor=True,
    provides_observation_string=False,
    provides_observation_tensor=True)

class CluedoGame(pyspiel.Game):
    def __init__(self, params=None, game_params: CluedoParams = None) -> None:
        game_params = game_params or CluedoParams()
        self.game_params = game_params
        n=self.game_params.n_players
        n_actions = 6*6*9
        game_info = pyspiel.GameInfo(
            num_distinct_actions=n_actions,
            max_chance_outcomes=math.comb(n* 3, 3),
            num_players=n,
            min_utility=-1,
            max_utility=n-1,
            utility_sum=0.0,
            max_game_length=1000
        )
        super().__init__(_GAME_TYPE, game_info, params or dict())

    def new_initial_state(self, game_params=None) -> CluedoState:
        """Returns a state corresponding to the start of a game."""
        return CluedoState(self, self.game_params)

    def make_py_observer(self, iig_obs_type=None, params=None):
        """Returns an object used for observing game state."""
        return CluedoObserver(
            iig_obs_type or pyspiel.IIGObservationType(perfect_recall=False),
            self.game_params)

def random_choose(cards):
    card = random.sample(cards, 1)[0]
    return card

class CluedoState(pyspiel.State):
    """A python version of the state."""

    def __init__(self, game, params: CluedoParams = None):
        """Constructor; should only be called by Game.new_initial_state."""
        super().__init__(game)
        self.params = params
        self.players = list(range(self.params.n_players))
        self.cards = set()
        self.cards_dice = dict()
        self.information_state = dict()
        for i in range(self.params.n_players+1):
            self.information_state[i] = np.zeros((21,self.params.n_players+1))
        self.accusation = dict()
        self.dice_step = 0
        self.suggestion_step = 0
        self._curr_player = 0
        self._winner = -1
        self._loser = -1
        self.suspects = {0, 1, 2, 3, 4, 5}
        self.weapons = {6, 7, 8, 9, 10, 11}
        self.rooms = {12, 13, 14, 15, 16, 17, 18, 19, 20}
        self.init_actions = [set(item) for item in list(itertools.product(self.suspects, self.weapons, self.rooms))]
        self.history = list()
        self.entropy = float()


    def current_player(self):
        """Returns id of the next player to move, or TERMINAL if game is over."""
        if self.is_terminal():
            return pyspiel.PlayerId.TERMINAL
        elif self.dice_step < self.params.n_players+1:
            return pyspiel.PlayerId.CHANCE
        else:
            return self._curr_player

    def get_state_entropy(self):
        unknown_cards = copy.deepcopy(self.cards)
        for i in range(self.params.n_players):
            for card in range(21):
                if self.information_state[self._curr_player][card][i] == 1:
                    unknown_cards.remove(card)
        if np.sum(self.information_state[self._curr_player][0:6,self.params.n_players]) == 1:
            suspect_entropy = 0
        else:
            suspect_entropy = math.log2(len(unknown_cards & self.suspects))
        if np.sum(self.information_state[self._curr_player][6:12,self.params.n_players]) == 1:
            weapon_entropy = 0
        else:
            weapon_entropy = math.log2(len(unknown_cards & self.weapons))
        if np.sum(self.information_state[self._curr_player][12:21,self.params.n_players]) == 1:
            room_entropy = 0
        else:
            room_entropy = math.log2(len(unknown_cards & self.rooms))

        self.entropy = -suspect_entropy - weapon_entropy - room_entropy


    def winner(self):
        """Returns the id of the winner if the bid originator has won.
            -1 otherwise.
            """
        return self._winner

    # def loser(self):
    #     """Returns the id of the loser if the bid originator has lost.
    #     -1 otherwise.
    #     """
    #     return self._loser

    def _legal_actions(self, player) -> List[set] or None:
        """Returns a list of legal actions"""
        # check this is not the chance player, for some reason that is handled separately
        assert player >= 0
        self.suspects = {0, 1, 2, 3, 4, 5}&self.cards
        self.weapons = {6, 7, 8, 9, 10, 11}&self.cards
        self.rooms = {12, 13, 14, 15, 16, 17, 18, 19, 20}&self.cards
        actions_sets= [set(item) for item in list(itertools.product(self.suspects, self.weapons, self.rooms))]
        actions = []
        for i in range(len(self.init_actions)):
            if self.init_actions[i] in actions_sets:
                actions.append(i)
        # print(actions)
        return actions

    def chance_outcomes(self):
        assert self.is_chance_node()
        if self.dice_step == 0:
            num_possibilities = len(self.suspects)*len(self.weapons)*len(self.rooms)
            probability = 1.0 / num_possibilities
            chance_outcomes = [(i, probability) for i in range(num_possibilities)]
            return chance_outcomes
        else:
            num_possibilities = math.comb(self.params.n_players * 3+3-3*self.dice_step, 3)
            probability = 1.0 / num_possibilities
            chance_outcomes = [(i, probability) for i in range(num_possibilities)]
            return chance_outcomes

    def next_player(self, player) ->int:
        if player + 1 >= self.params.n_players:
            next_player = 0
        else:
            next_player = player + 1
        return next_player

    def suggest(self, player, action):
        curr_player = self.next_player(player)
        action_set = self.init_actions[action]
        while action_set & self.cards_dice[curr_player] == set():
            if curr_player == player:
                self.history.append([player, action, action_set, -1, 0])
                for i in action_set:
                    self.information_state[curr_player][i][self.params.n_players] = 1
                break
            curr_player = self.next_player(curr_player)

        if curr_player != player:
            # print(action & self.cards_dice[curr_player])
            show_card = random_choose(action_set & self.cards_dice[curr_player])
            self.history.append([player, action, action_set, curr_player, 1])
            # print('player'+str(curr_player)+'show card'+str(show_card)+' to '+ str(player))
            self.information_state[player][show_card][curr_player] = 1
        else:
            self.history.append([player, action, action_set, -1, 0])
            new_answer = action_set - (action_set & self.cards_dice[curr_player])
            if new_answer != {}:
                for i in new_answer:
                    self.information_state[player][i][self.params.n_players] = 1

    def if_accuse(self, player):
        answer = []
        for i in range(21):
            if self.information_state[player][i][self.params.n_players] == 1:
                answer.append(i)
        if len(answer) == 3:
            self.accuse(player, answer)
        else:
            pass

    def accuse(self, player, action):
        # print('player'+str(player)+'accuse'+str(action))
        self.accusation[player] = set(action)
        self._winner = player

    def _apply_action(self, action: int) -> None:

        if self.is_chance_node():
            if self.dice_step == 0:
                self.cards_dice[self.params.n_players] = self.init_actions[action]
                self.cards = self.cards|self.init_actions[action]
                for card in self.cards_dice[self.params.n_players]:
                    self.information_state[self.params.n_players][card][self.params.n_players] = 1
            else:
                cards_left = set(range(21)) - self.cards
                combinations = itertools.combinations(cards_left, 3)
                dice_options = []
                for combo in combinations:
                    dice_options.append(set(combo))
                self.cards_dice[self.dice_step-1] = dice_options[action]
                self.cards = self.cards|dice_options[action]
                for card in self.cards_dice[self.dice_step-1]:
                    self.information_state[self.params.n_players][card][self.dice_step-1] = 1
                    self.information_state[self.dice_step-1][card][self.dice_step-1] = 1
            self.dice_step += 1
        else:
            self.suggest(self._curr_player, action)
            self.suggestion_step += 1
            self.if_accuse(self._curr_player)
            self._curr_player = self.next_player(self._curr_player)


    def clone(self):
        cp = super().clone()
        return cp

    def is_terminal(self):
        """Returns True if the game is over."""
        return self._winner >= 0


    def returns(self):
        """Total reward for each player over the course of the game so far."""
        if not self.is_terminal():
            return [0]*self.params.n_players
        else:
            score = [-1]*self.params.n_players
            score[self._winner] = self.params.n_players-1
            return score

    def __str__(self):
        """String for debug purposes. No particular semantics are required."""
        return f"card_dice={self.cards_dice}, player={self._curr_player}," \
               f"information_state={self.information_state[self._curr_player]}\"" \
               f"public_history={self.history}"


class CluedoObserver:
    """Observer, conforming to the PyObserver interface (see observation.py)."""

    def __init__(self, iig, params):
        """Initializes an empty observation tensor."""
        if params == None:
            raise ValueError(f"Observation needs params for setup; passed {params}")
        self.params = params
        size = 21*(params.n_players+1)
        shape = (21, params.n_players+1)
        self.tensor = np.zeros(size, np.float32)
        self.dict = {"observation": np.reshape(self.tensor, shape)}

    def set_from(self, state: CluedoState, player: int):
        """Updates `tensor` and `dict` to reflect `state` from PoV of `player`."""
        self.dict["observation"] = state.information_state[state._curr_player]

    def string_from(self, state: CluedoState, player: int):
        """Observation of `state` from the PoV of `player`, as a string."""
        return f"information_state{state.information_state[state._curr_player]}"


pyspiel.register_game(_GAME_TYPE, CluedoGame)