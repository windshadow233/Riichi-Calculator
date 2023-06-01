from checker import *
import re
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
        self._has_furu = None
        self._is_concealed_hand = None
        self._kuisagari = 0

        self._prevailing_wind = None
        self._dealer_wind = None
        self._is_self_draw = None
        self._lichi = None
        self._dora = None
        self._ippatsu = None
        self._is_under_the_sea = None
        self._is_after_a_kong = None
        self._is_robbing_the_kong = None
        self._is_blessing_of_heaven = None
        self._is_blessing_of_earth = None

        self.hu_tile = None
        self.has_yaku = False
        self.hand_tiles, self.called_tiles = [], []
        self.is_hu = False
        self.combinations = []
        self.max_score_index = None

        self.fu = self.yaku_list = self.number = self.level = self.score = None

    def update(
            self,
            tiles: str,
            hu_tile: str,
            prevailing_wind,
            dealer_wind,
            is_self_draw,
            lichi,
            dora,
            ippatsu=False,
            is_under_the_sea=False,
            is_after_a_kong=False,
            is_robbing_the_kong=False,
            is_blessing_of_heaven=False,
            is_blessing_of_earth=False
    ):
        """
        万子:1-9m
        筒子:1-9p
        索子:1-9s
        东南西北:1-4z
        白发中:5-7z
        :param tiles: 手牌字符串，若有副露则以空格隔离，例：19m19p19s1234567z，1233m 5555m 789m 123m
        :param hu_tile: 和了牌
        :param prevailing_wind: 场风 (东:1, 南:2, 西:3, 北:4)
        :param dealer_wind: 自风 (同上)
        :param is_self_draw: 是否自摸
        :param lichi: 立直时值为1, 两立直时值为2, 否则为0 (非门清状态下此参数无效)
        :param dora: 宝牌数量(包含宝牌、立直翻的里宝牌、赤宝牌)
        :param ippatsu: 是否为一发(当lichi为0时,此参数无效)
        :param is_under_the_sea: 是否为海底捞月、河底捞鱼
        :param is_after_a_kong: 是否为岭上开花(当is_self_draw为False或副露无杠时,此参数无效)
        :param is_robbing_the_kong: 是否为抢杠(当is_self_draw为True或手牌有此牌时,此参数无效)
        :param is_blessing_of_heaven: 是否为天和(非「亲家无副露自摸和」时,此参数无效)
        :param is_blessing_of_earth: 是否为地和(非「子家无副露自摸和」时,此参数无效)
        """
        self.is_hu = False
        self.tiles_str = tiles
        self.hu_tile = self.checker.str2id(hu_tile)[0][0]
        self.hand_tiles, self.called_tiles = self.checker.str2id(self.tiles_str)
        self.hand_tiles.append(self.hu_tile)
        self._hand_counter = Counter(self.hand_tiles)
        self._tiles += self.hand_tiles
        for meld in self.called_tiles:
            if self.checker.is_concealed_kong(meld):
                self._tiles += [meld[0]] * 4
            else:
                self._tiles += meld
        self._counter = Counter(self._tiles)
        if any(n > 4 for n in self._counter.values()):
            return
        self._tiles_set = set(self._tiles)
        if not 18 >= len(self._tiles) >= 14:
            return
        self.combinations = list(self.checker.search_combinations(self.hand_tiles, len(self.called_tiles)))
        self.is_hu = bool(self.combinations) and self.checker.check_called_tiles(self.called_tiles)
        self._has_furu = bool(self.called_tiles)
        self._is_concealed_hand = not self._has_furu or all(self.checker.is_concealed_kong(_) for _ in self.called_tiles)
        self._kuisagari = 1 - self._is_concealed_hand
        if self.thirteen_orphans():
            self.is_hu = True

        self._prevailing_wind = [30, 40, 50, 60][prevailing_wind - 1]
        self._dealer_wind = [30, 40, 50, 60][dealer_wind - 1]
        self._is_self_draw = is_self_draw
        if not self._is_concealed_hand:
            lichi = 0
        self._lichi = lichi
        self._dora = dora
        self._ippatsu = ippatsu and bool(lichi)
        self._is_under_the_sea = is_under_the_sea
        self._is_after_a_kong = is_after_a_kong and is_self_draw and any(self.checker.is_kong(_) for _ in self.called_tiles)
        self._is_robbing_the_kong = is_robbing_the_kong and not is_self_draw and self._counter[self.hu_tile] == 1
        self._is_blessing_of_heaven = is_blessing_of_heaven and dealer_wind == 1 and is_self_draw and not self._has_furu
        self._is_blessing_of_earth = is_blessing_of_earth and dealer_wind != 1 and is_self_draw and not self._has_furu

        if self.is_hu:
            self.fu, self.yaku_list, self.number, self.level, self.score = self.calculate()

        if self.level == YAKU_MAN and self.score > 8000:
            number = self.score // 8000
            self.level = f'{number}倍役满'
        else:
            self.level = SCORE_LEVELS.get(self.level)

    def hand_string(self):
        return ' '.join(ID2NAME[tile] for tile in self.hand_tiles)

    def called_string(self):
        s = ''
        for called_tile in self.called_tiles:
            if len(called_tile) == 5:
                s += f'「█ {ID2NAME[called_tile[0]]} {ID2NAME[called_tile[0]]} █」'
            else:
                s += '「' + ' '.join(ID2NAME[tile] for tile in called_tile) + '」'
        return s

    def __str__(self):
        if self.tiles_str == '':
            return ''
        s = "手牌: "
        s += self.hand_string()
        if self._has_furu:
            s += '\n副露: '
            s += self.called_string()
        if self.is_hu:
            s += f'\n和了牌: {ID2NAME[self.hu_tile]}'
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

    def pure_double_chow(self):
        """一杯口（门清限定）"""
        values = []
        if not self._is_concealed_hand:
            return np.array([0])
        for combination in self.combinations:
            seqs = filter(self.checker.is_seq, combination)
            seq_start_tiles = [_[0] for _ in seqs]
            count = Counter(seq_start_tiles)
            if not count:
                values.append(0)
                continue
            if max(count.values()) == 4:
                values.append(0)
                continue
            if sum(map(lambda x: x >= 2, count.values())) == 1:
                values.append(1)
            else:
                values.append(0)
        return np.array(values)

    def value_tiles(self):
        """役牌番数"""
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
        if (self._counter[70] == 2 and self._counter[80] >= 3 and self._counter[90] >= 3) or\
               (self._counter[70] >= 3 and self._counter[80] == 2 and self._counter[90] >= 3) or \
               (self._counter[70] >= 3 and self._counter[80] >= 3 and self._counter[90] == 2):
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
        if self._tiles_set.issubset(TERMINALS_HONORS) and not self.thirteen_orphans():
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
                    if self.checker.is_seq(tiles):
                        comb_has_seq = True
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

    """三番"""

    def mixed_pure_hand(self):
        """混一色(副露减一番)"""
        if self._tiles_set.isdisjoint(HONORS):
            return 0
        rm_honor = self._tiles_set.difference(HONORS)
        if rm_honor.issubset(CHARACTERS) or rm_honor.issubset(DOTS) or rm_honor.issubset(BAMBOOS):
            return 3 - self._kuisagari
        return 0

    def twice_pure_double_chows(self):
        """二杯口（门清限定）"""
        if self._has_furu:
            return np.array([0])
        values = []
        for combination in self.combinations:
            seqs = filter(self.checker.is_seq, combination)
            seq_start_tiles = [_[0] for _ in seqs]
            count = Counter(seq_start_tiles)
            if list(count.values()) in [[2, 2], [4]]:
                values.append(3)
            else:
                values.append(0)
        return np.array(values)

    def outside_hand(self):
        """全纯带幺九(副露减一番)"""
        for called_tile in self.called_tiles:
            if not called_tile[0] in TERMINALS and not called_tile[-1] in TERMINALS:
                return np.zeros(shape=len(self.combinations))
        values = []
        for combination in self.combinations:
            for tiles in combination:
                if not tiles[0] in TERMINALS and not tiles[-1] in TERMINALS:
                    values.append(0)
                    break
            else:
                values.append(3 - self._kuisagari)
        return np.array(values)

    """六番"""

    def pure_hand(self):
        """清一色(副露减一番)"""
        if self._tiles_set.issubset(CHARACTERS) or self._tiles_set.issubset(DOTS) or self._tiles_set.issubset(BAMBOOS):
            return 6 - self._kuisagari
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
                if is_tanki:
                    return 26
                return 13
        return 0

    def thirteen_orphans(self):
        """国士无双（十三面）（门清限定）"""
        if self._has_furu:
            return 0
        if self._tiles_set == TERMINALS_HONORS and len(self.hand_tiles) == 14:
            if self._tiles.count(self.hu_tile) > 1:
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
        called_winds = sum(map(lambda x: x[0] in WINDS, self.called_tiles))
        n = 0
        pair = 0
        for i, combination in enumerate(self.combinations):
            for tiles in combination:
                if tiles[0] in WINDS:
                    if self.checker.is_triplet(tiles):
                        n += 1
                    else:
                        pair += 1
            if called_winds + n == 3 and pair:
                self.max_score_index = i
                return 13
            if called_winds + n == 4:
                self.max_score_index = i
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
            if extra[0] == self.hu_tile:
                return 26
            return 13
        return 0

    def fussu(self):
        """计算符数"""
        if self.thirteen_orphans():
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
                            if not (self.hu_tile == tiles[0] and tiles[2] not in [8, 17, 26]) \
                                    and not (self.hu_tile == tiles[-1] and tiles[0] not in [0, 9, 18]):
                                value += 2
                                wait_form = 1
                    if self.checker.is_pair(tiles) and self.hu_tile == tiles[0]:
                        value += 2
                        wait_form = 2
            values.append(math.ceil(value / 10) * 10)
        return np.array(values)

    def calculate(self):
        """计算番数"""
        yaku_list: List[str] = []
        full = 0
        fu = self.fussu()
        if self._is_blessing_of_heaven:
            yaku_list.append('天和(役满)')
            full += 1
        if self._is_blessing_of_earth:
            yaku_list.append('地和(役满)')
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
        n = self.thirteen_orphans()
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
                common_yaku_list.append('海底捞月(1番)')
            else:
                common_yaku_list.append('河底捞鱼(1番)')
            number += 1
        if self._is_after_a_kong:
            common_yaku_list.append('岭上开花(1番)')
            number += 1
        if self._is_robbing_the_kong:
            common_yaku_list.append('抢杠(1番)')
            number += 1
        yaku_list: List[List[str]] = [[] for _ in self.combinations]
        number += self._lichi
        if self._lichi == 1:
            common_yaku_list.append('立直(1番)')
        elif self._lichi == 2:
            common_yaku_list.append('两立直(2番)')
        if self._ippatsu:
            common_yaku_list.append('一发(1番)')
            number += 1
        if self.concealed_hand_self_drawn():
            common_yaku_list.append('门前清自摸和(1番)')
            number += 1

        values = self.pure_double_chow()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('一杯口(1番)')
        number += values

        values = self.sequence_hand()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('平和(1番)')
        number += values

        values = self.seven_pairs()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('七对子(2番)')
        number += values

        values = self.twice_pure_double_chows()
        for i in np.where(values != 0)[0]:
            yaku_list[i].append('二杯口(3番)')
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

        n = self.mixed_pure_hand()
        if n != 0:
            common_yaku_list.append(f'混一色({n}番)')
        number += n

        values = self.outside_hand()
        n = np.max(values)
        for i in np.where(values != 0)[0]:
            yaku_list[i].append(f'纯全带幺九({n}番)')
        number += values

        n = self.pure_hand()
        if n != 0:
            common_yaku_list.append(f'清一色({n}番)')
        number += n
        number += self._dora
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
        if number - self._dora > 0:
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
        if self._dora:
            yaku.append(f'DORA {self._dora}')
        return fu, common_yaku_list + yaku, int(number), level, int(score)


if __name__ == '__main__':
    calculator = ScoreCalculator()
    calculator.update(
        tiles='111m999m1z 111s 999s',
        hu_tile='1z',
        prevailing_wind=1,
        dealer_wind=1,
        is_self_draw=0,
        lichi=0,
        dora=0,
        ippatsu=False,
        is_under_the_sea=True,
        is_after_a_kong=False,
        is_robbing_the_kong=False,
        is_blessing_of_heaven=False,
        is_blessing_of_earth=False
    )
    print(calculator)
