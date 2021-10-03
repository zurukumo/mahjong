class GameBase:
    def __init__(self):
        pass

    # 汎用関数
    def find_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return player

    def make_simple(self, original):
        if original == 16:
            return 35
        if original == 52:
            return 36
        if original == 88:
            return 37
        return original // 4

    def prange(self):
        return [self.players[i % 4] for i in range(self.teban, self.teban + 4)]
