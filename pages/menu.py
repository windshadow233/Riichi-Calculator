from nicegui import ui


def menu():
    with ui.row().classes('w-full items-center'):
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                ui.menu_item('🧮 立直麻将计算器', lambda: ui.navigate.to('/calculator'))
                ui.menu_item('📜 役种一览', lambda: ui.navigate.to('/yaku-list'))
                ui.menu_item('🎯 清一色听牌练习', lambda: ui.navigate.to('/chinitsu-practice'))
                ui.menu_item('🔍 点数速查', lambda: ui.navigate.to('/points-lookup'))
                ui.separator()
                ui.menu_item('Home', lambda: ui.navigate.to('/'))
                ui.menu_item('Close', menu.close)