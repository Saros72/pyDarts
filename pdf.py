import re
import datetime
import os
from fpdf import FPDF, XPos, YPos
from kivy.utils import platform

class TournamentPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.date_str = datetime.datetime.now().strftime("%d. %m. %Y")

    def header(self):
        self.set_fill_color(63, 81, 181)
        self.rect(0, 0, 210, 30, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('CustomFont', 'B', 18)
        self.cell(0, 10, 'pyDarts: TURNAJOVÝ REPORT', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('CustomFont', '', 9)
        self.cell(0, 5, f'Datum: {self.date_str} | Strana {self.page_no()}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('CustomFont', '', 7)
        self.set_text_color(170, 170, 170)
        self.cell(0, 10, 'Generováno systémem pyDarts', align='R')

    def truncate_text(self, text, max_w, font_size=11):
        self.set_font('CustomFont', '', font_size)
        if self.get_string_width(text) <= max_w:
            return text
        while self.get_string_width(text + "...") > max_w and len(text) > 0:
            text = text[:-1]
        return text + "..."

def parse_log(filename):
    if not os.path.exists(filename): return None
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {"rounds": [], "playoff_matches": [], "final_ranking": []}
    
    # Parsování kol
    round_blocks = re.split(r'--- KOLO (\d+) ---', content)
    for i in range(1, len(round_blocks), 2):
        r_num = round_blocks[i]
        r_data = round_blocks[i+1]
        matches = re.findall(r'\s*(.*?) vs (.*?) -> Vítěz: (.*)', r_data)
        standings = re.findall(r'(\d+)\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', r_data)
        data["rounds"].append({'num': r_num, 'matches': matches, 'standings': standings})

    # Parsování Playoff
    playoff_section = re.search(r'P L A Y O F F.*?\n(.*?)(?=\*|$|KONEČNÉ POŘADÍ)', content, re.DOTALL)
    if playoff_section:
        matches = re.findall(r'\[(.*?)\] (.*?) vs (.*?) -> (.*)', playoff_section.group(1))
        data["playoff_matches"] = matches

    # Parsování konečného pořadí
    final_rank_match = re.search(r'KONEČNÉ POŘADÍ ELITY\s*\*+\n(.*?)\*+', content, re.DOTALL)
    if final_rank_match:
        ranks = re.findall(r'(\d+)\. MÍSTO\s*:\s*(.*)', final_rank_match.group(1))
        data["final_ranking"] = ranks

    return data

def create_pdf(input_file="turnaj_log.txt", output_name="Turnajovy_Report_Tisk.pdf"):
    data = parse_log(input_file)
    if not data: 
        print(f"Log soubor {input_file} nebyl nalezen.")
        return None

    try:
        pdf = TournamentPDF()
        
        # Ošetření fontů pro Android/Desktop
        font_name = "Roboto-Regular.ttf"
        bold_name = "Roboto-Bold.ttf"
        
        # Pokud soubory nejsou v rootu, zkusíme systémové cesty nebo assety
        if not os.path.exists(font_name):
            font_name = "/system/fonts/Roboto-Regular.ttf"
        if not os.path.exists(bold_name):
            bold_name = "/system/fonts/Roboto-Bold.ttf"

        # Registrace fontů (ošetření chyb, pokud fonty chybí úplně)
        try:
            pdf.add_font('CustomFont', '', font_name)
            pdf.add_font('CustomFont', 'B', bold_name if os.path.exists(bold_name) else font_name)
        except:
            # Nouzový fallback na vestavěný font, pokud Roboto selže (nebude umět česky!)
            pdf.add_font('CustomFont', '', "helvetica") 

        pdf.set_auto_page_break(auto=True, margin=20)

        # --- ŠVÝCARSKÁ KOLA ---
        for rnd in data["rounds"]:
            pdf.add_page()
            pdf.set_text_color(63, 81, 181)
            pdf.set_font('CustomFont', 'B', 22)
            pdf.cell(0, 15, f"KOLO {rnd['num']} - ZÁPASY", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            for p1, p2, win in rnd['matches']:
                pdf.set_font('CustomFont', '', 11)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(55, 9, pdf.truncate_text(p1, 55), border='B')
                pdf.set_text_color(150, 150, 150)
                pdf.cell(10, 9, "vs", border='B', align='C')
                pdf.set_text_color(0, 0, 0)
                pdf.cell(55, 9, pdf.truncate_text(p2, 55), border='B')
                pdf.set_font('CustomFont', 'B', 10)
                pdf.set_text_color(46, 125, 50)
                pdf.cell(0, 9, f"  Vítěz: {pdf.truncate_text(win, 50)}", border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.add_page()
            pdf.set_text_color(63, 81, 181)
            pdf.set_font('CustomFont', 'B', 22)
            pdf.cell(0, 15, f"POŘADÍ PO {rnd['num']}. KOLE", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font('CustomFont', 'B', 10)
            headers = [("#", 10), ("Hráč", 80), ("B", 15), ("BH1", 20), ("BH", 20), ("SB", 20)]
            for txt, w in headers:
                pdf.cell(w, 10, txt, border=1, align='C', fill=True)
            pdf.ln()
            pdf.set_font('CustomFont', '', 11)
            for pos, name, b, bh1, bh, sb in rnd['standings']:
                fill = (int(pos) <= 3)
                if fill: pdf.set_fill_color(232, 234, 246)
                pdf.cell(10, 9, f"{pos}.", border=1, align='C', fill=fill)
                pdf.cell(80, 9, f" {pdf.truncate_text(name, 78)}", border=1, fill=fill)
                pdf.cell(15, 9, b, border=1, align='C', fill=fill)
                pdf.cell(20, 9, bh1, border=1, align='C', fill=fill)
                pdf.cell(20, 9, bh, border=1, align='C', fill=fill)
                pdf.cell(20, 9, sb, border=1, align='C', fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # --- PLAYOFF ---
        if data["playoff_matches"]:
            pdf.add_page()
            pdf.set_text_color(255, 152, 0)
            pdf.set_font('CustomFont', 'B', 24)
            pdf.cell(0, 15, "PLAYOFF", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            for stage, p1, p2, win in data["playoff_matches"]:
                pdf.set_fill_color(252, 243, 207)
                pdf.set_font('CustomFont', 'B', 10)
                pdf.cell(0, 7, f" {stage}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font('CustomFont', '', 11)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(60, 9, pdf.truncate_text(p1, 60), border='B')
                pdf.set_text_color(150, 150, 150)
                pdf.cell(10, 9, "vs", border='B', align='C')
                pdf.set_text_color(0, 0, 0)
                pdf.cell(60, 9, pdf.truncate_text(p2, 60), border='B')
                pdf.set_font('CustomFont', 'B', 10)
                pdf.set_text_color(46, 125, 50)
                pdf.cell(0, 9, f"  Vítěz: {pdf.truncate_text(win, 50)}", border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(4)

            if data["final_ranking"]:
                pdf.ln(10)
                pdf.set_fill_color(63, 81, 181)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('CustomFont', 'B', 16)
                pdf.cell(0, 12, "KONEČNÉ POŘADÍ TURNAJE", align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                pdf.set_text_color(0, 0, 0)
                colors = {"1": (255, 215, 0), "2": (192, 192, 192), "3": (205, 127, 50), "4": (235, 235, 235)}
                for pos, name in data["final_ranking"]:
                    pdf.set_fill_color(*colors.get(pos, (255, 255, 255)))
                    pdf.set_font('CustomFont', 'B', 12)
                    pdf.cell(40, 10, f"{pos}. MÍSTO", border=1, fill=True, align='C')
                    pdf.set_font('CustomFont', 'B', 14)
                    pdf.cell(0, 10, f"  {name.strip().upper()}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # --- LEGENDA ---
        pdf.add_page()
        pdf.set_text_color(63, 81, 181)
        pdf.set_font('CustomFont', 'B', 18)
        pdf.cell(0, 15, "VYSVĚTLIVKY HODNOCENÍ", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.set_text_color(0, 0, 0)
        popisy = [
            ("Body (B)", "Základní hodnocení: 1 za výhru, 0 za prohru."),
            ("Buchholz Cut 1 (BH1)", "Součet bodů všech soupeřů kromě toho nejslabšího."),
            ("Buchholz (BH)", "Součet bodů všech tvých soupeřů. Indikuje náročnost turnaje."),
            ("Sonneborn-Berger (SB)", "Body za poražené soupeře. Zvýhodňuje výhry nad silnějšími hráči."),
            ("Vzájemný zápas (VZ)", "Rozhoduje výsledek přímého souboje při rovnosti ostatních bodů.")
        ]
        for titl, text in popisy:
            pdf.set_font('CustomFont', 'B', 11)
            pdf.cell(0, 7, titl, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('CustomFont', '', 10)
            pdf.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        pdf.output(output_name)
        return os.path.abspath(output_name)
    except Exception as e:
        print(f"Chyba při generování PDF: {e}")
        return None

if __name__ == "__main__":
    create_pdf()
