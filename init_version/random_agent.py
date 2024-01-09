

# Those who have been suggested will still be suggested
import random


def random_policy(cards):
    action=[]
    if cards&{0,1,2,3,4,5} != {}:
        action.append(random.sample(cards&{0,1,2,3,4,5},1)[0])
    if cards&{6,7,8,9,10,11} != {}:
        action.append(random.sample(cards&{6,7,8,9,10,11},1)[0])
    if cards&{12,13,14,15,16,17,18,19,20} != {}:
        action.append(random.sample(cards&{12,13,14,15,16,17,18,19,20},1)[0])
    return set(action)
