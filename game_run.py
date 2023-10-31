from game_core import *
import random
from random_agent import random_policy
from gpt_agent import gpt_agent

def game_run(model):
    state = model.state
    # player = 1
    player = random.choice(state.players)
    while model.state.is_terminal() is None:
        if player < state.n_players:
            action = random_policy(state.cards)
        else:
            action = gpt_agent(state)
        print('player' + str(player) + 'suggests' + str(action))
        state.suggest(player, action)
        state.step += 1
        state.if_accuse(player)
        player = state.next_player(player)
    if model.state.is_terminal() is not None:
        print('step' + str(state.step) + " winner is " + str(model.state.is_terminal()))
        return model.state.is_terminal()


if __name__ == "__main__":
    game_run(GameModel(3))
