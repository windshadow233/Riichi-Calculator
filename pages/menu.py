from nicegui import ui
from .calculator import calculator_page
from .yaku_list import yaku_list_page
from .chinitsu_practice import chinitsu_practice_page
from .chinitsu_discard_practice import chinitsu_discard_practice_page
from .score_table import score_table_page


pages = [
    ['🧮 立直麻将计算器', '/calculator', calculator_page],
    ['📜 役种一览', '/yaku-list', yaku_list_page],
    ['🎯 清一色听牌练习', '/chinitsu-practice', chinitsu_practice_page],
    ['🎯 清一色切牌练习', '/chinitsu-discard-practice', chinitsu_discard_practice_page],
    ['🔍 点数速查', '/score-table', score_table_page]
]


def menu():
    with ui.row().classes('w-full items-center'):
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                for name, path, _ in pages:
                    ui.menu_item(name, lambda p=path: ui.navigate.to(p))
                ui.separator()
                ui.menu_item('🏠 主页', lambda: ui.navigate.to('/'))
                ui.menu_item('❌ 关闭', menu.close)