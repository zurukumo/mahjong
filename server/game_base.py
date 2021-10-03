class GameBase:
    def __init__(self):
        pass

    # 汎用関数
    def prange(self):
        return [self.players[i % 4] for i in range(self.teban, self.teban + 4)]
