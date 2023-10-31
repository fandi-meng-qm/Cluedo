from game_run import game_run
from game_core import GameModel


def win_rate(n_player, n):
    win_list = n_player * [0]
    for _ in range(n):
        winner = game_run(GameModel(n_player))
        win_list[winner - 1] += 1
    print([a/n for a in win_list])
    return [a/n for a in win_list]


win_rate(3, 20)
