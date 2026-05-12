# tournament_setup.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp
from kivymd.toast import toast
from kivy.core.clipboard import Clipboard
from kivy.app import App  # Přidáno pro přístup k web_server

import math
import socket
import datetime  # Přidáno pro formátování data na webu

# --- KONFIGURACE BAREV ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
#CARD_BG = [0.12, 0.15, 0.20, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
WHITE = [1, 1, 1, 1]

KV_SETUP = f"""
<SetupOptionCard@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(65)
    padding: [dp(15), 0]
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: {CARD_BG}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]

<CustomSwitch@ButtonBehavior+BoxLayout>:
    active: False
    size_hint: None, None
    size: dp(60), dp(26) 
    pos_hint: {{'center_y': .5}}
    canvas.before:
        Color:
            rgba: {WIN_GREEN} if self.active else [0.25, 0.25, 0.25, 1]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2,]
        Color:
            rgba: {WHITE}
        Ellipse:
            pos: (self.x + dp(3) + (self.width - dp(26)) * (1 if self.active else 0), self.y + dp(3))
            size: dp(20), dp(20)

<TournamentSetupScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        MDTopAppBar:
            title: "PŘEDVOLBY TURNAJE"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(20), dp(15)]
            spacing: dp(15)

            # 1. SEKCE: TYP ROZLOSOVÁNÍ
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                
                Label:
                    text: "PRVNÍ KOLO"
                    font_size: '13sp'
                    color: [0.5, 0.5, 0.5, 1]
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'
                    text_size: self.size

                SetupOptionCard:
                    Label:
                        text: "Typ rozlosování"
                        color: {WHITE}
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    BoxLayout:
                        size_hint: None, None
                        size: dp(170), dp(42)
                        pos_hint: {{'center_y': .5}}
                        spacing: dp(2)
                        canvas.before:
                            Color:
                                rgba: [0.2, 0.2, 0.2, 1]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(10),]

                        Button:
                            text: "NÁHODNÝ"
                            font_size: '11sp'
                            bold: True
                            background_normal: ''
                            background_color: (0,0,0,0)
                            color: {WHITE}
                            on_release: root.draw_type = "NÁHODNÝ"
                            canvas.before:
                                Color:
                                    rgba: app.theme_cls.primary_color if root.draw_type == "NÁHODNÝ" else (0,0,0,0)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(8), 0, 0, dp(8)]

                        Button:
                            text: "NASAZENÍ"
                            font_size: '11sp'
                            bold: True
                            background_normal: ''
                            background_color: (0,0,0,0)
                            color: {WHITE}
                            on_release: root.draw_type = "NASAZENÍ"
                            canvas.before:
                                Color:
                                    rgba: app.theme_cls.primary_color if root.draw_type == "NASAZENÍ" else (0,0,0,0)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [0, dp(8), dp(8), 0]

            # 2. SEKCE: PLAY-OFF
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)

                Label:
                    text: "ZÁVĚR TURNAJE"
                    font_size: '13sp'
                    color: [0.5, 0.5, 0.5, 1]
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'
                    text_size: self.size

                SetupOptionCard:
                    Label:
                        text: "Play off pro 4 nejlepší"
                        color: {WHITE}
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    CustomSwitch:
                        active: root.playoff_enabled
                        on_release: root.playoff_enabled = not root.playoff_enabled

            # 3. SEKCE: PARAMETRY TURNAJE
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)

                Label:
                    text: "PARAMETRY TURNAJE"
                    font_size: '13sp'
                    color: [0.5, 0.5, 0.5, 1]
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'
                    text_size: self.size

                SetupOptionCard:
                    Label:
                        text: "Počet hráčů"
                        color: {WHITE}
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                    
                    Label:
                        text: str(root.players_count)
                        bold: True
                        font_size: '20sp'
                        color: {WIN_GREEN}
                        size_hint_x: None
                        width: dp(60)

                SetupOptionCard:
                    Label:
                        text: "Počet základních kol"
                        color: {WHITE}
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                    
                    Label:
                        text: str(root.rounds_count)
                        bold: True
                        font_size: '22sp'
                        color: {WIN_GREEN}
                        size_hint_x: None
                        width: dp(60)


            # 4. SEKCE: TURNAJ ONLINE
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)

                Label:
                    text: "TURNAJ ONLINE"
                    font_size: '13sp'
                    color: [0.5, 0.5, 0.5, 1]
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'
                    text_size: self.size

                SetupOptionCard:
                    # Snížený pravý padding pro lepší zarovnání
                    padding: [dp(15), 0, dp(25), 0]

                    Label:
                        text: root.ip_address
                        color: {WHITE}
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                        font_size: '15sp'
                    
                    MDIconButton:
                        icon: "share-variant"
                        theme_text_color: "Custom"
                        text_color: {WIN_GREEN}
                        pos_hint: {{'center_y': .5}}
                        size_hint: None, None
                        size: dp(42), dp(42)
                        on_release: root.share_ip()

            Widget:

            AnchorLayout:
                anchor_x: 'center'
                size_hint_y: None
                height: dp(80)
                Button:
                    text: "START"
                    size_hint: (None, None)
                    size: (dp(280), dp(55))
                    font_size: '18sp'
                    bold: True
                    color: 1, 1, 1, 1
                    background_normal: ''
                    background_color: 0, 0, 0, 0
                    on_release: 
                        app.playoff_enabled = root.playoff_enabled
                        app.create_tournament(root.draw_type, root.rounds_count, root.playoff_enabled)
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
"""

class TournamentSetupScreen(MDScreen):
    draw_type = StringProperty("NÁHODNÝ")
    rounds_count = NumericProperty(0)
    players_count = NumericProperty(0)
    playoff_enabled = BooleanProperty(False)
    ip_address = StringProperty("Zjišťuji IP...")

    def __init__(self, **kwargs):
        Builder.load_string(KV_SETUP)
        super().__init__(**kwargs)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"http://{ip}:8000"
        except Exception:
            return "http://127.0.0.1:8000"

    def share_ip(self):
        Clipboard.copy(self.ip_address)
        toast(f"Adresa zkopírována: {self.ip_address}")

    def on_pre_enter(self):
        app = App.get_running_app()
        self.players_count = len(app.selected_names)
        self.rounds_count = self.swiss_rounds_logic(self.players_count)
        self.ip_address = self.get_local_ip()

        # ODESLÁNÍ DAT NA SERVER PRO DIVÁKY
        dnes = datetime.date.today().strftime("%d. %m. %Y")
        if app.web_server:
            app.web_server.update_data({
                "title": "Příprava turnaje",
                "date": dnes,
                "players_count": self.players_count,
                "rounds_count": self.rounds_count,
                "phase": "lobby"
            })

    def swiss_rounds_logic(self, n):
        if n <= 1: return 0
        base = math.ceil(math.log2(n))
        rounds = base + 1
        if n <= 10: return min(rounds, 4)
        if n <= 16: return min(rounds, 5)
        if n <= 32: return min(rounds, 6)
        if n <= 64: return min(rounds, 7)
        return min(rounds, 8)
