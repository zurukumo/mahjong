import itertools
import pickle


# 面子の抜き出し
def get_mentsu(tehai, n_mentsu, start):
    max1, max2 = [0, 0], [0, 0]

    for i in range(start, 9):
        # 順子を抜き出し
        if i <= 6 and tehai[i] >= 1 and tehai[i+1] >= 1 and tehai[i+2] >= 1:
            tehai[i] -= 1
            tehai[i+1] -= 1
            tehai[i+2] -= 1
            cur1, cur2 = get_mentsu(tehai, n_mentsu + 1, i)
            tehai[i] += 1
            tehai[i+1] += 1
            tehai[i+2] += 1

            if cur1[0] * 2 + cur1[1] > max1[0] * 2 + max1[1]:
                max1 = cur1
            if cur2[0] * 8 + cur2[1] > max2[0] * 8 + max2[1]:
                max2 = cur2

        # 刻子を抜き出し
        if tehai[i] >= 3:
            tehai[i] -= 3
            cur1, cur2 = get_mentsu(tehai, n_mentsu + 1, i)
            tehai[i] += 3

            if cur1[0] * 2 + cur1[1] > max1[0] * 2 + max1[1]:
                max1 = cur1
            if cur2[0] * 8 + cur2[1] > max2[0] * 8 + max2[1]:
                max2 = cur2

    if max1 == [0, 0] and max2 == [0, 0]:
        n_tatsu = get_tatsu(tehai, 0, 0)
        return [n_mentsu, n_tatsu], [n_mentsu, n_tatsu]

    return max1, max2


# 塔子の抜き出し
def get_tatsu(tehai, n_tatsu, start):
    max = 0

    for i in range(start, 9):
        # 両面・辺張塔子を抜き出し
        if i <= 7 and tehai[i] >= 1 and tehai[i+1] >= 1:
            tehai[i] -= 1
            tehai[i+1] -= 1
            n = get_tatsu(tehai, n_tatsu + 1, i)
            tehai[i] += 1
            tehai[i+1] += 1

            if n > max:
                max = n

        # 嵌張塔子を抜き出し
        if i <= 6 and tehai[i] >= 1 and tehai[i+2] >= 1:
            tehai[i] -= 1
            tehai[i+2] -= 1
            n = get_tatsu(tehai, n_tatsu + 1, i)
            tehai[i] += 1
            tehai[i+2] += 1

            if n > max:
                max = n

        # 対子を抜き出し
        if tehai[i] >= 2:
            tehai[i] -= 2
            n = get_tatsu(tehai, n_tatsu + 1, i)
            tehai[i] += 2

            if n > max:
                max = n

    if max == 0:
        return n_tatsu

    return max


# 向聴テーブルの作成
def make_shanten_table():
    shanten_table = dict()

    for tehai in itertools.product([0, 1, 2, 3, 4], repeat=9):
        # 手牌が14枚より多い場合はスキップ
        if sum(tehai) > 14:
            continue

        print(tehai)

        mt = get_mentsu(list(tehai), 0, 0)

        shanten_table[tehai] = mt

    with open('core/shanten_table.pickle', 'wb') as f:
        pickle.dump(shanten_table, f)


make_shanten_table()
