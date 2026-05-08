# after_playoff_results.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty
from kivy.factory import Factory
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivy.clock import Clock

# --- KONFIGURACE BAREV ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
WHITE = [1, 1, 1, 1]
GREY = [0.6, 0.6, 0.6, 1]
BLACK = [0.0, 0.0, 0.0, 1]
GOLD = [0.831, 0.686, 0.216, 1]
SILVER = [0.75, 0.75, 0.75, 1] 
BRONZE = [0.75, 0.5, 0.3, 1]

class Tab(BoxLayout, MDTabsBase):
    pass

KV_CONTENT = f'''
<AfterPlayoffCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(10), 0, dp(15), 0]
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

<AfterPlayoffScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        MDTopAppBar:
            title: "VÝSLEDKY TURNAJE"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1

        MDTabs:
            id: result_tabs
            background_color: app.theme_cls.primary_color
            indicator_color: {WIN_GREEN}
            tab_display_mode: "fixed"
            tab_hint_x: True
            size_hint_y: 1
            
            Tab:
                title: "PLAY OFF"
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [dp(15), dp(10), dp(15), dp(10)]
                    spacing: dp(10)
                    ScrollView:
                        bar_width: dp(2)
                        bar_color: 0.5, 0.5, 0.5, 0.5
                        bar_inactive_color: 0.5, 0.5, 0.5, 0.2
                        scroll_type: ['bars', 'content']
                        BoxLayout:
                            id: playoff_results_container
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(6)

            Tab:
                title: "ZÁKLADNÍ ČÁST"
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [dp(15), dp(10), dp(15), dp(10)]
                    spacing: dp(5)
                    
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
                        bar_width: dp(2)
                        bar_color: 0.5, 0.5, 0.5, 0.5
                        bar_inactive_color: 0.5, 0.5, 0.5, 0.2
                        scroll_type: ['bars', 'content']
                        BoxLayout:
                            id: basic_results_container
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(6)

        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            size_hint_y: None
            height: dp(90)
            padding: [0, 0, 0, dp(10)]
            
            Button:
                text: "UKONČIT TURNAJ"
                size_hint: (None, None)
                size: (dp(280), dp(55))
                font_size: '18sp'
                bold: True
                color: {WHITE}
                background_normal: ''
                background_color: [0, 0, 0, 0]
                on_release: app.go_back_to_home()
                canvas.before:
                    Color:
                        rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12),]
'''

Builder.load_string(KV_CONTENT)

class AfterPlayoffCard(BoxLayout):
    rank = StringProperty("")
    player_name = StringProperty("")
    circle_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty(WHITE)

class AfterPlayoffScreen(MDScreen):
    playoff_results = ListProperty([]) 

    def on_enter(self):
        Clock.schedule_once(self.fill_data, 0.2)

    def fill_data(self, dt):
        if 'playoff_results_container' not in self.ids or 'basic_results_container' not in self.ids:
            return
           
        carousel = self.ids.result_tabs.carousel
        carousel.anim_move_duration = 0.1 
            
        try:
            self.fill_playoff_part()
            self.fill_basic_part()
            self.ids.result_tabs.switch_tab("PLAY OFF")
        except Exception as e:
            print(f"DEBUG: Chyba při přepínání tabu: {e}")

    def fill_basic_part(self):
        app = MDApp.get_running_app()
        container = self.ids.basic_results_container
        container.clear_widgets()
        
        ranking = app.app_manager.get_ranking()
        for i, player in enumerate(ranking):
            card = Factory.FinalLeaderboardCard(
                rank=str(i + 1),
                player_name=player['name'],
                points=str(int(player['points'])),
                bh=str(player.get('buchholz', 0)),
                playoff_active=True 
            )
            card.update_colors()
            container.add_widget(card)

    def fill_playoff_part(self):
        app = MDApp.get_running_app()
        container = self.ids.playoff_results_container
        container.clear_widgets()
        
        medal_colors = [GOLD, SILVER, BRONZE, app.theme_cls.primary_color]
        text_colors = [BLACK, BLACK, BLACK, WHITE]
        
        for i, name in enumerate(self.playoff_results):
            m_idx = i if i < 3 else 3
            card = AfterPlayoffCard(
                rank=str(i + 1),
                player_name=name,
                circle_color=medal_colors[m_idx],
                text_color=text_colors[m_idx]
            )
            container.add_widget(card)

if 'AfterPlayoffScreen' not in Factory.classes:
    Factory.register('AfterPlayoffScreen', cls=AfterPlayoffScreen)
