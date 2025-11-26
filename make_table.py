import tqdm
import copy
from itertools import permutations
from mahjong.utils import *


def ptn(a):
    if len(a) == 1:
        return [a]
    ret = list(permutations(a))
    h1 = set()
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            key = str(a[i] + [0] + a[j])
            if key not in h1:
                h1.add(key)
                h2 = set()
                t1 = copy.deepcopy(a)
                t1.pop(i)
                t1.pop(j - 1)
                if len(a[i]) + len(a[j]) < 9:
                    ret += ptn([a[i] + [0] + a[j]] + t1)
                    ret += ptn([a[j] + [0] + a[i]] + t1)
                for k in range(len(a[i] + a[j]) + 1):
                    t = [0] * len(a[j]) + a[i] + [0] * len(a[j])
                    for m in range(len(a[j])):
                        t[k + m] += a[j][m]
                    t = list(filter(bool, t))
                    if any(_ > 4 for _ in t):
                        continue
                    if len(t) > 9:
                        continue
                    if str(t) not in h2:
                        h2.add(str(t))
                        t2 = copy.deepcopy(a)
                        t2.pop(i)
                        t2.pop(j - 1)
                        ret += ptn([t] + t2)
    return ret


def unique(ret):
    for i in range(len(ret)):
        ret[i] = tuple(map(tuple, ret[i]))
    ret = list(set(ret))
    for i in range(len(ret)):
        ret[i] = list(map(list, ret[i]))
    return ret


def remove_one_from_ptn(a):
    ptns = []
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] == 0:
                continue
            a[i][j] -= 1
            new_ptn = copy.deepcopy(a)
            a[i][j] += 1
            if new_ptn[i][j] != 0:
                ptns.append(new_ptn)
            else:
                if len(new_ptn[i]) == 1:
                    new_ptn.pop(i)
                    ptns.append(new_ptn)
                    continue
                if j == 0:
                    new_ptn[i].pop(0)
                elif j == len(a[i]) - 1:
                    new_ptn[i].pop()
                else:
                    if new_ptn[i][j - 1] == 0:
                        left, right = new_ptn[i][:j - 1], new_ptn[i][j + 1:]
                        new_ptn.pop(i)
                        new_ptn.insert(i, left)
                        if right:
                            new_ptn.insert(i + 1, right)
                    elif new_ptn[i][j + 1] == 0:
                        left, right = new_ptn[i][:j], new_ptn[i][j + 2:]
                        new_ptn.pop(i)
                        new_ptn.insert(i, right)
                        if left:
                            new_ptn.insert(i, left)
                    ptns.append(new_ptn)
    return ptns


agari_table = []
machi_table = []
chitoi = ptn([[2], [2], [2], [2], [2], [2], [2]])
chitoi = list(filter(lambda x: all(_ in [0, 2] for _ in sum(x, [])), chitoi))
chitoi = unique(chitoi)
agari_patterns = []
machi_patterns = []
for p in tqdm.tqdm(chitoi):
    agari_patterns.append(p)
    machi_patterns.extend(remove_one_from_ptn(p))
for a in [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [2]],
          [[1, 1, 1], [1, 1, 1], [1, 1, 1], [3], [2]],
          [[1, 1, 1], [1, 1, 1], [3], [3], [2]],
          [[1, 1, 1], [3], [3], [3], [2]],
          [[3], [3], [3], [3], [2]]]:
    ptns = unique(ptn(a))
    for p in tqdm.tqdm(ptns):
        agari_patterns.append(p)
        machi_patterns.extend(remove_one_from_ptn(p))

machi_patterns = unique(machi_patterns)
agari_patterns = unique(agari_patterns)


for p in machi_patterns:
    if sum(len(_) for _ in p) + 2 * (len(p) - 1) > 9:
        continue
    key = ptn2key(p)
    machi_table.append(key)
    assert ptn2key(key2ptn(key)) == key


for p in agari_patterns:
    if sum(len(_) for _ in p) + 2 * (len(p) - 1) > 9:
        continue
    key = ptn2key(p)
    agari_table.append(key)
    assert ptn2key(key2ptn(key)) == key


print('清一色听牌pattern数:', len(machi_table))
with open('data/MACHI_TABLE.pkl', 'wb') as f:
    f.write(pickle.dumps(machi_table))

with open('data/AGARI_TABLE.pkl', 'wb') as f:
    f.write(pickle.dumps(agari_table))