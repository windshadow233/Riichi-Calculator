import re

import streamlit as st
from score import ScoreCalculator, ID2NAME
import math

st.set_page_config(
    page_title="麻雀の計算",
)
calculator = ScoreCalculator()
st.write("<h3><center>一个<del>可能有bug的</del>立直麻将计算器</center></h3>", unsafe_allow_html=True)
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 30px;
}
.css-15zrgzn {display: none}
</style>
""",
    unsafe_allow_html=True,
)
with st.form(key="mahjong"):
    col1, col2 = st.columns([4, 1])
    with col1:
        tiles = st.text_input(
            label="牌面",
            help="请按照以下格式书写牌面字符串: "
                 "其中，万、饼、索、字分别用数字1-9加上字母'm'、'p'、's'、'z'进行表示。"
                 "東南西北白發中分别用1z-7z表示。"
                 "副露以空格分隔，写在手牌后，如果是暗杠，则写五次对应的数字。"
                 "例如, 若和牌者的手牌有三萬、五萬、两个一饼，和了牌是四萬，副露为一二三饼的顺子、白板的暗杠以及六索的明杠，则应在此栏填入下面的字符串: "
                 "'35m11p 123p 55555z 6666s'，并且在后面的'和了牌'一栏填写'4m'"
        ).strip()
    with col2:
        hu_tile = st.text_input(label="和了牌", help="表示方法与'牌面'相同，只需填入一张牌（听牌计算时不需要填写）")
    col1, col2 = st.columns(2)
    with col1:
        prevailing_wind_str = st.radio(
            label="场风",
            options=['東', '南', '西', '北'],
            horizontal=True
        )
        prevailing_wind = ['東', '南', '西', '北'].index(prevailing_wind_str) + 1
    with col2:
        dealer_wind_str = st.radio(
            label="自风",
            options=['東', '南', '西', '北'],
            horizontal=True
        )
        dealer_wind = ['東', '南', '西', '北'].index(dealer_wind_str) + 1
    lichi = st.radio(
            label="立直情况",
            options=['无', '立直', '两立直'],
            horizontal=True
        )
    lichi = ['无', '立直', '两立直'].index(lichi)
    col1, col2, col3 = st.columns(3)
    with col1:
        is_self_draw = st.checkbox(
            label="自摸",
            help="荣和时不勾选此项"
        )
        ippatsu = st.checkbox(
            label="一发",
            help="立直后在无人鸣牌的状态下一巡内和牌"
        )
        is_under_the_sea = st.checkbox(
            label="海底捞月/河底捞鱼",
            help="最后一张牌自摸/荣和"
        )
    with col2:
        is_after_a_kong = st.checkbox(
            label="岭上开花",
            help="用摸到的岭上牌和牌"
        )
        is_robbing_the_kong = st.checkbox(
            label="抢杠",
            help="别家加杠时荣和（国士无双可抢暗杠）"
        )
    with col3:
        is_blessing_of_heaven = st.checkbox(
            label="天和",
            help="亲家第一巡和牌"
        )
        is_blessing_of_earth = st.checkbox(
            label="地和",
            help="子家第一巡轮到自己前无人鸣牌的状态下自摸和牌"
        )
    col1, col2 = st.columns(2)
    with col1:
        dora = st.number_input(
            label="宝牌数量",
            min_value=0,
            value=0,
            step=1,
            help="包含宝牌、赤宝牌、立直的里宝牌以及三人场的拔北宝牌"
        )
    with col2:
        game_number = st.number_input(
            label="本场数",
            min_value=0,
            step=1,
            help="本场数是亲家连庄次数，在亲家连庄成功结算点数完成之后加1。连庄失败则清零"
        )


    def calculate():
        try:
            calculator.update(
                tiles=tiles,
                hu_tile=hu_tile,
                prevailing_wind=prevailing_wind,
                dealer_wind=dealer_wind,
                is_self_draw=is_self_draw,
                lichi=lichi,
                dora=dora,
                ippatsu=ippatsu,
                is_under_the_sea=is_under_the_sea,
                is_after_a_kong=is_after_a_kong,
                is_robbing_the_kong=is_robbing_the_kong,
                is_blessing_of_heaven=is_blessing_of_heaven,
                is_blessing_of_earth=is_blessing_of_earth
            )
            if calculator.is_hu:
                st.write("最高得点手牌拆分")
                if calculator.combinations:
                    comb = calculator.combinations[calculator.max_score_index]
                    comb = ' '.join('「' + ' '.join(ID2NAME[tile] for tile in meld) + '」' for meld in comb)
                    st.info(comb)
                else:
                    st.info(calculator.hand_string())
                if calculator.called_tiles:
                    st.write("副露")
                    st.info(calculator.called_string())
                st.write("役种、宝牌")
                st.info(''.join([f'〖{yaku}〗' for yaku in calculator.yaku_list]))
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        label="和了牌",
                        value=ID2NAME[calculator.hu_tile]
                    )
                with col2:
                    st.metric(
                        label="符数",
                        value=calculator.fu
                    )
                number = calculator.number
                with col3:
                    st.metric(
                        label="番数",
                        value=number
                    )
                with col4:
                    st.metric(
                        label="基本点",
                        value=calculator.score
                    )
                if calculator.level:
                    st.info(calculator.level)
                if dealer_wind == 1:
                    if is_self_draw:
                        score_info = f"每人支付東家「{math.ceil(2 * calculator.score / 100) * 100 + 100 * game_number}」点"
                    else:
                        score_info = f"放铳者支付東家「{math.ceil(6 * calculator.score / 100) * 100 + 300 * game_number}」点"
                else:
                    if is_self_draw:
                        score_info = f"東家支付{dealer_wind_str}家「{math.ceil(2 * calculator.score / 100) * 100 + 100 * game_number}」点，" \
                                     f"其他人各支付{dealer_wind_str}家「{math.ceil(calculator.score / 100) * 100 + 100 * game_number}」点"
                    else:
                        score_info = f"放铳者支付{dealer_wind_str}家「{math.ceil(4 * calculator.score / 100) * 100 + 300 * game_number}」点"
                st.info(score_info)
            else:
                st.warning("没有和牌")
        except:
            st.error("输入有误")


    col1, col2 = st.columns(2)
    with col1:
        btn1 = st.form_submit_button(label="和牌计算")
    with col2:
        btn2 = st.form_submit_button(label="听牌计算")

    if btn1:
        if not re.match('(:?[1-9][mps])|(:?[1-7]z)', hu_tile):
            st.error("请正确填写和了牌")
            st.stop()
        calculate()
    elif btn2:
        try:
            is_wait = calculator.checker.calculate_ready_hand(tiles, False)
            if not is_wait:
                st.warning("没有听牌")
            else:
                is_wait = list(sorted(is_wait))
                st.info(f"听{'、'.join('「' + ID2NAME[tile] + '」' for tile in is_wait)}")
        except:
            st.error("输入有误")
