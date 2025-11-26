from nicegui import ui, html
from pages.utils import text_with_background
from mahjong.utils import *
from mahjong.display import id2png


def chinitsu_practice_page():
    global_status = {
        'tiles': [],
        'ans': [],
        'streaks': 0,
        'selections': {}
    }
    ui.page_title('清一色听牌练习')
    with ui.card().classes('flat bordered').style('overflow-x: scroll; max-width: 100vw; min-width: 40vw'):
        with html.header().style('text-align: center; font-size: 32px;'):
            html.strong('清一色听牌练习')

        with ui.row().classes('w-full justify-center'):
            card_type = ui.radio(options=['万', '饼', '索', '随机'], value='万', on_change=lambda: change_type()).props('inline')

        def change_type():
            if not switch_btn.value:
                return
            question_display_area.clear()
            clear_selection()
            generate_question(card_type.value)

        def start():
            switch_btn.set_text('结束')
            submit_btn.enable()
            generate_question(card_type.value)

        def clear_selection():
            for key in list(global_status['selections'].keys()):
                global_status['selections'].pop(key)
                key.delete()
            selection_area.clear()

        def end():
            switch_btn.set_text('开始')
            submit_btn.disable()
            question_display_area.clear()
            clear_selection()
            info.clear()

        def generate_question(card_type):
            question_display_area.clear()
            clear_selection()
            if card_type == '随机':
                card_type = random.randint(0, 2)
            else:
                card_type = {'万': 0, '饼': 1, '索': 2}[card_type]
            ptn = random_pattern()
            tiles = pattern2tiles(card_type, ptn)
            global_status['tiles'] = tiles
            global_status['ans'] = answer(tiles)
            selections = [10 * card_type + i for i in range(9)]
            with question_display_area:
                ui.html(id2png(tiles), sanitize=False)
                ui.separator()
            with selection_area:
                for i in selections:
                    with ui.column().classes('w-1/12').style('min-width: 50px'):
                        ui.html(id2png([i]), sanitize=False)
                        global_status['selections'][ui.checkbox()] = i

        def submit_answer():
            selections = [int(val) for key, val in global_status['selections'].items() if key.value]
            if not selections:
                return
            if selections == (ans := global_status['ans']):
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
                    text_with_background(f'回答错误！正确答案：', bgcolor='red')
                    ui.html(id2png(ans), sanitize=False)

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
