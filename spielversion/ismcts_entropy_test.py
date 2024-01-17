import random
import re
from open_spiel.python import rl_environment
import ismcts_entropy
import ismcts
from open_spiel.python.algorithms import mcts
from cluedo_game import CluedoGame, CluedoParams
import numpy as np
from open_spiel.python import rl_agent
import matplotlib.pyplot as plt


params = CluedoParams(3)
game = CluedoGame(game_params=params)

def deserialize_state(observations):
    state = game.new_initial_state()
    history = observations.split("[State]\nhistory=")[1].split("\n")[0]
    print(history)
    history_list = [int(i) for i in re.split(',|:', history)]
    # history to state
    player_list = history_list[::2]
    action_list = history_list[1::2]
    for i in range(len(player_list)):
        state=state.child(action_list[i])
    return game, state

class RandomAgent(rl_agent.AbstractAgent):
    def __init__(self, player_id, num_actions, bot):
        assert num_actions > 0
        self._player_id = player_id
        self._num_actions = num_actions
        self._bot = bot

    def step(self, time_step, is_evaluation=False):
        # If it is the end of the episode, don't select an action.
        if time_step.last():
            return

        assert "serialized_state" in time_step.observations

        # print(time_step.observations["serialized_state"])
        _, state = deserialize_state(time_step.observations["serialized_state"])
        legal_actions = time_step.observations["legal_actions"]
        probs = np.zeros(self._num_actions)
        # print(legal_actions)
        action = random.choice(legal_actions[self._player_id])
        # print(state.init_actions[action])
        probs[action] = 1.0

        return rl_agent.StepOutput(action=action, probs=probs)

class MCTSAgent(rl_agent.AbstractAgent):
  """MCTS agent class.

  Important note: this agent requires the environment to provide the full state
  in its TimeStep objects. Hence, the environment must be created with the
  use_full_state flag set to True, and the state must be serializable.
  """

  def __init__(self, player_id, num_actions, mcts_bot, name="mcts_agent"):
    assert num_actions > 0
    self._player_id = player_id
    self._mcts_bot = mcts_bot
    self._num_actions = num_actions

  def step(self, time_step, is_evaluation=False):
    # If it is the end of the episode, don't select an action.
    if time_step.last():
      return

    assert "serialized_state" in time_step.observations

    # print(time_step.observations["serialized_state"])
    _, state = deserialize_state(time_step.observations["serialized_state"])
    # Call the MCTS bot's step to get the action.
    probs = np.zeros(self._num_actions)
    action = self._mcts_bot.step(state)
    print(state.history)
    probs[action] = 1.0

    return rl_agent.StepOutput(action=action, probs=probs)


def test(n):
    env = rl_environment.Environment(game, include_full_state=True)
    num_players = env.num_players
    num_actions = env.action_spec()["num_actions"]
    # Create the MCTS bot. Both agents can share the same bot in this case since
    # there is no state kept between searches. See mcts.py for more info about
    # the arguments.
    ismcts_bot = ismcts_entropy.ISMCTSBot(
        game=env.game,
        uct_c=5,
        max_simulations=n,
        evaluator=mcts.RandomRolloutEvaluator())

    ismcts_bot2 = ismcts.ISMCTSBot(
        game=env.game,
        uct_c=5,
        max_simulations=n,
        evaluator=mcts.RandomRolloutEvaluator())

    agents = [
        MCTSAgent(
            player_id=0, num_actions=num_actions, mcts_bot=ismcts_bot),
        # RandomAgent(
        # player_id=1, num_actions=num_actions, bot=None),
        #
        # RandomAgent(
        #     player_id=2, num_actions=num_actions, bot=None)
        MCTSAgent(
            player_id=0, num_actions=num_actions, mcts_bot=ismcts_bot2),
        MCTSAgent(
            player_id=0, num_actions=num_actions, mcts_bot=ismcts_bot2)
    ]

    time_step = env.reset()
    while not time_step.last():
        # and time_step.observations["current_player"] is not:
      player_id = time_step.observations["current_player"]
      # print(player_id)
      agent_output = agents[player_id].step(time_step)
      # print(agent_output.action)
      time_step = env.step([agent_output.action])
      # print(time_step)
    # print(time_step.rewards)
    for agent in agents:
      agent.step(time_step)
    return time_step.rewards

def test_ismcts(n):
    count = 0
    for i in range(n):
        result= test()
        if result[0]==2:
            count +=1
    print(f"win rate of ismcts agent in 3-player game is {count/n}")


def test_simulations(n):
    return_list = []
    for i in range(2,n):
        if test(i)[0] == 2:
            return_list.append(1)
        else:
            return_list.append(0)
    return return_list
# test_ismcts(10)

def test_win_rate(n):
    data = []
    for i in range(10):
        return_list3 = test_simulations(n)
        data.append(return_list3)
    mean = np.mean(data, axis=0)
    x_axis = np.arange(2, 2 + len(mean))
    plt.plot(x_axis, mean)
    plt.xlabel('max_simulations')
    plt.ylabel('win_rate')
    # plt.legend()
    plt.title('ISMCTS with entropy on Cluedo')
    plt.show()

# cProfiler = cProfile.Profile()
# cProfiler.run('test_win_rate(6)')
# cProfiler.print_stats()

test_win_rate(12)
# win rate 50%