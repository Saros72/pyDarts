# player_manager.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.clock import Clock
import configparser
import os

# --- KONFIGURACE BAREV ---
DARK_BG = [0.1, 0.1, 0.12, 1]
CARD_BG = [0.18, 0.18, 0.22, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
RED_ERROR = [1, 0.3, 0.3, 1]
WHITE = [1, 1, 1, 1]
INDIGO_PRIMARY = [0.247, 0.318, 0.710, 1]

KV_PLAYERS = f"""
<PlayerEntryCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(55)
    padding: [dp(12), 0, 0, 0]
    spacing: dp(5)
    canvas.before:
        Color:
            rgba: {CARD_BG}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]

    Label:
        text: root.player_name
        font_size: '18sp'
        color: {WHITE}
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        shorten: True
        shorten_from: 'right'
        max_lines: 1

    BoxLayout:
        size_hint_x: None
        width: dp(120)
        spacing: 0
        Button:
            size_hint: None, None
            size: dp(35), dp(55)
            background_normal: ''
            background_color: (0,0,0,0)
            on_release: root.screen.move_player(root, -1)
            canvas:
                Color:
                    rgba: [0.6, 0.6, 0.6, 1]
                Triangle:
                    points: [self.x + dp(10), self.y + dp(22), self.x + dp(25), self.y + dp(22), self.x + dp(17.5), self.y + dp(35)]
        Button:
            size_hint: None, None
            size: dp(35), dp(55)
            background_normal: ''
            background_color: (0,0,0,0)
            on_release: root.screen.move_player(root, 1)
            canvas:
                Color:
                    rgba: [0.6, 0.6, 0.6, 1]
                Triangle:
                    points: [self.x + dp(10), self.y + dp(33), self.x + dp(25), self.y + dp(33), self.x + dp(17.5), self.y + dp(20)]
        Button:
            text: "×"
            size_hint: None, None
            size: dp(50), dp(55)
            background_normal: ''
            background_color: (0,0,0,0)
            font_size: '32sp'
            color: {RED_ERROR}
            on_release: root.screen.remove_player(root)

<PlayerListScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        MDTopAppBar:
            title: "Seznam hráčů"
            anchor_title: "left"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.go_back_to_home()]]

        BoxLayout:
            orientation: 'vertical'
            padding: [dp(15), dp(15)]
            spacing: dp(15)

            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(55)
                canvas.before:
                    Color:
                        rgba: {CARD_BG}
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(10),]
                TextInput:
                    id: player_input
                    hint_text: "Jméno hráče..."
                    multiline: False
                    font_size: '18sp'
                    padding: [dp(12), (self.height - self.line_height) / 2]
                    background_normal: ''
                    background_color: (0,0,0,0)
                    foreground_color: {WHITE}
                    cursor_color: {INDIGO_PRIMARY}
                    hint_text_color: [0.5, 0.5, 0.5, 1]
                    on_text_validate: root.add_player()
                
                Widget:
                    size_hint_x: None
                    width: dp(70)

                Button:
                    text: "+"
                    size_hint: None, None
                    size: dp(50), dp(55)
                    font_size: '35sp'
                    color: {WIN_GREEN}
                    background_normal: ''
                    background_color: (0,0,0,0)
                    on_release: root.add_player()

            ScrollView:
                id: scroll_view
                BoxLayout:
                    id: player_list
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)
"""

class PlayerEntryCard(BoxLayout):
    player_name = StringProperty("")
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen

class PlayerListScreen(MDScreen):
    filename = "players.ini"

    def __init__(self, **kwargs):
        Builder.load_string(KV_PLAYERS)
        super().__init__(**kwargs)
        self.load_players_to_ui()

    def scroll_to_bottom(self, dt):
        self.ids.scroll_view.scroll_y = 0

    def add_player(self, name_text=None):
        ti = self.ids.player_input
        name = name_text if name_text else ti.text.strip().title()
        if name:
            new_card = PlayerEntryCard(player_name=name, screen=self)
            self.ids.player_list.add_widget(new_card)
            if not name_text: 
                ti.text = ""
                # Odrolování dolů po přidání nového hráče
                Clock.schedule_once(self.scroll_to_bottom, 0.1)
            
            self.save_players()

    def remove_player(self, card_instance):
        if card_instance.parent:
            card_instance.parent.remove_widget(card_instance)
            self.save_players()

    def move_player(self, card, direction):
        container = self.ids.player_list
        if card in container.children:
            idx = container.children.index(card)
            new_idx = idx - direction 
            if 0 <= new_idx < len(container.children):
                container.remove_widget(card)
                container.add_widget(card, index=new_idx)
                self.save_players()

    def save_players(self):
        players = [child.player_name for child in reversed(self.ids.player_list.children) if hasattr(child, 'player_name')]
        config = configparser.ConfigParser()
        config['players'] = {'list': ','.join(players)}
        try:
            with open(self.filename, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Chyba při ukládání: {e}")

    def load_players_to_ui(self):
        if os.path.exists(self.filename):
            config = configparser.ConfigParser()
            try:
                config.read(self.filename, encoding='utf-8')
                if 'players' in config and 'list' in config['players']:
                    names_str = config['players']['list']
                    if names_str:
                        names = names_str.split(',')
                        for name in names:
                            if name.strip():
                                # Načtení bez automatického scrollu a zbytečného ukládání
                                new_card = PlayerEntryCard(player_name=name.strip(), screen=self)
                                self.ids.player_list.add_widget(new_card)
            except Exception as e:
                print(f"Chyba při načítání: {e}")
