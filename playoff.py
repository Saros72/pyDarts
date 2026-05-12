from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.factory import Factory
from kivymd.app import MDApp

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

<PlayoffMatchCard>:
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
            text: root.match_label
            font_size: '14sp'
            color: "#157DDC"
            bold: True
            halign: 'center'
            letter_spacing: 1.2

    MDBoxLayout:
        orientation: 'vertical'
        padding: [dp(15), dp(5), dp(5), dp(10)]
        spacing: dp(2)

        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: root.player1_name
                color: {WHITE}
                font_size: '17sp'
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                shorten: True
                shorten_from: 'right'
                max_lines: 1
            TournamentCheckbox:
                active: root.winner == 1
                pos_hint: {{'center_y': .5}}
                on_release: root.winner = 1

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
                text: root.player2_name
                color: {WHITE}
                font_size: '17sp'
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                shorten: True
                shorten_from: 'right'
                max_lines: 1
            TournamentCheckbox:
                active: root.winner == 2
                pos_hint: {{'center_y': .5}}
                on_release: root.winner = 2

<PlayoffScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        MDTopAppBar:
            id: toolbar
            title: "PLAY OFF"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(20), dp(15)]
            spacing: dp(20)

            ScrollView:
                BoxLayout:
                    id: playoff_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(15)

            AnchorLayout:
                anchor_x: 'center'
                size_hint_y: None
                height: dp(80)
                Button:
                    text: "POTVRDIT" if root.phase == "semi" else "VÝSLEDKY"
                    size_hint: (None, None)
                    size: (dp(280), dp(55))
                    font_size: '18sp'
                    bold: True
                    color: {WHITE}
                    background_normal: ''
                    background_color: (0,0,0,0)
                    on_release: root.next_step()
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
""")

class PlayoffMatchCard(BoxLayout):
    match_label = StringProperty("")
    player1_name = StringProperty("")
    player2_name = StringProperty("")
    winner = NumericProperty(0)

class PlayoffScreen(MDScreen):
    phase = StringProperty("semi")
    semi_winners = []
    semi_losers = []

    def on_pre_enter(self):
        self.phase = "semi"
        self.setup_semifinals()

    def setup_semifinals(self):
        app = MDApp.get_running_app()
        container = self.ids.playoff_container
        container.clear_widgets()
        
        ranking = app.app_manager.get_ranking()[:4]
        if len(ranking) < 4: return

        self.card1 = PlayoffMatchCard(
            match_label="SEMIFINÁLE A",
            player1_name=ranking[0]['name'],
            player2_name=ranking[3]['name']
        )
        self.card2 = PlayoffMatchCard(
            match_label="SEMIFINÁLE B",
            player1_name=ranking[1]['name'],
            player2_name=ranking[2]['name']
        )
        
        container.add_widget(self.card1)
        container.add_widget(self.card2)

    def next_step(self):
        app = MDApp.get_running_app()
        manager = app.app_manager

        if self.phase == "semi":
            if self.card1.winner == 0 or self.card2.winner == 0:
                return
            
            w1 = self.card1.player1_name if self.card1.winner == 1 else self.card1.player2_name
            w2 = self.card2.player1_name if self.card2.winner == 1 else self.card2.player2_name
            
            l1 = self.card1.player2_name if self.card1.winner == 1 else self.card1.player1_name
            l2 = self.card2.player2_name if self.card2.winner == 1 else self.card2.player1_name
            
            # Záznam semifinále do manažera a logu
            manager.add_playoff_result(self.card1.player1_name, self.card1.player2_name, w1, "Semifinále A")
            manager.add_playoff_result(self.card2.player1_name, self.card2.player2_name, w2, "Semifinále B")
            manager.save_detailed_log(app.log_filename)

            self.semi_winners = [w1, w2]
            self.semi_losers = [l1, l2]
            
            self.phase = "final"
            self.setup_final()
        else:
            if self.final_card.winner == 0 or self.third_card.winner == 0:
                return

            # Určení pořadí z karet finálového kola
            winner = self.final_card.player1_name if self.final_card.winner == 1 else self.final_card.player2_name
            second = self.final_card.player2_name if self.final_card.winner == 1 else self.final_card.player1_name
            
            third = self.third_card.player1_name if self.third_card.winner == 1 else self.third_card.player2_name
            fourth = self.third_card.player2_name if self.third_card.winner == 1 else self.third_card.player1_name

            # Záznam do logu (tyto názvy stage manager hledá pro tvorbu tabulky pořadí)
            manager.add_playoff_result(self.final_card.player1_name, self.final_card.player2_name, winner, "Finále")
            manager.add_playoff_result(self.third_card.player1_name, self.third_card.player2_name, third, "O 3. místo")
            manager.save_detailed_log(app.log_filename)

            # Předání dat obrazovce s výsledky
            results_screen = app.root.get_screen('after_playoff_screen')
            results_screen.playoff_results = [winner, second, third, fourth]
            
            app.root.current = 'after_playoff_screen'

    def setup_final(self):
        container = self.ids.playoff_container
        container.clear_widgets()
        
        self.final_card = PlayoffMatchCard(
            match_label="FINÁLE",
            player1_name=self.semi_winners[0],
            player2_name=self.semi_winners[1]
        )
        
        self.third_card = PlayoffMatchCard(
            match_label="O 3. MÍSTO",
            player1_name=self.semi_losers[0],
            player2_name=self.semi_losers[1]
        )
        
        container.add_widget(self.final_card)
        container.add_widget(self.third_card)

if 'PlayoffMatchCard' not in Factory.classes:
    Factory.register('PlayoffMatchCard', cls=PlayoffMatchCard)
