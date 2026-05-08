# selection.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
import configparser
import os

# --- KONFIGURACE BAREV (Sjednoceno s Indigo tématem) ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
WHITE = [1, 1, 1, 1]

KV_SELECTION = f"""
<TournamentCheckbox@ButtonBehavior+BoxLayout>:
    active: False
    size_hint: None, None
    size: dp(45), dp(50)
    canvas:
        Color:
            rgba: {WIN_GREEN} if self.active else [0.4, 0.4, 0.5, 1]
        Line:
            circle: (self.center_x, self.center_y, dp(10))
            width: dp(1.1)
        Color:
            rgba: {WIN_GREEN} if self.active else (0,0,0,0)
        Ellipse:
            pos: (self.center_x - dp(6), self.center_y - dp(6))
            size: dp(12), dp(12)

<TournamentSelectCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(15), 0, 0, 0]
    canvas.before:
        Color:
            rgba: {CARD_BG}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]

    Label:
        text: root.player_name
        font_size: '16sp'
        color: {WHITE}
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        shorten: True
        max_lines: 1

    TournamentCheckbox:
        active: root.is_selected
        on_release: root.is_selected = not root.is_selected

<SelectionScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        MDTopAppBar:
            title: "VÝBĚR HRÁČŮ"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(15), dp(10)]
            spacing: dp(10)

            ScrollView:
                id: selection_scroll
                BoxLayout:
                    id: tournament_list
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(6)

            AnchorLayout:
                anchor_x: 'center'
                size_hint_y: None
                height: dp(80)
                Button:
                    text: "POTVRDIT"
                    size_hint: (None, None)
                    size: (dp(280), dp(55))
                    font_size: '18sp'
                    bold: True
                    color: 1, 1, 1, 1
                    background_normal: ''
                    background_color: 0, 0, 0, 0
                    on_release: 
                        app.get_selected_players()
                        app.go_to_setup()
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
"""

class TournamentSelectCard(BoxLayout):
    player_name = StringProperty("")
    is_selected = BooleanProperty(False)

class SelectionScreen(MDScreen):
    def __init__(self, **kwargs):
        Builder.load_string(KV_SELECTION)
        super().__init__(**kwargs)

    def on_enter(self):
        from kivy.app import App
        app = App.get_running_app()
        container = self.ids.tournament_list
        container.clear_widgets()
        
        # Reset scrollu na začátek
        if hasattr(self.ids, 'selection_scroll'):
            self.ids.selection_scroll.scroll_y = 1.0
        
        if os.path.exists(app.filename):
            config = configparser.ConfigParser()
            try:
                config.read(app.filename, encoding='utf-8')
                if 'players' in config:
                    names = config['players']['list'].split(',')
                    for name in names:
                        player_n = name.strip()
                        if player_n:
                            is_already_selected = player_n in app.selected_names
                            container.add_widget(TournamentSelectCard(
                                player_name=player_n,
                                is_selected=is_already_selected
                            ))
            except Exception as e:
                print(f"Chyba při načítání hráčů: {e}")
