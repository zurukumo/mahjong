import pickle
import itertools

# 面子の抜き出し


def get_mentsu(tehai, n_mentsu, start):
    max = [[0, 0], [0, 0]]

    for i in range(start, 9):
        if tehai[i] == 0:
            continue

        # 順子を抜き出し
        if i <= 6 and tehai[i+1] and tehai[i+2]:
            tehai[i] -= 1
            tehai[i+1] -= 1
            tehai[i+2] -= 1
            n = get_mentsu(tehai, n_mentsu + 1, i)
            tehai[i] += 1
            tehai[i+1] += 1
            tehai[i+2] += 1

            if n[0][0] * 2 + n[0][1] > max[0][0] * 2 + max[0][1]:
                max[0] = n[0]
            if n[1][0] * 8 + n[1][1] > max[1][0] * 8 + max[1][1]:
                max[1] = n[1]

        # 刻子を抜き出し
        if tehai[i] >= 3:
            tehai[i] -= 3
            n = get_mentsu(tehai, n_mentsu + 1, i)
            tehai[i] += 3

            if n[0][0] * 2 + n[0][1] > max[0][0] * 2 + max[0][1]:
                max[0] = n[0]
            if n[1][0] * 8 + n[1][1] > max[1][0] * 8 + max[1][1]:
                max[1] = n[1]

    if max == [[0, 0], [0, 0]]:
        n_tatsu = get_tatsu(tehai, 0, 0)
        return [[n_mentsu, n_tatsu], [n_mentsu, n_tatsu]]

    return max

# 塔子の抜き出し


def get_tatsu(tehai, n_tatsu, start):
    max = 0

    for i in range(start, 9):
        if tehai[i] == 0:
            continue

        # 両面・辺張塔子を抜き出し
        if i <= 7 and tehai[i+1]:
            tehai[i] -= 1
            tehai[i+1] -= 1
            n = get_tatsu(tehai, n_tatsu + 1, i)
            tehai[i] += 1
            tehai[i+1] += 1

            if n > max:
                max = n

        # 嵌張塔子を抜き出し
        if i <= 6 and tehai[i+2]:
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

    for tehai in list(itertools.product([0, 1, 2, 3, 4], repeat=9)):
        # タプルをリストに変換
        tehai = list(tehai)

        # 手牌が14枚より大きい場合はスキップ
        if sum(tehai) > 14:
            continue

        mt = get_mentsu(tehai, 0, 0)

        # 面子も塔子も取れない場合はスキップ
        if mt == [[0, 0], [0, 0]]:
            continue

        # mtのパターンAとBが同じ場合はパターンBを省略
        if mt[0] == mt[1]:
            mt = [mt[0]]

        # 手牌列の生成
        tehai_line = 0
        for i in tehai:
            tehai_line *= 10
            tehai_line += i

        if tehai_line in shanten_table:
            continue

        shanten_table[tehai_line] = mt

    f = open('shanten_table.pickle', 'wb')
    pickle.dump(shanten_table, f)
    f.close()


make_shanten_table()
