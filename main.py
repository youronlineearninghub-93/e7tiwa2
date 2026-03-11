import os
import random
import requests
import textwrap
import gspread
import json
from google.oauth2.service_account import Credentials
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

# --- 1. إعدادات الخط ---
FONT_PATH = "Cairo-Bold.ttf"
if not os.path.exists(FONT_PATH):
    url = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf"
    r = requests.get(url)
    with open(FONT_PATH, "wb") as f: f.write(r.content)

# --- 2. الربط مع جوجل (باستخدام السر اللي هنحطه في GitHub) ---
def connect_google():
    # بياخد المفتاح من GitHub Secrets
    info = json.loads(os.environ['GCP_CREDENTIALS'])
    creds = Credentials.from_service_account_info(info, scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])
    return gspread.authorize(creds)

def create_text_sticker(text, v_w, v_h):
    wrapped = textwrap.wrap(text, width=38)
    ready_text = "\n".join([get_display(reshape(line)) for line in wrapped])
    img = Image.new('RGBA', (v_w, v_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = 52
    max_h = int(v_h * 0.5)
    while font_size > 18:
        font = ImageFont.truetype(FONT_PATH, font_size)
        bbox = draw.multiline_textbbox((0, 0), ready_text, font=font, spacing=12)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_h < max_h: break
        font_size -= 2

    x = (v_w - text_w) // 2
    y = int(v_h * 0.25) # المكان المظبوط بين الخطوط
    
    # رسم Outline أسود ونصوص بيضاء (ستايل Canva)
    draw.multiline_text((x, y), ready_text, font=font, fill="white", 
                        align="center", spacing=12, stroke_width=2, stroke_fill="black")
    img.save("temp_text.png")
    return "temp_text.png"

# --- 3. التشغيل الرئيسي ---
def run():
    gc = connect_google()
    # حطي لينك الشيت بتاعك هنا مكان الكلمة دي
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1CSL5eVnFIv5on8UhZZaOE1-X96aDDRryDa3NXew-hwI/edit"
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.get_worksheet(0)
    texts = worksheet.col_values(1)[1:] # بياخد القصص من أول عمود

    # هنا هيفترض إن عندك فولدر فيديوهات على GitHub للتجربة حالياً
    # (لاحقاً هنخليه يسحب من الدرايف)
    video_files = [f for f in os.listdir('raw_videos') if f.endswith(('.mp4', '.mov'))]
    
    for i, t in enumerate(texts):
        video_path = os.path.join('raw_videos', random.choice(video_files))
        clip = VideoFileClip(video_path)
        sticker = create_text_sticker(t, clip.w, clip.h)
        text_clip = ImageClip(sticker).set_duration(clip.duration)
        final = CompositeVideoClip([clip, text_clip])
        final.write_videofile(f"output_{i}.mp4", fps=24, codec="libx264")

if __name__ == "__main__":
    run()
