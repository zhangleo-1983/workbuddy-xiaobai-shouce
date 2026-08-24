#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《WorkBuddy 能干什么》朋友圈海报：竖版 + 可扫二维码（指向手册链接）。"""
import qrcode
from PIL import Image, ImageDraw, ImageFont

URL = "https://83c5ab1d2e97468785bd69bca2f2eac3.app.workbuddy.link"
OUT = "/Users/zhangliang/WorkBuddy/2026-08-24-13-51-12/朋友圈海报.png"

W, H = 1080, 1560
HIRAGINO = "/System/Library/Fonts/Hiragino Sans GB.ttc"
STHEITI = "/System/Library/Fonts/STHeiti Medium.ttc"

def font(path, size, idx=0):
    return ImageFont.truetype(path, size, index=idx)

def vgradient(w, h, c1, c2):
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        px[0, y] = (r, g, b)
    return base.resize((w, h))

# 背景：深蓝渐变
img = vgradient(W, H, (15, 28, 71), (37, 99, 235))
draw = ImageDraw.Draw(img, "RGBA")

# 顶部柔光
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-260, -360, 620, 520], fill=(96, 165, 250, 70))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

WHITE = (255, 255, 255, 255)
SOFT = (255, 255, 255, 205)
BLUE = (219, 234, 254, 255)

# 顶部胶囊标签
pill_w, pill_h = 360, 70
pill_x, pill_y = (W - pill_w) // 2, 120
draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                       radius=35, fill=(255, 255, 255, 38), outline=(255, 255, 255, 90))
draw.text(((W) // 2, pill_y + pill_h // 2), "小白 AI 上手指南", font=font(HIRAGINO, 32),
          fill=WHITE, anchor="mm")

# 主标题
draw.text((W // 2, 320), "WorkBuddy 能干什么", font=font(STHEITI, 84),
          fill=WHITE, anchor="mm")
draw.text((W // 2, 410), "小白 AI 实用场景手册", font=font(HIRAGINO, 40),
          fill=BLUE, anchor="mm")

# 描述三行
lines = ["22 篇真实场景，每篇只要 3 分钟", "翻到哪篇，用到哪篇", "Prompt 一键复制，照着做就行"]
y = 520
for ln in lines:
    draw.text((W // 2, y), ln, font=font(HIRAGINO, 38), fill=SOFT, anchor="mm")
    y += 60

# 白色卡片
card_w, card_h = 660, 700
card_x = (W - card_w) // 2
card_y = 760
draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                       radius=36, fill=(255, 255, 255, 255))

# 二维码
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,
                   box_size=12, border=4)
qr.add_data(URL)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="#0f172a", back_color="white").convert("RGB")
qr_size = 460
qr_img = qr_img.resize((qr_size, qr_size))
qr_x = (W - qr_size) // 2
qr_y = card_y + 60
img.paste(qr_img, (qr_x, qr_y))

# 卡片内文字
draw.text((W // 2, qr_y + qr_size + 55), "长按识别二维码", font=font(STHEITI, 40),
          fill=(15, 23, 42, 255), anchor="mm")
draw.text((W // 2, qr_y + qr_size + 110), "手机 / 电脑都能看 · 完全免费",
          font=font(HIRAGINO, 30), fill=(100, 116, 139, 255), anchor="mm")

# 底部
draw.text((W // 2, H - 70), "扫码读手册，先让 AI 帮你干一件小事",
          font=font(HIRAGINO, 32), fill=SOFT, anchor="mm")

img.convert("RGB").save(OUT, "PNG")
print("OK ->", OUT)
