import json
import random
from abc import ABC, abstractmethod
from datetime import datetime


class Player(ABC):
    MOVES = {
        'cooperate': 1,
        'cheat': 2,
    }

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        return random.choice(list(Player.MOVES.values()))


class Copycat(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        if index > 0:
            move = enemy_moves[len(enemy_moves) - 2]
        else:
            move = self.MOVES['cooperate']
        return move


class Copykitten(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        if index > 0:
            move = enemy_moves[len(enemy_moves) - 2]
        else:
            move = self.MOVES['cooperate']
        return move


class Cheater(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        return self.MOVES['cheat']


class Cooperator(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        return self.MOVES['cooperate']


class Grudger(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        if index > 0:
            if self.MOVES['cheat'] in enemy_moves:
                move = self.MOVES['cheat']
            else:
                move = self.MOVES['cooperate']
        else:
            move = self.MOVES['cooperate']
        return move


class Detective(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        if index > 0:
            if index <= 3:
                if index == 1:
                    move = self.MOVES['cheat']
                else:
                    move = self.MOVES['cooperate']
            if self.MOVES['cheat'] in enemy_moves:
                move = enemy_moves[index - 1]
            else:
                move = self.MOVES['cheat']
        else:
            move = self.MOVES['cooperate']
        return move


class Simpleton(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        if index > 0:
            if enemy_moves[index - 1] == self.MOVES['cooperate']:
                move = my_moves[index - 1]
            else:
                if my_moves[index - 1] == self.MOVES['cooperate']:
                    move = self.MOVES['cheat']
                elif my_moves[index - 1] == self.MOVES['cheat']:
                    move = self.MOVES['cooperate']
        else:
            move = self.MOVES['cooperate']
        return move


class Random(Player):
    def make_move(self, index: int, my_moves: list, enemy_moves: list) -> int:
        return random.choice(list(Player.MOVES.values()))


class Game:
    def __init__(self, player_a: Player, player_b: Player, settings: dict):
        self.player_a = player_a
        self.player_b = player_b
        self.settings = settings

    MOVES = Player.MOVES

    def play(self) -> tuple:
        moves_a, moves_b = [], []
        payoffs_a, payoffs_b = [], []
        for i in range(self.settings['game_rounds']):
            move_a = self.player_a.make_move(i, moves_a, moves_b)
            move_b = self.player_b.make_move(i, moves_b, moves_a)
            move_a = self.replace_move(move_a)
            move_b = self.replace_move(move_b)
            moves_a.append(move_a)
            moves_b.append(move_b)
            payoff_a, payoff_b = self.get_payoffs(move_a, move_b)
            payoffs_a.append(payoff_a)
            payoffs_b.append(payoff_b)
        return sum(payoffs_a), sum(payoffs_b)

    def get_payoffs(self, move_a: int, move_b: int) -> tuple:
        cooperate = self.MOVES['cooperate']
        cheat = self.MOVES['cheat']
        punishment = self.settings['payoffs']['punishment']
        sucker = self.settings['payoffs']['sucker']
        temptation = self.settings['payoffs']['temptation']
        reward = self.settings['payoffs']['reward']
        if move_a == cheat and move_b == cheat:
            return punishment, punishment
        elif move_a == cooperate and move_b == cheat:
            return sucker, temptation
        elif move_a == cheat and move_b == cooperate:
            return temptation, sucker
        elif move_a == cooperate and move_b == cooperate:
            return reward, reward

    def replace_move(self, move: int) -> int:
        dev_prob = self.settings['deviation_probability']
        if dev_prob < 1:
            return move
        if dev_prob > 100:
            dev_prob = 100
        x = random.randint(1, round(100 / dev_prob))
        if x == 1:
            if move == self.MOVES['cooperate']:
                move = self.MOVES['cheat']
            elif move == self.MOVES['cheat']:
                move = self.MOVES['cooperate']
        return move


class Tournament:
    def __init__(self, players: tuple[Player], population: dict, settings: dict):
        self.players = players
        self.population = population
        self.settings = settings

    def start(self) -> dict:
        data = {}
        for player_a in self.players:
            for index_a in range(self.population[player_a.name]):
                for player_b in self.players:
                    for index_b in range(self.population[player_b.name]):
                        if player_a.name == player_b.name and index_a == index_b:
                            continue
                        score_a, score_b = Game(player_a, player_b, self.settings).play()
                        name_a = f'{player_a.name}_{index_a + 1}'
                        if name_a in data:
                            data[name_a] += score_a
                        else:
                            data[name_a] = score_a
                        name_b = f'{player_b.name}_{index_b + 1}'
                        if name_b in data:
                            data[name_b] += score_b
                        else:
                            data[name_b] = score_b
        standings = []
        for key in sorted(data, key=data.get, reverse=True):
            standings.append((key, data[key]))
        population = self.population
        for _ in range(self.settings['losers_per_tournament']):
            best = standings[0][0].split('_')[0]
            worst = standings[len(standings) - 1][0].split('_')[0]
            population[best] += 1
            population[worst] -= 1
            standings.pop(0)
            standings.pop(len(standings) - 1)
        return population


def main():
    with open('settings.json') as f:
        settings = json.load(f)
    print('Settings')
    for i in settings:
        print(f'{i}: {settings[i]}')
    players = (
        Copycat('Copycat'),
        Copykitten('Copykitten'),
        Cheater('Cheater'),
        Cooperator('Cooperator'),
        Grudger('Grudger'),
        Detective('Detective'),
        Simpleton('Simpleton'),
        Random('Random'),
    )
    population = settings['population']
    start = datetime.now()
    for i in range(settings['tournament_rounds']):
        print(f'\n{i + 1}.')
        population = Tournament(players, population, settings).start()
        for x in population:
            print(f'{x}: {population[x]}')
    print('\nTime:', datetime.now() - start)


if __name__ == '__main__':
    main()
