# final_leaderboard.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.factory import Factory
from kivymd.app import MDApp

# --- KONFIGURACE BAREV (Sjednoceno) ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
WHITE = [1, 1, 1, 1]
GREY = [0.6, 0.6, 0.6, 1]
BLACK = [0.0, 0.0, 0.0, 1]

# KOVY PRO MEDAILE
GOLD = [0.831, 0.686, 0.216, 1]
SILVER = [0.75, 0.75, 0.75, 1] 
BRONZE = [0.75, 0.5, 0.3, 1]

KV_FINAL = f'''
<FinalLeaderboardCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(10), 0, dp(5), 0]
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: {CARD_BG}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]

    Label:
        text: root.rank
        size_hint_x: None
        width: dp(30)
        font_size: '14sp'
        bold: True
        color: root.text_color
        canvas.before:
            Color:
                rgba: root.circle_color
            Ellipse:
                pos: self.x + dp(2), self.center_y - dp(13)
                size: dp(26), dp(26)

    Label:
        text: root.player_name
        font_size: '16sp'
        color: {WHITE}
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        shorten: True
        shorten_from: 'right'

    BoxLayout:
        size_hint_x: None
        width: dp(85)
        orientation: 'horizontal'
        spacing: dp(2)
        
        Label:
            text: root.points
            size_hint_x: 0.5
            font_size: '17sp'
            bold: True
            color: {WIN_GREEN}
            halign: 'center'
        
        Label:
            text: root.bh
            size_hint_x: 0.5
            font_size: '13sp'
            color: {WHITE}
            halign: 'center'

<FinalLeaderboardScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        # --- TOPBAR S DYNAMICKÝM TITULKEM ---
        MDTopAppBar:
            id: toolbar
            title: "VÝSLEDKY - ZÁKLADNÍ ČÁST" if root.playoff_active else "VÝSLEDKY TURNAJE"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(15), dp(10)]
            spacing: dp(5)

            # HLAVIČKA TABULKY
            BoxLayout:
                size_hint_y: None
                height: dp(25)
                padding: [dp(10 + 30 + 8), 0, dp(5), 0] 
                spacing: dp(8)
                
                Label:
                    text: "HRÁČ"
                    halign: 'left'
                    text_size: self.size
                    color: {GREY}
                    font_size: '11sp'
                
                BoxLayout:
                    size_hint_x: None
                    width: dp(85)
                    orientation: 'horizontal'
                    Label:
                        text: "BODY"
                        font_size: '11sp'
                        color: {GREY}
                        halign: 'center'
                    Label:
                        text: "BH"
                        font_size: '11sp'
                        color: {GREY}
                        halign: 'center'

            ScrollView:
                id: final_scroll
                BoxLayout:
                    id: final_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(6)

            # --- SPODNÍ TLAČÍTKO (Sjednocené rozměry dp(55)) ---
            AnchorLayout:
                anchor_x: 'center'
                size_hint_y: None
                height: dp(80)
                Button:
                    text: "PLAY OFF" if root.playoff_active else "UKONČIT TURNAJ"
                    size_hint: (None, None)
                    size: (dp(280), dp(55))
                    font_size: '18sp'
                    bold: True
                    color: {WHITE}
                    background_normal: ''
                    background_color: (0,0,0,0)
                    on_release: 
                        if root.playoff_active: app.start_playoff()
                        else: app.go_back_to_home()
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
'''

class FinalLeaderboardCard(BoxLayout):
    rank = StringProperty("1")
    player_name = StringProperty("")
    points = StringProperty("0")
    bh = StringProperty("0")
    playoff_active = BooleanProperty(False)
    circle_color = ListProperty([0.247, 0.318, 0.710, 1]) # Default Indigo
    text_color = ListProperty(WHITE)

    def on_rank(self, *args):
        self.update_colors()

    def update_colors(self):
        try:
            r = int(self.rank)
        except:
            r = 0
            
        app = MDApp.get_running_app()
        default_color = app.theme_cls.primary_color

        if self.playoff_active:
            if r <= 4:
                self.circle_color = WIN_GREEN
                self.text_color = BLACK
            else:
                self.circle_color = default_color
                self.text_color = WHITE
        else:
            if r == 1:
                self.circle_color = GOLD
                self.text_color = BLACK
            elif r == 2:
                self.circle_color = SILVER
                self.text_color = BLACK
            elif r == 3:
                self.circle_color = BRONZE
                self.text_color = BLACK
            else:
                self.circle_color = default_color
                self.text_color = WHITE

class FinalLeaderboardScreen(MDScreen):
    playoff_active = BooleanProperty(False)

    def __init__(self, **kwargs):
        Builder.load_string(KV_FINAL)
        super().__init__(**kwargs)

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        self.playoff_active = getattr(app, 'playoff_enabled', False)
        self.ids.final_container.clear_widgets()
        if hasattr(self.ids, 'final_scroll'):
            self.ids.final_scroll.scroll_y = 1.0

    def on_enter(self):
        app = MDApp.get_running_app()
        container = self.ids.final_container
        container.clear_widgets()
        ranking = app.app_manager.get_ranking()
        
        for i, player in enumerate(ranking):
            bh_val = player.get('buchholz', 0)
            bh_display = str(int(bh_val)) if bh_val == int(bh_val) else f"{bh_val:.1f}"
            
            card = FinalLeaderboardCard(
                rank=str(i + 1),
                player_name=player['name'],
                points=str(int(player['points'])),
                bh=bh_display,
                playoff_active=self.playoff_active
            )
            card.update_colors()
            container.add_widget(card)

Factory.register('FinalLeaderboardCard', cls=FinalLeaderboardCard)
