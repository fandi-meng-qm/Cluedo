from dataclasses import dataclass
from typing import NamedTuple, Set, Tuple, List, Dict
import random
import numpy as np


def random_choose(cards):
    card = random.sample(cards, 1)[0]
    return card


@dataclass
class GameState:
    n_players: int
    players: List[int]
    cards_dice: Dict[int, set]
    cards: Set[int]
    accusation: Dict[int, set]
    information_state: Dict[int, dict]
    step: int

    def is_terminal(self):
        for i in range(1, self.n_players + 1):
            if self.accusation[i] == self.cards_dice[0]:
                return i
        return None

    def next_player(self, player):
        if player + 1 > self.n_players:
            next_player = (player + 1) % self.n_players
        else:
            next_player = player + 1
        return next_player

    # Currently, the information sets of other players are not updated after players raise suggestions
    def suggest(self, player, action):
        curr_player = self.next_player(player)
        while action & self.cards_dice[curr_player] == set():
            if curr_player == player:
                for i in action:
                    self.information_state[curr_player][i][0] = 1
                break
            curr_player = self.next_player(curr_player)
        if curr_player != player:
            # print(action & self.cards_dice[curr_player])
            show_card = random_choose(action & self.cards_dice[curr_player])
            print('player'+str(curr_player)+'show card'+str(show_card)+' to '+ str(player))
            self.information_state[player][show_card][curr_player] = 1
        else:
            new_answer = action - (action & self.cards_dice[curr_player])
            if new_answer != {}:
                for i in new_answer:
                    self.information_state[player][i][0] = 1

    def if_accuse(self, player):
        answer = []
        for i in self.information_state[player].keys():
            if self.information_state[player][i][0] == 1:
                answer.append(i)
        if len(answer) == 3:
            self.accuse(player, answer)
        else:
            pass

    def accuse(self, player, action):
        print('player'+str(player)+'accuse'+str(action))
        self.accusation[player] = set(action)


# Distribute cards, first draw three cards and put them in envelopes, then each player randomly divides them into
# three cards
def chance_outcome(n_players, cards_dice=None):
    if cards_dice is None:
        cards_dice = {}
    cards_dice[0] = {random.randint(0, 5), random.randint(6, 11), random.randint(12, 20)}
    cards_left = set(list(range(21))) - cards_dice[0]
    for i in range(1, n_players + 1):
        cards_dice[i] = set(random.sample(cards_left, 3))
        cards_left -= cards_dice[i]
    # print(cards_dice,cards_left)
    return cards_dice, cards_left


class GameModel:
    def __init__(self, n_players: int):
        self.n_players = n_players
        cards_dice, cards_left = chance_outcome(n_players)
        information_state = {}
        accusation = {}
        for i in range(1, n_players + 1):
            information_state[i] = {}
            accusation[i] = {}
            for j in set(list(range(21))) - cards_left:
                information_state[i][j] = [0] * (n_players + 1)
                if j in cards_dice[i]:
                    information_state[i][j][i] = 1
        # initial state
        self.state = GameState(n_players=n_players, players=list(range(1, n_players + 1)),
                               cards_dice=cards_dice, cards=set(list(range(21))) - cards_left, accusation=accusation,
                               information_state=information_state, step=0)
