from operator import methodcaller
from modules.analysis.tools import avg

import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.tools as tls
import numpy as np

class analysed_game: # subjective to the player being analysed
    def __init__(self, playerid, gameid, positions):
        self.playerid = playerid
        self.gameid = gameid
        self.positions = positions  # list(analysed_position)

    def move_numbers(self):
        return list(range(len(self.positions)))

    def graph_all(self):
        self.graph_rank_v_sd()
        self.graph_error_v_sd()
        self.graph_rank_v_percent()

    def graph_rank_v_sd(self):
        x = self.top_five_sds()
        y = self.ranks()

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_xlabel('top 5 std')
        ax.set_ylabel('move rank')
        fig.show()
        #plot_url = py.plot_mpl(fig, filename=self.playerid+'\\'+self.gameid+': Rank V SD')

    def graph_error_v_sd(self):
        x = self.top_five_sds()
        y = self.actual_errors()

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_xlabel('top 5 std')
        ax.set_ylabel('move error')
        fig.show()
        #plot_url = py.plot_mpl(fig, filename=self.playerid+'\\'+self.gameid+': Error V SD')

    def graph_rank_v_percent(self):
        x = self.percent_errors()
        y = self.ranks()

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_xlabel('percent error')
        ax.set_ylabel('move rank')
        fig.show()

    def rank_0_percent(self):
        return 100*sum(i.rank() == 0 for i in self.positions)/float(len(self.positions)+0.01)

    def rank_0_1030_percent(self):
        try:
            if len(self.positions[0:50]) > 10:
                return 100*sum((i.rank() == 0 or i.rank() == 1) for i in self.positions[0:50])/float(len(self.positions[0:50])+0.01)
            else:
                return 0
        except ValueError:
            return 0

    def rank_5more_percent(self):
        start = 20
        stop = 50
        try:
            if len(self.positions[start:]) > 10:
                return 100*sum((i.rank() > 5) for i in self.positions[start:])/float(len(self.positions[start:])+0.01)
            else:
                return 100
        except ValueError:
            return 100

    def error_difs(self):
        return list(i.error_dif() for i in self.positions)

    def avg_error_dif(self):
        return avg(self.error_difs())

    def top_five_sds(self):
        return list(i.top_five_sd() for i in self.positions)

    def expected_errors(self):
        return list(i.expected_error() for i in self.positions)

    def ranks(self):
        return list(i.rank() for i in self.positions)

    def avg_rank(self):
        return avg(self.ranks())

    def actual_errors(self):
        return list(i.actual_error() for i in self.positions)

    def avg_error(self):
        return avg(self.errors())

    def percent_errors(self):
        return list(i.percent_error() for i in self.positions)

    def accuracy_percentage(self, cp):
        return 100*sum(i.accuracy_less_than(cp) for i in self.positions)/float(len(self.positions)+0.01)

class analysed_position:
    def __init__(self, played, legals):
        self.played = played # analysed_move
        self.legals = sorted(legals, key=methodcaller('sort_val'))  # list(analysed_move)
        self.best_eval = bounded_eval(self.legals[0].sort_val())

    def expected_error(self):
        return avg(list(abs(self.best_eval - bounded_eval(i.sort_val())) for i in self.legals))

    def top_five_sd(self):
        return np.std(list(bounded_eval(i.sort_val()) for i in self.legals[:5])).item()

    def actual_error(self):
        return abs(self.best_eval - bounded_eval(self.played.sort_val()))

    def accuracy_less_than(self, cp):
        return self.actual_error() < cp

    def error_dif(self):
        return self.expected_error() - self.actual_error()

    def rank(self):
        return self.legals.index(self.played)

    def percent_error(self):
        try:
            return 100*(self.actual_error()/float(self.best_eval))
        except ZeroDivisionError:
            return 0

class analysed_move:
    def __init__(self, move, evaluation):
        self.move = move
        self.evaluation = evaluation

    def __str__(self):
        return str(self.move) + ': ' + str(self.evaluation)

    def sign(self, val):
        if val <= 0:
            return -1
        else:
            return 1

    def sort_val(self):
        if self.evaluation.cp is not None:
            return self.evaluation.cp
        elif self.evaluation.mate is not None:
            return self.sign(self.evaluation.mate) * (abs(100 + self.evaluation.mate)) * 10000
        else:
            return 0

def bounded_eval(e):
    return min(1000, max(-1000, e))