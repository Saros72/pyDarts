# about_tournament.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.metrics import dp

# --- KONFIGURACE BAREV (stejné jako v Home) ---
DARK_BG = [0.08, 0.08, 0.1, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
#CARD_BG = [0.12, 0.15, 0.20, 1]
TEXT_GRAY = [0.7, 0.7, 0.7, 1]
WHITE = [1, 1, 1, 1]
WIN_GREEN = [0.0, 0.9, 0.4, 1]
MATCH_BLUE = [0.08, 0.49, 0.86, 1]


KV_ABOUT = f'''
<InfoCard@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(15)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: {CARD_BG}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15),]

<AboutScreen>:
    md_bg_color: {DARK_BG}
    
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "O TURNAJI"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.go_back_to_home()]]
            right_action_items: [["", lambda x: None]] # Falešná ikona pro vycentrování

        ScrollView:
            do_scroll_x: False
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(15)
                spacing: dp(20)

                # --- ÚVOD ---
                InfoCard:
                    Label:
                        text: "Švýcarský systém"
                        font_size: '22sp'
                        bold: True

                        color: "#157DDC"
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                    Label:
                        text: "Tento systém je navržen tak, aby spravedlivě určil vítěze bez nutnosti vyřazování hráčů. Každý si zahraje všechna kola až do konce."
                        font_size: '15sp'
                        color: {WHITE}
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                # --- PÁROVÁNÍ ---
                InfoCard:
                    Label:
                        text: "Jak probíhá párování?"
                        font_size: '18sp'
                        bold: True
                        color: "#157DDC"
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                    Label:
                        text: "V prvním kole jsou hráči spárováni náhodně, nebo podle nasazení. Od druhého kola systém páruje hráče s podobným počtem bodů. Cílem je, aby proti sobě stáli výkonnostně vyrovnaní soupeři. Žádný hráč nehraje dvakrát se stejným hráčem."
                        font_size: '15sp'
                        color: {WHITE}
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                # --- VÝHODY ---
                InfoCard:
                    Label:
                        text: "Hlavní výhody"
                        font_size: '18sp'
                        bold: True
                        color: "#157DDC"
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                    Label:
                        text: "• Nikdo nevypadává po první prohře.\\n• Turnaj je spravedlivý i při velkém počtu hráčů.\\n• Systém se sám postará o to, aby si začátečníci zahráli se začátečníky a profíci s profíky."
                        font_size: '15sp'
                        color: {WHITE}
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                # --- HODNOCENÍ ---
                InfoCard:
                    Label:
                        text: "Kritéria pořadí"
                        font_size: '18sp'
                        bold: True
                        color: "#157DDC"
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None

                    Label:
                        markup: True
                        text: 
                            "1. [b]Body:[/b] Počet získaných vítězství.\\n" \
                            "2. [b]Buchholz Cut 1:[/b] Součet bodů soupeřů, přičemž se nejslabší výsledek soupeře škrtá. To eliminuje vliv náhodného losu nejslabšího hráče.\\n" \
                            "3. [b]Buchholz:[/b] Celkový součet bodů všech vašich soupeřů.\\n" \
                            "4. [b]Sonneborn-Berger:[/b] Součet bodů soupeřů, které jste dokázali porazit.\\n" \
                            "5. [b]Vzájemný zápas:[/b] Pokud je vše výše uvedené shodné, rozhoduje výsledek přímého souboje."
                        font_size: '15sp'
                        color: {WHITE}
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        text_size: self.width, None


                Widget:
                    size_hint_y: None
                    height: dp(20)
'''

class AboutScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

Builder.load_string(KV_ABOUT)
