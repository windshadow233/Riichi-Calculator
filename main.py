from nicegui import ui, app, html
from pages.menu import pages, menu

app.add_static_files('/static', 'static')


def root():
    ui.add_head_html("""
    <link rel="stylesheet" href="/static/style.css">
    """)
    menu()
    ui.sub_pages({
        '/': main_page,
        **{path: page for _, path, page in pages}
    })
    dark = ui.dark_mode(True)
    ui.switch('夜间模式').bind_value(dark)


async def main_page():
    ui.page_title('立直麻将工具箱')
    with ui.card().classes('w-full flat bordered'):
        html.strong("""欢迎使用立直麻将工具箱！此工具箱包含以下功能。""").style('text-align: center; font-size: 20px;')

        with ui.column().classes('w-full items-center'):
            for name, path, _ in pages:
                ui.button(name, on_click=lambda p=path: ui.navigate.to(p))
        
        html.p('注意：此网页版将不再维护与更新，建议使用小程序版 — 功能更多，体验更佳！').style('text-align: center; font-size: 14px; color: #666;')
        ui.image(source='/static/miniprogram.jpg').style('display:block; margin:12px auto; max-width:240px;')



ui.run(root, favicon='static/favicon.ico', reconnect_timeout=120)
