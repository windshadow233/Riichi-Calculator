from nicegui import ui, app
from pages import (
    calculator_page,
    yaku_list_page,
    chinitsu_practice_page,
    score_table_page,
    menu
)


app.add_static_files('/static', 'static')


def root():
    ui.add_head_html("""
    <link rel="stylesheet" href="/static/style.css">
    """)
    menu()
    ui.sub_pages({
        '/': main_page,
        '/calculator': calculator_page,
        '/yaku-list': yaku_list_page,
        '/chinitsu-practice': chinitsu_practice_page,
        '/score-table': score_table_page,
    })
    dark = ui.dark_mode(True)
    ui.switch('夜间模式').bind_value(dark)


def main_page():
    ui.page_title('立直麻将工具箱')
    with ui.card().classes('w-full flat bordered'):

        ui.label("""
        欢迎使用立直麻将工具箱！此工具箱包含下面功能。
        """)
        with ui.column().classes('w-full items-center'):
            ui.button('🧮 立直麻将计算器', on_click=lambda: ui.navigate.to('/calculator'))
            ui.button('📜 役种一览', on_click=lambda: ui.navigate.to('/yaku-list'))
            ui.button('🎯 清一色听牌练习', on_click=lambda: ui.navigate.to('/chinitsu-practice'))
            ui.button('🔍 点数速查', on_click=lambda: ui.navigate.to('/score-table'))


ui.run(root, favicon='static/favicon.ico', reconnect_timeout=120)