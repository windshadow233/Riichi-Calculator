from nicegui import ui


def text(s, color=None):
    if color:
        ui.label(s).classes(f'text-{color} font-bold text-lg wrap')
    else:
        ui.label(s).classes('font-bold text-lg wrap')


def text_with_background(s, bgcolor='gray-200', color=None):
    if color:
        ui.label(s).classes(f'w-full font-bold text-lg wrap p-2 rounded bg-{bgcolor} text-{color}')
    else:
        ui.label(s).classes(f'w-full font-bold text-lg wrap p-2 rounded bg-{bgcolor}')


def dialog(text):
    with ui.dialog() as dialog, ui.card():
        ui.label(text).style('white-space: pre-wrap')
        ui.button('关闭', on_click=dialog.close)
    dialog.open()


def help_button(help_text):
    with ui.button(icon='help').props('round dense flat').on('click.stop', lambda: dialog(help_text)):
        ui.tooltip(help_text).style('white-space: pre-wrap')