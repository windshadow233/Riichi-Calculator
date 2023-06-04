from st_pages import show_pages, Page
# menu = ["计算器", "役种一览"]
# choice = st.sidebar.selectbox("Menu", menu, label_visibility='collapsed')
# if choice == "计算器":
#     calculator_ui()

show_pages(
    [
        Page("pages/calculator.py", "麻雀の計算", icon="🧮"),
        Page("pages/yaku_list.py", "役种一览", icon="📋")
    ]
)