import random
import time
import threading # Přidáno pro běh serveru
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.utils import platform, get_color_from_hex
from kivymd.utils.set_bars_colors import set_bars_colors
from kivymd.toast import toast
from kivymd.color_definitions import colors

# Importy tvých modulů
from home import HomeScreen
from player_manager import PlayerListScreen
from selection import SelectionScreen, TournamentSelectCard
from tournament_setup import TournamentSetupScreen
from tournament_dashboard import TournamentDashboardScreen, PairCard
from leaderboard import LeaderboardScreen, LeaderboardCard
from final_leaderboard import FinalLeaderboardScreen, FinalLeaderboardCard
from swiss_manager import SwissManager
from playoff import PlayoffScreen
from after_playoff_results import AfterPlayoffScreen
from about_tournament import AboutScreen

# --- NOVÝ IMPORT SERVERU ---
from tournament_server import TournamentServer

# Definice tvé primární barvy
HEX_PRIMARY = "#3F51B5"
#HEX_PRIMARY = "#157DDC"


class TournamentApp(MDApp):
    filename = "players.ini"
    selected_names = []
    app_manager = None
    
    # --- PROMĚNNÁ PRO SERVER ---
    web_server = None
    
    playoff_enabled = BooleanProperty(False)
    last_back_tap = 0
    debug_logging = True  
    log_filename = "turnaj_log.txt"

    def build(self):
        # 1. Globální přepsání barvy Indigo
        clean_hex = HEX_PRIMARY.lstrip('#')
        colors["Indigo"]["500"] = clean_hex
        colors["Indigo"]["200"] = clean_hex
        colors["Indigo"]["700"] = clean_hex

        # 2. Nastavení barev pro systémovou lištu (Android)
        if platform == "android":
            set_bars_colors(get_color_from_hex(HEX_PRIMARY), get_color_from_hex(HEX_PRIMARY), "Dark")
            Window.softinput_mode = "resize"

        # 3. --- START SERVERU ---
        # Spouštíme hned při startu aplikace v samostatném vlákně
        try:
            self.web_server = TournamentServer(http_port=8000, ws_port=8765)
            server_thread = threading.Thread(target=self.web_server.run, daemon=True)
            server_thread.start()
        except Exception as e:
            print(f"Chyba při startu serveru: {e}")

        # 4. Konfigurace tématu
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        
        # Registrace komponent
        Factory.register('TournamentSelectCard', cls=TournamentSelectCard)
        Factory.register('PairCard', cls=PairCard)
        Factory.register('LeaderboardCard', cls=LeaderboardCard)
        Factory.register('FinalLeaderboardCard', cls=FinalLeaderboardCard)
        
        Window.bind(on_keyboard=self.on_key_down)
        
        self.sm = ScreenManager(transition=SlideTransition())
        
        # Registrace všech screenů
        self.sm.add_widget(HomeScreen(name='home_screen'))
        self.sm.add_widget(PlayerListScreen(name='list_screen'))
        self.sm.add_widget(AboutScreen(name='about_screen'))
        self.sm.add_widget(SelectionScreen(name='selection_screen'))
        self.sm.add_widget(TournamentSetupScreen(name='setup_screen'))
        self.sm.add_widget(TournamentDashboardScreen(name='dashboard_screen'))
        self.sm.add_widget(LeaderboardScreen(name='leaderboard_screen'))
        self.sm.add_widget(FinalLeaderboardScreen(name='final_screen'))
        self.sm.add_widget(PlayoffScreen(name='playoff_screen'))
        self.sm.add_widget(AfterPlayoffScreen(name='after_playoff_screen'))
        
        return self.sm

    # Zajištění vypnutí serveru při zavření aplikace
    def on_stop(self):
        # Pokud bys chtěl server explicitně ukončit, ale daemon=True se o to postará
        pass

    def on_key_down(self, window, key, *args):
        if key == 27:  # Klávesa ESC / Back
            current = self.sm.current
            current_time = time.time()
            double_tap_timeout = 2.0
            
            if current in ['final_screen', 'playoff_screen', 'after_playoff_screen']:
                self.go_back_to_home()
                return True

            if current in ['dashboard_screen', 'leaderboard_screen']:
                if self.app_manager and self.app_manager.round_history:
                    if current_time - self.last_back_tap < double_tap_timeout:
                        self.go_back_to_home()
                        self.app_manager = None
                        return True
                    else:
                        self.last_back_tap = current_time
                        toast("Stiskni ještě jednou pro ukončení turnaje")
                        return True
                
                elif current == 'dashboard_screen':
                    self.sm.transition.direction = 'right'
                    self.sm.current = 'setup_screen'
                    return True
                
                elif current == 'leaderboard_screen':
                    self.sm.transition.direction = 'right'
                    self.sm.current = 'dashboard_screen'
                    return True

            if current == 'setup_screen':
                self.sm.transition.direction = 'right'
                self.sm.current = 'selection_screen'
                return True
            
            elif current != 'home_screen':
                self.go_back_to_home()
                return True
                
        return False

    def on_players_click(self):
        self.sm.transition.direction = 'left'
        self.sm.transition.duration = 0.15
        self.sm.current = 'list_screen'

    def go_to_about(self):
        self.sm.transition.direction = 'left'
        self.sm.transition.duration = 0.15
        self.sm.current = 'about_screen'

    def go_back_to_home(self):
        self.sm.transition.direction = 'right'
        self.sm.transition.duration = 0.15
        self.sm.current = 'home_screen'

    def go_to_selection(self):
        self.selected_names = [] 
        selection_screen = self.sm.get_screen('selection_screen')
        selection_screen.ids.tournament_list.clear_widgets()
        self.playoff_enabled = False
        self.sm.transition.direction = 'left'
        self.sm.transition.duration = 0.18
        self.sm.current = 'selection_screen'

    def go_to_setup(self):
        self.get_selected_players()
        if len(self.selected_names) < 8:
            toast("Minimálně 8 hráčů")
            return
        self.sm.transition.direction = 'left'
        self.sm.transition.duration = 0.18
        self.sm.current = 'setup_screen'

    def get_selected_players(self):
        selection_screen = self.sm.get_screen('selection_screen')
        container = selection_screen.ids.tournament_list
        self.selected_names = [c.player_name for c in container.children if c.is_selected]
        self.selected_names.reverse()

    def create_tournament(self, draw_type, rounds, playoff):
        self.playoff_enabled = playoff
        players_to_load = list(self.selected_names)
        
        if draw_type == "NÁHODNÝ":
            random.shuffle(players_to_load)
        else:
            reordered = []
            temp = list(players_to_load)
            bye_player = None
            if len(temp) % 2 != 0:
                bye_player = temp.pop(-1)
            while len(temp) > 1:
                reordered.append(temp.pop(0))
                reordered.append(temp.pop(-1))
            if bye_player:
                reordered.append(bye_player)
            players_to_load = reordered
        
        self.app_manager = SwissManager(players_to_load)
        
        if self.debug_logging:
            with open(self.log_filename, "w", encoding="utf-8") as f:
                f.write("=== START NOVÉHO TURNAJE ===\n")

        dashboard = self.sm.get_screen('dashboard_screen')
        dashboard.current_round = 1
        dashboard.total_rounds = int(rounds)
        
        self.refresh_dashboard_ui(1)
        self.sm.transition.direction = 'left'
        self.sm.transition.duration = 0.18
        self.sm.current = 'dashboard_screen'

    def start_playoff(self):
        self.sm.transition.direction = 'left'
        self.sm.transition.duration = 0.18
        self.sm.current = 'playoff_screen'

    def refresh_dashboard_ui(self, round_num):
        dashboard = self.sm.get_screen('dashboard_screen')
        container = dashboard.ids.pairs_container
        container.clear_widgets()
        
        if hasattr(dashboard.ids, 'dashboard_scroll'):
            dashboard.ids.dashboard_scroll.scroll_y = 1.0
        
        pairings = self.app_manager.generate_pairings(round_num)
        
        match_count = 1
        for p1, p2 in pairings:
            card = PairCard(
                player1=p1, 
                player2=p2,
                match_label=f"{match_count}. ZÁPAS"
            )
            container.add_widget(card)
            match_count += 1
            
        for m in self.app_manager.matches:
            if m['round'] == round_num and m['p2'] is None:
                card = PairCard(
                    player1=m['p1'], 
                    is_bye=True, 
                    winner=1 
                )
                container.add_widget(card)

if __name__ == "__main__":
    TournamentApp().run()
