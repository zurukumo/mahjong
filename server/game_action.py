from random import shuffle

from .const import Const
from .kago import Kago


class GameAction:
    def start_game(self, player=None):
        # Player関連
        self.players = [
            Kago(id=0, game=self),
            Kago(id=1, game=self),
            Kago(id=2, game=self),
            Kago(id=3, game=self)
        ]

        # 半荘関連
        self.kyoku = 0
        self.honba = 0
        self.kyotaku = 0
        self.scores = [25000, 25000, 25000, 25000]
        shuffle(self.players)
        for i, player in enumerate(self.players):
            player.position = i

        self.prev_state = Const.INITIAL_STATE
        self.state = Const.KYOKU_START_STATE

    def start_kyoku(self):
        # 各プレイヤーの手牌・河・副露の初期化
        for player in self.players:
            player.tehai = []
            player.kawa = []
            player.huro = []

            player.richi_pc = None
            player.richi_pai = None
            player.is_richi_declare = False
            player.is_richi_complete = False

        # 手番設定(最初は1引く)
        self.teban = (self.kyoku - 1) % 4

        # 山生成
        self.yama = [i for i in range(136)]
        shuffle(self.yama)

        # ドラ生成
        self.dora = []
        for _ in range(10):
            self.dora.append(self.yama.pop())
        self.n_dora = 1

        # 嶺上生成
        self.rinshan = []
        for _ in range(4):
            self.rinshan.append(self.yama.pop())

        # 配牌
        for player in self.players:
            for _ in range(13):
                player.tsumo()

        # 最後の打牌・手番
        self.last_tsumo = None
        self.last_dahai = None
        self.last_teban = None

        # カンの個数
        self.n_kan = 0

        # プログラムカウンター
        self.pc = 0

        # 通知
        self.ronho_decisions = dict()
        self.minkan_decisions = dict()
        self.pon_decisions = dict()
        self.chi_decisions = dict()

        # 状態
        self.prev_state = self.state
        self.state = Const.KYOKU_START_STATE

    def tsumoho(self, player):
        if player.can_tsumoho():
            self.tsumoho_decisions[player.position] = True
            self.ankan_decisions[player.position] = None
            self.richi_decisions[player.position] = False

    def ankan(self, pais, player):
        if player.can_ankan(pais):
            self.tsumoho_decisions[player.position] = False
            self.ankan_decisions[player.position] = pais
            self.richi_decisions[player.position] = False

    def richi_declare(self, player):
        for i in player.tehai:
            if player.can_richi_declare(i):
                self.tsumoho_decisions[player.position] = False
                self.ankan_decisions[player.position] = None
                self.richi_decisions[player.position] = True
                break

    def dahai(self, dahai, player):
        if player.can_dahai(dahai):
            self.dahai_decisions[player.position] = dahai

    def ronho(self, player):
        if player.can_ronho():
            self.ronho_decisions[player.position] = True
            self.pon_decisions[player.position] = [None, None]
            self.chi_decisions[player.position] = [None, None]

    def pon(self, pais, pai, player):
        if player.can_pon(pais, pai):
            self.ronho_decisions[player.position] = False
            self.pon_decisions[player.position] = [pais, pai]
            self.chi_decisions[player.position] = [None, None]

    def chi(self, pais, pai, player):
        if player.can_chi(pais, pai):
            self.ronho_decisions[player.position] = False
            self.pon_decisions[player.position] = [None, None]
            self.chi_decisions[player.position] = [pais, pai]

    def ryukyoku(self):
        is_tenpais = []
        for player in self.players:
            is_tenpais.append(bool(player.calc_shanten() <= 0))

        n_tenpai = is_tenpais.count(True)
        scores = []
        score_movements = []
        for i, player in enumerate(self.players):
            if is_tenpais[i] and n_tenpai == 1:
                score_movements.append(3000)
            if is_tenpais[i] and n_tenpai == 2:
                score_movements.append(1500)
            if is_tenpais[i] and n_tenpai == 3:
                score_movements.append(1000)
            if not is_tenpais[i] and n_tenpai == 1:
                score_movements.append(-1000)
            if not is_tenpais[i] and n_tenpai == 2:
                score_movements.append(-1500)
            if not is_tenpais[i] and n_tenpai == 3:
                score_movements.append(-3000)
            if n_tenpai == 0 or n_tenpai == 4:
                score_movements.append(0)

            self.scores[i] += score_movements[i]
            scores.append(self.scores[i])

        self.honba += 1
        if not is_tenpais[self.kyoku % 4]:
            self.kyoku += 1

        return {
            'scores': scores,
            'scoreMovements': score_movements
        }

    def next_kyoku(self):
        if self.state == Const.AGARI_STATE:
            self.state = Const.KYOKU_START_STATE
        elif self.state == Const.RYUKYOKU_STATE:
            self.state = Const.KYOKU_START_STATE
