from typing import List
import matplotlib.pyplot as plt
import numpy as np
from cluedo_game import CluedoGame, CluedoParams
from ismcts_test import test_simulations


def plot_data(data: List[List[float]], title: str) -> None:
    for dat in data:
        plt.plot(dat)
    plt.xlabel("number of itertions")
    plt.ylabel("score")
    plt.title(title)
    plt.show()


def plot_series_with_shaded_error_bars(data: List[List[float]], title: str, series_label: str = 'series',
                                       show: bool = True, x_label: str = 'max_simulations', y_label: str = 'score') -> None:

    data = np.array(data)
    n = len(data)
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0) / np.sqrt(n)
    # plt.plot(mean, label=series_label)
    x_axis = np.arange(2, 2 + len(mean))
    plt.plot(x_axis, mean, label=series_label)
    plt.fill_between(x_axis, mean - std, mean + std, alpha=0.5)
    # plt.fill_between(range(len(mean)), mean - std, mean + std, alpha=0.5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.title(title)
    if show: plt.show()


def run_error_bars():
    data_3 = []
    for i in range(5):
        return_list3 = test_simulations(5)
        data_3.append(return_list3)
    plot_series_with_shaded_error_bars(data_3, "ISMCTS on Cluedo",
                                       series_label="ISMCTS", show=True)


if __name__ == "__main__":
    params = CluedoParams(3)
    game = CluedoGame(game_params=params)
    run_error_bars()
