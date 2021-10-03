from .game_action import GameAction
from .game_routine import GameRoutine

# TODO 喰い替え禁止


class Game(GameAction, GameRoutine):
    def prange(self):
        return [self.players[i % 4] for i in range(self.teban, self.teban + 4)]
