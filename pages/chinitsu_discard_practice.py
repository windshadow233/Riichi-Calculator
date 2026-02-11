from nicegui import ui, html
import random
from pages.utils import text_with_background, text
from mahjong.utils import kiri_answer, random_pattern, pattern2tiles, add_one_tile, is_agari
from mahjong.display import id2png


async def chinitsu_discard_practice_page():
    global_status = {
        'tiles': [],
        'ans': [],
        'analysis': [],
        'streaks': 0,
        'boxes': {}
    }
    ui.page_title('清一色切牌练习')
    with ui.card().classes('flat bordered').style('overflow-x: scroll; max-width: 100vw; min-width: 40vw'):
        with html.header().style('text-align: center; font-size: 32px;'):
            html.strong('清一色切牌练习')
        html.strong('门前清一色经常不知道切哪张？来练练吧！').style('text-align: center;')
        html.strong('不考虑听牌改良与和牌番数，你仅需要找出「切出后听牌枚数最多」的那张牌，若已经和了，选“和了”。可能存在多解，选其一即可。').style('text-align: center;')

        with ui.row().classes('w-full justify-center'):
            card_type = ui.radio(options=['万', '饼', '索', '随机'], value='万', on_change=lambda: change_type()).props('inline')

        def change_type():
            if not switch_btn.value:
                return
            question_display_area.clear()
            info.clear()
            clear_boxes()
            submit_btn.enable()
            generate_question(card_type.value)

        def start():
            switch_btn.set_text('结束')
            submit_btn.enable()
            generate_question(card_type.value)

        def clear_boxes():
            for key in list(global_status['boxes'].keys()):
                global_status['boxes'].pop(key)
                key.delete()
            selection_area.clear()

        def on_change(e, id_):
            if e.value:
                for k, v in global_status['boxes'].items():
                    if v != id_:
                        k.value = False

        def end():
            switch_btn.set_text('开始')
            submit_btn.disable()
            question_display_area.clear()
            clear_boxes()
            info.clear()

        def generate_question(card_type):
            question_display_area.clear()
            clear_boxes()
            if card_type == '随机':
                card_type = random.randint(0, 2)
            else:
                card_type = {'万': 0, '饼': 1, '索': 2}[card_type]
            ptn = random_pattern()
            tiles = pattern2tiles(card_type, ptn)
            tiles = add_one_tile(tiles)
            global_status['tiles'] = tiles
            global_status['ans'], global_status['analysis'] = kiri_answer(tiles)
            boxes = list(set(tiles))
            with question_display_area:
                ui.html(id2png(tiles), sanitize=False)
                ui.separator()
            with selection_area:
                for i in boxes:
                    with ui.column().classes('w-1/12').style('min-width: 50px'):
                        ui.html(id2png([i]), sanitize=False)
                        global_status['boxes'][ui.checkbox(on_change=lambda e, x=i: on_change(e, x))] = i
                with ui.column().classes('w-1/12').style('min-width: 50px'):
                    ui.html(id2png([-4]), sanitize=False)
                    global_status['boxes'][ui.checkbox(on_change=lambda e, x=-1: on_change(e, x))] = -1

        def submit_answer():
            for key, val in global_status['boxes'].items():
                if key.value:
                    select = val
                    break
            else:
                return
            if select in (ans := global_status['ans']):
                global_status['streaks'] += 1
                info.clear()
                with info:
                    text_with_background('回答正确！', bgcolor='green')
                    text_with_background(f'当前连对 {global_status["streaks"]} 题。', bgcolor='blue')
                generate_question(card_type.value)
            else:
                submit_btn.disable()
                global_status['streaks'] = 0
                info.clear()
                with info:
                    text_with_background('回答错误！正确答案：', bgcolor='red')
                    ui.html(id2png(ans), sanitize=False)
                    if analysis := global_status['analysis']:
                        ui.separator()
                        with ui.expansion('解析', icon='help').classes('w-full').style('font-size: 18px; font-weight: bold;'):
                            for tile, (s, machi_tiles) in analysis:
                                with ui.row():
                                    text('切:')
                                    ui.html(id2png([tile]), sanitize=False)
                                    text('听:')
                                    ui.html(id2png(machi_tiles), sanitize=False)
                                text(f'共 {s} 枚', color='green')
                                ui.separator()
                    def nxt():
                        submit_btn.enable()
                        info.clear()
                        generate_question(card_type.value)
                    ui.button('继续', on_click=nxt)

        question_display_area = ui.column().classes('justify-center')
        selection_area = ui.row().classes('justify-center w-full')

        with ui.row():
            switch_btn = ui.switch('开始', on_change=lambda: start() if switch_btn.value else end())
            submit_btn = ui.button('提交答案', on_click=lambda: submit_answer())
            submit_btn.disable()
        info = ui.column().classes('w-full')
