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