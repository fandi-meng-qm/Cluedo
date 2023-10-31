import random


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
