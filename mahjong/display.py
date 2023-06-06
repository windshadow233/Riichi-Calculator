import base64
import streamlit as st
from typing import List, Iterable

BLANK = """<img class="blank-tile" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E">"""


@st.cache_resource
def load_png():
    pngs = {}
    for i in range(9):
        pngs[i] = f"app/static/png/{i + 1}man.png"
    pngs[-1] = "app/static/png/akaman.png"
    for i in range(10, 19):
        pngs[i] = f"app/static/png/{i - 9}pin.png"
    pngs[9] = "app/static/png/akapin.png"

    for i in range(20, 29):
        pngs[i] = f"app/static/png/{i - 19}sou.png"
    pngs[19] = "app/static/png/akasou.png"

    pngs[30] = "app/static/png/tan.png"

    pngs[40] = "app/static/png/nan.png"

    pngs[50] = "app/static/png/xia.png"

    pngs[60] = "app/static/png/pei.png"

    pngs[70] = "app/static/png/haku.png"

    pngs[80] = "app/static/png/hatsu.png"

    pngs[90] = "app/static/png/chun.png"

    pngs[-2] = "app/static/png/back.png"
    return pngs


def render_png(pngs):
    html = ''.join([f'<img class="tile" src="{_}"/>' if _ else BLANK for _ in pngs])
    return f'<div class="tiles">{html}</div>'


def _str2pngid(tiles: str):
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

    def sort_key(x):
        return x if x % 10 != 9 else x + 5

    m = list(sorted((map(lambda x: int(x) - 1, m)), key=sort_key))
    p = list(sorted(map(lambda x: int(x) + 9, p), key=sort_key))
    s = list(sorted(map(lambda x: int(x) + 19, s), key=sort_key))
    z = list(sorted(map(lambda x: 10 * (int(x) + 2), z)))
    return m + p + s + z


def str2pngid(tiles: str):
    items = tiles.split()
    for item in items:
        yield _str2pngid(item)


def id2png(ids: List[int]):
    pngs = list(map(PNGS.get, ids))
    return render_png(pngs)


def str2png(tiles: str, fold_concealed_kongs=False):
    seqs = str2pngid(tiles)
    id_list = []
    for seq in seqs:
        if len(seq) == 5 and len(set(seq)) == 1 and fold_concealed_kongs:
            id_list += [-2, seq[1], seq[2], -2, -3]
        else:
            id_list += seq + [-3]
    return id2png(id_list[:-1])


PNGS = load_png()
