# tournament_dashboard.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, ColorProperty, BooleanProperty, NumericProperty
from kivy.factory import Factory
from kivymd.app import MDApp
from kivymd.toast import toast

# --- KONFIGURACE BAREV ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
HEADER_BG = [0.12, 0.14, 0.2, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
WHITE = [1, 1, 1, 1]

Builder.load_string(f"""
<TournamentCheckbox@ButtonBehavior+BoxLayout>:
    active: False
    size_hint: None, None
    size: dp(50), dp(50)
    canvas:
        Color:
            rgba: {WIN_GREEN} if self.active else [0.4, 0.4, 0.5, 1]
        Line:
            circle: (self.center_x, self.center_y, dp(11))
            width: dp(1.2)
        Color:
            rgba: {WIN_GREEN} if self.active else (0,0,0,0)
        Ellipse:
            pos: (self.center_x - dp(6.5), self.center_y - dp(6.5))
            size: dp(13), dp(13)

<PairCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(135)
    canvas.before:
        Color:
            rgba: {CARD_BG}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15),]

    # --- ZÁHLAVÍ (Zápas / BYE) ---
    BoxLayout:
        size_hint_y: None
        height: dp(32)
        canvas.before:
            Color:
                rgba: {HEADER_BG}
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [(dp(15), dp(15)), (dp(15), dp(15)), (0, 0), (0, 0)]
        Label:
            text: "BYE" if root.is_bye else root.match_label
            font_size: '14sp'
            color: app.theme_cls.primary_color
            bold: True
            halign: 'center'
            letter_spacing: 1.2

    # --- OBSAH ---
    MDBoxLayout:
        orientation: 'vertical'
        padding: [dp(15), dp(5), dp(5), dp(10)]
        
        # SEKCE ZÁPAS
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(2)
            opacity: 1 if not root.is_bye else 0
            disabled: root.is_bye
            size_hint_y: 1 if not root.is_bye else 0.001

            BoxLayout:
                orientation: 'horizontal'
                Label:
                    text: root.player1
                    color: {WHITE}
                    font_size: '17sp'
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size
                    shorten: True
                    shorten_from: 'right'  # Zkracování na konci
                    max_lines: 1
                TournamentCheckbox:
                    active: root.winner == 1
                    pos_hint: {{'center_y': .5}}
                    on_release: root.select_winner(1)

            Widget:
                size_hint_y: None
                height: dp(2)
                canvas:
                    Color:
                        rgba: [1, 1, 1, 0.08]
                    Line:
                        points: [self.x + dp(5), self.y, self.right - dp(20), self.y]
                        width: 1

            BoxLayout:
                orientation: 'horizontal'
                Label:
                    text: root.player2
                    color: {WHITE}
                    font_size: '17sp'
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size
                    shorten: True
                    shorten_from: 'right'  # Zkracování na konci
                    max_lines: 1
                TournamentCheckbox:
                    active: root.winner == 2
                    pos_hint: {{'center_y': .5}}
                    on_release: root.select_winner(2)

        # SEKCE BYE
        MDBoxLayout:
            orientation: 'vertical'
            opacity: 1 if root.is_bye else 0
            disabled: not root.is_bye
            size_hint_y: 1 if root.is_bye else 0.001
            Label:
                text: root.player1
                font_size: '17sp'
                bold: False
                color: {WIN_GREEN}
                halign: 'center'
                valign: 'middle'
                text_size: self.size
                shorten: True
                shorten_from: 'right' # Zkracování na konci i u BYE

<TournamentDashboardScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}
        MDTopAppBar:
            title: "KOLO " + str(root.current_round) + "/" + str(root.total_rounds)
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(20), dp(15)]
            spacing: dp(15)
            ScrollView:
                id: dashboard_scroll
                BoxLayout:
                    id: pairs_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(12)
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
                    color: (1, 1, 1, 1)
                    background_normal: ''
                    background_color: (0, 0, 0, 0)
                    on_release: root.confirm_results()
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
""")

class PairCard(BoxLayout):
    match_label = StringProperty("")
    player1 = StringProperty("")
    player2 = StringProperty("")
    is_bye = BooleanProperty(False)
    winner = NumericProperty(0)

    def select_winner(self, num):
        if self.is_bye:
            return
        self.winner = num

class TournamentDashboardScreen(MDScreen):
    current_round = NumericProperty(1)
    total_rounds = NumericProperty(5)

    def confirm_results(self):
        app = MDApp.get_running_app()
        container = self.ids.pairs_container
        
        for card in container.children:
            if not card.is_bye and card.winner == 0:
                toast(f"Chybí výsledek: {card.player1} vs {card.player2}")
                return

        for card in reversed(container.children):
            if not card.is_bye:
                winner_name = card.player1 if card.winner == 1 else card.player2
                app.app_manager.add_result(
                    card.player1, 
                    card.player2, 
                    winner_name, 
                    self.current_round
                )

        app.app_manager.record_round_state(self.current_round)
        leaderboard = app.sm.get_screen('leaderboard_screen')
        if hasattr(leaderboard.ids, 'leaderboard_scroll'):
            leaderboard.ids.leaderboard_scroll.scroll_y = 1.0
            
        self.manager.transition.direction = 'left'
        self.manager.current = 'leaderboard_screen'

if 'PairCard' not in Factory.classes:
    Factory.register('PairCard', cls=PairCard)