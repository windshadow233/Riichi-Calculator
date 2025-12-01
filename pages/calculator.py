from nicegui import ui
import re
import math
from mahjong.display import id2png, str2png
from mahjong.score import ScoreCalculator, AKA_MAN, AKA_PIN, AKA_SOU
from pages.utils import text, text_with_background, help_button


def calculator_page():
    gap = 3
    calculator = ScoreCalculator()

    def read_data():
        tiles = tiles_input.value.strip()
        hu_tile = hu_tile_input.value.strip()
        prevailing_wind = {'东': 0, '南': 1, '西': 2, '北': 3}[prevailing_wind_str.value]
        dealer_wind = {'东': 0, '南': 1, '西': 2, '北': 3}[dealer_wind_str.value]
        riichi = {'无': 0, '立直': 1, '两立直': 2}[riichi_str.value]
        is_self_draw = is_self_draw_box.value
        dora = dora_input.value.strip()
        ura_dora = ura_dora_input.value.strip()
        north_dora = nuki_dora_box.value
        ippatsu = ippatsu_box.value
        is_three_player_game = is_three_player_game_box.value
        is_under_the_sea = is_under_the_sea_box.value
        is_after_a_kong = is_after_a_kong_box.value
        is_robbing_the_kong = is_robbing_the_kong_box.value
        is_blessing_of_heaven = is_blessing_of_heaven_box.value
        is_blessing_of_earth = is_blessing_of_earth_box.value
        use_ancient_yaku = use_ancient_yaku_box.value
        is_blessing_of_man = is_blessing_of_man_box.value
        tsubamegaeshi = tsubamegaeshi_box.value
        kanfuri = kanfuri_box.value
        return locals()

    def calculate_agari():
        display.clear()
        try:
            data = read_data()
            calculator.update(
                **data
            )
            if not calculator.is_hu:
                with display:
                    text_with_background('没有和牌', bgcolor='red')
                return
            with display:
                text('最高打点手牌拆分')
            if calculator.combinations:
                comb = calculator.combinations[calculator.max_score_index]
                aka_dora_count = calculator.hand_aka_dora
                id_list = []
                for seq in comb:
                    id_list += [*seq, -3]
                id_list = ' ' + ' '.join(map(str, id_list)) + ' '
                id_list = id_list.replace(' 4 ', f' {AKA_MAN} ', aka_dora_count[0]).replace('14', str(AKA_PIN),
                                                                                            aka_dora_count[1]).replace(
                    '24', str(AKA_SOU), aka_dora_count[2])
                id_list = list(map(int, id_list[1:-1].split(' ')))
                with display:
                    ui.html(id2png(id_list[:-1]), sanitize=False)
            else:
                with display:
                    ui.html(id2png(calculator.hand_tiles), sanitize=False)
            if calculator.called_tiles:
                tiles = data['tiles']
                with display:
                    ui.separator()
                    text('副露')
                    ui.html(str2png(tiles[re.search(' +', tiles).end():], True), sanitize=False)
            with display:
                ui.separator()
                with ui.row().classes(f'w-full gap-{gap}'):
                    with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                        text('宝牌指示牌')
                        if dora := data['dora']:
                            ui.html(str2png(dora), sanitize=False)
                        else:
                            text_with_background('未填入', bgcolor='orange')
                    with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                        text('里宝指示牌')
                        if data['riichi']:
                            if ura_dora := data['ura_dora']:
                                ui.html(str2png(ura_dora), sanitize=False)
                            else:
                                text_with_background('未填入', bgcolor='orange')
                        else:
                            text_with_background('未立直', bgcolor='green')
                ui.separator()
                text('役种、宝牌')
                if not calculator.has_yaku:
                    text_with_background('无役', bgcolor='red')
                    return
                with ui.scroll_area().classes('w-full h-30'):
                    text_with_background(''.join([f'〖{yaku}〗' for yaku in calculator.yaku_list]), bgcolor='blue')
                ui.separator()
                with ui.row().classes(f'w-full gap-{gap}'):
                    with ui.column().classes(f'w-[calc(25%-{gap * 3}px)]'):
                        text('和了牌')
                        ui.html(str2png(data['hu_tile']), sanitize=False)
                    with ui.column().classes(f'w-[calc(25%-{gap * 3}px)]'):
                        text('符数')
                        text(calculator.fu, color='green')
                    with ui.column().classes(f'w-[calc(25%-{gap * 3}px)]'):
                        text('番数')
                        text(calculator.number, color='green')
                    with ui.column().classes(f'w-[calc(25%-{gap * 3}px)]'):
                        text('基本点')
                        text(calculator.score, color='green')
                if calculator.level:
                    with ui.row().classes(f'w-full gap-{gap}'):
                        text_with_background(calculator.level, bgcolor='green')
                game_number = game_number_input.value
                if data['dealer_wind'] == 1:
                    if data['is_self_draw']:
                        score_info = f"每人支付東家「{math.ceil(2 * calculator.score / 100) * 100 + 100 * game_number}」点"
                    else:
                        score_info = f"放铳者支付東家「{math.ceil(6 * calculator.score / 100) * 100 + 300 * game_number}」点"
                        if game_number:
                            score_info += f'（三麻「{math.ceil(6 * calculator.score / 100) * 100 + 200 * game_number}」点）'
                else:
                    if data['is_self_draw']:
                        score_info = f"東家支付{dealer_wind_str.value}家「{math.ceil(2 * calculator.score / 100) * 100 + 100 * game_number}」点，" \
                                     f"其他人各支付{dealer_wind_str.value}家「{math.ceil(calculator.score / 100) * 100 + 100 * game_number}」点"
                    else:
                        score_info = f"放铳者支付{dealer_wind_str.value}家「{math.ceil(4 * calculator.score / 100) * 100 + 300 * game_number}」点"
                        if game_number:
                            score_info += f'（三麻「{math.ceil(4 * calculator.score / 100) * 100 + 200 * game_number}」点）'
                with ui.row().classes(f'w-full gap-{gap}'):
                    text_with_background(score_info, bgcolor='green')
        except Exception as e:
            with display:
                text_with_background(f'输入有误', bgcolor='red')

    def calculate_machi():
        display.clear()
        try:
            tiles = tiles_input.value.strip()
            is_wait = calculator.checker.calculate_ready_hand(tiles, False)
            if not is_wait:
                with display:
                    text('没有听牌', color='red')
            else:
                is_wait = list(sorted(is_wait))
                with display:
                    text('听牌', color='green')
                    ui.html(id2png(is_wait), sanitize=False)
        except Exception as e:
            ui.notify(f'输入有误{e}', type='negative', color='negative')

    ui.page_title('立直麻将计算器')
    with ui.card().classes('flat bordered').style('overflow-x: scroll; max-width: 100vw'):
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.input(label="牌面").classes(f'w-[calc(70%-{gap * 3}px)]') as tiles_input:
                help_button("请按照以下格式填写牌面字符串: "
                                                               "\n其中，万、饼、索分别用数字1-9加上字母'm'、'p'、's'进行表示。赤宝牌用数字0加上对应的字母表示。"
                                                               "\n字牌(東南西北白發中)分别用1z-7z表示。"
                                                               "\n副露以空格分隔，写在手牌后，如果是暗杠，则写五次对应的数字。"
                                                               "\n例如, 若和牌者的手牌有三萬、赤五萬、两个一饼，和了牌是四萬，副露为一二三饼的顺子、白板的暗杠以及六索的明杠，则应在此栏填入下面的字符串:"
                                                               "\n'30m11p 123p 55555z 6666s'，并且在后面的'和了牌'一栏填写'4m'")
            with ui.input(label="和了牌",
                          validation={'输入错误': lambda s: calculate_button and re.match('^([0-9][mps]|[1-7]z)$', s) is not None}).classes(f'w-[calc(30%-{gap * 3}px)]') as hu_tile_input:
                help_button("表示方法与'牌面'相同，只填一张牌（听牌计算时不需要填写）")
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.input(label="宝牌指示牌").classes(f'w-[calc(50%-{gap * 3}px)]') as dora_input:
                help_button("表示方法与'牌面'相同")
            with ui.input(label="里宝指示牌").classes(f'w-[calc(50%-{gap * 3}px)]') as ura_dora_input:
                help_button("表示方法与'牌面'相同")
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                ui.label('场风')
                prevailing_wind_str = ui.radio(options=['东', '南', '西', '北'], value='东').props('inline')
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                ui.label('自风')
                dealer_wind_str = ui.radio(options=['东', '南', '西', '北'], value='东').props('inline')
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                ui.label('立直情况')
                riichi_str = ui.radio(options=['无', '立直', '两立直'], value='无').props('inline').classes('w-full')
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                game_number_input = ui.number(label='本场数', value=0, min=0, step=1, precision=1).classes(f'w-full')
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.column().classes(f'w-[calc(33%-{gap * 3}px)]'):
                with ui.checkbox(text='自摸') as is_self_draw_box:
                    help_button('荣和时不勾选此项')
                with ui.checkbox(text='一发') as ippatsu_box:
                    help_button('立直后在无人鸣牌的状态下一巡内和牌')
                with ui.checkbox(text='海底/河底') as is_under_the_sea_box:
                    help_button('最后一张牌自摸/荣和')
            with ui.column().classes(f'w-[calc(33%-{gap * 3}px)]'):
                with ui.checkbox(text='岭上') as is_after_a_kong_box:
                    help_button('用摸到的岭上牌和牌')
                with ui.checkbox(text='抢杠') as is_robbing_the_kong_box:
                    help_button('别家加杠时荣和（国士无双可抢暗杠')

            with ui.column().classes(f'w-[calc(33%-{gap * 3}px)]'):
                with ui.checkbox(text='天和') as is_blessing_of_heaven_box:
                    help_button('亲家第一巡无鸣牌的状态下和牌')
                with ui.checkbox(text='地和') as is_blessing_of_earth_box:
                    help_button('子家第一巡轮到自己前无人鸣牌的状态下自摸和牌')
        with ui.expansion('古役').classes('w-full'):
            with ui.row().classes(f'w-full gap-{gap}'):
                with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                    with ui.checkbox(text='开启古役') as use_ancient_yaku_box:
                        help_button('计算收录在「雀魂」游戏中的古役')
                    with ui.checkbox(text='燕返') as tsubamegaeshi_box:
                        help_button('荣和别家的第一张立直宣言牌')
                with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                    with ui.checkbox(text='杠振') as kanfuri_box:
                        help_button('荣和别家开杠后打出的牌')
                    with ui.checkbox(text='人和') as is_blessing_of_man_box:
                        help_button('子家第一巡轮到自己前无人鸣牌的状态下荣和')
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                is_three_player_game_box = ui.checkbox(text='三麻')
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                nuki_dora_box = ui.number(label='拔北宝牌', value=0, min=0, max=4, step=1, precision=1).classes(
                    f'w-full')
        ui.separator()
        with ui.row().classes(f'w-full gap-{gap}'):
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                calculate_button = ui.button('和牌计算', on_click=calculate_agari).props('raised')
            with ui.column().classes(f'w-[calc(50%-{gap * 3}px)]'):
                ui.button('听牌计算', on_click=calculate_machi).props('raised')
        ui.separator()
        display = ui.column().classes(f'w-full gap-{gap}')
