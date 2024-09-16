import csv
import os
import re
from random import randint

from core.shanten import calc_shanten, get_yuko
from paihu_debugger import debug


class PaihuParser():
    DAHAI_MODE = 0
    RIICHI_MODE = 1
    ANKAN_MODE = 2
    KAKAN_MODE = 3
    RON_MINKAN_PON_CHII_MODE = 4

    SHUNTSU_TYPE = 0
    MINKO_TYPE = 1
    MINKAN_TYPE = 2
    ANKAN_TYPE = 3

    YEARS = [2015, 2016, 2017]

    def __init__(self, mode=DAHAI_MODE, max_count=1500000, debug=False):
        self.count = 0
        self.mode = mode
        self.max_count = max_count
        self.debug = debug
        for year in PaihuParser.YEARS:
            file_dir = f'./paihus/xml{year}'
            for filename in os.listdir(file_dir):
                self.filename = filename
                self.ts = -1
                self.parse_xml(f'{file_dir}/{filename}')

    def url(self):
        return 'https://tenhou.net/0/?log={}&ts={}'.format(self.filename.replace('.xml', ''), self.ts)

    def pai(self, x):
        return x // 4

    def is_ankan(self, m):
        return not bool(m & 0x0003)

    def is_shuntsu(self, m):
        return bool(m & 0x0004)

    def is_minko(self, m):
        return not self.is_shuntsu(m) and bool(m & 0x0008)

    def is_kakan(self, m):
        return not self.is_shuntsu(m) and bool(m & 0x0010)

    def is_minkan(self, m):
        return not (self.is_ankan(m) or self.is_shuntsu(m) or self.is_minko(m) or self.is_kakan(m))

    def is_kan(self, m):
        return self.is_ankan(m) or self.is_kakan(m) or self.is_minkan(m)

    def sample_riichi(self, who):
        elem, _ = self.actions[self.action_i + 1]

        # リーチ中
        if self.riichi[who]:
            return

        # 暗槓以外の副露をしている
        n_huro = sum(self.huro_type[who])
        n_ankan = self.huro_type[who][PaihuParser.ANKAN_TYPE]
        if n_huro != n_ankan:
            return

        if calc_shanten(tehai=self.tehai[who], n_huro=n_ankan) == 0:
            if elem == 'REACH':
                y = 1
            else:
                # ダマテンは継続しがちなので適宜飛ばす
                if randint(1, 3) <= 2:
                    return
                y = 0
            self.output(who, y)

    def sample_ankan(self, who):
        elem, attr = self.actions[self.action_i + 1]
        attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

        # リーチ中
        if self.riichi[who]:
            if self.tehai[who][self.last_tsumo] != 4:
                return

            tmp_tehai = self.tehai[who][::]
            n_huro = sum(self.huro_type[who])

            tmp_tehai[self.last_tsumo] = 3
            shanten1 = calc_shanten(tmp_tehai, n_huro)
            machi1 = get_yuko(tmp_tehai, [4] * 34, n_huro=n_huro)

            tmp_tehai[self.last_tsumo] = 0
            n_huro += 1
            shanten2 = calc_shanten(tmp_tehai, n_huro)
            machi2 = get_yuko(tmp_tehai, [4] * 34, n_huro=n_huro)

            if shanten1 != shanten2 or machi1 != machi2:
                return

            if elem == 'N' and self.is_ankan(int(attr['m'])):
                self.output(who, 1)
            else:
                self.output(who, 0)

        # リーチ中じゃない
        else:
            for i in range(34):
                if self.tehai[who][i] != 4:
                    continue

                if elem == 'N' and self.is_ankan(int(attr['m'])):
                    self.output(who, 1)
                else:
                    if randint(1, 3) == 1:
                        self.output(who, 0)

    def sample_ron_minkan_pon_chii(self):
        next_elem, next_attr = self.actions[self.action_i + 1]
        for who in range(4):
            if who == self.last_teban:
                continue

            # 何もしない -> 0, ロン -> 1, 明槓 -> 2, ポン -> 3, 左牌をチー -> 4, 中央牌をチー -> 5, 右牌をチー -> 6
            y = 0
            if next_elem == 'AGARI':
                # ダブロン、トリロンの可能性があるので全てのAGARIタグを見る
                for elem, attr in self.actions[self.action_i + 1:]:
                    if elem != 'AGARI':
                        break
                    if int(attr['who']) == who:
                        y = 1
            elif next_elem == 'N' and self.is_minkan(int(next_attr['m'])) and int(next_attr['who']) == who:
                y = 2
            elif next_elem == 'N' and self.is_minko(int(next_attr['m'])) and int(next_attr['who']) == who:
                y = 3
            elif next_elem == 'N' and self.is_shuntsu(int(next_attr['m'])) and int(next_attr['who']) == who:
                y = 4 + ((int(next_attr['m']) & 0xFC00) >> 10) % 3

            self.output(who, y)

    def m(self, who, m):
        if self.is_ankan(m):
            # 暗槓
            p = ((m & 0xFF00) >> 8) // 4
            self.huro[who][p] += 4
            self.tehai[who][p] -= 4
            self.huro_type[who][PaihuParser.ANKAN_TYPE] += 1
            # print(self.url())
            # print('暗槓', self.jp(p))
            # print('最後の打牌', self.jp(self.last_dahai))
            # input()

        else:
            # 順子
            if self.is_shuntsu(m):
                p = ((m & 0xFC00) >> 10) // 3
                p += (p // 7) * 2
                for i in range(3):
                    self.huro[who][p + i] += 1
                    self.tehai[who][p + i] -= 1
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][PaihuParser.SHUNTSU_TYPE] += 1
                # print(self.url())
                # print('順子', self.jp(p))
                # t = ((m & 0xFC00) >> 10) % 3
                # print('鳴いた場所', t)
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

            # 明刻
            elif self.is_minko(m):
                p = ((m & 0xFE00) >> 9) // 3
                self.huro[who][p] += 3
                self.tehai[who][p] -= 3
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][PaihuParser.MINKO_TYPE] += 1
                # print(self.url())
                # print('明刻', self.jp(p))
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

            # 加槓
            elif self.is_kakan(m) == 1:
                p = ((m & 0xFE00) >> 9) // 3
                self.huro[who][p] += 1
                self.huro_type[who][PaihuParser.MINKO_TYPE] -= 1
                self.huro_type[who][PaihuParser.MINKAN_TYPE] += 1
                # print(self.url())
                # print('加槓', self.jp(p))
                # input()

            # 大明槓
            else:
                p = ((m & 0xFF00) >> 8) // 4
                self.huro[who][p] += 4
                self.tehai[who][p] -= 4
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][PaihuParser.MINKAN_TYPE] += 1
                # print(self.url())
                # print('大明槓', self.jp(p))
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

    def output(self, who, y):
        # 出力ファイル名の決定
        if self.mode == PaihuParser.DAHAI_MODE:
            output_file = 'dahai.csv'
        elif self.mode == PaihuParser.RIICHI_MODE:
            output_file = 'riichi.csv'
        elif self.mode == PaihuParser.ANKAN_MODE:
            output_file = 'ankan.csv'
        elif self.mode == PaihuParser.KAKAN_MODE:
            output_file = 'kakan.csv'
        elif self.mode == PaihuParser.RON_MINKAN_PON_CHII_MODE:
            output_file = 'ron_minkan_pon_chii.csv'

        with open('./datasets/' + output_file, 'a') as f:
            writer = csv.writer(f)

            x = []

            # 手牌(4)
            for i in range(1, 4 + 1):
                x += [1 if self.tehai[who][j] >= i else 0 for j in range(34)]

            # 赤(1)
            x += self.aka[who]

            # 河(20 * 4)
            for i in range(who, who + 4):
                i = i % 4
                for j in range(20):
                    tmp = [0] * 34
                    if j < len(self.kawa[i]):
                        tmp[self.kawa[i][j]] = 1
                    x += tmp

            # 最終打牌(3)
            for i in range(who + 1, who + 4):
                i = i % 4
                tmp = [0] * 34
                if i == self.last_teban:
                    tmp[self.last_dahai] = 1
                x += tmp

            # 副露(4 * 4)
            for i in range(who, who + 4):
                i = i % 4
                for j in range(1, 4 + 1):
                    x += [1 if self.huro[i][k] >= j else 0 for k in range(34)]

            # ドラ(4)
            for i in range(1, 4 + 1):
                x += [1 if self.dora[j] >= i else 0 for j in range(34)]

            # リーチ(4)
            for i in range(who, who + 4):
                i = i % 4
                x += [1] * 34 if self.riichi[i] else [0] * 34

            # 局数(12)
            for i in range(12):
                if i == min(self.kyoku, 11):
                    x += [1] * 34
                else:
                    x += [0] * 34

            # 座順(4)
            for i in range(4):
                if i == who:
                    x += [1] * 34
                else:
                    x += [0] * 34

            writer.writerow([y] + x)

            # デバッグ開始
            if self.debug:
                print(self.url())
                debug(x, y)
                input()

        self.count += 1
        print(self.count, '/', self.max_count)
        if self.count == self.max_count:
            print('終了')
            exit()

    def parse_xml(self, filename):
        with open(filename, 'r') as xml:
            self.actions = []
            for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()):
                attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
                self.actions.append((elem, attr))

            for action_i, (elem, attr) in enumerate(self.actions):
                self.action_i = action_i

                # 開局
                if elem == 'INIT':
                    self.parse_init_tag(attr)

                # ツモ
                elif re.match(r'[T|U|V|W][0-9]+', elem):
                    self.parse_tsumo_tag(elem)

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    self.parse_dahai_tag(elem)

                # 副露
                elif elem == 'N':
                    who = int(attr['who'])
                    self.m(who, int(attr['m']))

                # リーチ成立
                elif elem == 'REACH' and attr['step'] == '2':
                    who = int(attr['who'])
                    self.riichi[who] = True

                elif elem == 'DORA':
                    pai = self.pai(int(attr['hai']))
                    self.dora[pai] += 1

                # 和了
                elif elem == 'AGARI':
                    who = int(attr['who'])
                    self.who = who

    def parse_init_tag(self, attr):
        self.ts += 1
        self.tehai = [[0] * 34 for _ in range(4)]
        self.aka = [[0] * 34 for _ in range(4)]
        self.kawa = [[] for _ in range(4)]
        self.huro = [[0] * 34 for _ in range(4)]
        self.huro_type = [[0] * 4 for _ in range(4)]
        self.dora = [0] * 34
        self.riichi = [False] * 4
        self.kyoku = None
        self.ten = [[0] * 34 for _ in range(4)]

        # 配牌をパース
        for who in range(4):
            for pai in map(int, attr[f'hai{who}'].split(',')):
                self.tehai[who][self.pai(pai)] += 1
                if pai in [16, 52, 88]:
                    self.aka[who][self.pai(pai)] = 4

        # 局数、本場、供託、ドラをパース
        kyoku, honba, kyotaku, _, _, dora = map(int, attr['seed'].split(','))
        self.kyoku = kyoku
        self.dora[self.pai(dora)] += 1

        # 点棒状況をパース
        for who, ten in enumerate(map(int, attr['ten'].split(','))):
            self.ten[who][min(33, ten // 20)] = 4

        self.last_dahai = -1
        self.last_tsumo = -1

    def parse_tsumo_tag(self, elem):
        idx = {'T': 0, 'U': 1, 'V': 2, 'W': 3}
        who = idx[elem[0]]
        pai = self.pai(int(elem[1:]))

        self.tehai[who][pai] += 1
        if pai in [16, 52, 88]:
            self.aka[who][pai] = 4
        self.last_tsumo = pai

        # リーチの抽出
        if self.mode == PaihuParser.RIICHI_MODE:
            self.sample_riichi(who)

        # 暗槓の抽出
        if self.mode == PaihuParser.ANKAN_MODE:
            self.sample_ankan(who)

    def parse_dahai_tag(self, elem):
        idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
        who = idx[elem[0]]
        pai = self.pai(int(elem[1:]))

        # 打牌の抽出
        if self.mode == PaihuParser.DAHAI_MODE and self.riichi[who]:
            if randint(1, 30) == 1:
                self.output(who, pai)

        # 打牌の処理
        self.kawa[who].append(pai)
        self.tehai[who][pai] -= 1
        self.last_dahai = pai
        self.last_teban = who

        # ロン、ミンカン、ポン、チーの抽出
        if self.mode == PaihuParser.RON_MINKAN_PON_CHII_MODE:
            self.sample_ron_minkan_pon_chii()


if __name__ == '__main__':
    PaihuParser(mode=PaihuParser.RON_MINKAN_PON_CHII_MODE, max_count=100000, debug=False)
