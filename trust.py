import random
import string
import sys
from datetime import datetime
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print('Enter the command: pip install matplotlib')
    sys.exit()

population = {}
punishment = ''
temptation = ''
sucker = ''
reward = ''
rounds = ''
cycles = ''
losers = ''
mistake_prob = ''


class Copycat():
    name = 'Copycat'
    first_move = 'cooperate'

    @staticmethod
    def next_move(i, a, b):
        return b[i - 1]


class Copykitten():
    name = 'Copykitten'
    first_move = 'cooperate'

    @staticmethod
    def next_move(i, a, b):
        if b[i - 1] == 'cheat':
            if i > 0:
                if b[i - 1] == b[i - 2]:
                    move = 'cheat'
                else:
                    move = 'cooperate'
            else:
                move = 'cooperate'
        else:
            move = 'cooperate'
        return move


class Cheater():
    name = 'Cheater'
    first_move = 'cheat'

    @staticmethod
    def next_move(i, a, b):
        return 'cheat'


class Cooperator():
    name = 'Cooperator'
    first_move = 'cooperate'

    @staticmethod
    def next_move(i, a, b):
        return 'cooperate'


class Grudger():
    name = 'Grudger'
    first_move = 'cooperate'

    @staticmethod
    def next_move(i, a, b):
        if 'cheat' in b:
            move = 'cheat'
        else:
            move = 'cooperate'
        return move


class Detective():
    name = 'Detective'
    first_move = 'cooperate'

    @staticmethod
    def next_move(i, a, b):
        if i <= 3:
            if i == 1:
                move = 'cheat'
            else:
                move = 'cooperate'
        if 'cheat' in b:
            move = b[i - 1]
        else:
            move = 'cheat'
        return move


class Simpleton():
    name = 'Simpleton'
    first_move = 'cooperate'

    @staticmethod
    def next_move(i, a, b):
        if b[i - 1] == 'cooperate':
            move = a[i - 1]
        else:
            if a[i - 1] == 'cooperate':
                move = 'cheat'
            elif a[i - 1] == 'cheat':
                move = 'cooperate'
        return move


class Random():
    name = 'Random'
    first_move = random.choice(('cooperate', 'cheat'))

    @staticmethod
    def next_move(i, a, b):
        return random.choice(('cooperate', 'cheat'))


class Game:
    PLAYERS = (
        Copycat(),
        Copykitten(),
        Cheater(),
        Cooperator(),
        Grudger(),
        Detective(),
        Simpleton(),
        Random(),
    )

    def __init__(self, player_a, player_b):
        self.player_a = player_a
        self.player_b = player_b

    def play(self):
        wrong_moves_a = self.mistakes()
        wrong_moves_b = self.mistakes()
        moves_a, moves_b = [], []
        payoffs_a, payoffs_b = [], []
        for i in range(rounds):
            if i > 0:
                move_a = self.player_a.next_move(i, moves_a, moves_b)
                move_b = self.player_b.next_move(i, moves_b, moves_a)
                if i in wrong_moves_a:
                    move_a = self.replace_move(move_a)
                if i in wrong_moves_b:
                    move_b = self.replace_move(move_b)
            else:
                move_a = self.player_a.first_move
                move_b = self.player_b.first_move
            moves_a.append(move_a)
            moves_b.append(move_b)
            payoff_1, payoff_2 = self.get_payoffs(move_a, move_b)
            payoffs_a.append(payoff_1)
            payoffs_b.append(payoff_2)
        return sum(payoffs_a), sum(payoffs_b)

    @staticmethod
    def get_payoffs(move_a, move_b):
        if move_a == 'cheat' and move_b == 'cheat':
            return punishment, punishment
        elif move_a == 'cooperate' and move_b == 'cheat':
            return sucker, temptation
        elif move_a == 'cheat' and move_b == 'cooperate':
            return temptation, sucker
        elif move_a == 'cooperate' and move_b == 'cooperate':
            return reward, reward

    @staticmethod
    def mistakes():
        true_mistake_prob = (rounds - 2) * mistake_prob / rounds
        number_of_mistakes = round((rounds - 2) * true_mistake_prob / 100)
        wrong_moves = []
        if number_of_mistakes > 0:
            for i in range(number_of_mistakes):
                while True:
                    x = random.randint(1, rounds - 1)
                    if i > 0:
                        if x in wrong_moves:
                            wrong_moves.append(random.randint(1, rounds - 1))
                            break
                        else:
                            continue
                    else:
                        wrong_moves.append(random.randint(1, rounds - 1))
                        break
        return wrong_moves

    @staticmethod
    def replace_move(move):
        if move == 'cooperate':
            return 'cheat'
        elif move == 'cheat':
            return 'cooperate'


class Tournament:
    def play(self):
        result = {}
        for i in range(len(Game.PLAYERS)):
            player_a = Game.PLAYERS[i]
            for a in range(population[player_a.name]):
                for j in range(len(Game.PLAYERS)):
                    player_b = Game.PLAYERS[j]
                    for b in range(population[player_b.name]):
                        if i < j and a == b:
                            continue
                        elif i == j and a == b:
                            continue
                        else:
                            score_a, score_b = Game(player_a, player_b).play()
                            n = f'{player_a.name}{a + 1}'
                            if n in result:
                                result[n] += score_a
                            else:
                                result[n] = 0
                                result[n] += score_a
                            n = f'{player_b.name}{b + 1}'
                            if n in result:
                                result[n] += score_b
                            else:
                                result[n] = 0
                                result[n] += score_b
        self.evolution(result)

    @staticmethod
    def evolution(result):
        tuples = [(k, result[k]) for k in sorted(result, key=result.get, reverse=False)]
        for x in range(losers):
            loser = [i for i in tuples[x][0] if i not in string.digits]
            winner = [i for i in tuples[::-1][x][0] if i not in string.digits]
            population[''.join(loser)] -= 1
            population[''.join(winner)] += 1

"""
def general_plot(changes):
    for i in changes:
        plt.plot(changes[i], label=i)
    plt.legend(loc='upper left', borderaxespad=0.5)
    plt.title('Evolution')
    plt.xlabel('Cycles')
    plt.ylabel('Population')
    plt.show()
"""

def separate_plots(changes):
    coordinates = (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
    )
    fig, axs = plt.subplots(3, 3)
    x = 0
    for i in changes:
        axs[coordinates[x]].plot(changes[i])
        axs[coordinates[x]].set_title(i)
        x += 1
    for ax in axs.flat:
        ax.set(xlabel='Cycles', ylabel='Population')
    fig.delaxes(axs[2, 2])
    fig.tight_layout()
    fig.show()
    input()


def progress_bar(it, prefix='', size=60, out=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'='*x}{('·'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print('\n', flush=True, file=out)


def main():
    try:
        global population
        global punishment, sucker, reward, temptation
        global rounds, cycles, losers, mistake_prob
        print('Population')
        for i in range(len(Game.PLAYERS)):
            name = Game.PLAYERS[i].name
            population[name] = int(input(f'{name}: '))
        print('\nPayoffs')
        punishment = float(input('Punishment: '))
        temptation = float(input('Temptation: '))
        sucker = float(input('Sucker: '))
        reward = float(input('Reward: '))
        rounds = int(input('\nRounds: '))
        cycles = int(input('Cycles: '))
        losers = int(input('Losers per cycle: '))
        if losers < 1 or losers >= sum(population.values()):
            raise ValueError
        mistake_prob = float(input('Mistake probability: '))
        if mistake_prob < 0 or mistake_prob >= 100:
            raise ValueError
        print('')
        changes = {}
        start = datetime.now()
        for _ in progress_bar(range(cycles), 'Evolution: '):
            Tournament().play()
            for i in population:
                if i in changes:
                    changes[i].append(population[i])
                else:
                    changes[i] = [population[i]]
                    changes[i].append(population[i])
        print('Population after evolution')
        for i in population:
            print(f'{i}: {population[i]}')
        print('\nTime:', datetime.now() - start)
        separate_plots(changes)
    except ValueError:
        print('\nError: incorrect input')
        return


if __name__ == '__main__':
    main()
