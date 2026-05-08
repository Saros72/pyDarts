import json
import math
from functools import cmp_to_key

class SwissManager:
    def __init__(self, players):
        self.players = players
        self.matches = []  
        self.bye_history = set()
        self.round_history = []
        self.playoff_matches = []  

    def swiss_rounds_logic(self, n):
        """Určuje doporučený počet kol na základě počtu hráčů."""
        if n <= 1: return 0
        base = math.ceil(math.log2(n))
        rounds = base + 1
        if n <= 10: return min(rounds, 4)
        if n <= 16: return min(rounds, 5)
        if n <= 32: return min(rounds, 6)
        if n <= 64: return min(rounds, 7)
        return min(rounds, 8)

    def add_result(self, p1, p2, winner, round_num):
        """Přidá výsledek zápasu základní části."""
        match = {'p1': p1, 'p2': p2, 'winner': winner, 'round': round_num}
        self.matches.append(match)
        if p2 is None:
            self.bye_history.add(p1)

    def add_playoff_result(self, p1, p2, winner, stage_name):
        """Zaznamená výsledek zápasu v Playoff."""
        self.playoff_matches.append({
            'stage': stage_name,
            'p1': p1,
            'p2': p2,
            'winner': winner
        })

    def get_player_points(self, player, up_to_round):
        return sum(1 for m in self.matches if m['winner'] == player and m['round'] <= up_to_round)

    def get_opponents(self, player, up_to_round):
        opps = []
        for m in self.matches:
            if m['round'] > up_to_round: continue
            if m['p1'] == player and m['p2'] is not None:
                opps.append(m['p2'])
            elif m['p2'] == player:
                opps.append(m['p1'])
        return opps

    def get_buchholz(self, player, up_to_round):
        opponents = self.get_opponents(player, up_to_round)
        return sum(self.get_player_points(opp, up_to_round) for opp in opponents)

    def get_buchholz_cut1(self, player, up_to_round):
        opponents = self.get_opponents(player, up_to_round)
        if not opponents: return 0
        opp_points = [self.get_player_points(opp, up_to_round) for opp in opponents]
        if len(opp_points) > 1:
            opp_points.remove(min(opp_points))
        return sum(opp_points)

    def get_sonneborn_berger(self, player, up_to_round):
        sb_score = 0
        for m in self.matches:
            if m['round'] > up_to_round: continue
            if m['winner'] == player and m['p2'] is not None:
                loser = m['p2'] if m['p1'] == player else m['p1']
                sb_score += self.get_player_points(loser, up_to_round)
        return sb_score

    def get_ranking_data(self, up_to_round=99):
        data = []
        for p in self.players:
            data.append({
                'name': p,
                'points': self.get_player_points(p, up_to_round),
                'bh1': self.get_buchholz_cut1(p, up_to_round),
                'buchholz': self.get_buchholz(p, up_to_round),
                'sb': self.get_sonneborn_berger(p, up_to_round)
            })

        def compare(a, b):
            if a['points'] != b['points']: return b['points'] - a['points']
            if a['bh1'] != b['bh1']: return b['bh1'] - a['bh1']
            if a['buchholz'] != b['buchholz']: return b['buchholz'] - a['buchholz']
            if a['sb'] != b['sb']: return b['sb'] - a['sb']
            for m in self.matches:
                if m['round'] <= up_to_round and m['p2'] is not None:
                    if (m['p1'] == a['name'] and m['p2'] == b['name']) or \
                       (m['p1'] == b['name'] and m['p2'] == a['name']):
                        if m['winner'] == a['name']: return -1
                        if m['winner'] == b['name']: return 1
            return 0

        data.sort(key=cmp_to_key(compare))
        return data

    def record_round_state(self, round_num):
        self.round_history = [r for r in self.round_history if r['round'] != round_num]
        ranked = self.get_ranking_data(round_num)
        round_ranking = []
        for row in ranked:
            opps = self.get_opponents(row['name'], round_num)
            opp_stat = ", ".join([f"{o}({self.get_player_points(o, round_num)})" for o in opps])
            round_ranking.append({
                'name': row['name'], 'points': row['points'],
                'bh1': row['bh1'], 'buchholz': row['buchholz'], 
                'sb': row['sb'], 'opp_stat': opp_stat
            })
        self.round_history.append({'round': round_num, 'ranking': round_ranking, 'matches': [m for m in self.matches if m['round'] == round_num]})
        self.round_history.sort(key=lambda x: x['round'])

    def get_ranking(self):
        return self.get_ranking_data(99)

    def already_played(self, p1, p2):
        for m in self.matches:
            if m['p2'] is None: continue
            if (m['p1'] == p1 and m['p2'] == p2) or (m['p2'] == p1 and m['p1'] == p2):
                return True
        return False

    def generate_pairings(self, round_num):
        ranking = self.get_ranking()
        unpaired = [item['name'] for item in ranking]
        if len(unpaired) % 2 != 0:
            for i in range(len(unpaired)-1, -1, -1):
                candidate = unpaired[i]
                if candidate not in self.bye_history:
                    self.add_result(candidate, None, candidate, round_num)
                    unpaired.pop(i)
                    break
        def backtrack(candidates):
            if not candidates: return []
            p1 = candidates[0]
            rest = candidates[1:]
            for i in range(len(rest)):
                p2 = rest[i]
                if not self.already_played(p1, p2):
                    res = backtrack(rest[:i] + rest[i+1:])
                    if res is not None: return [(p1, p2)] + res
            return None
        pairings = backtrack(unpaired)
        if pairings is None:
            pairings = []
            temp_list = list(unpaired)
            while len(temp_list) > 1:
                p1 = temp_list.pop(0)
                p2 = temp_list.pop(0)
                pairings.append((p1, p2))
        return pairings

    def save_detailed_log(self, filename="turnaj_log.txt"):
        """Uloží kompletní analýzu turnaje včetně Playoff tabulky."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== ANALÝZA TURNAJE ===\n")
            
            for r in self.round_history:
                f.write(f"\n--- KOLO {r['round']} ---\n")
                f.write("ZÁPASY:\n")
                for m in r['matches']:
                    opp = m['p2'] if m['p2'] else "BYE"
                    f.write(f"  {m['p1']} vs {opp} -> Vítěz: {m['winner']}\n")
                
                f.write(f"\n{'Poř.':<4} {'Jméno':<20} {'B':<3} {'BH1':<4} {'Bhz':<4} {'SB':<4} {'Soupeři'}\n")
                f.write("-" * 100 + "\n")
                for i, row in enumerate(r['ranking']):
                    f.write(f"{i+1:<4} {row['name']:<20} {row['points']:<3} {row['bh1']:<4} {row['buchholz']:<4} {row['sb']:<4} {row['opp_stat']}\n")

            if self.playoff_matches:
                f.write("\n" + "="*60 + "\n")
                f.write(" " * 22 + "P L A Y O F F\n")
                f.write("="*60 + "\n")
                
                results = {"1": "", "2": "", "3": "", "4": ""}
                for m in self.playoff_matches:
                    f.write(f"[{m['stage']}] {m['p1']} vs {m['p2']} -> {m['winner']}\n")
                    
                    s = m['stage'].lower()
                    if "finále" in s and "3." not in s:
                        results["1"] = m['winner']
                        results["2"] = m['p1'] if m['winner'] == m['p2'] else m['p2']
                    elif "3. místo" in s:
                        results["3"] = m['winner']
                        results["4"] = m['p1'] if m['winner'] == m['p2'] else m['p2']

                if results["1"] and results["3"]:
                    f.write("\n" + "*"*60 + "\n")
                    f.write(" " * 18 + "KONEČNÉ POŘADÍ ELITY\n")
                    f.write("*"*60 + "\n")
                    f.write(f"   1. MÍSTO: {results['1'].upper()}\n")
                    f.write(f"   2. MÍSTO: {results['2'].upper()}\n")
                    f.write(f"   3. MÍSTO: {results['3'].upper()}\n")
                    f.write(f"   4. MÍSTO: {results['4'].upper()}\n")
                    f.write("*"*60 + "\n")
