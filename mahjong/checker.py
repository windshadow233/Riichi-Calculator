from typing import List, Iterable
from copy import deepcopy, copy
from collections import Counter
import numpy as np

MANS = {0, 1, 2, 3, 4, 5, 6, 7, 8}
PINS = {10, 11, 12, 13, 14, 15, 16, 17, 18}
SOUS = {20, 21, 22, 23, 24, 25, 26, 27, 28}
AKA_MAN = -1
AKA_PIN = 9
AKA_SOU = 19
ONES = {0, 10, 20}
NINES = {8, 18, 28}
TERMINALS = {*ONES, *NINES}
WINDS = {30, 40, 50, 60}
DRAGONS = {70, 80, 90}
HONORS = {*WINDS, *DRAGONS}
TERMINALS_HONORS = {*TERMINALS, *HONORS}
GREENS = {21, 22, 23, 25, 27, 80}
ALL = {*MANS, *PINS, *SOUS, *HONORS}

CHARACTERS_UNICODE = "🀇🀈🀉🀊🀋🀌🀍🀎🀏"
DOTS_UNICODE = "🀙🀚🀛🀜🀝🀞🀟🀠🀡"
BAMBOOS_UNICODE = "🀐🀑🀒🀓🀔🀕🀖🀗🀘"
HONORS_UNICODE = "🀀🀁🀂🀃🀆🀅🀄"


ID2UNICODE = {
    **{i: CHARACTERS_UNICODE[i] for i in range(9)},
    **{i: DOTS_UNICODE[i - 10] for i in range(10, 19)},
    **{i: BAMBOOS_UNICODE[i - 20] for i in range(20, 29)},
    **{i: HONORS_UNICODE[i // 10 - 3] for i in HONORS}
}


class Mahjong:

    def _str2id(self, tiles: str):
        stack = ''
        m = p = s = z = ''
        for c in tiles:
            if c.isdigit():
                stack += c
            elif c == 'm':
                m += stack
                stack = ''
            elif c == 'p':
                p += stack
                stack = ''
            elif c == 's':
                s += stack
                stack = ''
            elif c == 'z':
                z += stack
                stack = ''
            else:
                raise ValueError('Wrong string!')
        if stack != '':
            raise ValueError('Wrong string!')
        if not (all('0' <= _ <= '9' for _ in m + p + s) and all('1' <= _ <= '7' for _ in z)):
            raise ValueError('Wrong string!')
        red_count = np.array([m.count('0'), p.count('0'), s.count('0')])
        m = list(map(lambda x: int(x) - 1, sorted(m.replace('0', '5'))))
        p = list(map(lambda x: int(x) + 9, sorted(p.replace('0', '5'))))
        s = list(map(lambda x: int(x) + 19, sorted(s.replace('0', '5'))))
        z = list(map(lambda x: 10 * (int(x) + 2), sorted(z)))
        return m + p + s + z, red_count

    def str2id(self, tiles: str):
        """
        万子:0-9m
        筒子:0-9p
        索子:0-9s
        东南西北:1-4z
        白发中:5-7z
        """
        hand_tiles, *called_tiles = tiles.split(' ')
        hand_tiles, red_count = self._str2id(hand_tiles)
        for i, called in enumerate(called_tiles):
            called_tiles[i], c = self._str2id(called)
            red_count += c
        return hand_tiles, called_tiles, red_count

    def _id2unicode(self, ids: Iterable[int]):
        return ''.join(map(ID2UNICODE.get, ids))

    def id2unicode(self, hand_tiles: Iterable[int], called_tiles: List[List[int]] = None):
        if called_tiles is None:
            called_tiles = []
        hand_tiles = self._id2unicode(hand_tiles)
        called_tiles = ' '.join(self._id2unicode(_) for _ in called_tiles)
        return ' '.join([hand_tiles, called_tiles]).strip()

    def _search_triplet(self, tiles: List[int]):
        res = []
        counter = Counter(tiles)
        for c, number in counter.items():
            if number >= 3:
                res.append((c, c, c))
        return res

    def _search_seq(self, tiles: List[int]):
        res = []
        tiles = list(set(tiles))
        tiles.sort()
        for i in range(len(tiles) - 2):
            if tiles[i] + 2 == tiles[i + 1] + 1 == tiles[i + 2]:
                res.append((tiles[i], tiles[i + 1], tiles[i + 2]))
        return res

    def _search_meld(self, tiles: List[int]):
        return self._search_triplet(tiles) + self._search_seq(tiles)

    def is_kong(self, tiles: List[int]):
        return 5 >= len(tiles) >= 4 and len(set(tiles)) == 1

    def is_exposed_kong(self, tiles: List[int]):
        return len(tiles) == 4 and len(set(tiles)) == 1

    def is_concealed_kong(self, tiles: List[int]):
        return len(tiles) == 5 and len(set(tiles)) == 1

    def is_pair(self, tiles: List[int]):
        return len(tiles) == 2 and tiles[0] == tiles[1]

    def is_triplet(self, tiles: List[int]):
        return len(tiles) == 3 and tiles[0] == tiles[1] == tiles[2]

    def is_seq(self, tiles: List[int]):
        return len(tiles) == 3 and tiles[0] + 2 == tiles[1] + 1 == tiles[2]

    def _remove_items(self, tiles: List[int], items: Iterable[int]):
        tiles = copy(tiles)
        for item in items:
            tiles.remove(item)
        return tiles

    def check_called_tiles(self, called_tiles: List[List[int]]):
        for called_meld in called_tiles:
            if not self.is_triplet(called_meld) and not self.is_seq(called_meld) and not self.is_kong(called_meld):
                return False
        return True

    def search_combinations(self, tiles: List[int], called_count):
        res = []
        counter = Counter(tiles)
        if called_count == 0:
            if all(i == 2 for i in counter.values()) and len(counter) == 7:
                res.append([(i, i) for i in counter.keys()])

        def split(tiles: List[int], current=None):
            current = current or []
            if len(tiles) == 2 and tiles[0] == tiles[1]:
                current.append((tiles[0], tiles[0]))
                if len(current) + called_count != 5:
                    return
                res.append(current)
                return
            melds = self._search_meld(tiles)
            if not melds:
                return
            for meld in melds:
                current.append(meld)
                tiles_left = self._remove_items(tiles, meld)
                split(tiles_left, deepcopy(current))
                current.pop()
        split(tiles)
        res = set([tuple(sorted(_, key=lambda x: (-len(x), x[0]))) for _ in res])
        return res

    def calculate_ready_hand(self, tiles: str, to_unicode=True):
        """
        听牌计算（必须包含雀头或单骑听雀头的情形）
        万子:1-9m
        筒子:1-9p
        索子:1-9s
        东南西北:1-4z
        白发中:5-7z
        :param tiles: 手牌字符串，若有副露则以空格隔离，例：19m19p19s1234567z，1233m 5555m 789m 123m
        :param to_unicode: 是否将结果转化为易读的字符串
        """
        hand_tiles, called_tiles, _ = self.str2id(tiles)
        if not self.check_called_tiles(called_tiles):
            return
        res = set()
        total_counter = Counter(hand_tiles + sum(called_tiles, []))

        if len(hand_tiles) == 13 and not called_tiles:
            """Check thirteen orphans"""
            diff = TERMINALS_HONORS.difference(set(hand_tiles))
            diff.update(set(hand_tiles).difference(TERMINALS_HONORS))
            if len(diff) <= 1:
                if len(diff) == 1:
                    res.add(diff.pop())
                else:
                    res.update(TERMINALS_HONORS)
                return self.id2unicode(res) if to_unicode else res

        for i in ALL:
            if total_counter[i] < 4:
                combs = self.search_combinations(hand_tiles + [i], len(called_tiles))
                if combs:
                    res.add(i)
        return self.id2unicode(res) if to_unicode else res
