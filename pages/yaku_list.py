import streamlit as st
import json
from mahjong.checker import Mahjong, ID2ICON

st.write("<h3><center>役种一览</center></h3>", unsafe_allow_html=True)
st.markdown(
    """<style>
.css-15zrgzn {display: none}
footer {visibility: hidden;}
[data-testid="column"] {
    width: calc(25% - 1rem) !important;
    flex: 1 1 calc(25% - 1rem) !important;
    min-width: calc(20% - 1rem) !important;
}
.css-1l269bu {max-width:20% !important;}
[data-testid="stText"] {font-size: 45px}
</style>
""",
    unsafe_allow_html=True,
)
maj = Mahjong()
TABS = ["一番", "二番", "三番", "六番", "满贯", "役满", "双倍役满"]
NUMBERS = ['1', '2', '3', '6', '5', '13', '26']
with open("pages/yaku_list.json", encoding='utf-8') as f:
    DATA = json.loads(f.read())
tabs = st.tabs(
    [s.center(5, '\u2001') for s in TABS]
)
for i in range(7):
    d = DATA[NUMBERS[i]]
    with tabs[i]:
        for item in d:
            name = item.get('name')
            desc = item.get('desc')
            concealed_required = item.get('門前')
            kuisagari = item.get('食い下がり')
            example = item.get('example')
            st.subheader(name)
            st.info(desc)
            if concealed_required:
                st.warning("门清限定")
            elif kuisagari:
                st.warning("副露减一番")
            if example:
                tiles, hu_tile = example.rsplit(' ', 1)
                hand_tiles, called_tiles = maj.str2id(tiles)
                hu_tile = maj.str2id(hu_tile)[0][0]
                s = [
                    ''.join(ID2ICON[tile] for tile in hand_tiles),
                    ID2ICON[hu_tile]
                ]
                if called_tiles:
                    s.insert(1, ' '.join(
                        f'🀫{ID2ICON[_[0]]}{ID2ICON[_[0]]}🀫' if len(_) == 5 else ''.join(ID2ICON[tile] for tile in _)
                        for _ in called_tiles)
                    )
                st.text(' '.join(s))
            st.divider()