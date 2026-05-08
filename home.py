from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.metrics import dp
#from cast_dialog import CastHandler

# Barva pozadí (černo-modrá)
DARK_BG = [0.08, 0.08, 0.1, 1]

KV_HOME = f'''
<HomeScreen>:
    md_bg_color: {DARK_BG}
    
    MDBoxLayout:
        orientation: "vertical"

        # --- HORNÍ LIŠTA ---
        MDTopAppBar:
            id: toolbar
#            title: "[i]py[/i][b]Darts[/b]"
            anchor_title: "left"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["share-variant", lambda x: None]] 
            right_action_items: 
                [
                ["help-circle-outline", lambda x: None], 
                ["account-multiple", lambda x: app.on_players_click()], 
                ["cast", lambda x: None]
                ]

        # --- STŘEDOVÁ ČÁST S LOGEM ---


        # --- BLOK S LOGEM ---
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(120)
            spacing: dp(10)

            Label:
                markup: True
                text: "[i][color=#666666]py[/color][/i][b][color=#3F51B5]Darts[/color][/b]"
                font_size: '42sp'
                size_hint_y: None
                height: dp(60)

            Label:
                text: "Turnaj hraný švýcarským systémem"
                font_size: '14sp'
                color: [0.5, 0.5, 0.5, 1]
                size_hint_y: None
                height: dp(30)
#                italic: True

        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            padding: dp(20)  # Mezera, aby logo nebylo až ke krajům
            
            Image:
                source: 'logo.png'
                # size_hint 0.9 znamená, že zabere max 90% dostupné šířky/výšky
                size_hint: 0.9, 0.9 
                allow_stretch: True
                keep_ratio: True

        # --- SPODNÍ ČÁST (POUZE TLAČÍTKO) ---
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(120)
            padding: [0, 0, 0, dp(0)]  # Odsazení odspodu obrazovky

            AnchorLayout:
                anchor_x: 'center'
                Button:
                    text: "ZAHÁJIT TURNAJ"
                    size_hint: None, None
                    width: dp(280)
                    height: dp(55)
                    font_size: '17sp'
                    bold: True
                    color: 1, 1, 1, 1
                    background_normal: ''
                    background_color: 0, 0, 0, 0
                    on_release: app.go_to_selection()
                    canvas.before:
                        Color:
                            rgba: app.theme_cls.primary_color if self.state == 'normal' else app.theme_cls.primary_dark
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]

        # --- PATIČKA ---
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(2)
            padding: [0, 0, 0, dp(30)] 

            Label:
                text: "v0.1.0"
                font_size: '14sp'
                color: [0.3, 0.3, 0.3, 1]
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'center'
                valign: 'bottom'

            Label:
                text: "Powered by Sároš"
                font_size: '14sp'
                color: [0.3, 0.3, 0.3, 1]
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'center'
                valign: 'top'
'''

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Načtení KV stringu
Builder.load_string(KV_HOME)
