from server.game_action import GameAction
from server.game_routine import GameRoutine

# TODO 喰い替え禁止


class Game(GameAction, GameRoutine):
    def __init__(self, debug=False):
        self.debug = debug

    def prange(self):
        return [self.players[i % 4] for i in range(self.teban, self.teban + 4)]
