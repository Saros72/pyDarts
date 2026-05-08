# cast_dialog.py
import time
import socket
import threading
import os
import random
import pychromecast
from PIL import Image, ImageDraw, ImageFont
from http.server import HTTPServer, SimpleHTTPRequestHandler

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, MDList
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

# --- KONFIGURACE BAREV (Indigo #3F51B5) ---
INDIGO_MAIN = (63, 81, 181)       # Pro PIL (RGB 0-255)
HEX_PRIMARY = "#3F51B5"           # Pro Kivy (Hex)

DARK_BG = (13, 13, 18)
CARD_BG = (31, 31, 36)
WIN_GREEN = (0, 230, 102)
WHITE = (255, 255, 255)
IMAGE_NAME = "bracket.png"
PORT = 8000
DEFAULT_APP_ID = "CC1AD845"

PLAYERS = [{"name": f"Procházková Martina {i+1}", "points": 0} for i in range(32)]

# --- POMOCNÉ FUNKCE ---
def truncate_device_name(name, limit=28):
    if len(name) <= limit: return name
    return name[:limit-3] + "..."

def shorten_name(name, font, max_width):
    if font.getlength(name) <= max_width: return name
    temp = name
    while font.getlength(temp + "...") > max_width and len(temp) > 0: temp = temp[:-1]
    return temp.strip() + "..."

def generate_leaderboard_image(players, round_num):
    W, H = 1920, 1080
    img = Image.new('RGB', (W, H), color=DARK_BG)
    draw = ImageDraw.Draw(img)
    font_path = "/system/fonts/Roboto-Bold.ttf"
    if not os.path.exists(font_path): font_path = "/system/fonts/DroidSans-Bold.ttf"

    def get_font(size):
        try: return ImageFont.truetype(font_path, size)
        except: return ImageFont.load_default()

    num_players = len(players)
    if num_players > 40: col_count, col_w, gap = 3, 550, 50
    elif num_players > 14: col_count, col_w, gap = 2, 750, 80
    else: col_count, col_w, gap = 1, 850, 0

    items_per_col = (num_players + col_count - 1) // col_count
    top_p, bot_p, t_size, t_gap = 50, 30, 75, 35
    available_h = H - top_p - t_size - t_gap - bot_p
    spacing = 10
    card_h = min(95, (available_h // items_per_col) - spacing)
    start_y = top_p + t_size + t_gap
    total_w = (col_w * col_count) + (gap * (col_count - 1))
    start_x = (W - total_w) // 2

    title_f = get_font(t_size)
    name_f = get_font(int(card_h * 0.60))
    pts_f = get_font(int(card_h * 0.75))
    rank_f = get_font(int(card_h * 0.45))

    # Titulek v obrázku je nyní bílý
    draw.text((W//2, top_p + (t_size//2)), f"POŘADÍ TURNAJE - KOLO {round_num}/6", fill=WHITE, font=title_f, anchor="mm")

    sorted_p = sorted(players, key=lambda x: x['points'], reverse=True)
    v_offset = int(card_h * 0.02)

    for i, p in enumerate(sorted_p):
        col, row = i // items_per_col, i % items_per_col
        x, y = start_x + (col * (col_w + gap)), start_y + (row * (card_h + spacing))
        if y + card_h > H - 5: break
        
        draw.rounded_rectangle([x-1, y-1, x + col_w + 1, y + card_h + 1], radius=15, fill=INDIGO_MAIN)
        draw.rounded_rectangle([x, y, x + col_w, y + card_h], radius=15, fill=CARD_BG)
        cy = y + (card_h // 2)
        cy_text, circle_r = cy + v_offset, int(card_h // 2.5)
        
        draw.ellipse([x + 18, cy - circle_r, x + 18 + circle_r*2, cy + circle_r], fill=INDIGO_MAIN)
        draw.text((x + 18 + circle_r, cy_text), str(i+1), fill=WHITE, font=rank_f, anchor="mm")
        
        disp_name = shorten_name(p["name"].upper(), name_f, col_w - (circle_r * 2) - 150)
        draw.text((x + (circle_r * 2) + 50, cy_text), disp_name, fill=WHITE, font=name_f, anchor="lm")
        draw.text((x + col_w - 30, cy_text), str(p["points"]), fill=WIN_GREEN, font=pts_f, anchor="rm")
    
    img.save(IMAGE_NAME)

# --- UI KOMPONENTY ---

class DeviceItem(OneLineIconListItem):
    def __init__(self, cast, callback, **kwargs):
        safe_name = truncate_device_name(cast.name)
        super().__init__(
            text=safe_name, 
            theme_text_color="Custom", 
            text_color=[1, 1, 1, 1], 
            **kwargs
        )
        self.cast = cast
        self.on_release = lambda: callback(cast)
        icon = IconLeftWidget(icon="television", theme_text_color="Custom", text_color=[1, 1, 1, 1])
        self.add_widget(icon)

class CastHandler:
    browser = None

    def show_device_dialog(self):
        self.app = MDApp.get_running_app()
        self.container = MDBoxLayout(orientation="vertical", spacing=dp(5), padding=[dp(5), dp(5), dp(10), dp(10)], size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))

        self.loader_box = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40), padding=[dp(10), 0, 0, 0])
        
        # Okamžitě bílý spinner
        self.spinner = MDSpinner(
            size_hint=(None, None), 
            size=(dp(24), dp(24)), 
            active=True, 
            pos_hint={'center_y': .5},
            palette=[[1, 1, 1, 1], [1, 1, 1, 1]],
            line_width=dp(2.2)
        )
        
        self.loader_label = MDLabel(
            text="Vyhledávání...", 
            theme_text_color="Custom", 
            text_color=[1, 1, 1, 1],
            valign="middle", 
            size_hint_y=None, 
            height=dp(40)
        )
        
        self.loader_box.add_widget(self.spinner)
        self.loader_box.add_widget(self.loader_label)
        self.container.add_widget(self.loader_box)

        self.scroll = ScrollView(size_hint=(1, None))
        self.device_list = MDList(size_hint_y=None)
        self.device_list.bind(minimum_height=self.device_list.setter('height'))
        self.scroll.add_widget(self.device_list)
        self.container.add_widget(self.scroll)

        self.dialog = MDDialog(
            title="ODESLAT DO ZAŘÍZENÍ",
            type="custom",
            content_cls=self.container,
            size_hint=(0.85, None),
            auto_dismiss=False,
            buttons=[MDFlatButton(text="ZRUŠIT", theme_text_color="Custom", text_color=[1, 1, 1, 1], on_release=lambda x: self.dialog.dismiss())],
        )
        
        self.dialog.md_bg_color = get_color_from_hex(HEX_PRIMARY)
        
        self.dialog.open()
        Clock.schedule_once(lambda dt: self.fix_layout(), 0.1)
        threading.Thread(target=self.discover_devices, daemon=True).start()

    def fix_layout(self, *args):
        max_dialog_h = self.app.root.height * 0.65
        needed_h = self.container.padding[1] + self.loader_box.height + self.device_list.height + dp(105)
        self.dialog.height = min(max_dialog_h, needed_h)
        self.scroll.height = self.dialog.height - self.container.padding[1] - self.loader_box.height - dp(115)

    def discover_devices(self):
        chromecasts, browser = pychromecast.get_chromecasts()
        self.browser = browser
        filtered = [c for c in chromecasts if not any(x in c.model_name.lower() for x in ["mini", "audio", "speaker", "nest"])]
        Clock.schedule_once(lambda dt: self.update_device_list(filtered))

    def update_device_list(self, chromecasts):
        if self.loader_box.parent:
            self.container.remove_widget(self.loader_box)
            self.loader_box.height = 0
        self.device_list.clear_widgets()
        self.device_list.add_widget(Widget(size_hint_y=None, height=dp(10)))

        if not chromecasts:
            self.device_list.add_widget(OneLineIconListItem(text="Žádná TV nenalezena.", theme_text_color="Custom", text_color=[1, 1, 1, 1]))
        else:
            for cast in chromecasts:
                self.device_list.add_widget(DeviceItem(cast, self.select_device))
        Clock.schedule_once(lambda dt: self.fix_layout(), 0.1)

    def select_device(self, cast):
        self.dialog.dismiss()
        threading.Thread(target=self.broadcast_logic, args=(cast,), daemon=True).start()

    def reset_and_start_tv(self, cast):
        cast.wait()
        try:
            cast.quit_app()
            time.sleep(2)
        except: pass
        cast.start_app(DEFAULT_APP_ID)
        time.sleep(4)
        return cast.media_controller

    def broadcast_logic(self, cast):
        try:
            threading.Thread(target=lambda: HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1)); local_ip = s.getsockname()[0]; s.close()

            mc = self.reset_and_start_tv(cast)
            if self.browser: self.browser.stop_discovery()

            base_url = f"http://{local_ip}:{PORT}/{IMAGE_NAME}"
            for r in range(1, 7):
                PLAYERS.sort(key=lambda x: x['points'], reverse=True)
                for i in range(0, len(PLAYERS), 2):
                    if i+1 < len(PLAYERS): PLAYERS[random.choice([i, i+1])]['points'] += 1
                
                generate_leaderboard_image(PLAYERS, r)
                url = f"{base_url}?v={int(time.time())}"
                mc.play_media(url, "image/png")
                time.sleep(2); mc.play(); time.sleep(10)
        except Exception as e: print("Chyba:", e)
