import base64
from typing import List, Iterable

BLANK = """<img class="blank-tile" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E">"""

SVGS = {}


def load_svg():
    for i in range(9):
        with open(f"static/svg/{i + 1}man.svg", "r") as f:
            SVGS[i] = f.read()
    with open("static/svg/akaman.svg", "r") as f:
        SVGS[-1] = f.read()

    for i in range(10, 19):
        with open(f"static/svg/{i - 9}pin.svg", "r") as f:
            SVGS[i] = f.read()
    with open("static/svg/akapin.svg", "r") as f:
        SVGS[9] = f.read()

    for i in range(20, 29):
        with open(f"static/svg/{i - 19}sou.svg", "r") as f:
            SVGS[i] = f.read()
    with open("static/svg/akasou.svg", "r") as f:
        SVGS[19] = f.read()

    with open("static/svg/tan.svg", "r") as f:
        SVGS[30] = f.read()

    with open("static/svg/nan.svg", "r") as f:
        SVGS[40] = f.read()

    with open("static/svg/xia.svg", "r") as f:
        SVGS[50] = f.read()

    with open("static/svg/pei.svg", "r") as f:
        SVGS[60] = f.read()

    with open("static/svg/haku.svg", "r") as f:
        SVGS[70] = f.read()

    with open("static/svg/hatsu.svg", "r") as f:
        SVGS[80] = f.read()

    with open("static/svg/chun.svg", "r") as f:
        SVGS[90] = f.read()

    with open("static/svg/back.svg", "r") as f:
        SVGS[-2] = f.read()


def render_svg(svgs):
    """Renders the given svg string."""
    b64 = [base64.b64encode(svg.encode('utf-8')).decode("utf-8") if svg else None for svg in svgs]
    html = ''.join([f'<img class="tile" src="data:image/svg+xml;base64,{_}"/>' if _ else BLANK for _ in b64])
    return f'<div class="tiles">{html}</div>'


def _str2svgid(tiles: str):
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


def str2svgid(tiles: str):
    items = tiles.split(' ')
    for item in items:
        yield _str2svgid(item)


def id2svg(ids: List[int]):
    svgs = [SVGS.get(_) for _ in ids]
    return render_svg(svgs)


def str2svg(tiles: str, fold_concealed_kongs=False):
    seqs = str2svgid(tiles)
    id_list = []
    for seq in seqs:
        if len(seq) == 5 and fold_concealed_kongs:
            id_list += [-2, seq[1], seq[2], -2, -3]
        else:
            id_list += seq + [-3]
    return id2svg(id_list[:-1])


load_svg()
