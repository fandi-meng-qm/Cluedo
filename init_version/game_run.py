from init_version.game_core import *
import random
from random_agent import random_policy


# def game_run(model):
#     state = model.state
#     # player = 1
#     player = random.choice(state.players)
#     while model.state.is_terminal() is None:
#         if player < state.n_players:
#             action = random_policy(state.cards)
#         else:
#             action = gpt_agent(state)
#         print('player' + str(player) + 'suggests' + str(action))
#         state.suggest(player, action)
#         state.step += 1
#         state.if_accuse(player)
#         player = state.next_player(player)
#     if model.state.is_terminal() is not None:
#         print('step' + str(state.step) + " winner is " + str(model.state.is_terminal()))
#         return model.state.is_terminal()

def game_run(model):
    state = model.state
    print('0,1,2,3,4,5 are murderer cards, 6,7,8,9,10,11 are weapon cards, left are room cards')
    print('The cards distribution is:')
    print('(PS: 0 means the envelope and 1 means player 1...)')
    print(state.cards_dice)
    # player = 1
    player = random.choice(state.players)
    while model.state.is_terminal() is None:
        action = random_policy(state.cards)

        print('player ' + str(player) + ' suggests' + str(action))
        state.suggest(player, action)
        state.step += 1
        state.if_accuse(player)
        player = state.next_player(player)
    if model.state.is_terminal() is not None:
        print('step' + str(state.step) + " winner is " + str(model.state.is_terminal()))
        return model.state.is_terminal()

if __name__ == "__main__":
    game_run(GameModel(3))
