import streamlit as st
import json
from mahjong.checker import Mahjong
from mahjong.svg import str2svg

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
.tiles {height:100%; overflow-x:scroll; overflow-y:hidden; white-space: nowrap;}
.tile {width: 40px;height:50px;}
.blank-tile {width: 10px;height:50px;}
</style>
""",
    unsafe_allow_html=True,
)
maj = Mahjong()
TABS = ["一番", "二番", "三番", "六番", "满贯", "役满", "双倍役满"]
NUMBERS = ['1', '2', '3', '6', '5', '13', '26']
with open("static/yaku_list.json", encoding='utf-8') as f:
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
                st.write(str2svg(example), unsafe_allow_html=True)
            st.divider()