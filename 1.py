from PIL import Image, ImageDraw, ImageFont

def make_hela_png(path="hela.png"):
    W, H = 368, 512
    R = 30   # 圆角半径，可调大或调小

    # --- 白色背景 ---
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # --- 生成圆角蒙版 ---
    mask = Image.new("L", (W, H), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, W, H), radius=R, fill=255)

    # --- 应用圆角 ---
    img.putalpha(mask)

    draw = ImageDraw.Draw(img)

    # 自动调字体，使两字合适
    def get_font(size):
        try:
            return ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", size)
        except:
            return ImageFont.load_default()

    target_h = int(H * 0.75)  # 目标高度比例
    font_size = 25
    while True:
        font = get_font(font_size)
        h1 = draw.textbbox((0, 0), "和", font=font)[3]
        h2 = draw.textbbox((0, 0), "了", font=font)[3]
        if h1 + h2 >= target_h:
            break
        font_size += 4

    font = get_font(font_size)

    # 字位置
    w1, h1 = draw.textsize("和", font=font)
    w2, h2 = draw.textsize("了", font=font)

    total_h = h1 + h2
    y1 = (H - total_h) // 2
    y2 = y1 + h1

    x1 = (W - w1) // 2
    x2 = (W - w2) // 2

    draw.text((x1, y1), "和", fill="#902118", font=font, stroke_width=4)
    draw.text((x2, y2), "了", fill="#902118", font=font, stroke_width=4)

    img.save(path)
    print("saved:", path)


make_hela_png('static/png/agari.png')
