import threading
import json
import asyncio
import websockets
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from datetime import datetime

# --- KONFIGURACE BAREV ---
COLORS = {
    "dark_bg": "#14141a",     
    "card_bg": "#262b40",     
    "header_bg": "#1f2433",   
    "win_green": "rgb(0, 230, 102)",  
    "text_white": "#ffffff",
    "text_gray": "#8a8d9b",
    "match_blue": "#157DDC"
}

class TournamentServer:
    def __init__(self, http_port=8000, ws_port=8765):
        self.http_port = http_port
        self.ws_port = ws_port
        self.clients = set()
        self.current_date = datetime.now().strftime("%d. %m. %Y")
        
        self.data = {
            "phase": "lobby",
            "title": "Turnaj v šipkách",
            "date": self.current_date,
            "players_count": 0,
            "rounds_count": 0,
            "round": 1,
            "total_rounds": 0,
            "matches": []
        }
        self.loop = None

    def update_data(self, new_data):
        self.data.update(new_data)
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.broadcast(), self.loop)

    async def broadcast(self):
        if not self.clients: return
        message = json.dumps(self.data)
        await asyncio.gather(*[client.send(message) for client in self.clients])

    async def ws_handler(self, ws):
        self.clients.add(ws)
        await ws.send(json.dumps(self.data))
        try:
            await ws.wait_closed()
        finally:
            self.clients.remove(ws)

    def start_http(self):
        server_address = ('0.0.0.0', self.http_port)
        httpd = HTTPServer(server_address, self.create_handler())
        httpd.serve_forever()

    def create_handler(self):
        self_ptr = self
        class TournamentHTTPHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(self_ptr.generate_html().encode("utf-8"))
            def log_message(self, format, *args): return 
        return TournamentHTTPHandler

    def generate_html(self):
        return f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>pyDarts Online</title>
    <style>
        :root {{
            --app-blue: {COLORS['match_blue']};
            --win-green: {COLORS['win_green']};
        }}
        
        body {{ 
            background-color: {COLORS['dark_bg']}; 
            color: {COLORS['text_white']}; 
            font-family: sans-serif; 
            margin: 0; padding: 10px;
            display: flex; justify-content: center;
            color-scheme: dark;
            text-rendering: optimizeLegibility;
            scroll-behavior: smooth;
        }}
        
        #app {{ width: 98%; }}

        .header {{ 
            text-align: center; padding: 15px; background: {COLORS['card_bg']}; 
            border-radius: 10px; margin-bottom: 15px; 
            border-bottom: 3px solid var(--app-blue);
        }}
        
        .title {{ 
            color: var(--app-blue) !important; 
            font-size: 20px; font-weight: bold; text-transform: uppercase;
            filter: drop-shadow(0 0 0 var(--app-blue)); 
        }}
        
        /* ZELENÁ PRO STATISTIKY V LOBBY */
        .stat-val {{ 
            color: var(--win-green) !important; 
            font-size: 24px; font-weight: bold; display: block;
            filter: drop-shadow(0 0 0 var(--win-green));
        }}

        .section-title {{ 
            color: var(--app-blue) !important; 
            font-size: 15px; font-weight: bold; margin-bottom: 12px; text-align: center; 
            border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;
            filter: drop-shadow(0 0 0 var(--app-blue));
        }}

        .match-card {{
            background: {COLORS['card_bg']}; border-radius: 8px; overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
            display: flex; flex-direction: column;
        }}

        .match-body {{ 
            padding: 10px 12px; height: 64px; 
            display: flex; flex-direction: column; justify-content: center; 
        }}
        
        /* ZELENÁ PRO BYE */
        .bye-name {{
            font-size: 17px; color: var(--win-green) !important; 
            text-align: center; width: 100%; display: block; font-weight: bold;
            filter: drop-shadow(0 0 0 var(--win-green));
        }}
        
        .dot {{
            width: 14px; height: 14px; 
            border: 2px solid #5d617a; border-radius: 50%; 
            flex-shrink: 0; display: flex; align-items: center; justify-content: center;
            background: transparent;
            box-sizing: border-box;
        }}
        
        /* ZELENÁ PRO VÍTĚZE */
        .dot.winner {{ 
            border-color: var(--win-green) !important;
            filter: drop-shadow(0 0 0 var(--win-green));
        }}

        .dot.winner::after {{
            content: ""; width: 8px; height: 8px; 
            background-color: var(--win-green) !important;
            border-radius: 50%; display: block;
        }}

        .setup-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 15px; }}
        .stat-card {{ background: {COLORS['card_bg']}; padding: 10px; border-radius: 8px; text-align: center; }}
        .stat-lbl {{ color: {COLORS['text_gray']}; font-size: 10px; text-transform: uppercase; }}
        #live_view {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; align-items: start; }}
        
        .criteria-list {{ background: {COLORS['card_bg']}; padding: 15px; border-radius: 8px; font-size: 13px; }}
        .criteria-item {{ margin-bottom: 10px; text-align: left; }}
        .label {{ font-weight: bold; display: block; margin-bottom: 2px; }}
        .desc {{ color: {COLORS['text_gray']}; font-size: 12px; }}

        .match-header {{ background: {COLORS['header_bg']}; padding: 6px; text-align: center; font-size: 10px; font-weight: bold; color: var(--app-blue); }}
        .player-row {{ display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }}
        .player-name {{ font-size: 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; margin-right: 8px; }}
        .divider {{ height: 1px; background: rgba(255,255,255,0.08); margin: 3px 0; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div class="title" id="main_title">Turnaj v šipkách</div>
            <div style="font-size: 11px; color: {COLORS['text_gray']}; margin-top: 4px;" id="date_text">{self.current_date}</div>
        </div>

        <div id="lobby_view">
            <div class="setup-grid">
                <div class="stat-card"><span class="stat-val" id="p_count">--</span><span class="stat-lbl">Hráčů</span></div>
                <div class="stat-card"><span class="stat-val" id="r_count">--</span><span class="stat-lbl">Kol</span></div>
            </div>
            <div class="criteria-list">
                <div class="section-title">Kritéria pořadí</div>
                <div class="criteria-item"><span class="label">1. Body</span><span class="desc">Počet získaných vítězství.</span></div>
                <div class="criteria-item"><span class="label">2. Buchholz Cut 1</span><span class="desc">Součet bodů soupeřů bez nejslabšího.</span></div>
                <div class="criteria-item"><span class="label">3. Buchholz</span><span class="desc">Celkový součet bodů všech soupeřů.</span></div>
                <div class="criteria-item"><span class="label">4. Sonneborn-Berger</span><span class="desc">Součet bodů poražených soupeřů.</span></div>
                <div class="criteria-item"><span class="label">5. Vzájemný zápas</span><span class="desc">Výsledek přímého souboje.</span></div>
            </div>
        </div>

        <div id="live_view" class="hidden"></div>
    </div>

    <script>
        let ws;
        let lastRound = -1;

        function connect() {{
            ws = new WebSocket("ws://" + location.hostname + ":{self.ws_port}");
            ws.onmessage = (e) => {{
                const data = JSON.parse(e.data);
                const lobby = document.getElementById('lobby_view');
                const live = document.getElementById('live_view');
                const title = document.getElementById('main_title');
                const dateText = document.getElementById('date_text');

                if (data.phase === "lobby") {{
                    lobby.classList.remove('hidden');
                    live.classList.add('hidden');
                    live.innerHTML = ""; 
                    title.innerText = data.title || "Turnaj v šipkách";
                    dateText.style.display = "block";
                    document.getElementById('p_count').innerText = data.players_count;
                    document.getElementById('r_count').innerText = data.rounds_count;
                    lastRound = -1;
                }} else {{
                    lobby.classList.add('hidden');
                    live.classList.remove('hidden');
                    dateText.style.display = "none";
                    
                    if (data.round !== lastRound) {{
                        window.scrollTo(0, 0);
                        lastRound = data.round;
                    }}

                    live.innerHTML = "";
                    
                    let roundDisplay = "KOLO " + data.round;
                    if (data.total_rounds && data.total_rounds > 0) {{
                        roundDisplay += "/" + data.total_rounds;
                    }}
                    title.innerText = roundDisplay;
                    
                    data.matches.forEach((m) => {{
                        let card = document.createElement('div');
                        card.className = 'match-card';
                        if (m.is_bye) {{
                            card.innerHTML = `<div class="match-header">BYE</div>
                                             <div class="match-body"><span class="bye-name">${{m.p1}}</span></div>`;
                        }} else {{
                            card.innerHTML = `<div class="match-header">${{m.label || 'ZÁPAS'}}</div>
                                             <div class="match-body">
                                                <div class="player-row">
                                                    <span class="player-name">${{m.p1}}</span>
                                                    <div class="dot ${{m.winner === 1 ? 'winner' : ''}}"></div>
                                                </div>
                                                <div class="divider"></div>
                                                <div class="player-row">
                                                    <span class="player-name">${{m.p2}}</span>
                                                    <div class="dot ${{m.winner === 2 ? 'winner' : ''}}"></div>
                                                </div>
                                             </div>`;
                        }}
                        live.appendChild(card);
                    }});
                }}
            }};
            ws.onclose = () => setTimeout(connect, 2000);
        }}
        connect();
    </script>
</body>
</html>
"""

    def run(self):
        threading.Thread(target=self.start_http, daemon=True).start()
        async def main_ws():
            self.loop = asyncio.get_running_loop()
            async with websockets.serve(self.ws_handler, "0.0.0.0", self.ws_port):
                await asyncio.Future() 
        try: asyncio.run(main_ws())
        except: pass

if __name__ == "__main__":
    server = TournamentServer()
    server.run()
