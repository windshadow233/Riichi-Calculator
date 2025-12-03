import pickle
import random
from collections import Counter
from mahjong.checker import Mahjong

mahjong = Mahjong()


class AutoCleanCounter(Counter):
    def __setitem__(self, key, value):
        if value == 0:
            del self[key]
        else:
            super(AutoCleanCounter, self).__setitem__(key, value)


def key2ptn(key):
    bits = bin(key)[2:][::-1].split('0')
    ptn = []
    cur = []
    for ones in bits:
        if len(ones) % 2 == 0:
            cur.append(len(ones) // 2)
        else:
            cur.append((len(ones) - 1) // 2)
            ptn.append(cur)
            cur = []

    return ptn


def ptn2key(a):
    ret = 0
    length = -1
    for b in a:
        for i in b:
            length += 1
            if i == 1:
                ret |= 0b11 << length
                length += 2
            elif i == 2:
                ret |= 0b1111 << length
                length += 4
            elif i == 3:
                ret |= 0b111111 << length
                length += 6
            elif i == 4:
                ret |= 0b11111111 << length
                length += 8
        ret |= 0b1 << length
        length += 1
    return ret


with open('data/AGARI_TABLE.pkl', 'rb') as f:
    AGARI_TABLE = pickle.loads(f.read())

with open('data/MACHI_TABLE.pkl', 'rb') as f:
    MACHI_TABLE = pickle.loads(f.read())


def to_pattern(counter: AutoCleanCounter):
    counter = list(sorted(counter.items(), key=lambda x: x[0]))
    pattern = []
    current_digit, current_type = None, None
    new = []
    for tile, c in counter:
        digit, t = tile % 10, tile // 10
        if t != current_type or digit - 2 > current_digit or t == 4:
            if new:
                pattern.append(new)
                new = []
        if t == current_type and t != 4 and digit - 2 == current_digit:
            new.extend([0, c])
        else:
            new.append(c)
        current_digit, current_type = digit, t
    if new:
        pattern.append(new)
    return pattern


def is_agari(counter: AutoCleanCounter):
    pattern = to_pattern(counter)
    key = ptn2key(pattern)
    return key in AGARI_TABLE


def machi(t, counter: AutoCleanCounter):
    res = []
    base = t * 10
    for i in range(9):
        tile = i + base
        if counter[tile] == 4:
            continue
        counter[tile] += 1
        if is_agari(counter):
            res.append(tile)
        counter[tile] -= 1
    return res


def random_pattern():
    key = random.choice(MACHI_TABLE)
    return key2ptn(key)


def pattern2tiles(t, ptn):
    """
    :param t: int 花色，0-3分别表示万筒索字
    :param ptn: List[List[int]]
    内部的list表示一组连续的（最多相隔1）的牌，数字表示张数，相邻list之间必须相隔2以上（可以更多，但必须保证所有数字不超出9）。数字至少为1，至多为9，并且单调递增。
    :return: 随机生成一组符合pattern的牌
    """
    sep_count = len(ptn) - 1
    min_length = sum(len(_) for _ in ptn) + 2 * sep_count
    extra_sep_size = 9 - min_length
    base = t * 10
    start = 0
    tiles = []
    cur = start
    extra = random.randint(0, extra_sep_size)
    cur += extra
    extra_sep_size -= extra
    for group in ptn:
        for count in group:
            for _ in range(count):
                tiles.append(cur + base)
            cur += 1
        cur += 2
        extra = random.randint(0, extra_sep_size)
        cur += extra
        extra_sep_size -= extra
    return tiles


def add_one_tile(tiles):
    t = tiles[0] // 10
    counter = AutoCleanCounter(tiles)
    candidates = []
    for i in range(9):
        tile = t * 10 + i
        if counter[tile] < 4:
            candidates.append(tile)
    return sorted(tiles + [random.choice(candidates)])


def machi_answer(tiles):
    t = tiles[0] // 10
    counter = AutoCleanCounter(tiles)
    return machi(t, counter)


def kiri_answer(tiles):
    t = tiles[0] // 10
    counter = AutoCleanCounter(tiles)
    if is_agari(counter):
        return [-1]
    max_count = {i: 4 - counter[i] for i in range(t * 10, t * 10 + 9)}
    record = {}
    for tile in tiles:
        if tile in record:
            continue
        counter[tile] -= 1
        machi_tiles = machi(t, counter)
        counter[tile] += 1
        record[tile] = sum(max_count[m] for m in machi_tiles)
    m = max(record.values())
    return sorted([tile for tile, val in record.items() if val == m])
