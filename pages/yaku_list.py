from nicegui import ui, html
import json
from mahjong.display import id2png
from pages.utils import text_with_background
import aiofiles


async def load():
    tabs = [s.center(6, '\u2001') for s in ["一番", "二番", "三番", "六番", "满贯", "役满", "双倍役满"]]
    numbers = ['1', '2', '3', '6', '5', '13', '26']
    async with aiofiles.open("data/yaku_list.json", encoding='utf-8') as f:
        data = json.loads(await f.read())
    return tabs, numbers, data


async def yaku_list_page():
    ui.page_title('役种一览')
    tabs, numbers, data = await load()
    with ui.card().classes('flat bordered').style('overflow-x: scroll; max-width: 100vw'):
        with html.header().style('text-align:center; font-size: 32px;'):
            html.strong('役种一览')
        ui.label("""
        仅收录了游戏《雀魂》中支持的役种。
        """)

        with ui.tabs().style('overflow-x: scroll; max-width: 95vw') as t:
            tabs = [ui.tab(s) for s in tabs]
        with ui.tab_panels(t, value=tabs[0]).style('overflow-x: scroll; max-width: 95vw'):
            for i in range(7):
                d = data[numbers[i]]
                with ui.tab_panel(tabs[i]):
                    for item in d:
                        name = item.get('name')
                        desc = item.get('desc')
                        concealed_required = item.get('門前')
                        kuisagari = item.get('食い下がり')
                        example = item.get('example')
                        with html.header().style('font-size: 26px;'):
                            html.strong(name)
                        ui.chat_message(desc, avatar='/static/png/ichihime-0_0.png')
                        if concealed_required:
                            text_with_background("门清限定", bgcolor='blue')
                        elif kuisagari:
                            text_with_background("副露减一番", bgcolor='orange')
                        if example:
                            ui.html(id2png(example), sanitize=False)
                        ui.separator()
