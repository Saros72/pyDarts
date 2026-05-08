# leaderboard.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.factory import Factory

# --- KONFIGURACE BAREV (Sjednoceno) ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
WHITE = [1, 1, 1, 1]

KV_LEADERBOARD = f"""
<LeaderboardCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(10), 0, dp(15), 0]
    spacing: dp(10)
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
        color: {WHITE}
        canvas.before:
            Color:
                rgba: app.theme_cls.primary_color
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

    Label:
        text: root.points
        size_hint_x: None
        width: dp(50)
        font_size: '18sp'
        bold: True
        color: {WIN_GREEN}
        halign: 'right'
        valign: 'middle'
        text_size: self.size

<LeaderboardScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        # --- TOPBAR S CENTROVANÝM TITULKEM ---
        MDTopAppBar:
            id: toolbar
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(15), dp(10)]
            spacing: dp(10)

            ScrollView:
                id: leaderboard_scroll
                BoxLayout:
                    id: leaderboard_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(6)

            # --- SPODNÍ TLAČÍTKO (Sjednocené rozměry) ---
            AnchorLayout:
                anchor_x: 'center'
                size_hint_y: None
                height: dp(80)
                
                Button:
                    id: next_round_btn
                    text: "DALŠÍ KOLO"
                    size_hint: (None, None)
                    size: (dp(280), dp(55))
                    font_size: '18sp'
                    bold: True
                    color: (1, 1, 1, 1)
                    background_normal: ''
                    background_color: (0, 0, 0, 0)
                    on_release: root.go_to_next_round()
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
"""

class LeaderboardCard(BoxLayout):
    rank = StringProperty("1")
    player_name = StringProperty("")
    points = StringProperty("0")

class LeaderboardScreen(MDScreen):
    def __init__(self, **kwargs):
        Builder.load_string(KV_LEADERBOARD)
        super().__init__(**kwargs)

    def on_pre_enter(self):
        self.ids.leaderboard_container.clear_widgets()
        
        if hasattr(self.ids, 'leaderboard_scroll'):
            self.ids.leaderboard_scroll.scroll_y = 1.0

    def on_enter(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        dash = app.sm.get_screen('dashboard_screen')
        self.ids.toolbar.title = f"POŘADÍ {dash.current_round}/{dash.total_rounds}"
        
        if dash.current_round >= dash.total_rounds:
            self.ids.next_round_btn.text = "VÝSLEDKY"
        else:
            self.ids.next_round_btn.text = "DALŠÍ KOLO"
        
        container = self.ids.leaderboard_container
        container.clear_widgets() 
        
        ranking = app.app_manager.get_ranking()
        for i, player in enumerate(ranking):
            card = LeaderboardCard(
                rank=str(i + 1),
                player_name=player['name'],
                points=str(int(player['points']))
            )
            container.add_widget(card)

    def go_to_next_round(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        dashboard = app.sm.get_screen('dashboard_screen')
        
        if dashboard.current_round >= dashboard.total_rounds:
            if app.debug_logging:
                app.app_manager.record_round_state(dashboard.current_round)
                app.app_manager.save_detailed_log(app.log_filename)
                
            self.manager.transition.direction = 'left'
            self.manager.current = 'final_screen'
        else:
            dashboard.current_round += 1
            dashboard.ids.pairs_container.clear_widgets()
            app.refresh_dashboard_ui(dashboard.current_round)
            
            self.manager.transition.direction = 'left'
            self.manager.current = 'dashboard_screen'

Factory.register('LeaderboardCard', cls=LeaderboardCard)
