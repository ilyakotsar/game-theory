import random
import string
import sys
from datetime import datetime
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError as error:
    print(error)
    print('Enter the command: pip install matplotlib')
    sys.exit()


MOVES = ('cooperate', 'cheat')


class Copycat():
    name = 'Copycat'
    first_move = 'cooperate'

    @staticmethod
    def next_move(*args):
        i, other_moves = args[0], args[2]
        return other_moves[i - 1]


class Copykitten():
    name = 'Copykitten'
    first_move = 'cooperate'

    @staticmethod
    def next_move(*args):
        i, other_moves = args[0], args[2]
        if other_moves[i - 1] == 'cheat':
            if i > 0:
                if other_moves[i - 1] == other_moves[i - 2]:
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
    def next_move(*args):
        return 'cheat'


class Cooperator():
    name = 'Cooperator'
    first_move = 'cooperate'

    @staticmethod
    def next_move(*args):
        return 'cooperate'


class Grudger():
    name = 'Grudger'
    first_move = 'cooperate'

    @staticmethod
    def next_move(*args):
        other_moves = args[2]
        if 'cheat' in other_moves:
            move = 'cheat'
        else:
            move = 'cooperate'
        return move


class Detective():
    name = 'Detective'
    first_move = 'cooperate'

    @staticmethod
    def next_move(*args):
        i, other_moves = args[0], args[2]
        if i <= 3:
            if i == 1:
                move = 'cheat'
            else:
                move = 'cooperate'
        if 'cheat' in other_moves:
            move = other_moves[i - 1]
        else:
            move = 'cheat'
        return move


class Simpleton():
    name = 'Simpleton'
    first_move = 'cooperate'

    @staticmethod
    def next_move(*args):
        i, my_moves, other_moves = args[0], args[1], args[2]
        if other_moves[i - 1] == 'cooperate':
            move = my_moves[i - 1]
        else:
            if my_moves[i - 1] == 'cooperate':
                move = 'cheat'
            elif my_moves[i - 1] == 'cheat':
                move = 'cooperate'
        return move


class Random():
    name = 'Random'
    first_move = random.choice(MOVES)

    @staticmethod
    def next_move(*args):
        return random.choice(MOVES)


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

    def play(self, pun, sucker, reward, tempt, rounds, mist_prob):
        wrong_moves_a = Game.mistakes(rounds, mist_prob)
        wrong_moves_b = Game.mistakes(rounds, mist_prob)
        moves_a, moves_b = [], []
        payoffs_a, payoffs_b = [], []
        for i in range(rounds):
            if i > 0:
                move_a = self.player_a.next_move(i, moves_a, moves_b)
                move_b = self.player_b.next_move(i, moves_b, moves_a)
                if i in wrong_moves_a:
                    move_a = MOVES[::-1][MOVES.index(move_a)]
                if i in wrong_moves_b:
                    move_b = MOVES[::-1][MOVES.index(move_b)]
            else:
                move_a = self.player_a.first_move
                move_b = self.player_b.first_move
            moves_a.append(move_a)
            moves_b.append(move_b)
            payoff_1, payoff_2 = Game.get_payoffs(move_a, move_b, pun, sucker, reward, tempt)
            payoffs_a.append(payoff_1)
            payoffs_b.append(payoff_2)
        return sum(payoffs_a), sum(payoffs_b)

    @staticmethod
    def get_payoffs(move_a, move_b, pun, sucker, reward, tempt):
        if move_a == 'cheat' and move_b == 'cheat':
            payoff_a, payoff_b = pun, pun
        elif move_a == 'cooperate' and move_b == 'cheat':
            payoff_a, payoff_b = sucker, tempt
        elif move_a == 'cheat' and move_b == 'cooperate':
            payoff_a, payoff_b = tempt, sucker
        elif move_a == 'cooperate' and move_b == 'cooperate':
            payoff_a, payoff_b = reward, reward
        return payoff_a, payoff_b

    @staticmethod
    def mistakes(rounds, mist_prob):
        true_mist_prob = (rounds - 2) * mist_prob / rounds
        number_of_mistakes = round((rounds - 2) * true_mist_prob / 100)
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


class Tournament:
    @staticmethod
    def play(population, pun, sucker, reward, tempt, rounds, losers, mist_prob):
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
                            score_a, score_b = Game(player_a, player_b).play(pun, sucker, reward, tempt, rounds, mist_prob)
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
        # evolution
        tuples = [(k, result[k]) for k in sorted(result, key=result.get, reverse=False)]
        for x in range(losers):
            loser = [i for i in tuples[x][0] if i not in string.digits]
            winner = [i for i in tuples[::-1][x][0] if i not in string.digits]
            population[''.join(loser)] -= 1
            population[''.join(winner)] += 1


def show_graph(changes):
    for i in changes:
        plt.plot(changes[i], label=i)
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
    plt.title('Evolution')
    plt.xlabel('Cycles')
    plt.ylabel('Population')
    plt.grid()
    plt.show()


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
        print('Population')
        population = {}
        population[Game.PLAYERS[0].name] = int(input('Copycat: '))
        population[Game.PLAYERS[1].name] = int(input('Copykitten: '))
        population[Game.PLAYERS[2].name] = int(input('Cheater: '))
        population[Game.PLAYERS[3].name] = int(input('Cooperator: '))
        population[Game.PLAYERS[4].name] = int(input('Grudger: '))
        population[Game.PLAYERS[5].name] = int(input('Detective: '))
        population[Game.PLAYERS[6].name] = int(input('Simpleton: '))
        population[Game.PLAYERS[7].name] = int(input('Random: '))
        print('\nPayoffs')
        pun = float(input('Punishment: '))
        sucker = float(input('Sucker: '))
        reward = float(input('Reward: '))
        tempt = float(input('Temptation: '))
        rounds = int(input('\nRounds: '))
        cycles = int(input('Cycles: '))
        losers = int(input('Losers per cycle: '))
        if losers < 1 or losers >= sum(population.values()):
            print('Error: invalid input')
            return
        mist_prob = float(input('Mistake probability: '))
        if mist_prob < 0 or mist_prob >= 100:
            print('Error: invalid input')
            return
        print('')
        changes = {}
        start = datetime.now()
        for _ in progress_bar(range(cycles), 'Evolution: '):
            Tournament().play(population, pun, sucker, reward, tempt, rounds, losers, mist_prob)
            for i in population:
                if i in changes:
                    changes[i].append(population[i])
                else:
                    changes[i] = []
                    changes[i].append(population[i])
        print('Population after evolution')
        for i in population:
            print(f'{i}: {population[i]}')
        print('\nTime:', datetime.now() - start)
        show_graph(changes)
    except ValueError as error:
        print(error)
        return


if __name__ == '__main__':
    main()
