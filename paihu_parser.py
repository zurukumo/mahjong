import csv
import os
import re
from random import randint

from core.shanten import calc_shanten, get_yuko
from paihu_debugger import debug


class Parser():
    DAHAI_MODE = 0
    RICHI_MODE = 1
    PON_MODE = 2
    CHI_MODE = 3
    ANKAN_MODE = 4
    KAKAN_MODE = 5
    MINKAN_MODE = 6

    SHUNTSU_TYPE = 0
    MINKO_TYPE = 1
    MINKAN_TYPE = 2
    ANKAN_TYPE = 3

    def __init__(self, years=[2015, 2016, 2017], mode=DAHAI_MODE, max_count=1500000, debug=False):
        self.count = 0
        self.mode = mode
        self.max_count = max_count
        self.debug = debug
        for year in years:
            file_dir = './paihus/xml' + str(year)
            for filename in os.listdir(file_dir):
                self.filename = filename
                self.ts = -1
                self.xml_parse(file_dir + '/' + filename)

    def url(self):
        return 'https://tenhou.net/0/?log={}&ts={}'.format(self.filename.replace('.xml', ''), self.ts)

    def jp(self, c):
        return ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
                '東', '南', '西', '北', '白', '発', '中', '-'][c]

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

    def sample_richi(self, who):
        elem, _ = self.actions[self.action_i + 1]

        # リーチ中
        if sum(self.richi[who]) >= 1:
            return

        # 暗槓以外の副露をしている
        n_huro = sum(self.huro_type[who])
        n_ankan = self.huro_type[who][Parser.ANKAN_TYPE]
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
        if sum(self.richi[who]) >= 1:
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

    def sample_pon(self, pai, who):
        elem, attr = self.actions[self.action_i + 1]
        attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
        for i in range(who + 1, who + 4):
            i = i % 4
            # リーチ中
            if sum(self.richi[i]) >= 1:
                return
            # 次がロン
            if elem == 'AGARI' and attr['who'] != attr['fromWho']:
                return

            if self.tehai[i][pai] >= 2:
                if elem == 'N' and self.is_minko(int(attr['m'])):
                    y = 1
                else:
                    y = 0
                self.output(i, y)

    def sample_chi(self, pai, who):
        elem, attr = self.actions[self.action_i + 1]
        attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
        i = (who + 1) % 4

        # 字牌 or リーチ中
        if pai >= 27 or sum(self.richi[i]) >= 1:
            return

        # 次がロン
        if elem == 'AGARI' and attr['who'] != attr['fromWho']:
            return

        # 次がポン・カン
        if elem == 'N' and (self.is_minko(int(attr['m'])) or self.is_kan(int(attr['m']))):
            return

        cond1 = pai % 9 <= 6 and self.tehai[i][pai + 1] >= 1 and self.tehai[i][pai + 2] >= 1
        cond2 = 1 <= pai % 9 <= 7 and self.tehai[i][pai - 1] >= 1 and self.tehai[i][pai + 1] >= 1
        cond3 = 2 <= pai % 9 and self.tehai[i][pai - 2] >= 1 and self.tehai[i][pai - 1] >= 1
        if cond1 or cond2 or cond3:
            if elem == 'N' and self.is_shuntsu(int(attr['m'])):
                y = ((int(attr['m']) & 0xFC00) >> 10) % 3 + 1
            else:
                y = 0

            self.output(i, y)

    def m(self, who, m):
        if self.is_ankan(m):
            # 暗槓
            p = ((m & 0xFF00) >> 8) // 4
            self.huro[who][p] += 4
            self.tehai[who][p] -= 4
            self.huro_type[who][Parser.ANKAN_TYPE] += 1
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
                self.huro_type[who][Parser.SHUNTSU_TYPE] += 1
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
                self.huro_type[who][Parser.MINKO_TYPE] += 1
                # print(self.url())
                # print('明刻', self.jp(p))
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

            # 加槓
            elif self.is_kakan(m) == 1:
                p = ((m & 0xFE00) >> 9) // 3
                self.huro[who][p] += 1
                self.huro_type[who][Parser.MINKO_TYPE] -= 1
                self.huro_type[who][Parser.MINKAN_TYPE] += 1
                # print(self.url())
                # print('加槓', self.jp(p))
                # input()

            # 大明槓
            else:
                p = ((m & 0xFF00) >> 8) // 4
                self.huro[who][p] += 4
                self.tehai[who][p] -= 4
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Parser.MINKAN_TYPE] += 1
                # print(self.url())
                # print('大明槓', self.jp(p))
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

    def output(self, who, y):
        # 出力ファイル名の決定
        if self.mode == Parser.DAHAI_MODE:
            output_file = 'dahai.csv'
        elif self.mode == Parser.RICHI_MODE:
            output_file = 'richi.csv'
        elif self.mode == Parser.PON_MODE:
            output_file = 'pon.csv'
        elif self.mode == Parser.CHI_MODE:
            output_file = 'chi.csv'
        elif self.mode == Parser.ANKAN_MODE:
            output_file = 'ankan.csv'
        elif self.mode == Parser.KAKAN_MODE:
            output_file = 'kakan.csv'
        elif self.mode == Parser.MINKAN_MODE:
            output_file = 'minkan.csv'

        with open('./datasets/' + output_file, 'a') as f:
            writer = csv.writer(f)

            x = []

            # 手牌(4)
            for n in range(1, 4 + 1):
                x += [1 if self.tehai[who][i] >= n else 0 for i in range(34)]

            # 赤(3)
            x += [1] * 34 if self.aka[who][4] != 0 else [0] * 34
            x += [1] * 34 if self.aka[who][4 + 9] != 0 else [0] * 34
            x += [1] * 34 if self.aka[who][4 + 9 + 9] != 0 else [0] * 34

            # # 河(20 * 4)
            # for i in range(who, who + 4):
            #     i = i % 4
            #     for j in range(20):
            #         tmp = [0] * 34
            #         if len(self.kawa[i]) < j:
            #             tmp[self.kawa[i][j]] = 1

            #         x += tmp
            # # 副露(4 * 4 * 4)
            # for i in range(who, who + 4):
            #     for j in range(4)

            #     i = i % 4
            #     x += self.huro[i]
            # # ドラ(1)
            # for n in range(1, 4 + 1):
            #     x += [1 if self.dora[i] >= n else 0 for i in range(34)]
            # # リーチ(3)
            # for i in range(who + 1, who + 4):
            #     i = i % 4
            #     x += self.richi[i]
            # # 局数(1)
            # x += self.kyoku
            # # 座順(1)
            # x += [4 if i == who else 0 for i in range(34)]
            # # 点数状況(4)
            # for i in range(who, who + 4):
            #     i = i % 4
            #     x += self.ten[i]

            # # 最後の打牌(1)
            # x += [4 if i == self.last_dahai else 0 for i in range(34)]

            sparse_keys = []
            for k, v in enumerate(x):
                if v == 1:
                    sparse_keys.append(k)

            writer.writerow([y] + sparse_keys)

            # デバッグ開始
            if self.debug:
                print(self.url())
                debug(x)
                input()

        self.count += 1
        print(self.count, '/', self.max_count)
        if self.count == self.max_count:
            print('終了')
            exit()

    def xml_parse(self, filename):
        with open(filename, 'r') as xml:
            self.actions = re.findall(r'<(.*?)[ /](.*?)/?>', xml.read())
            for action_i, (elem, attr) in enumerate(self.actions):
                self.action_i = action_i
                attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

                # 開局
                if elem == 'INIT':
                    self.ts += 1
                    self.tehai = [[0] * 34 for _ in range(4)]
                    self.aka = [[0] * 34 for _ in range(4)]
                    self.kawa = [[0] * 34 for _ in range(4)]
                    self.huro = [[0] * 34 for _ in range(4)]
                    self.huro_type = [[0] * 4 for _ in range(4)]
                    self.dora = [0] * 34
                    self.richi = [[0] * 34 for _ in range(4)]
                    self.kyoku = [0] * 34
                    self.ten = [[0] * 34 for _ in range(4)]

                    for who in range(4):
                        for pai in map(int, attr['hai' + str(who)].split(',')):
                            self.tehai[who][self.pai(pai)] += 1
                            if pai in [16, 52, 88]:
                                self.aka[who][self.pai(pai)] = 4

                    kyoku, honba, kyotaku, _, _, dora = map(int, attr['seed'].split(','))
                    self.kyoku[kyoku] = 4
                    self.dora[self.pai(dora)] += 1

                    for who, ten in enumerate(map(int, attr['ten'].split(','))):
                        self.ten[who][min(33, ten // 20)] = 4

                    self.last_dahai = -1
                    self.last_tsumo = -1

                # ツモ
                elif re.match(r'[T|U|V|W][0-9]+', elem):
                    idx = {'T': 0, 'U': 1, 'V': 2, 'W': 3}
                    who = idx[elem[0]]
                    pai = self.pai(int(elem[1:]))

                    self.tehai[who][pai] += 1
                    if pai in [16, 52, 88]:
                        self.aka[who][pai] = 4
                    self.last_tsumo = pai

                    # リーチの抽出
                    if self.mode == Parser.RICHI_MODE:
                        self.sample_richi(who)

                    # 暗槓の抽出
                    if self.mode == Parser.ANKAN_MODE:
                        self.sample_ankan(who)

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                    who = idx[elem[0]]
                    pai = self.pai(int(elem[1:]))

                    # 打牌の抽出
                    if self.mode == Parser.DAHAI_MODE and sum(self.richi[who]) == 0:
                        n_huro = sum(self.huro_type[who])
                        # n_huro = 0 -> 50
                        # n_huro = 1 -> 20
                        # n_huro = 2 -> 8
                        # n_huro = 3 -> 3
                        # n_huro = 4 -> 1
                        if randint(1, 50 // (2.5 ** n_huro) + 1) == 1:
                            self.output(who, pai)

                    # 打牌の処理
                    self.kawa[who][pai] += 1
                    self.tehai[who][pai] -= 1
                    self.last_dahai = pai

                    # ポンの抽出
                    if self.mode == Parser.PON_MODE:
                        self.sample_pon(pai, who)

                    # チーの抽出
                    if self.mode == Parser.CHI_MODE:
                        self.sample_chi(pai, who)

                # 副露
                elif elem == 'N':
                    who = int(attr['who'])
                    self.m(who, int(attr['m']))

                # リーチ成立
                elif elem == 'REACH' and attr['step'] == '2':
                    who = int(attr['who'])
                    self.richi[who][self.last_dahai] = 4

                elif elem == 'DORA':
                    pai = self.pai(int(attr['hai']))
                    self.dora[pai] += 1

                # 和了
                elif elem == 'AGARI':
                    who = int(attr['who'])
                    self.who = who


Parser(
    years=[2015, 2016, 2017],
    mode=Parser.RICHI_MODE,
    max_count=300000,
    debug=False
)
