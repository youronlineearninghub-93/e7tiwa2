import os
import requests

# 1. تحميل الخط أوتوماتيكياً لو مش موجود
FONT_PATH = "Cairo-Bold.ttf"
if not os.path.exists(FONT_PATH):
    print("Downloading font...")
    url = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf"
    r = requests.get(url)
    with open(FONT_PATH, "wb") as f:
        f.write(r.content)

# 2. بقية الكود اللي هيظبط العربي والألوان والمقاسات
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_text_sticker(text, v_w, v_h):
    # معالجة العربي
    wrapped = textwrap.wrap(text, width=38)
    ready_text = "\n".join([get_display(reshape(line)) for line in wrapped])
    
    img = Image.new('RGBA', (v_w, v_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # اختيار مقاس الخط المناسب (Auto-resize)
    font_size = 52
    max_h = int(v_h * 0.5) # المساحة اللي حددتيها في الصور
    
    while font_size > 18:
        font = ImageFont.truetype(FONT_PATH, font_size)
        bbox = draw.multiline_textbbox((0, 0), ready_text, font=font, spacing=12)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_h < max_h: break
        font_size -= 2

    # الإحداثيات (بين علامات التنصيص بالظبط)
    x = (v_w - text_w) // 2
    y = int(v_h * 0.25) # البداية من الخط العلوي في صورتك size.PNG
    
    # الرسم (أبيض + Outline أسود)
    draw.multiline_text((x, y), ready_text, font=font, fill="white", 
                        align="center", spacing=12, stroke_width=2, stroke_fill="black")
    
    img.save("temp_text.png")
    return "temp_text.png"

print("Main Script Ready!")
