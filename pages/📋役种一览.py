import streamlit as st
import json
from mahjong.display import id2png

st.set_page_config(
    page_title="役种一览.",
    page_icon="📋",
)
st.write("<h3><center>役种一览</center></h3>", unsafe_allow_html=True)
st.write("<p align='right'>仅收录了游戏《雀魂》中支持的役种</p>", unsafe_allow_html=True)
st.write(
    """<style>
#MainMenu {visibility: hidden;}
.css-15zrgzn {display: none}
footer {visibility: hidden;}
[data-testid="column"] {
    width: calc(25% - 1rem) !important;
    flex: 1 1 calc(25% - 1rem) !important;
    min-width: calc(20% - 1rem) !important;
}
.css-1l269bu {max-width:20% !important;}
[data-testid="stText"] {font-size: 45px}
.tiles {height:100%; overflow-x:scroll; overflow-y:hidden; white-space: nowrap;margin : 0px 0 5px 0;}
.tile {height:50px;margin:1px}
.blank-tile {width: 10px;height:50px;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load():
    tabs = [s.center(6, '\u2001') for s in ["一番", "二番", "三番", "六番", "满贯", "役满", "双倍役满"]]
    numbers = ['1', '2', '3', '6', '5', '13', '26']
    with open("static/yaku_list.json", encoding='utf-8') as f:
        data = json.loads(f.read())
    return tabs, numbers, data


TABS, NUMBERS, DATA = load()
TABS = st.tabs(TABS)

for i in range(7):
    d = DATA[NUMBERS[i]]
    with TABS[i]:
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
                st.write(id2png(example), unsafe_allow_html=True)
            st.divider()
