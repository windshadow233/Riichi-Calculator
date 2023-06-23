import streamlit as st

st.set_page_config(
    page_title="点数速查",
    page_icon="🔍",
)
style = """<style>
#MainMenu {visibility: hidden;}
.css-15zrgzn {display: none}
footer {visibility: hidden;}
[data-testid="column"] {
    width: calc(25% - 1rem) !important;
    flex: 1 1 calc(25% - 1rem) !important;
    min-width: calc(20% - 1rem) !important;
}
.css-1l269bu {max-width:20% !important;}
[data-testid="stText"] {font-size: 45px}
.tiles {height:100%; overflow-x:scroll; overflow-y:hidden; white-space: nowrap;margin : 0px 0 5px 0;}
.tile {height:50px;margin:1px}
.blank-tile {width: 10px;height:50px;}
.wikitable > tr > th, .wikitable > * > tr > th {
    background-color: #eaecf0;
    text-align: center;
}
.wikitable > tr > th, .wikitable > tr > td, .wikitable > * > tr > th, .wikitable > * > tr > td {
    border: 1px solid #a2a9b1;
    padding: 0.2em 0.4em;
}
th {
    display: table-cell;
    vertical-align: inherit;
    font-weight: bold;
    text-align: -internal-center;
}
.wikitable {
    background-color: #f8f9fa;
    color: #202122;
    margin: 1em 0;
    border: 1px solid #a2a9b1;
    border-collapse: collapse;
}
table {
    border-collapse: separate;
    text-indent: initial;
    border-spacing: 2px;
}
</style>
"""
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
<td colspan="5" rowspan="1" style="border-bottom-color: #f8f9fa;">
</td></tr>
<tr>
<th>4番</th>
<td>- <br>(2600)</td>
<td><b>9600</b><br>(3200)</td>
<td style="background-color: #ff8;"><span style="color:#005090;"><b>11600</b><br>(3900)</span>
</td>
<td colspan="8" rowspan="1" style="border-bottom-color: #f8f9fa;"><span style="font-size: 110%;"><b>满贯</b></span><br><span style="font-size: 110%;"><b>12000</b></span><br>(4000)
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
<td colspan="5" rowspan="1" style="border-bottom-color: #f8f9fa;">
</td></tr>
<tr>
<th>4番</th>
<td>- <br>(1300,<br>2600)</td>
<td><b>6400</b><br>(1600,<br>3200)</td>
<td style="background-color: #ff8;"><span style="color:#005090;"><b>7700</b><br>(2000,<br>3900)</span></td>
<td colspan="8" rowspan="1" style="border-bottom-color: #f8f9fa;"><span style="font-size: 110%;"><b>满贯</b></span><br><span style="font-size: 110%;"><b>8000</b></span><br>(2000,<br>4000)
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
st.write(style, unsafe_allow_html=True)
tabs = [s.center(6, '\u2001') for s in ['亲家', '子家']]
tab1, tab2 = st.tabs(tabs)
with tab1:
    st.write(table1, unsafe_allow_html=True)
with tab2:
    st.write(table2, unsafe_allow_html=True)