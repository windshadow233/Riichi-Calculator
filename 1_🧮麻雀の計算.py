import re
import streamlit as st
import math
from mahjong.score import ScoreCalculator, AKA_MAN, AKA_PIN, AKA_SOU
from mahjong.display import str2png, id2png
from detection.detect import load_model, recognize, to_string
from PIL import Image

st.set_page_config(
    page_title="麻雀の計算",
    page_icon="🧮",
)
calculator = ScoreCalculator()
st.write("<h3><center>一个<del>可能有bug的</del>立直麻将计算器</center></h3>", unsafe_allow_html=True)
st.write(
    """
<style>
#MainMenu {visibility: hidden;}
[data-testid="stMetricValue"] {
    font-size: 30px;
}
.css-15zrgzn {display: none}
footer {visibility: hidden;}
[data-testid="column"] {
    width: calc(25% - 1rem) !important;
    flex: 1 1 calc(25% - 1rem) !important;
    min-width: calc(20% - 1rem) !important;
}
.css-1l269bu {max-width:20% !important;}
.tiles {height:100%; overflow-x:scroll; overflow-y:hidden; white-space: nowrap;margin : -15px 0 5px 0}
.tile {height:50px;margin:1px}
.blank-tile {width: 10px;height:50px;}
</style>
""",
    unsafe_allow_html=True,
)

with st.form(key="mahjong"):
    with st.expander("拍照识别(beta)", expanded=False):
        st.info("模型正在开发中，在这里打个广告招募数据标注工程师~")
        st.info("建议横屏拍摄，并将手牌沿水平方向连续放置，识图功能会将手牌的最后一张识别为和了牌。如有副露，将副露与手牌分开并且两两分开横向放置。考虑到图像有效识别区域的长宽比例，当副露较多时，将它们放置在手牌的下方为佳。")
        image = st.file_uploader(
            label="选取相册图片或拍照上传",
            type=("jpg", "jpeg", "png")
        )
        col1, col2 = st.columns(2)
        with col1:
            btn = st.form_submit_button(label="识别图片")
        with col2:
            conf = st.slider(label="置信度阈值", min_value=10, max_value=90, value=50, step=5, format="%d%%", help="置信度小于该值的检测结果将被忽略")
    if btn and image:
        with st.spinner('正在努力识别中，请稍等片刻'):
            try:
                image = Image.open(image)
                model = load_model()
                groups, res = recognize(model, image, conf / 100, False)
                tile_string, hu_string = to_string(groups)
                st.success("识别结果的图片与文本如下，您可将文本分别复制到下方的'牌面'栏与'和了牌'栏。如有识别错误，请进行手动修改并push开发者优化模型。")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(image, use_column_width=True)
                with col2:
                    st.image(res, use_column_width=True)
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.code(tile_string, language=None)
                with col2:
                    st.code(hu_string, language=None)
            except:
                st.warning('未能检测到麻将牌，建议push开发者优化模型')
    col1, col2 = st.columns([5, 1])
    with col1:
        tiles = st.text_input(
            label="牌面",
            help="请按照以下格式书写牌面字符串: "
                 "其中，万、饼、索分别用数字1-9加上字母'm'、'p'、's'进行表示。赤宝牌用数字0表示。"
                 "字牌(東南西北白發中)分别用1z-7z表示。"
                 "副露以空格分隔，写在手牌后，如果是暗杠，则写五次对应的数字。"
                 "例如, 若和牌者的手牌有三萬、赤五萬、两个一饼，和了牌是四萬，副露为一二三饼的顺子、白板的暗杠以及六索的明杠，则应在此栏填入下面的字符串: "
                 "'30m11p 123p 55555z 6666s'，并且在后面的'和了牌'一栏填写'4m'"
        ).strip()
    with col2:
        hu_tile = st.text_input(label="和了牌", help="表示方法与'牌面'相同，只填一张牌（听牌计算时不需要填写）", max_chars=2)
    col1, col2 = st.columns(2)
    with col1:
        dora = st.text_input(
            label="宝牌指示牌",
            help="表示方法与'牌面'相同"
        )
        prevailing_wind_str = st.radio(
            label="场风",
            options=['東', '南', '西', '北'],
            horizontal=True
        )
        prevailing_wind = ['東', '南', '西', '北'].index(prevailing_wind_str) + 1
    with col2:
        ura_dora = st.text_input(
            label="里宝牌指示牌",
            help="表示方法与'牌面'相同"
        )
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
    with col2:
        is_after_a_kong = st.checkbox(
            label="岭上",
            help="用摸到的岭上牌和牌"
        )
        is_robbing_the_kong = st.checkbox(
            label="抢杠",
            help="别家加杠时荣和（国士无双可抢暗杠）"
        )
    with col3:
        is_blessing_of_heaven = st.checkbox(
            label="天和",
            help="亲家第一巡无鸣牌的状态下和牌"
        )
        is_blessing_of_earth = st.checkbox(
            label="地和",
            help="子家第一巡轮到自己前无人鸣牌的状态下自摸和牌"
        )
    is_under_the_sea = st.checkbox(
            label="海底捞月/河底捞鱼",
            help="最后一张牌自摸/荣和"
    )
    with st.expander("古役", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            use_ancient_yaku = st.checkbox(
                label="使用古役",
                help="包含「雀魂」游戏中收录的古役"
            )
            tsubamegaeshi = st.checkbox(
                label="燕返",
                help="荣和别家的第一张立直宣言牌"
            )
        with col2:
            kanfuri = st.checkbox(
                label="杠振",
                help="荣和别家开杠后打出的牌"
            )
            is_blessing_of_man = st.checkbox(
                label="人和",
                help="子家第一巡轮到自己前无人鸣牌的状态下荣和"
            )
    col1, col2 = st.columns(2)
    with col1:
        north_dora = st.number_input(
            label="拔北宝牌数量",
            min_value=0,
            value=0,
            step=1,
            help="三麻限定"
        )
    with col2:
        game_number = st.number_input(
            label="本场数",
            min_value=0,
            step=1,
            help="本场数在亲家连庄或流局之后加1，其他情况下清零"
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
                ura_dora=ura_dora,
                north_dora=north_dora,
                ippatsu=ippatsu,
                is_under_the_sea=is_under_the_sea,
                is_after_a_kong=is_after_a_kong,
                is_robbing_the_kong=is_robbing_the_kong,
                is_blessing_of_heaven=is_blessing_of_heaven,
                is_blessing_of_earth=is_blessing_of_earth,
                use_ancient_yaku=use_ancient_yaku,
                is_blessing_of_man=is_blessing_of_man,
                tsubamegaeshi=tsubamegaeshi,
                kanfuri=kanfuri
            )
            if calculator.is_hu:
                st.write("最高得点手牌拆分")
                if calculator.combinations:
                    comb = calculator.combinations[calculator.max_score_index]
                    aka_dora_count = calculator.hand_aka_dora
                    id_list = []
                    for seq in comb:
                        id_list += [*seq, -3]
                    id_list = ' ' + ' '.join(map(str, id_list)) + ' '
                    id_list = id_list.replace(' 4 ', f' {AKA_MAN} ', aka_dora_count[0]).replace('14', str(AKA_PIN), aka_dora_count[1]).replace('24', str(AKA_SOU), aka_dora_count[2])
                    id_list = list(map(int, id_list[1:-1].split(' ')))
                    st.write(id2png(id_list[:-1]), unsafe_allow_html=True)
                else:
                    st.write(id2png(calculator.hand_tiles), unsafe_allow_html=True)
                if calculator.called_tiles:
                    st.write("副露")
                    st.write(str2png(tiles[re.search(' +', tiles).end():], True), unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.write("宝牌指示牌")
                    if dora:
                        st.write(str2png(dora), unsafe_allow_html=True)
                    else:
                        st.warning("未填入宝牌指示牌")
                if lichi:
                    with col2:
                        st.write("里宝牌指示牌")
                        if ura_dora:
                            st.write(str2png(ura_dora), unsafe_allow_html=True)
                        else:
                            st.warning("未填入里宝牌指示牌")
                st.write("役种、宝牌")
                if not calculator.has_yaku:
                    st.warning("无役")
                    st.stop()
                st.info(''.join([f'〖{yaku}〗' for yaku in calculator.yaku_list]))
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        label="和了牌",
                        value=""
                    )
                    st.write(str2png(hu_tile), unsafe_allow_html=True)
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
                    st.success(calculator.level)
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
                st.success(score_info)
            else:
                st.warning("没有和牌")
        except ValueError:
            st.error("输入有误")


    col1, col2 = st.columns(2)
    with col1:
        btn1 = st.form_submit_button(label="和牌计算", type='primary')
    with col2:
        btn2 = st.form_submit_button(label="听牌计算")

    if btn1:
        if not re.match('(:?\\d[mps])|(:?[1-7]z)', hu_tile):
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
                st.write("听牌")
                st.write(id2png(is_wait), unsafe_allow_html=True)
        except:
            st.error("输入有误")