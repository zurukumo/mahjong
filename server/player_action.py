from .agari import Agari


class PlayerAction:
    def open_dora(self):
        self.game.n_dora += 1

    def tsumoho(self):
        agari = Agari(self, self.game)
        yakus = []
        for i in range(len(Agari.YAKU)):
            if agari.yaku[i] > 0:
                yakus.append({'name': Agari.YAKU[i], 'han': agari.yaku[i]})

        doras = []
        uradoras = []
        for i in range(5):
            if i < self.game.n_dora:
                doras.append(self.game.dora[i])
                uradoras.append(self.game.dora[i + 5])

        score_movements = agari.score_movements
        for i, score_movement in enumerate(score_movements):
            self.game.scores[i] += score_movement

        self.game.kyotaku = 0
        if self.position == self.game.kyoku % 4:
            self.game.honba += 1
            self.game.renchan = True
        else:
            self.game.honba = 0
            self.game.kyoku += 1
            self.game.renchan = False

    def tsumo(self):
        pai = self.game.yama.pop()

        self.tehai.append(pai)
        self.tehai.sort()
        self.game.last_tsumo = pai

    def ankan(self, pais):
        for i in pais:
            self.tehai.pop(self.tehai.index(i))
        self.huro.append({'type': 'ankan', 'pais': pais})
        self.game.n_kan += 1
        self.game.pc += 10
        self.game.ankan_flg = True

    def richi_declare(self):
        self.is_richi_declare = True
        self.richi_pc = self.game.pc

    def dahai(self, pai):
        self.tehai.pop(self.tehai.index(pai))
        self.kawa.append(pai)
        self.game.last_dahai = pai
        self.game.last_teban = self.game.teban
        self.game.pc += 1

    def richi_complete(self):
        self.game.scores[self.position] -= 1000
        self.is_richi_complete = True
        self.game.kyotaku += 1

    def richi(self, pai):
        if self.is_richi_declare and self.richi_pai not in self.kawa:
            self.richi_pai = pai

    def ronho(self):
        agari = Agari(self, self.game)
        yakus = []
        for i in range(len(Agari.YAKU)):
            if agari.yaku[i] > 0:
                yakus.append({'name': Agari.YAKU[i], 'han': agari.yaku[i]})

        doras = []
        uradoras = []
        for i in range(5):
            if i < self.game.n_dora:
                doras.append(self.game.dora[i])
                if self.is_richi_complete:
                    uradoras.append(self.game.dora[i + 5])

        score_movements = agari.score_movements
        for i, score_movement in enumerate(score_movements):
            self.game.scores[i] += score_movement

        self.game.kyotaku = 0
        if self.position == self.game.kyoku % 4:
            self.game.honba += 1
            self.game.renchan = True
        else:
            self.game.honba = 0
            self.game.kyoku += 1
            self.game.renchan = False

    def pon(self, pais, pai):
        for i in pais:
            if i != pai:
                self.tehai.pop(self.tehai.index(i))
        self.huro.append({'type': 'pon', 'pais': pais})
        self.game.players[self.game.last_teban].kawa.pop(
            self.game.players[self.game.last_teban].kawa.index(pai)
        )
        self.game.teban = self.position
        self.game.pc += 10

    def chi(self, pais, pai):
        for i in pais:
            if i != pai:
                self.tehai.pop(self.tehai.index(i))
        self.huro.append({'type': 'chi', 'pais': pais})
        self.game.players[self.game.last_teban].kawa.pop(
            self.game.players[self.game.last_teban].kawa.index(pai)
        )
        self.game.teban = self.position
        self.game.pc += 10
