﻿import itertools
import pickle

with open('core/shanten_table.pickle', 'rb') as f:
    shanten_table = pickle.load(f)


def calc_shanten(tehai, n_huuro):
    # 雀頭がないときの向聴数
    min_shanten = get_temporary_shanten(tehai, n_huuro)

    # 雀頭がある場合の向聴数
    for i in range(34):
        if tehai[i] >= 2:
            tehai[i] -= 2
            min_shanten = min(min_shanten, get_temporary_shanten(tehai, n_huuro) - 1)
            tehai[i] += 2

    return min_shanten


# 一般手の一時的な向聴数の計算
def get_temporary_shanten(tehai, n_huuro):
    m = shanten_table[tuple(tehai[0:9])]
    p = shanten_table[tuple(tehai[9:18])]
    s = shanten_table[tuple(tehai[18:27])]
    z = [0, 0]

    # 字牌の刻子・対子を抜き出し
    for i in range(27, 34):
        if tehai[i] >= 3:
            z[0] += 1
        elif tehai[i] == 2:
            z[1] += 1

    min_shanten = 8

    for m, p, s in itertools.product(m, p, s):
        n_mentsu = m[0] + p[0] + s[0] + z[0] + n_huuro
        n_tatsu = m[1] + p[1] + s[1] + z[1]

        # 塔子オーバー時の補正
        if n_mentsu + n_tatsu > 4:
            n_tatsu = 4 - n_mentsu

        # シャンテン数を求める公式
        min_shanten = min(min_shanten, 8 - n_mentsu * 2 - n_tatsu)

    return min_shanten


# 七対子の向聴数の計算
def calc_shanten7(tehai):
    n_toitsu, n_tanki = 0, 0

    for i in range(34):
        if tehai[i] >= 2:
            n_toitsu += 1
        elif tehai[i] == 1:
            n_tanki += 1

    if (n_toitsu + n_tanki < 7):
        return 6 - n_toitsu + (7 - n_toitsu - n_tanki)
    else:
        return 6 - n_toitsu


# 国士無双の向聴数の計算
def calc_shanten13(tehai):
    n_yaochu, has_toitsu = 0, 0
    yaochu = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]

    for i in yaochu:
        if tehai[i] >= 1:
            n_yaochu += 1
        if tehai[i] >= 2:
            has_toitsu = 1

    return 13 - n_yaochu - has_toitsu


# 牌番号がny以上の有効牌を返す関数
def get_yuko(jun, rest, n_huuro=0, ny=0):
    yuko = []

    n_shanten = calc_shanten(jun, n_huuro)

    for i in range(ny, 34):
        if rest[i] > 0:
            jun[i] += 1
            if calc_shanten(jun, n_huuro) < n_shanten:
                yuko.append(i)
            jun[i] -= 1

    return yuko


# 牌番号がnm以上の無効牌を返す関数
def get_muko(jun, nm):
    muko = []

    n_shanten = calc_shanten(jun)

    for i in range(nm, 34):
        if jun[i] > 0:
            jun[i] -= 1
            if calc_shanten(jun) == n_shanten:
                muko.append(i)
            jun[i] += 1

    return muko


# 待ち牌を返す関数
def get_machi(jun, rest, n_huuro=0):
    machi = []

    for i in range(34):
        if rest[i] > 0:
            jun[i] += 1
            if calc_shanten(jun, n_huuro) == -1:
                machi.append(i)
            elif n_huuro == 0 and calc_shanten7(jun) == -1:
                machi.append(i)
            elif n_huuro == 0 and calc_shanten13(jun) == -1:
                machi.append(i)
            jun[i] -= 1

    return machi
