from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import configparser
import os

# --- TVOJE PŮVODNÍ BARVY ---
DARK_BG = [0.1, 0.1, 0.12, 1]
CARD_BG = [0.15, 0.17, 0.25, 1]
CARD_BG_DRAG = [0.25, 0.28, 0.4, 1]
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
            rgba: {CARD_BG_DRAG} if root.is_dragging else {CARD_BG}
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

        # Šipka nahoru - skrytá pokud je first
        Button:
            size_hint: None, None
            size: dp(35), dp(55)
            background_normal: ''
            background_color: (0,0,0,0)
            disabled: root.is_first
            opacity: 0 if root.is_first else 1
            on_release: root.screen.move_player(root, 1)
            canvas:
                Color:
                    rgba: (0.6, 0.6, 0.6, 0) if root.is_first else (0.6, 0.6, 0.6, 1)
                Triangle:
                    points: [self.x + dp(10), self.y + dp(22), self.x + dp(25), self.y + dp(22), self.x + dp(17.5), self.y + dp(35)]

        # Šipka dolů - skrytá pokud je last
        Button:
            size_hint: None, None
            size: dp(35), dp(55)
            background_normal: ''
            background_color: (0,0,0,0)
            disabled: root.is_last
            opacity: 0 if root.is_last else 1
            on_release: root.screen.move_player(root, -1)
            canvas:
                Color:
                    rgba: (0.6, 0.6, 0.6, 0) if root.is_last else (0.6, 0.6, 0.6, 1)
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
    on_size: root.update_layout(self.width)
    
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: {DARK_BG}

        MDTopAppBar:
            title: "SEZNAM HRÁČŮ"
            anchor_title: "center"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.go_back_to_home()]]
            right_action_items: [["", lambda x: None]]

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
                do_scroll_x: False

                GridLayout:
                    id: player_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(10)
                    padding: [0, dp(5), 0, dp(5)]
"""

# Jak dlouho musíš držet, než se aktivuje drag (v sekundách)
LONG_PRESS_TIME = 0.4


class PlayerEntryCard(BoxLayout):
    player_name = StringProperty("")
    is_first = BooleanProperty(False)
    is_last = BooleanProperty(False)
    is_dragging = BooleanProperty(False)

    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        self._long_press_event = None
        self._touch_start_pos = None
        self._drag_active = False

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        # Pokud klik míří na pravý panel s tlačítky (šipky + křížek),
        # nech to projít normálně - tj. nezahajuj long press
        # Pravý panel je v posledních dp(120) zprava
        right_panel_x = self.right - dp(120)
        if touch.x >= right_panel_x:
            return super().on_touch_down(touch)

        # Jinak začneme čekat na long-press
        self._touch_start_pos = (touch.x, touch.y)
        self._drag_active = False
        self._long_press_event = Clock.schedule_once(
            lambda dt: self._start_drag(touch), LONG_PRESS_TIME
        )
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        # Pokud probíhá drag, řeš ho přes screen
        if self._drag_active:
            self.screen.on_drag_move(self, touch)
            return True

        # Když se hodně pohne před long-pressem, zruš ho (jde o scroll)
        if self._long_press_event and self._touch_start_pos:
            dx = abs(touch.x - self._touch_start_pos[0])
            dy = abs(touch.y - self._touch_start_pos[1])
            if dx > dp(10) or dy > dp(10):
                self._long_press_event.cancel()
                self._long_press_event = None

        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._long_press_event:
            self._long_press_event.cancel()
            self._long_press_event = None

        if self._drag_active:
            self.screen.on_drag_end(self, touch)
            self._drag_active = False
            self._touch_start_pos = None
            return True

        self._touch_start_pos = None
        return super().on_touch_up(touch)

    def _start_drag(self, touch):
        self._drag_active = True
        self._long_press_event = None
        self.screen.on_drag_start(self, touch)


class PlayerListScreen(MDScreen):
    filename = "players.ini"

    def __init__(self, **kwargs):
        Builder.load_string(KV_PLAYERS)
        super().__init__(**kwargs)
        self._drag_card = None
        self._drag_placeholder = None
        self._drag_offset_y = 0
        self.load_players_to_ui()

    def update_layout(self, width):
        if width > dp(800):
            self.ids.player_list.cols = 2
        else:
            self.ids.player_list.cols = 1

    def scroll_to_bottom(self, dt):
        self.ids.scroll_view.scroll_y = 0

    def _refresh_edge_flags(self):
        """Nastaví is_first / is_last na kartách aby se skryly krajní šipky."""
        container = self.ids.player_list
        # children jsou v Kivy v opačném pořadí - poslední přidaný je první v children
        # vizuálně nahoře je children[-1], dole children[0]
        cards = [c for c in container.children if isinstance(c, PlayerEntryCard)]
        if not cards:
            return
        # Vizuální pořadí shora dolů: reversed(children)
        visual_order = list(reversed(cards))
        for i, card in enumerate(visual_order):
            card.is_first = (i == 0)
            card.is_last = (i == len(visual_order) - 1)

    def add_player(self, name_text=None):
        ti = self.ids.player_input
        name = name_text if name_text else ti.text.strip().title()
        if name:
            new_card = PlayerEntryCard(player_name=name, screen=self)
            self.ids.player_list.add_widget(new_card)
            if not name_text:
                ti.text = ""
                Clock.schedule_once(self.scroll_to_bottom, 0.1)
            self._refresh_edge_flags()
            self.save_players()

    def remove_player(self, card_instance):
        if card_instance.parent:
            card_instance.parent.remove_widget(card_instance)
            self._refresh_edge_flags()
            self.save_players()

    def move_player(self, card, direction):
        """direction = +1 nahoru (vizuálně), -1 dolů (vizuálně).
        Pozn.: v children-listu je vizuální nahoru = vyšší index."""
        container = self.ids.player_list
        if card in container.children:
            idx = container.children.index(card)
            new_idx = idx + direction  # +1 = vizuálně nahoru = vyšší index v children
            if 0 <= new_idx < len(container.children):
                container.remove_widget(card)
                container.add_widget(card, index=new_idx)
                self._refresh_edge_flags()
                self.save_players()

    # ---- DRAG & DROP ----

    def on_drag_start(self, card, touch):
        """Začátek tažení - kartu vyzvedneme nad seznam."""
        container = self.ids.player_list
        if card not in container.children:
            return

        card.is_dragging = True

        # Spočítej offset mezi prstem a středem karty (ve window coords)
        card_window_pos = card.to_window(card.x, card.y)
        self._drag_offset_y = touch.y - card_window_pos[1]

        # Zapamatuj si původní index (v children-listu)
        self._drag_original_index = container.children.index(card)

        # Vytvoř placeholder (prázdné místo)
        placeholder = Widget(size_hint_y=None, height=card.height)
        self._drag_placeholder = placeholder

        # Vyměň kartu za placeholder na stejném místě
        container.remove_widget(card)
        container.add_widget(placeholder, index=self._drag_original_index)

        # Připoj kartu přímo na screen (aby se mohla volně pohybovat)
        card.size_hint = (None, None)
        card.width = container.width
        self.add_widget(card)

        # Polož ji na aktuální prst
        card.center_y = touch.y - self._drag_offset_y + card.height / 2
        card.x = container.to_window(container.x, 0)[0]
        # Převod zpět na lokál screenu
        local_x, _ = self.to_widget(*container.to_window(container.x, 0))
        card.x = local_x

        self._drag_card = card

    def on_drag_move(self, card, touch):
        """Pohyb prstu během tažení."""
        if self._drag_card is None or self._drag_placeholder is None:
            return

        container = self.ids.player_list

        # Posuň kartu za prstem (lokálně ve screen souřadnicích)
        local_pos = self.to_widget(touch.x, touch.y)
        card.center_y = local_pos[1]

        # Auto-scroll když jsme blízko okrajů scrollview
        sv = self.ids.scroll_view
        sv_local = self.to_widget(*sv.to_window(sv.x, sv.y))
        sv_bottom = sv_local[1]
        sv_top = sv_local[1] + sv.height
        edge = dp(60)

        if local_pos[1] > sv_top - edge and sv.scroll_y < 1:
            sv.scroll_y = min(1, sv.scroll_y + 0.02)
        elif local_pos[1] < sv_bottom + edge and sv.scroll_y > 0:
            sv.scroll_y = max(0, sv.scroll_y - 0.02)

        # Najdi pozici, kam bychom kartu vložili (kterou kartu právě překrýváme)
        cards = [c for c in container.children if isinstance(c, PlayerEntryCard)]
        target_index = None
        for c in cards:
            # převod středu karty do screen souřadnic
            cx, cy = c.to_window(c.center_x, c.center_y)
            _, local_cy = self.to_widget(cx, cy)
            if abs(local_cy - local_pos[1]) < c.height / 2:
                target_index = container.children.index(c)
                break

        # Pokud jsme nad/pod krajní kartou, přesun placeholderu na kraj
        if target_index is None:
            # Najdi, jestli jsme nad nejvyšší nebo pod nejnižší kartou
            if cards:
                top_card = max(cards, key=lambda c: c.center_y)
                bot_card = min(cards, key=lambda c: c.center_y)
                top_y = self.to_widget(*top_card.to_window(0, top_card.center_y))[1]
                bot_y = self.to_widget(*bot_card.to_window(0, bot_card.center_y))[1]
                if local_pos[1] > top_y:
                    target_index = len(container.children) - 1
                elif local_pos[1] < bot_y:
                    target_index = 0

        # Pokud máme target a placeholder není už tam, přesuň ho
        if target_index is not None and self._drag_placeholder in container.children:
            current_idx = container.children.index(self._drag_placeholder)
            if current_idx != target_index:
                container.remove_widget(self._drag_placeholder)
                # Po remove se indexy posunou, ale Kivy add_widget(index=) bere
                # aktuální stav children, takže jen vlož na target
                target_index = max(0, min(target_index, len(container.children)))
                container.add_widget(self._drag_placeholder, index=target_index)

    def on_drag_end(self, card, touch):
        """Pustil prst - vrať kartu do seznamu na pozici placeholderu."""
        if self._drag_card is None or self._drag_placeholder is None:
            return

        container = self.ids.player_list
        # Pozice, kam placeholder ukazuje
        if self._drag_placeholder in container.children:
            final_index = container.children.index(self._drag_placeholder)
            container.remove_widget(self._drag_placeholder)
        else:
            final_index = self._drag_original_index

        # Odpoj kartu ze screen
        self.remove_widget(card)

        # Vrať defaultní size_hint
        card.size_hint_x = 1
        card.size_hint_y = None
        card.height = dp(55)

        # Vlož ji zpět do seznamu
        final_index = max(0, min(final_index, len(container.children)))
        container.add_widget(card, index=final_index)

        card.is_dragging = False
        self._drag_card = None
        self._drag_placeholder = None

        self._refresh_edge_flags()
        self.save_players()

    # ---- IO ----

    def save_players(self):
        players = [child.player_name for child in reversed(self.ids.player_list.children)
                   if isinstance(child, PlayerEntryCard)]
        config = configparser.ConfigParser()
        config['players'] = {'list': ','.join(players)}
        with open(self.filename, 'w', encoding='utf-8') as f:
            config.write(f)

    def load_players_to_ui(self):
        if os.path.exists(self.filename):
            config = configparser.ConfigParser()
            config.read(self.filename, encoding='utf-8')
            if 'players' in config:
                names = config['players'].get('list', '').split(',')
                for name in names:
                    if name.strip():
                        self.ids.player_list.add_widget(
                            PlayerEntryCard(player_name=name.strip(), screen=self)
                        )
        Clock.schedule_once(lambda dt: self._refresh_edge_flags(), 0)
