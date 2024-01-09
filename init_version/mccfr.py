from collections import defaultdict
import random
from init_version.game_core import GameModel
import numpy as np

def random_policy(cards):
    action=[]
    if cards&{0,1,2,3,4,5} != {}:
        action.append(random.sample(cards&{0,1,2,3,4,5},1)[0])
    if cards&{6,7,8,9,10,11} != {}:
        action.append(random.sample(cards&{6,7,8,9,10,11},1)[0])
    if cards&{12,13,14,15,16,17,18,19,20} != {}:
        action.append(random.sample(cards&{12,13,14,15,16,17,18,19,20},1)[0])
    return set(action)

class RandomAgent:
    def __init__(self, player_id):
        self.player_id = player_id

    def take_action(self, cards):
        return random_policy(cards)


class MCCFRAgent:
    def __init__(self, player_id):
        self.player_id = player_id
        self.regrets = defaultdict(float)
        self.strategy_sum = defaultdict(float)

    def get_strategy(self, information_state):
        normalizing_sum = sum([max(self.regrets[(information_state, a)], 0) for a in range(21)])
        if normalizing_sum == 0:
            return [1/21] * 21
        return [max(self.regrets[(information_state, a)], 0) / normalizing_sum for a in range(21)]

    def traverse_tree(self, game_state, reach_prob):
        if game_state.is_terminal():
            return game_state.returns()[self.player_id - 1]

        player = game_state.next_player(game_state.step)
        information_state = str(game_state.information_state[player])

        strategy = self.get_strategy(information_state)
        action_probabilities = np.random.choice(range(21), p=strategy)
        expected_value = 0

        for action in game_state.cards:
            if action_probabilities[action] == 0: continue

            next_game_state = deepcopy(game_state)
            next_game_state.suggest(player, action)

            if player == self.player_id:
                regret = self.traverse_tree(next_game_state, reach_prob) - expected_value
                self.regrets[(information_state, action)] += regret
            else:
                expected_value += action_probabilities[action] * self.traverse_tree(next_game_state, reach_prob * action_probabilities[action])

        return expected_value

    def take_action(self, game_state):
        information_state = str(game_state.information_state[self.player_id])
        strategy = self.get_strategy(information_state)
        return np.argmax(strategy)

def play_game(agents):
    game = GameModel(len(agents))
    while game.state.is_terminal() is None:
        current_player = game.state.next_player(game.state.step)
        agent = agents[current_player - 1]
        action = agent.take_action(game.state)
        game.state.suggest(current_player, action)
        game.state.step += 1

    return game.state.is_terminal()

def compete(mccfr_agent, num_random_agents, n_games=1000):
    wins = 0

    for _ in range(n_games):
        agents = [mccfr_agent] + [RandomAgent(i + 2) for i in range(num_random_agents)]
        random.shuffle(agents)
        winner = play_game(agents)
        if isinstance(agents[winner - 1], MCCFRAgent):
            wins += 1

    return wins / n_games

# Example usage:
mccfr_agent = MCCFRAgent(1)
win_rate = compete(mccfr_agent, 2, n_games=1000)
print(f"MCCFR Agent win rate: {win_rate:.2%}")