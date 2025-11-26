from nicegui import ui, html


table1 = """<table class="wikitable" style="text-align: center; border-style: none">
<tbody><tr>
<th>
</th>
<th>20符<br><small>(平和自摸)</small>
</th>
<th>25符<br><small>(七对子)</small></th>
<th>30符</th>
<th>40符</th>
<th>50符</th>
<th>60符</th>
<th>70符</th>
<th>80符</th>
<th>90符</th>
<th>100符</th>
<th>110符
</th></tr>
<tr>
<th>1番</th>
<td>-</td>
<td>-</td>
<td><b>1500</b><br>(500)</td>
<td><b>2000</b><br>(700)</td>
<td><b>2400</b><br>(800)</td>
<td><b>2900</b><br>(1000)</td>
<td><b>3400</b><br>(1200)</td>
<td><b>3900</b><br>(1300)</td>
<td><b>4400</b><br>(1500)</td>
<td><b>4800</b><br>(1600)</td>
<td><b>5300</b><br></td></tr>
<tr>
<th>2番</th>
<td>-<br>(700)</td>
<td><b>2400</b><br></td>
<td><b>2900</b><br>(1000)</td>
<td><b>3900</b><br>(1300)</td>
<td><b>4800</b><br>(1600)</td>
<td><b>5800</b><br>(2000)</td>
<td><b>6800</b><br>(2300)</td>
<td><b>7700</b><br>(2600)</td>
<td><b>8700</b><br>(2900)</td>
<td><b>9600</b><br>(3200)</td>
<td><b>10600</b><br>(3600)
</td></tr>
<tr>
<th>3番</th>
<td>- <br>(1300)</td>
<td><b>4800</b><br>(1600)</td>
<td><b>5800</b><br>(2000)</td>
<td><b>7700</b><br>(2600)</td>
<td><b>9600</b><br>(3200)</td>
<td style="background-color:#ff8;"><span style="color:#005090;"><b>11600</b><br>(3900)</span></td>
<td colspan="5" rowspan="1" style="border-bottom-color: var(--cell-bg-color);">
</td></tr>
<tr>
<th>4番</th>
<td>- <br>(2600)</td>
<td><b>9600</b><br>(3200)</td>
<td style="background-color: #ff8;"><span style="color:#005090;"><b>11600</b><br>(3900)</span>
</td>
<td colspan="8" rowspan="1" style="border-bottom-color: var(--cell-bg-color);"><span style="font-size: 110%;"><b>满贯</b></span><br><span style="font-size: 110%;"><b>12000</b></span><br>(4000)
</td></tr>
<tr>
<th>5番</th>
<td colspan="11" style="border-top: none;">
</td></tr>
<tr>
<th>6番<br>7番</th>
<td colspan="11"><span style="font-size: 110%;"><b>跳满</b></span><br><span style="font-size: 110%;"><b>18000</b></span><br>(6000)
</td></tr>
<tr>
<th>8番<br>9番<br>10番</th>
<td colspan="11"><span style="font-size: 110%;"><b>倍满</b></span><br><span style="font-size: 110%;"><b>24000</b></span><br>(8000)
</td></tr>
<tr>
<th>11番<br>12番</th>
<td colspan="11"><span style="font-size: 110%;"><b>三倍满</b></span><br><span style="font-size: 110%;"><b>36000</b></span><br>(12000)
</td></tr>
<tr>
<th>13番或以上</th>
<td colspan="11"><span style="font-size: 110%;"><b>累计役满</b>/<b>役满</b></span><br><span style="font-size: 110%;"><b>48000</b></span><br>(16000)
</td></tr></tbody></table>"""
table2 = """<table class="wikitable" style="text-align:center">
<tbody><tr>
<th></th>
<th>20符<br><small>(平和自摸)</small></th>
<th>25符<br><small>(七对子)</small></th>
<th>30符</th>
<th>40符</th>
<th>50符</th>
<th>60符</th>
<th>70符</th>
<th>80符</th>
<th>90符</th>
<th>100符</th>
<th>110符</th></tr>
<tr>
<th>1番</th>
<td>-</td>
<td>-</td>
<td><b>1000</b><br>(300,<br>500)</td>
<td><b>1300</b><br>(400,<br>700)</td>
<td><b>1600</b><br>(400,<br>800)</td>
<td><b>2000</b><br>(500,<br>1000)</td>
<td><b>2300</b><br>(600,<br>1200)</td>
<td><b>2600</b><br>(700,<br>1300)</td>
<td><b>2900</b><br>(800,<br>1500)</td>
<td><b>3200</b><br>(800,<br>1600)</td>
<td><b>3600</b><br>
</td></tr>
<tr>
<th>2番</th>
<td>- <br>(400,<br>700)</td>
<td><b>1600</b><br></td>
<td><b>2000</b><br>(500,<br>1000)</td>
<td><b>2600</b><br>(700,<br>1300)</td>
<td><b>3200</b><br>(800,<br>1600)</td>
<td><b>3900</b><br>(1000,<br>2000)</td>
<td><b>4500</b><br>(1200,<br>2300)</td>
<td><b>5200</b><br>(1300,<br>2600)</td>
<td><b>5800</b><br>(1500,<br>2900)</td>
<td><b>6400</b><br>(1600,<br>3200)</td>
<td><b>7100</b><br>(1800,<br>3600)
</td></tr>
<tr>
<th>3番</th>
<td>- <br>(700,<br>1300)</td>
<td><b>3200</b><br>(800,<br>1600)</td>
<td><b>3900</b><br>(1000,<br>2000)</td>
<td><b>5200</b><br>(1300,<br>2600)</td>
<td><b>6400</b><br>(1600,<br>3200)</td>
<td style="background-color: #ff8;"><span style="color:#005090;"><b>7700</b><br>(2000,<br>3900)</span></td>
<td colspan="5" rowspan="1" style="border-bottom-color: var(--cell-bg-color);">
</td></tr>
<tr>
<th>4番</th>
<td>- <br>(1300,<br>2600)</td>
<td><b>6400</b><br>(1600,<br>3200)</td>
<td style="background-color: #ff8;"><span style="color:#005090;"><b>7700</b><br>(2000,<br>3900)</span></td>
<td colspan="8" rowspan="1" style="border-bottom-color: var(--cell-bg-color);"><span style="font-size: 110%;"><b>满贯</b></span><br><span style="font-size: 110%;"><b>8000</b></span><br>(2000,<br>4000)
</td></tr>
<tr>
<th>5番</th>
<td colspan="11"></td></tr>
<tr>
<th>6番<br>7番</th>
<td colspan="11"><span style="font-size: 110%;"><b>跳满</b></span><br><span style="font-size: 110%;"><b>12000</b></span><br>(3000,<br>6000)</td></tr>
<tr>
<th>8番<br>9番<br>10番</th>
<td colspan="11"><span style="font-size: 110%;"><b>倍满</b></span><br><span style="font-size: 110%;"><b>16000</b></span><br>(4000,<br>8000)</td></tr>
<tr>
<th>11番<br>12番</th>
<td colspan="11"><span style="font-size: 110%;"><b>三倍满</b></span><br><span style="font-size: 110%;"><b>24000</b></span><br>(6000,<br>12000)
</td></tr>
<tr>
<th>13番或以上</th>
<td colspan="11"><span style="font-size: 110%;"><b>累计役满</b>/<b>役满</b></span><br><span style="font-size: 110%;"><b>32000</b></span><br>(8000,<br>16000)</td></tr></tbody></table>
"""


def score_table_page():
    ui.page_title('点数速查')
    with ui.card().classes('w-full flat bordered').style('overflow-x: scroll; max-width: 100vw'):
        with html.header().style('text-align:center; font-size: 32px;'):
            html.strong('点数速查')

        ui.label("""
        为方便通过符番数快速得出点数，这里将维基百科「日本麻將計分方法」中的速查表抄了过来，如下所示。
        """)

        with ui.tabs().style('overflow-x: scroll; max-width: 100vw') as tabs:
            one = ui.tab('亲家')
            two = ui.tab('子家')
        with ui.tab_panels(tabs, value=one):
            with ui.tab_panel(one):
                ui.html(table1, sanitize=False).style('overflow-x: scroll; max-width: 100vw')
            with ui.tab_panel(two):
                ui.html(table2, sanitize=False).style('overflow-x: scroll; max-width: 100vw')