from .const import Const

# TODO ダブロン検証


class GameRoutine:
    def next(self):
        # 局開始状態
        if self.state == Const.KYOKU_START_STATE:
            if self.kyoku >= 8 or any(bool(self.scores[i] < 0) for i in range(4)):
                self.state = Const.SYUKYOKU_STATE
                return True

            self.start_kyoku()

            self.state = Const.TSUMO_STATE
            return True

        # ツモ状態
        elif self.state == Const.TSUMO_STATE:
            # 山がなくなったら流局
            if len(self.yama) == 0:
                self.state = Const.RYUKYOKU_STATE
                return True

            # 前回が暗槓でなければ手番を増やす
            if not self.ankan_flg:
                self.teban = (self.teban + 1) % 4
            self.ankan_flg = False

            player = self.players[self.teban]

            # ツモ
            player.tsumo()

            # ツモ和するかどうか
            if player.decide_tsumoho():
                self.state = Const.AGARI_STATE
                return True

            # 暗槓するかどうか
            if player.decide_ankan():
                self.state = Const.TSUMO_STATE
                return True

            # リーチするかどうか
            if player.decide_richi():
                self.state = Const.DAHAI_STATE
                return True

            self.state = Const.DAHAI_STATE
            return True

        # 打牌状態
        elif self.state == Const.DAHAI_STATE:
            self.players[self.teban].decide_dahai()
            self.state = Const.NAKI_STATE
            return True

        # 鳴き状態
        elif self.state == Const.NAKI_STATE:
            # ロン和するかどうか(重複あり)
            flg = False
            for player in self.prange()[1:]:
                if player.decide_ronho():
                    flg = True

            if flg:
                self.state = Const.AGARI_STATE
                return True

            # ロンじゃなければリーチ成立
            player = self.players[self.teban]
            if player.is_richi_declare and not player.is_richi_complete:
                player.richi_complete()

            # ポンするかどうか
            for player in self.prange()[1:]:
                if player.decide_pon():
                    self.state = Const.DAHAI_STATE
                    return True

            # チーするかどうか
            player = self.players[(self.teban + 1) % 4]
            if player.decide_chi():
                self.state = Const.DAHAI_STATE
                return True

            self.state = Const.TSUMO_STATE
            return True

        # 和了り状態
        elif self.state == Const.AGARI_STATE:
            self.next_kyoku()
            return True

        # 流局状態
        elif self.state == Const.RYUKYOKU_STATE:
            self.ryukyoku()
            self.next_kyoku()
            return True

        # 終局状態
        elif self.state == Const.SYUKYOKU_STATE:
            pass
