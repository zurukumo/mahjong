from .const import Const

# TODO ダブロン検証


class GameRoutine:
    def next(self):
        # 局開始状態
        if self.state == Const.KYOKU_START_STATE:
            if self.kyoku >= 8 or any(bool(self.scores[i] < 0) for i in range(4)):
                self.prev_state = Const.KYOKU_START_STATE
                self.state = Const.SYUKYOKU_STATE
                return True

            self.start_kyoku()

            self.prev_state = self.state
            self.state = Const.TSUMO_STATE
            return True

        # ツモ状態
        elif self.state == Const.TSUMO_STATE:
            # 山がなくなったら流局
            if len(self.yama) == 0:
                self.prev_state = Const.TSUMO_STATE
                self.state = Const.RYUKYOKU_STATE
                return True

            # 前回が暗槓でなければ手番を増やす
            if self.prev_state != Const.TSUMO_STATE:
                self.teban = (self.teban + 1) % 4

            player = self.players[self.teban]

            # ツモ
            player.tsumo()

            # ツモ和するかどうか
            if player.decide_tsumoho():

                self.prev_state = Const.TSUMO_STATE
                self.state = Const.AGARI_STATE
                return True

            # 暗槓するかどうか
            if player.decide_ankan():
                self.prev_state = Const.TSUMO_STATE
                self.state = Const.TSUMO_STATE
                return True

            # リーチするかどうか
            if player.decide_richi():
                self.prev_state = Const.TSUMO_STATE
                self.state = Const.DAHAI_STATE
                return True

            self.prev_state = Const.TSUMO_STATE
            self.state = Const.DAHAI_STATE
            return True

        # 打牌受信状態
        elif self.state == Const.DAHAI_STATE:
            player = self.players[self.teban]

            player.decide_dahai()

            # 選択を格納
            self.ronho_decisions = dict()
            self.pon_decisions = dict()
            self.chi_decisions = dict()

            # AIの選択を格納
            for player in self.players:
                if player.type == 'kago' or player.type == 'dqn':
                    self.ronho_decisions[player.position] = player.decide_ronho()
                    self.pon_decisions[player.position] = [player.decide_pon(), self.last_dahai]
                    self.chi_decisions[player.position] = [player.decide_chi(), self.last_dahai]

            self.prev_state = Const.DAHAI_STATE
            self.state = Const.NOTICE2_STATE
            return True

        # 通知2受信状態
        elif self.state == Const.NOTICE2_STATE:
            if len(self.ronho_decisions) != 4 or len(self.pon_decisions) != 4 or len(self.chi_decisions) != 4:
                return False

            # ロン決定
            for who, tf in self.ronho_decisions.items():
                if not tf:
                    continue
                self.players[who].ronho()

                self.prev_state = Const.NOTICE2_STATE
                self.state = Const.AGARI_STATE
                return True

            # ロンじゃなければリーチ成立
            for player in self.players:
                if player.is_richi_declare and not player.is_richi_complete:
                    player.richi_complete()
                    break

            # ポン決定
            for who, (pais, pai) in self.pon_decisions.items():
                if pais is not None:
                    self.players[who].pon(pais, pai)

                    self.dahai_decisions = dict()
                    self.prev_state = Const.NOTICE2_STATE
                    self.state = Const.DAHAI_STATE
                    return True

            # チー決定
            for who, (pais, pai) in self.chi_decisions.items():
                if pais is not None:
                    self.players[who].chi(pais, pai)

                    self.dahai_decisions = dict()
                    self.prev_state = Const.NOTICE2_STATE
                    self.state = Const.DAHAI_STATE
                    return True

            self.prev_state = Const.NOTICE2_STATE
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
