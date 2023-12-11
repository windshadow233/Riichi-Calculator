from mahjong.checker import *
import numpy as np
import math

NONE = 0
MAN_GAN = 1
HANE_MAN = 2
BAI_MAN = 3
SAN_BAI_MAN = 4
YAKU_MAN = 5
TOTAL_YAKU_MAN = 6

SCORE_LEVELS = {
    MAN_GAN: '满贯',
    HANE_MAN: '跳满',
    BAI_MAN: '倍满',
    SAN_BAI_MAN: '三倍满',
    YAKU_MAN: '役满',
    TOTAL_YAKU_MAN: '累计役满'
}


class ScoreCalculator:
    """以下判断以和了型为前提条件"""

    def __init__(self):
        self.tiles_str = ''
        self.checker = Mahjong()
        self._hand_counter = None
        self._counter = None
        self._tiles = []
        self._tiles_set = set()
        self._has_furu = False
        self._is_concealed_hand = False
        self._kuisagari = 0

        self._prevailing_wind = None
        self._dealer_wind = None
        self._is_self_draw = False
        self._riichi = None
        self.hand_aka_dora = []
        self._aka_dora = 0
        self.dora = []
        self.ura_dora = []
        self._north_dora = 0
        self._ippatsu = None
        self._is_three_player_game = False
        self._is_under_the_sea = False
        self._is_after_a_kong = False
        self._is_robbing_the_kong = False
        self._is_blessing_of_heaven = False
        self._is_blessing_of_earth = False

        self.hu_tile = None
        self.has_yaku = False
        self.hand_tiles, self.called_tiles = [], []
        self._is_thirteen_orphans = False
        self.is_hu = False
        self.combinations = []
        self.max_score_index = None

        self._use_ancient_yaku = False
        self._is_blessing_of_man = False
        self._tsubamegaeshi = False
        self._kanfuri = False

        self.fu = self.yaku_list = self.number = self.level = self.score = None

    def update(
            self,
            tiles: str,
            hu_tile: str,
            prevailing_wind,
            dealer_wind,
            is_self_draw,
            riichi,
            dora,
            ura_dora,
            north_dora=0,
            ippatsu=False,
            is_three_player_game=False,
            is_under_the_sea=False,
            is_after_a_kong=False,
            is_robbing_the_kong=False,
            is_blessing_of_heaven=False,
            is_blessing_of_earth=False,
            use_ancient_yaku=False,
            is_blessing_of_man=False,
            tsubamegaeshi=False,
            kanfuri=False
    ):
        """
        万子:0-9m
        饼子:0-9p
        索子:0-9s
        (其中，0是赤宝牌，即红色的5万、5饼、5索)
        东南西北:1-4z
        白发中:5-7z
        :param tiles: 手牌字符串，若有副露则以空格隔离，例：19m19p19s1234567z，1233m 5555m 789m 123m
        :param hu_tile: 和了牌
        :param prevailing_wind: 场风 (东:1, 南:2, 西:3, 北:4)
        :param dealer_wind: 自风 (同上)
        :param is_self_draw: 是否自摸
        :param riichi: 立直时值为1, 两立直时值为2, 否则为0 (非门清状态下此参数无效)
        :param dora: 宝牌指示牌(包含宝牌、杠宝牌)
        :param ura_dora: 里宝牌指示牌(包含里宝牌、杠里宝牌)
        :param north_dora: 拔北宝牌数(三麻限定，拔北宝牌数)
        :param ippatsu: 是否为一发(当riichi为0时,此参数无效)
        :param is_three_player_game: 是否为三麻
        :param is_under_the_sea: 是否为海底捞月、河底捞鱼
        :param is_after_a_kong: 是否为岭上开花(当is_self_draw为False或副露无杠时,此参数无效)
        :param is_robbing_the_kong: 是否为抢杠(当is_self_draw为True或手牌有此牌时,此参数无效)
        :param is_blessing_of_heaven: 是否为天和(非「亲家无副露自摸和」时,此参数无效)
        :param is_blessing_of_earth: 是否为地和(非「子家无副露自摸和」时,此参数无效)
        :param use_ancient_yaku: 是否使用古役（仅考虑雀魂麻将游戏里的古役）
        :param is_blessing_of_man: 是否为人和(非「子家无副露荣和」时,此参数无效)
        :param tsubamegaeshi: 是否触发燕返（use_ancient_yaku为True时有效）
        :param kanfuri: 是否杠振（use_ancient_yaku为True时有效）
        """
        self.__init__()
        self.tiles_str = tiles
        self.hu_tile, _ = self.checker.str2id(hu_tile)
        self.hu_tile = self.hu_tile[0]
        self.hand_tiles, self.called_tiles = self.checker.str2id(self.tiles_str)
        self.hand_tiles.append(self.hu_tile)

        self.hand_aka_dora = [self.hand_tiles.count(_) for _ in [AKA_MAN, AKA_PIN, AKA_SOU]]
        self.hand_tiles = list(sorted(map(lambda x: x + 5 if x in AKA_DORA else x, self.hand_tiles)))
        self._aka_dora = sum(self.hand_aka_dora)
        self._is_three_player_game = is_three_player_game

        self._hand_counter = Counter(self.hand_tiles)
        self._tiles.extend(self.hand_tiles)
        for i, meld in enumerate(self.called_tiles):
            aka_dora = np.array([meld.count(_) for _ in AKA_DORA]).clip(0, 4)
            self._aka_dora += sum(aka_dora)
            self.called_tiles[i] = meld = list(sorted(map(lambda x: x + 5 if x in AKA_DORA else x, meld)))
            if self.checker.is_concealed_kong(meld):
                self._tiles.extend([meld[0]] * 4)
            else:
                self._tiles.extend(meld)
        self._counter = Counter(self._tiles)
        if any(n > 4 for n in self._counter.values()):
            return
        if not self._is_three_player_game:
            north_dora = 0
        if north_dora + self._counter[60] > 4:
            return
        if not 18 >= len(self._tiles) >= 14:
            return
        self._tiles_set = set(self._tiles)
        self._has_furu = bool(self.called_tiles)
        self._is_concealed_hand = not self._has_furu or all(self.checker.is_concealed_kong(_) for _ in self.called_tiles)
        self._kuisagari = 1 - self._is_concealed_hand
        self._prevailing_wind = [30, 40, 50, 60][prevailing_wind - 1]
        self._dealer_wind = [30, 40, 50, 60][dealer_wind - 1]
        self._is_self_draw = is_self_draw
        self.dora = self.checker.str2id(dora)[0]
        self.dora = list(map(lambda x: x + 5 if x % 10 == 9 else x, self.dora))
        self.ura_dora = self.checker.str2id(ura_dora)[0]
        self.ura_dora = list(map(lambda x: x + 5 if x % 10 == 9 else x, self.ura_dora))
        self._north_dora = north_dora
        if not self._is_concealed_hand:
            riichi = 0
        self._riichi = riichi
        self._ippatsu = ippatsu and bool(riichi)
        self._is_under_the_sea = is_under_the_sea
        self._is_after_a_kong = is_after_a_kong and is_self_draw and any(self.checker.is_kong(_) for _ in self.called_tiles)
        self._is_robbing_the_kong = is_robbing_the_kong and not is_self_draw and self._counter[self.hu_tile] == 1
        self._is_blessing_of_heaven = is_blessing_of_heaven and dealer_wind == 1 and is_self_draw and not self._has_furu
        self._is_blessing_of_earth = is_blessing_of_earth and dealer_wind != 1 and is_self_draw and not self._has_furu

        self.combinations = list(self.checker.search_combinations(self.hand_tiles, len(self.called_tiles)))
        if not self.combinations and not self._has_furu:
            self._is_thirteen_orphans = self.thirteen_orphans()
        else:
            self._is_thirteen_orphans = False
        self.is_hu = bool(self.combinations) and self.checker.check_called_tiles(self.called_tiles) or bool(self._is_thirteen_orphans)
        self._use_ancient_yaku = use_ancient_yaku
        self._is_blessing_of_man = is_blessing_of_man and not is_self_draw and dealer_wind != 1 and not self._has_furu
        self._tsubamegaeshi = tsubamegaeshi and not self._is_self_draw
        self._kanfuri = kanfuri and not self._is_self_draw
        if self.is_hu:
            self.fu, self.yaku_list, self.number, self.level, self.score = self.calculate()

        if self.level == YAKU_MAN and self.score > 8000:
            number = self.score // 8000
            self.level = f'{number}倍役满'
        else:
            self.level = SCORE_LEVELS.get(self.level)

    def hand_unicode(self):
        return ''.join(ID2UNICODE[_] for _ in self.hand_tiles)

    def called_unicode(self):
        return '\u2001'.join(f'🀫{ID2UNICODE[_[0]]}{ID2UNICODE[_[0]]}🀫' if len(_) == 5 else ''.join(ID2UNICODE[tile] for tile in _) for _ in self.called_tiles)

    def dora_unicode(self):
        return ''.join(ID2UNICODE[_] for _ in self.dora)

    def ura_dora_unicode(self):
        return ''.join(ID2UNICODE[_] for _ in self.ura_dora)

    def __str__(self):
        if self.tiles_str == '':
            return ''
        s = "手牌: "
        s += self.hand_unicode()
        if self._has_furu:
            s += '\n副露: '
            s += self.called_unicode()
        if self.is_hu:
            s += f'\n和了牌: {ID2UNICODE[self.hu_tile]}'
            s += f'\n宝牌指示牌: {self.dora_unicode()}'
            if self._riichi:
                s += f'\n里宝牌指示牌: {self.ura_dora_unicode()}'
            s += f'\n符数: {self.fu}'
            s += '\n役种、宝牌: ' + '、'.join(self.yaku_list)
            s += f'\n番数: {self.number}'
            if self.level:
                s += f' ==> {self.level}'
            s += f'\n基本点: {self.score}'
        else:
            s += '\n没有和'
        return s

    def _is_sequence_hand(self, combination):
        """判断某一种组合是否满足平和(可非门清)"""
        two_sided_wait = False
        for tiles in combination:
            if self.checker.is_triplet(tiles):
                return 0
            if self.checker.is_pair(tiles):
                if tiles[0] in DRAGONS or tiles[0] == self._dealer_wind or tiles[0] == self._prevailing_wind:
                    return 0
            if self.checker.is_seq(tiles):
                if (self.hu_tile == tiles[0] and tiles[2] not in NINES) \
                        or (self.hu_tile == tiles[-1] and tiles[0] not in ONES):
                    two_sided_wait = True
        if two_sided_wait:
            return 1
        return 0

    def _is_seven_pairs(self, combination):
        """判断某一种组合是否满足七对子"""
        if len(combination) != 7:
            return 0
        if all(self.checker.is_pair(tiles) for tiles in combination):
            return 2
        return 0

    """一番"""

    def all_simple(self):
        """断幺九"""
        if self._tiles_set.isdisjoint(TERMINALS_HONORS):
            return 1
        return 0

    def concealed_hand_self_drawn(self):
        """门清自摸"""
        if self._is_concealed_hand and self._is_self_draw:
            return 1
        return 0

    def value_tiles(self):
        """役牌"""
        n = 0
        for called_tile in self.called_tiles:
            if called_tile[0] in DRAGONS:
                n += 1
            if called_tile[0] == self._prevailing_wind:
                n += 1
            if called_tile[0] == self._dealer_wind:
                n += 1
        combination = self.combinations[0]
        for tiles in combination:
            if self.checker.is_triplet(tiles):
                tile = tiles[0]
                if tile in DRAGONS:
                    n += 1
                if tile == self._prevailing_wind:
                    n += 1
                if tile == self._dealer_wind:
                    n += 1
        return n

    def sequence_hand(self):
        """平和(门清限定)"""
        if self._has_furu:
            return np.array([0])
        values = []
        for combination in self.combinations:
            if len(combination) != 5:
                values.append(0)
                continue
            value = self._is_sequence_hand(combination)
            values.append(value)
        return np.array(values)

    def shiiaruraotai(self):
        """古役 十二落抬"""
        if len(self.called_tiles) == 4:
            if all(not self.checker.is_concealed_kong(_) for _ in self.called_tiles):
                return 1
        return 0

    """二番"""

    def seven_pairs(self):
        """七对子(门清限定)"""
        if self._has_furu:
            return np.array([0])
        values = []
        for combination in self.combinations:
            values.append(self._is_seven_pairs(combination))
        return np.array(values)

    def all_pungs(self):
        """对对和"""
        values = []
        called_pung_count = sum(map(lambda x: self.checker.is_triplet(x) or self.checker.is_kong(x), self.called_tiles))
        for combination in self.combinations:
            s = sum(map(self.checker.is_triplet, combination))
            if s + called_pung_count == 4:
                values.append(2)
            else:
                values.append(0)
        return np.array(values)

    def three_kongs(self):
        """三杠子"""
        if sum(self.checker.is_kong(_) for _ in self.called_tiles) == 3:
            return 2
        return 0

    def small_three_dragons(self):
        """小三元"""
        c = [self._counter[i] for i in DRAGONS]
        if all(_ >= 2 for _ in c) and c.count(2) == 1:
            return 2
        return 0

    def three_concealed_triplets(self):
        """三暗刻"""
        values = []
        consealed_kong_count = sum(map(self.checker.is_concealed_kong, self.called_tiles))
        for combination in self.combinations:
            s = 0
            for tiles in combination:
                if self.checker.is_triplet(tiles):
                    if self.hu_tile != tiles[0] or self._is_self_draw or self._hand_counter[self.hu_tile] == 4:
                        s += 1
            if s + consealed_kong_count == 3:
                values.append(2)
            else:
                values.append(0)
        return np.array(values)

    def pure_straight(self):
        """一气通贯(副露减一番)"""
        values = []
        called_seqs = list(filter(self.checker.is_seq, self.called_tiles))
        called_seq_start_tiles = list(map(lambda x: x[0], called_seqs))
        for combination in self.combinations:
            seqs = list(filter(self.checker.is_seq, combination))
            seq_start_tiles = [_[0] for _ in seqs] + called_seq_start_tiles
            if len(seq_start_tiles) < 3:
                values.append(0)
                continue
            seq_start_tiles.sort()
            if seq_start_tiles[0] + 3 in seq_start_tiles and seq_start_tiles[0] + 6 in seq_start_tiles:
                values.append(2 - self._kuisagari)
            elif seq_start_tiles[1] + 3 in seq_start_tiles and seq_start_tiles[1] + 6 in seq_start_tiles:
                values.append(2 - self._kuisagari)
            else:
                values.append(0)
        return np.array(values)

    def all_mixed_terminals(self):
        """混老头"""
        if self._tiles_set.isdisjoint(HONORS):
            return 0
        if self._tiles_set.issubset(TERMINALS_HONORS) and not self._is_thirteen_orphans:
            return 2
        return 0

    def mixed_outside_hand(self):
        """混全带幺九(副露减一番)"""
        if self._tiles_set.isdisjoint(HONORS):
            return np.array([0])
        has_seq = any(self.checker.is_seq(_) for _ in self.called_tiles)
        for called_tile in self.called_tiles:
            if not called_tile[0] in TERMINALS_HONORS and not called_tile[-1] in TERMINALS_HONORS:
                return np.array([0])
        values = []
        for combination in self.combinations:
            comb_has_seq = has_seq
            for tiles in combination:
                if not tiles[0] in TERMINALS_HONORS and not tiles[-1] in TERMINALS_HONORS:
                    values.append(0)
                    break
                if not comb_has_seq:
                    comb_has_seq = self.checker.is_seq(tiles)
            else:
                if comb_has_seq:
                    values.append(2 - self._kuisagari)
                else:
                    values.append(0)
        return np.array(values)

    def mixed_triple_chow(self):
        """三色同顺(副露减一番)"""
        values = []
        called_seqs = list(filter(self.checker.is_seq, self.called_tiles))
        called_seq_start_tiles = list(map(lambda x: x[0], called_seqs))
        for combination in self.combinations:
            seqs = list(filter(self.checker.is_seq, combination))
            seq_start_tiles = [_[0] for _ in seqs] + called_seq_start_tiles
            if len(seq_start_tiles) < 3:
                values.append(0)
                continue
            seq_start_tiles.sort()
            if seq_start_tiles[0] + 10 in seq_start_tiles and seq_start_tiles[0] + 20 in seq_start_tiles:
                values.append(2 - self._kuisagari)
            elif seq_start_tiles[1] + 10 in seq_start_tiles and seq_start_tiles[1] + 20 in seq_start_tiles:
                values.append(2 - self._kuisagari)
            else:
                values.append(0)
        return np.array(values)

    def triple_pungs(self):
        """三色同刻"""
        values = []
        called_triplets = list(filter(lambda x: self.checker.is_triplet(x) or self.checker.is_kong(x), self.called_tiles))
        called_triplet_ids = list(map(lambda x: x[0], called_triplets))
        for combination in self.combinations:
            triplets = list(filter(self.checker.is_triplet, combination))
            tiles = [_[0] for _ in triplets] + called_triplet_ids
            if len(tiles) < 3:
                values.append(0)
                continue
            tiles.sort()
            if tiles[0] + 10 in tiles and tiles[0] + 20 in tiles:
                values.append(2)
            elif tiles[1] + 10 in tiles and tiles[1] + 20 in tiles:
                values.append(2)
            else:
                values.append(0)
        return np.array(values)

    def all_types(self):
        """古役 五门齐"""
        if not self._tiles_set.isdisjoint(MANS) \
            and not self._tiles_set.isdisjoint(PINS) \
            and not self._tiles_set.isdisjoint(SOUS) \
            and not self._tiles_set.isdisjoint(WINDS) \
            and not self._tiles_set.isdisjoint(DRAGONS):
            return 2
        return 0

    def three_consecutive_triplets(self):
        """古役 三连刻"""
        values = []
        called_triplets = list(filter(lambda x: self.checker.is_triplet(x) or self.checker.is_kong(x), self.called_tiles))
        called_triplet_ids = list(map(lambda x: x[0], called_triplets))
        for combination in self.combinations:
            triplets = list(filter(self.checker.is_triplet, combination))
            tiles = [_[0] for _ in triplets] + called_triplet_ids
            if len(tiles) < 3:
                values.append(0)
                continue
            tiles.sort()
            if tiles[0] + 1 in tiles and tiles[0] + 2 in tiles:
                values.append(2)
            elif tiles[1] + 1 in tiles and tiles[1] + 2 in tiles:
                values.append(2)
            else:
                values.append(0)
        return np.array(values)

    """三番"""

    def pure_double_chows(self):
        """二杯口（一杯口1番）（门清限定）"""
        if self._has_furu:
            return np.array([0])
        values = []
        for combination in self.combinations:
            seqs = filter(self.checker.is_seq, combination)
            seq_start_tiles = [_[0] for _ in seqs]
            count = Counter(seq_start_tiles)
            if not count:
                values.append(0)
            elif list(count.values()) in [[2, 2], [4]]:
                values.append(3)
            elif sum(map(lambda x: x >= 2, count.values())) == 1:
                values.append(1)
            else:
                values.append(0)
        return np.array(values)

    def outside_hand(self):
        """纯全带幺九（副露减一番）"""
        for called_tile in self.called_tiles:
            if not called_tile[0] in TERMINALS and not called_tile[-1] in TERMINALS:
                return np.array([0])
        values = []
        for combination in self.combinations:
            for tiles in combination:
                if not tiles[0] in TERMINALS and not tiles[-1] in TERMINALS:
                    values.append(0)
                    break
            else:
                values.append(3 - self._kuisagari)
        return np.array(values)

    def three_identical_sequences(self):
        """古役 一色三同顺 （副露减一番）"""
        called_seq_start_tiles = [_[0] for _ in filter(self.checker.is_seq, self.called_tiles)]
        values = []
        for combination in self.combinations:
            seqs = filter(self.checker.is_seq, combination)
            seq_start_tiles = [_[0] for _ in seqs]
            count = Counter(seq_start_tiles + called_seq_start_tiles)
            if not count:
                values.append(0)
            elif any(_ >= 3 for _ in count.values()):
                values.append(3 - self._kuisagari)
            else:
                values.append(0)
        return np.array(values)

    """六番"""

    def pure_hand(self):
        """染手，（混一色3番）(副露减一番)"""
        rm_honor = self._tiles_set.difference(HONORS)
        if rm_honor.issubset(MANS) or rm_honor.issubset(PINS) or rm_honor.issubset(SOUS):
            if self._tiles_set.isdisjoint(HONORS):
                return 6 - self._kuisagari
            return 3 - self._kuisagari
        return 0

    """满贯"""

    def ippinmoyue(self):
        """古役 一筒摸月"""
        if self._is_under_the_sea and self._is_self_draw and self.hu_tile == 10:
            return 5
        return 0

    def cyupinraoyui(self):
        """古役 九筒捞鱼"""
        if self._is_under_the_sea and not self._is_self_draw and self.hu_tile == 18:
            return 5
        return 0

    """役满"""

    def four_concealed_triplets(self):
        """四暗刻、四暗刻单骑（门清限定）"""
        if not self._is_concealed_hand:
            return 0
        consealed_kong_count = sum(map(self.checker.is_concealed_kong, self.called_tiles))
        for i, combination in enumerate(self.combinations):
            s = 0
            is_tanki = False
            for tiles in combination:
                if self.checker.is_triplet(tiles):
                    if self.hu_tile != tiles[0] or self._is_self_draw:
                        s += 1
                if self.checker.is_pair(tiles) and self.hu_tile == tiles[0]:
                    is_tanki = True
            if s + consealed_kong_count == 4:
                self.max_score_index = i
                if is_tanki or self._is_blessing_of_heaven:
                    return 26
                return 13
        return 0

    def thirteen_orphans(self):
        """国士无双（十三面）（门清限定）"""
        if self._has_furu:
            return 0
        if self._tiles_set == TERMINALS_HONORS and len(self.hand_tiles) == 14:
            if self._counter[self.hu_tile] > 1 or self._is_blessing_of_heaven:
                """国士十三面"""
                return 26
            return 13
        return 0

    def four_kongs(self):
        """四杠子"""
        if sum(self.checker.is_kong(_) for _ in self.called_tiles) == 4:
            return 13
        return 0

    def big_three_dragons(self):
        """大三元"""
        if all(self._counter[i] >= 3 for i in DRAGONS):
            return 13
        return 0

    def all_green(self):
        """绿一色"""
        if self._tiles_set.issubset(GREENS):
            return 13
        return 0

    def all_honors(self):
        """字一色"""
        if self._tiles_set.issubset(HONORS):
            return 13
        return 0

    def four_winds(self):
        """小四喜、大四喜"""
        c = [self._counter[i] for i in WINDS]
        if all(_ >= 2 for _ in c):
            pair_count = c.count(2)
            if pair_count == 1:
                return 13
            if pair_count == 0:
                return 26
        return 0

    def all_terminals(self):
        """清老头"""
        if self._tiles_set.issubset(TERMINALS):
            return 13
        return 0

    def nine_gates(self):
        """（纯正）九莲宝灯（门清限定）"""
        if self._has_furu:
            return 0
        d = copy(self._hand_counter)
        first_tile = self._tiles[0]
        if first_tile not in ONES:
            return 0
        d[first_tile] -= 3
        for offset in range(1, 8):
            d[first_tile + offset] -= 1
        d[first_tile + 8] -= 3
        extra = list(filter(lambda x: d[x] == 1, d))
        if all(map(lambda x: x >= 0, d.values())) and extra:
            if extra[0] == self.hu_tile or self._is_blessing_of_heaven:
                return 26
            return 13
        return 0

    def big_seven_stars(self):
        """古役 大七星（门清限定）"""
        if self._has_furu:
            return 0
        if self.hand_tiles == [30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80, 80, 90, 90]:
            return 26
        return 0

    def big_wheels(self):
        """古役 大车轮"""
        if self._has_furu:
            return 0
        if self.hand_tiles == [11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17]:
            return 13
        return 0

    def big_bamboos(self):
        """古役 大竹林"""
        if self._has_furu:
            return 0
        if self.hand_tiles == [21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27]:
            return 13
        return 0

    def big_numbers(self):
        """古役 大数邻"""
        if self._has_furu:
            return 0
        if self.hand_tiles == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]:
            return 13
        return 0

    def three_years_on_stone(self):
        """古役 石上三年"""
        if self._riichi == 2 and self._is_under_the_sea:
            return 13
        return 0

    def fussu(self):
        """计算符数"""
        if self._is_thirteen_orphans:
            """国士无双固定为25符"""
            return np.array([25])
        values = []
        fixed_value = 20
        if self._is_concealed_hand and not self._is_self_draw:
            fixed_value += 10

        for called_tiles in self.called_tiles:
            if self.checker.is_triplet(called_tiles):
                if called_tiles[0] in TERMINALS_HONORS:
                    fixed_value += 4
                else:
                    fixed_value += 2
            elif self.checker.is_exposed_kong(called_tiles):
                if called_tiles[0] in TERMINALS_HONORS:
                    fixed_value += 16
                else:
                    fixed_value += 8
            elif self.checker.is_concealed_kong(called_tiles):
                if called_tiles[0] in TERMINALS_HONORS:
                    fixed_value += 32
                else:
                    fixed_value += 16
        for combination in self.combinations:
            value = fixed_value
            wait_form = None
            if self._is_seven_pairs(combination):
                """七对子固定为25符"""
                values.append(25)
                continue
            if fixed_value == 20:
                if self._is_sequence_hand(combination):
                    """平和型手牌"""
                    if not self._has_furu:
                        """平和没有其他附加的符"""
                        values.append(value)
                        continue
                    else:
                        """副露平和型固定为30符"""
                        values.append(30)
                        continue
            if self._is_self_draw:
                value += 2
            for tiles in combination:
                if self.checker.is_triplet(tiles):
                    exposed_divide = 1
                    if tiles[0] == self.hu_tile and not self._is_self_draw and self._hand_counter[self.hu_tile] == 3:
                        exposed_divide = 2
                    if tiles[0] in TERMINALS_HONORS:
                        value += 8 / exposed_divide
                    else:
                        value += 4 / exposed_divide
                if self.checker.is_pair(tiles):
                    if tiles[0] == self._prevailing_wind:
                        value += 2
                    if tiles[0] == self._dealer_wind:
                        value += 2
                    if tiles[0] in DRAGONS:
                        value += 2
                if wait_form is None:
                    if self.checker.is_seq(tiles) and self.hu_tile in tiles:
                        if self.hu_tile == tiles[1]:
                            value += 2
                            wait_form = 0
                        else:
                            if not (self.hu_tile == tiles[0] and tiles[2] not in NINES) \
                                    and not (self.hu_tile == tiles[-1] and tiles[0] not in ONES):
                                value += 2
                                wait_form = 1
                    if self.checker.is_pair(tiles) and self.hu_tile == tiles[0]:
                        value += 2
                        wait_form = 2
            values.append(math.ceil(value / 10) * 10)
        return np.array(values)

    def _calc_dora(self, x):
        if x in NINES:
            return x - 8
        if x in WINDS:
            return ((x // 10 - 2) % 4 + 3) * 10
        if x in DRAGONS:
            return ((x // 10 - 6) % 3 + 7) * 10
        if x == 0 and self._is_three_player_game:
            return 8
        return x + 1

    def dora_count(self):
        n = self._north_dora + self._aka_dora
        dora = map(self._calc_dora, self.dora)
        counter = copy(self._counter)
        counter.update([60] * self._north_dora)
        n += sum(counter[_] for _ in dora)
        if self._riichi:
            ura_dora = map(self._calc_dora, self.ura_dora)
            n += sum(counter[_] for _ in ura_dora)
        return n

    def calculate(self):
        """计算基本点数"""
        yaku_list: List[str] = []
        full = 0
        fu = self.fussu()
        if self._is_blessing_of_heaven:
            yaku_list.append('天和(役满)')
            full += 1
        if self._is_blessing_of_earth:
            yaku_list.append('地和(役满)')
            full += 1
        if self._use_ancient_yaku:
            if self._is_blessing_of_man:
                yaku_list.append('人和(役满)')
                full += 1
            if self.three_years_on_stone():
                yaku_list.append('石上三年(役满)')
                full += 1
        n = self.four_kongs()
        if n != 0:
            yaku_list.append('四杠子(役满)')
            full += 1
        n = self.big_three_dragons()
        if n != 0:
            yaku_list.append('大三元(役满)')
            full += 1
        n = self.all_green()
        if n != 0:
            yaku_list.append('绿一色(役满)')
            full += 1
        n = self.all_honors()
        if n != 0:
            yaku_list.append('字一色(役满)')
            full += 1
        n = self.four_winds()
        if n != 0:
            if n == 26:
                yaku_list.append('大四喜(2倍役满)')
                full += 2
            else:
                yaku_list.append('小四喜(役满)')
                full += 1
        n = self.all_terminals()
        if n != 0:
            yaku_list.append('清老头(役满)')
            full += 1
        n = self.four_concealed_triplets()
        if n != 0:
            if n == 26:
                yaku_list.append('四暗刻单骑(2倍役满)')
                full += 2
            else:
                yaku_list.append('四暗刻(役满)')
                full += 1
        n = self._is_thirteen_orphans
        if n != 0:
            if n == 26:
                yaku_list.append('国士无双十三面(2倍役满)')
                full += 2
            else:
                yaku_list.append('国士无双(役满)')
                full += 1
        n = self.nine_gates()
        if n != 0:
            if n == 26:
                yaku_list.append('纯正九莲宝灯(2倍役满)')
                full += 2
            else:
                yaku_list.append('九莲宝灯(役满)')
                full += 1
        if self._use_ancient_yaku:
            if self.big_seven_stars():
                n = 26
                yaku_list.append('大七星(2倍役满)')
            elif self.big_wheels():
                n = 13
                yaku_list.append('大车轮(役满)')
            elif self.big_bamboos():
                n = 13
                yaku_list.append('大竹林(役满)')
            elif self.big_numbers():
                n = 13
                yaku_list.append('大数邻(役满)')
            else:
                n = 0
            full += n // 13
        if full:
            self.has_yaku = True
            fu = np.max(fu)
            if self.max_score_index is None:
                self.max_score_index = 0
            return fu, yaku_list, 13 * full, YAKU_MAN, full * 8000
        number = np.zeros(shape=len(self.combinations))
        common_yaku_list = []
        if self._is_under_the_sea:
            if self._is_self_draw:
                if self._use_ancient_yaku and self.ippinmoyue():
                    common_yaku_list.append('一筒摸月(5番)')
                    n = 5
                else:
                    common_yaku_list.append('海底捞月(1番)')
                    n = 1
            else:
                if self._use_ancient_yaku and self.cyupinraoyui():
                    common_yaku_list.append('九筒捞鱼(5番)')
                    n = 5
                else:
                    common_yaku_list.append('河底捞鱼(1番)')
                    n = 1
            number += n
        if self._is_after_a_kong:
            common_yaku_list.append('岭上开花(1番)')
            number += 1
        if self._is_robbing_the_kong:
            common_yaku_list.append('抢杠(1番)')
            number += 1
        if self._use_ancient_yaku:
            if self._tsubamegaeshi:
                common_yaku_list.append('燕返(1番)')
                number += 1
            if self._kanfuri:
                common_yaku_list.append('杠振(1番)')
                number += 1
        yaku_list: List[List[str]] = [[] for _ in self.combinations]
        number += self._riichi
        if self._riichi == 1:
            common_yaku_list.append('立直(1番)')
        elif self._riichi == 2:
            common_yaku_list.append('两立直(2番)')
        if self._ippatsu:
            common_yaku_list.append('一发(1番)')
            number += 1
        if self.concealed_hand_self_drawn():
            common_yaku_list.append('门前清自摸和(1番)')
            number += 1

        values = self.sequence_hand()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('平和(1番)')
        number += values

        values = self.seven_pairs()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('七对子(2番)')
        number += values

        values = self.pure_double_chows()
        for i in np.where(values != 0)[0]:
            if values[i] == 3:
                yaku_list[i].append('二杯口(3番)')
            elif values[i] == 1:
                yaku_list[i].append('一杯口(1番)')
        number += values

        n = self.all_simple()
        if n != 0:
            common_yaku_list.append('断幺九(1番)')
        number += n

        n = self.value_tiles()
        if n != 0:
            common_yaku_list.append(f'役牌({n}番)')
        number += n

        values = self.all_pungs()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('对对和(2番)')
        number += values

        n = self.three_kongs()
        if n != 0:
            common_yaku_list.append('三杠子(2番)')
        number += n

        n = self.small_three_dragons()
        if n != 0:
            common_yaku_list.append('小三元(2番)')
        number += n

        values = self.three_concealed_triplets()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('三暗刻(2番)')
        number += values

        values = self.pure_straight()
        n = np.max(values)
        for i in np.where(values != 0)[0]:
            yaku_list[i].append(f'一气通贯({n}番)')
        number += values

        n = self.all_mixed_terminals()
        if n != 0:
            common_yaku_list.append('混老头(2番)')
        number += n

        values = self.mixed_outside_hand()
        n = np.max(values)
        for i in np.where(values != 0)[0]:
            yaku_list[i].append(f'混全带幺九({n}番)')
        number += values

        values = self.mixed_triple_chow()
        n = np.max(values)
        for i in np.where(values != 0)[0]:
            yaku_list[i].append(f'三色同顺({n}番)')
        number += values

        values = self.triple_pungs()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('三色同刻(2番)')
        number += values

        values = self.outside_hand()
        n = np.max(values)
        for i in np.where(values != 0)[0]:
            yaku_list[i].append(f'纯全带幺九({n}番)')
        number += values

        if self._use_ancient_yaku:
            values = self.three_identical_sequences()
            n = np.max(values)
            for i in np.where(values != 0)[0]:
                yaku_list[i].append(f'一色三同顺({n}番)')
            number += values

            n = self.all_types()
            if n:
                common_yaku_list.append('五门齐(2番)')
            number += n

            values = self.three_consecutive_triplets()
            for i in np.where(values != 0)[0]:
                yaku_list[i].append('三连刻(2番)')
            number += values

            n = self.shiiaruraotai()
            if n:
                common_yaku_list.append('十二落抬(1番)')
            number += n

        n = self.pure_hand()
        if n != 0:
            if n <= 3:
                common_yaku_list.append(f'混一色({n}番)')
            else:
                common_yaku_list.append(f'清一色({n}番)')
        number += n
        dora_count = self.dora_count()
        number += dora_count
        score = fu * 2 ** (number + 2)
        max_score = np.max(score)
        if (score == max_score).sum() == 1:
            self.max_score_index = score.argmax()
        else:
            self.max_score_index = ((score == max_score) * number).argmax()
        i = self.max_score_index
        fu = fu[i]
        yaku = yaku_list[i]
        score = score[i]
        number = number[i]
        if number - dora_count > 0:
            self.has_yaku = True
        if number < 5:
            if score > 2000:
                score = 2000
                level = MAN_GAN
            else:
                level = NONE
        elif number == 5:
            score = 2000
            level = MAN_GAN
        elif 6 <= number <= 7:
            score = 3000
            level = HANE_MAN
        elif 8 <= number <= 10:
            score = 4000
            level = BAI_MAN
        elif 11 <= number <= 12:
            score = 6000
            level = SAN_BAI_MAN
        else:
            score = 8000
            level = TOTAL_YAKU_MAN
        if dora_count:
            yaku.append(f'ドラ {dora_count}')
        return fu, common_yaku_list + yaku, int(number), level, int(score)


if __name__ == '__main__':
    calculator = ScoreCalculator()
    calculator.update(
        tiles='55z66z 77777z 11111z 11111s',
        hu_tile='5z',
        prevailing_wind=1,
        dealer_wind=1,
        is_self_draw=0,
        riichi=2,
        dora='363z99s',
        ura_dora='99s336z',
        north_dora=4,
        ippatsu=False,
        is_under_the_sea=True,
        is_after_a_kong=False,
        is_robbing_the_kong=False,
        is_blessing_of_heaven=False,
        is_blessing_of_earth=False,
        use_ancient_yaku=False
    )
    print(calculator)
