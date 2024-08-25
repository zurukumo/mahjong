import random

from kago_utils.hai import Hai136List
from kago_utils.shanten import Shanten
from shanten import calc_shanten

for n_huuro in range(5):
    print(f"副露数: {n_huuro}")
    for _ in range(10000):
        yama = list(range(136))
        random.shuffle(yama)

        tehai = Hai136List(yama[:14-n_huuro*3])

        shanten_old = calc_shanten(tehai.to_hai34_counter().data, n_huuro)
        shanten_new = Shanten().calculate_shanten_for_regular(tehai, n_huuro)

        assert shanten_old == shanten_new, (tehai.to_hai34_string(), shanten_old, shanten_new)
