# -*- coding: utf-8 -*-

"""
Projekt: Cat Show App der KECB Katzenausstellung
Copyright (c) 2026 Brigitte Portner
Alle Rechte vorbehalten
"""




import streamlit as st
import pandas as pd
import re
import time
from streamlit_autorefresh import st_autorefresh
import qrcode
import json
import os
from io import BytesIO
# --- IMPORTS FÜR DIE PDF-GENERIERUNG ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

# Zentrale Logo URL
LOGO_URL = "logo_kecb.png"

st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0.1; } }
    @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

@keyframes flashGreen {
    0% { background-color: #1a4a9e; }
    50% { background-color: #28a745; }
    100% { background-color: #1a4a9e; }
}

	.voted-flash {
    		animation: flashGreen 2s ease-in-out;
	}
    /* Greift NUR noch auf die Buttons im Home-Menü zu: */
    .home-buttons div.stButton > button {
        width: 100% !important;
        height: 50px !important;
        background-color: #1a4a9e !important; /* Feste blaue Hintergrundfarbe */
        color: white !important; /* Weiße Schrift auf blauem Grund */
    }

    /* Login Container */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background-color: #f8f9fa;
        border-radius: 20px;
        border: 2px solid #1a4a9e;
        max-width: 400px;
        margin: 5% auto;
    }

    /* Erzeugt einheitliche Höhen für alle Boxen in einer Zeile */
    .grid-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* --- STEWARD CARDS STYLES (ORIGINAL WIEDERHERGESTELLT) --- */
    /* Der Kasten umschließt jetzt das Meta-Grid UND die Buttons */
    .steward-card-wrapper {
        background-color: #f8f9fa !important; /* Karte komplett hellgrau */
        border: 1px solid #dcdcdc !important;
        border-radius: 12px !important;
        padding: 16px 16px 12px 16px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    .steward-card-wrapper.gerichtet {
        border: 1px dashed #cccccc !important;
        opacity: 0.6 !important;
    }
    
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #1a4a9e;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }
    .card-cat-number {
        font-size: 22px !important;
        font-weight: 800;
        color: #1a4a9e;
    }
    .card-meta-main {
        font-size: 15px !important;
        font-weight: 700;
        color: #222;
    }
    .grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 12px;
        margin-bottom: 12px;
    }
    .card-meta-sub {
        font-size: 13px !important;
        color: #555;
    }
    .meta-label {
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        font-size: 11px !important;
        letter-spacing: 0.5px;
    }

    /* --- GLOBALE BUTTONS (DASHBOARD) --- */
    div.stButton > button, .stButton button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        font-size: 12px !important;
        transition: all 0.2s ease;
        margin-bottom: 5px;
        border: 2px solid #1a4a9e !important;
        color: white !important;
    }

    /* --- BUTTONS SPEZIFISCH IM STEWARD PANEL VERKLEINERN --- */
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        height: 35px !important;
        min-height: 35px !important;
        min-width: 100px !important;
        padding: 0px 5px !important;
        font-size: 8px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }

    /* Spalten-spezifische Button-Farben für das Steward-    /* --- KEYFRAMES FÜR DAS FARBLICHE PULSIEREN (OHNE TEXT-BLINKEN) --- */
    @keyframes pulseBlue   { 0% { background-color: #007bff; } 50% { background-color: #0044aa; } 100% { background-color: #007bff; } }
    @keyframes pulseOrange { 0% { background-color: #ff9800; } 50% { background-color: #cc6600; } 100% { background-color: #ff9800; } }
    @keyframes pulseGreen  { 0% { background-color: #28a745; } 50% { background-color: #1a662c; } 100% { background-color: #28a745; } }
    @keyframes pulseYellow { 0% { background-color: #ffc107; } 50% { background-color: #cca300; } 100% { background-color: #ffc107; } }

    /* Spalten-spezifische Button-Farben & einheitliche Größen für das Steward-Pult */
    
    /* SPALTE 1: AUFRUFEN -> BLAU */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #007bff !important;
        border: none !important;
        color: white !important;
        width: 100% !important;
        height: 35px !important;
    }
    /* Wenn Aktiv: Blau pulsieren */
    .st-blink-btn div[data-testid="stHorizontalBlock"] > div:nth-child(1) button,
    div:nth-child(1) .st-blink-btn button {
        animation: pulseBlue 1.5s infinite ease-in-out !important;
        box-shadow: 0 0 12px rgba(0, 123, 255, 0.5) !important;
    }
    
    /* SPALTE 2: WIRD GERICHTET -> ORANGE */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #ff9800 !important;
        border: none !important;
        color: white !important;
        width: 100% !important;
        height: 35px !important;
    }
    /* Wenn Aktiv: Orange pulsieren */
    .st-blink-btn div[data-testid="stHorizontalBlock"] > div:nth-child(2) button,
    div:nth-child(2) .st-blink-btn button {
        animation: pulseOrange 1.5s infinite ease-in-out !important;
        box-shadow: 0 0 12px rgba(255, 152, 0, 0.5) !important;
    }
    
    /* SPALTE 3: BIV -> GRÜN */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        background-color: #28a745 !important;
        border: none !important;
        color: white !important;
        width: 100% !important;
        height: 35px !important;
    }
    /* Wenn Aktiv: Grün pulsieren */
    .st-blink-btn div[data-testid="stHorizontalBlock"] > div:nth-child(3) button,
    div:nth-child(3) .st-blink-btn button {
        animation: pulseGreen 1.5s infinite ease-in-out !important;
        box-shadow: 0 0 12px rgba(40, 167, 69, 0.5) !important;
    }
    
    /* SPALTE 4: NOM -> GELB */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
        background-color: #ffc107 !important;
        border: none !important;
        color: black !important;
        width: 100% !important;
        height: 35px !important;
    }
    /* Wenn Aktiv: Gelb pulsieren */
    .st-blink-btn div[data-testid="stHorizontalBlock"] > div:nth-child(4) button,
    div:nth-child(4) .st-blink-btn button {
        animation: pulseYellow 1.5s infinite ease-in-out !important;
        box-shadow: 0 0 12px rgba(255, 193, 7, 0.5) !important;
    }
    
    /* SPALTE 5: GERICHTET -> GRAU (Erledigt braucht kein Blinken) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {
        background-color: #6c757d !important;
        border: none !important;
        color: white !important;
        width: 100% !important;
        height: 35px !important;
    }

    /* Erweiterte Hover Effekte für ein haptisches Feedback */
    div[data-testid="stHorizontalBlock"] > div > button:hover {
        transform: scale(1.02);           /* Button wird beim Drüberfahren minimal größer */
        cursor: pointer;                  /* Mauszeiger wird zur Hand */
        filter: brightness(110%);         /* Macht die Farbe einen Tick leuchtender statt nur dunkler */
        transition: all 0.2s ease-in-out; /* Lässt die Änderung sanft gleiten, nicht hart springen */
    }

    /* Individuelle Anpassung, falls du bei den spezifischen Farben bleiben willst: */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover { background-color: #0069d9 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover { background-color: #e68a00 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover { background-color: #218838 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover { background-color: #e0a800 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button:hover { background-color: #5a6268 !important; }


    /* Hover Effekte (Ebenfalls flexibel für aktive Blink-Zustände) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover { background-color: #0069d9 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover { background-color: #e68a00 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover { background-color: #218838 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover { background-color: #e0a800 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button:hover { background-color: #5a6268 !important; }

    /* Blinken für aktive Container-Wrapper im Python-Code */
    .button-class button, .st-blink-btn button, .blink-active button {
        animation: blinker 1.3s linear infinite !important;
        box-shadow: 0 0 15px rgba(0,0,0,0.2) !important;
    }


    /* Dashboard & Richter-Layout Styles */
    .judge-header-box { 
        background-color: #1a4a9e; color: white; padding: 8px; border-radius: 10px; text-align: center; 
        font-size: 12px !important; text-transform: uppercase; font-weight: bold; 
        margin-bottom: 10px; border: 2px solid #0d2a5e; height: 60px; 
        display: flex; align-items: center; justify-content: center; 
    }
    
    .class-label-box { 
        background-color: #e9ecef; color: #1a4a9e; padding: 5px; border-radius: 10px; text-align: center; 
        font-size: 11px !important; text-transform: uppercase; font-weight: 800; 
        border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center; 
        height: 90px; width: 100%; line-height: 1.1; 
    }

    .cat-card, .placeholder-box { height: 95px; padding: 5px; border: 2px solid #1a4a9e; text-align: center; background-color: #f0f0f0; border-radius: 14px; margin-bottom: 5px; min-height: 90px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .placeholder-box { height: 95px; border: 1px solid #d1d1d1; background-color: #f2f2f2 !important; color: #999999; }
    .winner-card { height: 99px; border: 1px solid #ff4d4d !important; background-color: #ffcccc !important; color: #b21f2d !important; }
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 14px !important; color: #333; font-weight: bold; margin-top: 2px; line-height: 1.1; }

    /* Richter Initialen Kreise */
    .judge-initials-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid #eee;
    }
    .judge-circle {
        width: 24px;
        height: 24px;
        background-color: #008800;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        cursor: help;
    }

    /* Overlay als zentrierte Box (80% Größe) */
    .winner-overlay {
        position: fixed;
        top: 10%; left: 10%; 
        width: 80vw; height: 80vh;
        background-color: white;
        z-index: 9999999;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center;
        border-radius: 40px;
        box-shadow: 0px 0px 100px rgba(0,0,0,0.5);
        border: 15px solid #1a4a9e;
        padding: 40px;
        animation: fadeIn 0.5s ease-out;
    }
    .overlay-backdrop {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0,0,0,0.7);
        z-index: 9999998;
    }

    /* Titel Anpassungen Overlay */
    .ov-header {
        font-size: 24px !important; font-weight: 500; color: #333;
        text-transform: uppercase;
        border-bottom: 2px solid #ccc; width: 80%;
        padding-bottom: 15px; margin-bottom: 30px;
    }
    .ov-cat-name {
        font-size: 45px !important; font-weight: 900;
        text-transform: uppercase; color: #000;
        margin-bottom: 20px; line-height: 1.1;
        width: 90%; word-wrap: break-word;
    }
    .ov-owner {
        font-size: 30px !important; font-style: italic; color: #444;
    }
    
    /* Klasse für Hauptüberschriften neben dem Logo */
    .header-text {
        text-transform: uppercase !important;
        font-size: 26px !important;
        font-weight: bold;
        color: #1a4a9e;
        margin: 0 !important;
    }
    
    /* Tags */
    .tag-container { margin-top: 4px; display: flex; justify-content: center; flex-wrap: wrap; gap: 3px; }
    .tag { font-weight: bold; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; color: white; }
    .tag-zumrichten { background-color: #007bff; }
    .tag-biv { background-color: #28a745; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }

    /* --- AB HIER IN DEINEM SKRIPT ERSETZEN --- */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] div.stButton > button {
        height: 25px !important;
        min-height: 25px !important;
        min-width: 10px !important;
        padding: 0px 5px !important;
        font-size: 8px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }
                
    /* SPALTE 1: AUFRUFEN -> BLAU */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #007bff !important; border: 2px solid #0056b3 !important; color: white !important; }
    
    /* SPALTE 2: WIRD GERICHTET -> ORANGE */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #ff9800 !important; border: 2px solid #d37e00 !important; color: white !important; }
    
    /* SPALTE 3: BIV -> GRÜN */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { background-color: #28a745 !important; border: 2px solid #1e7e34 !important; color: white !important; }
    
    /* SPALTE 4: NOM -> GELB */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(4) button { background-color: #ffc107 !important; border: 2px solid #d39e00 !important; color: black !important; }
    
    /* SPALTE 5: GERICHTET -> GRAU */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(5) button { background-color: #6c757d !important; border: 2px solid #545b62 !important; color: white !important; }

    /* Hover Effekte */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover { background-color: #0069d9 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover { background-color: #e68a00 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover { background-color: #218838 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover { background-color: #e0a800 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(5) button:hover { background-color: #5a6268 !important; }
    
    .tag-wirdgerichtet { background-color: #ff9800 !important; animation: blinker 1.5s infinite; color: white; }

</style>


</style>

    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
# --- 2. GLOBALER SPEICHER (SUPABASE-VERSION) ---
from supabase import create_client, Client
import streamlit as st

class GlobalStore:
    def __init__(self):
        # Hier nutzen wir die Werte aus deinen Secrets
        url = st.secrets["NEXT_PUBLIC_SUPABASE_URL"]
        key = st.secrets["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]
        
        self.client: Client = create_client(url, key)
        self.data = {"votes": {}} 
        self.active_overlay = None
        self.overlay_start_time = 0
        self.load_backup()

    def save_backup(self):
        """Speichert in der Supabase-Tabelle."""
        try:
            self.client.table("app_data").upsert({"id": 1, "content": self.data}).execute()
        except Exception:
            pass

    def load_backup(self):
        """Lädt aus der Supabase-Tabelle."""
        try:
            res = self.client.table("app_data").select("content").eq("id", 1).execute()
            if res.data:
                self.data = res.data[0]["content"]
        except Exception:
            self.data = {"votes": {}}

    def set_data(self, key, field=None, value=None):
        if field is None:
            self.data[key] = value
        else:
            if key not in self.data:
                self.data[key] = {}
            self.data[key][field] = value
        self.save_backup()

@st.cache_resource
def get_store():
    return GlobalStore()

store = get_store()


# --- 3. SESSION STATE & URL PARAMETER (FIXED: DAUERHAFT EINGELOGGT) ---
q_params = st.query_params

# 1. Prüfen, ob Zugangsdaten direkt in der URL stecken (Erzwingt das Login bei jedem Rerun)
if "auth" in q_params and q_params["auth"] == "true":
    st.session_state.authenticated = True
    st.session_state.user_role = q_params.get("role", "Public")
    
       # Falls eine bestimmte Ansicht in der URL steht, diese erzwingen
    if "view" in q_params:
        v_param = q_params["view"].lower()
        if v_param == "steward": st.session_state.view = "Steward_Panel"
        elif v_param == "richter": st.session_state.view = "Judge_Voting"
        elif v_param == "admin": st.session_state.view = "Home"
        elif v_param == "bis-admin": st.session_state.view = "BIS_Admin_Control"
        elif v_param == "qr": st.session_state.view = "QR_Codes"
        elif v_param == "qr-gen": st.session_state.view = "QR_Codes_Gen"
        elif v_param == "nominated": st.session_state.view = "Nominated_Cats"
		
        # --- NEU: URL-PARAMETER FÜR DIE BEIDEN TEST-SEITEN ---
        elif v_param == "test-live-admin": st.session_state.view = "Test_Live_Admin"
        elif v_param == "test-live-voting": st.session_state.view = "Test_Live_Voting"




# 2. Standard-Fallbacks, falls nichts in der URL steht
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Public"
if "view" not in st.session_state:
    st.session_state.view = "Dashboard"

# Falls man manuell über das Menü navigiert, ohne URL-Parameter zu verlieren
if "view" in q_params and not st.session_state.authenticated:
    v_param = q_params["view"].lower()
    if v_param == "katzenaufruf": st.session_state.view = "Dashboard"
    elif v_param == "bis": st.session_state.view = "BIS_Public"
    elif v_param in ["admin", "steward", "richter", "bis-admin"]:
        st.session_state.view = "Login"
        st.session_state.target_role = v_param
        

# NEU: Richter-Parameter aus der URL sichern, falls übergeben
if "judge" in q_params: 
    st.session_state.url_judge = q_params["judge"]
elif "url_judge" not in st.session_state: 
    st.session_state.url_judge = "--"


def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = "Public"
    st.session_state.view = "Dashboard"
    st.query_params.clear() # Löscht die Login-Parameter aus der URL beim Logout
    st.rerun()


# --- 4. HILFSFUNKTIONEN ---
def display_header_with_logo(text):
    col_text, col_logo = st.columns([5, 1]) 
    with col_text:
        st.markdown(f"<p class='header-text'>{text}</p>", unsafe_allow_html=True)
    with col_logo:
        st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
        st.image(LOGO_URL, width=100)
        st.markdown("</div>", unsafe_allow_html=True)

def render_overlay_html(row):
    kat_nr = str(row.get('KATALOG-NR', '')).replace('.0', '')
    rasse = row.get('RASSE', '')
    farbe = row.get('FARBE', '')
    name_gross = str(row.get('NAME', '')).upper()
    besitzer = f"{row.get('BESITZER VORNAME', '')} {row.get('BESITZER NACHNAME', '')}"
    return f"""
        <div class="overlay-backdrop"></div>
        <div class="winner-overlay">
            <div class="ov-header">{kat_nr}. {rasse} {farbe}</div>
            <div class="ov-cat-name">{name_gross}</div>
            <div class="ov-owner">{besitzer}</div>
            <div style="margin-top: 50px;">
            <div style="font-weight: bold; font-size: 22px; color: #1a4a9e; margin-top: 10px;">KECB BURGDORF 2026</div>
            </div>
        </div>
    """

def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=600)
def load_labels():
    try:
        df = pd.read_excel("2026.xlsx", engine='openpyxl', header=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.fillna("-")
        df['KLASSE_INTERNAL'] = df['AUSSTELLUNGSKLASSE'] if 'AUSSTELLUNGSKLASSE' in df.columns else df.get('KLASSE', '')
        if 'KATALOG-NR' in df.columns:
            df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)

        # --- NEU: ABSOLUT RISIKO-FREIE WEICHE FÜR TAG 1 & TAG 2 ---
        # Wir prüfen, welcher Tag im globalen Sidebar-Radio-Button gewählt ist
        # Falls der Selector auf "Tag 2" steht, nehmen wir SELECTION 2, sonst SELECTION 1
        day_selector = st.session_state.get("judge_day_selector", "Tag 1")
        
        if "2" in str(day_selector):
            df['SELECTION'] = df['SELECTION 2'] if 'SELECTION 2' in df.columns else df.get('SELECTION', '-')
        else:
            df['SELECTION'] = df['SELECTION 1'] if 'SELECTION 1' in df.columns else df.get('SELECTION', '-')
        # -----------------------------------------------------------
		
        return df
    except:
        return None

def get_full_label(row):
    r = row.get('RASSE_KURZ', row.get('RASSE', ''))
    fg_col = [c for c in row.index if "FARBGRUPPE" in c or "FARB-GRUPPE" in c]
    fg_val = row[fg_col[0]] if fg_col else row.get('FARBGRUPPE', '')
    g = roman_to_numeric(fg_val)
    e = row.get('FARBE', '')
    return f"{r} {g} ({e})".strip() if g else f"{r} ({e})".strip()

def set_view(name):
    store.active_overlay = None   
    st.session_state.view = name
    st.rerun()


# --- 5. NAVIGATION & ZUGRIFF ---
access_map = {
    "Public": ["Dashboard", "BIS_Public", "Login"],
    "Richter": ["Judge_Voting",  "Test_Live_Voting", "Dashboard", "BIS_Public"],
    "Steward": ["Steward_Panel", "Dashboard", "BIS_Public"],
    "Admin": ["Home", "Dashboard", "BIS_Public", "Judge_Voting", "Steward_Panel", "BIS_Admin_Control", "Test_Live_Admin", "Test_Live_Voting","QR_Codes", "QR_Codes_Gen", "Nominated_Cats", "Judge_List", "Nomination_Labels", "Admin_Panel"]
}

st.markdown("""
        <style>
        div.stButton > button {
            background-color: #ffffff !important;
            color: #1a4a9e !important;
            border: 2px solid #1a4a9e !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            width: 100% !important;
            display: block !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #1a4a9e !important;
            color: #ffffff !important;
        }
        .login-container {
            border: 2px solid #1a4a9e !important;
            border-radius: 15px;
            padding: 20px;
            background-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)
    
available_views = access_map.get(st.session_state.user_role, ["Dashboard"])
st.sidebar.image(LOGO_URL, width=150)

# HIER WURDE format_func HINZUGEFÜGT: Tauscht bei der Anzeige die Unterstriche gegen Leerzeichen
st.session_state.view = st.sidebar.radio(
    "Menü:", 
    available_views, 
    index=available_views.index(st.session_state.view) if st.session_state.view in available_views else 0,
    format_func=lambda x: x.replace("_", " ")
)
#if st.session_state.view != "BIS_Public":
   # store.active_overlay = None	

if st.session_state.authenticated:
    if st.sidebar.button("Abmelden"): logout()
elif st.session_state.view != "Login":
    if st.sidebar.button("🔒 Interner Login"): set_view("Login")

# --- Copyright Bereich ---
st.sidebar.markdown("---") # Trennlinie für saubere Optik
st.sidebar.markdown(
    """
    <div style="font-size: 0.8em; color: gray; text-align: center;">
        © 2026 Brigitte Portner<br>
        Alle Rechte vorbehalten.
    </div>
    """, 
    unsafe_allow_html=True
)
    
# --- 6. VIEWS ---

# LOGIN VIEW
if st.session_state.view == "Login":
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #ffffff !important;
            color: #1a4a9e !important;
            border: 2px solid #1a4a9e !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            width: 100% !important;
            display: block !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #1a4a9e !important;
            color: #ffffff !important;
        }
        .login-container {
            border: 2px solid #1a4a9e !important;
            border-radius: 15px;
            padding: 20px;
            background-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.image(LOGO_URL, width=150)
    st.markdown("<h2 style='text-align:center; color:#1a4a9e; text-transform: uppercase; font-size: 20px;'>Interner Bereich</h2>", unsafe_allow_html=True)
    
    role_map = {"admin": "Admin", "steward": "Steward", "richter": "Richter", "bis-admin": "Admin"}
    target = st.session_state.get("target_role", "Richter")
    role_list = ["Admin", "Steward", "Richter"]
    def_idx = role_list.index(role_map.get(target, "Richter"))

    role_input = st.selectbox("Rolle wählen:", role_list, index=def_idx)
    password = st.text_input("Passwort:", type="password")
    
    if st.button("Anmelden"):
        if role_input == "Admin" and password == "admin2026":
            st.session_state.user_role, st.session_state.authenticated = "Admin", True
            st.query_params.update(auth="true", role="Admin") 
            set_view("Home")
        elif role_input == "Steward" and password == "steward2026":
            st.session_state.user_role, st.session_state.authenticated = "Steward", True
            st.query_params.update(auth="true", role="Steward") 
            set_view("Steward_Panel")
        elif role_input == "Richter" and password == "judge2026":
            st.session_state.user_role, st.session_state.authenticated = "Richter", True
            st.query_params.update(auth="true", role="Richter") 
            set_view("Judge_Voting")
        else:
            st.error("Passwort ungültig.")
    
    if st.button("Abbrechen"): set_view("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)


# HOME (ADMIN NUR)
elif st.session_state.view == "Home":
    display_header_with_logo("🐾 KECB Burgdorf 2026")
    st.markdown('<div class="home-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"):
            st.query_params.update({"view": "katzenaufruf"})
            set_view("Dashboard")
            st.rerun()
        if st.button("🏆 BEST IN SHOW (PUBLIC)"):
            st.query_params.update({"view": "bis"})
            set_view("BIS_Public")
            st.rerun()
        if st.button("🗳️ RICHTER-VOTING"):
            st.query_params.update({"view": "richter", "auth": "true", "role": "Richter"})
            set_view("Judge_Voting")
            st.rerun()
			        # --- NEU: BUTTON FÜR DAS RICHTER-TEST-VOTING ---
        if st.button("🧪 [TEST] LIVE-VOTING (RICHTER)"):
            st.query_params.update({"view": "test-live-voting", "auth": "true", "role": "Admin"})
            set_view("Test_Live_Voting")
            st.rerun()
    with col2:
        if st.button("📝 STEWARD-PULT"):
            st.query_params.update({"view": "steward", "auth": "true", "role": "Steward"})
            set_view("Steward_Panel")
            st.rerun()
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"):
            st.query_params.update({"view": "bis-admin", "auth": "true", "role": "Admin"})
            set_view("BIS_Admin_Control")
            st.rerun()
		 # --- NEU: BUTTON FÜR DEN LIVE-ADMIN-TEST ---
        if st.button("🎛️ [TEST] LIVE-ADMIN CONTROL"):
            st.query_params.update({"view": "test-live-admin", "auth": "true", "role": "Admin"})
            set_view("Test_Live_Admin")
            st.rerun()
        if st.button("⚙️ ADMIN-KONSOLE (RESET)"):
            st.query_params.update({"view": "admin", "auth": "true", "role": "Admin"})
            set_view("Admin_Panel")
            st.rerun()
            # NEU: Der Button für die QR-Zentrale direkt im Admin-Menü
        if st.button("📱 QR-CODE ZENTRALE"):
            st.query_params.update({"view": "qr", "auth": "true", "role": "Admin"})
            set_view("QR_Codes")
            st.rerun()
	            # NEU: Der Button für die QR-Zentrale direkt im Admin-Menü
        if st.button("📱 QR-CODE GENERATOR"):
            st.query_params.update({"view": "qr-gen", "auth": "true", "role": "Admin"})
            set_view("QR_Codes_Gen")
            st.rerun()
             # NEU: Button für die nominierten Katzen
        if st.button("🐈 NOMINIERTE KATZEN LISTE"):
            st.query_params.update({"view": "nominated", "auth": "true", "role": "Admin"})
            set_view("Nominated_Cats")
            st.rerun()
            # NEU: Button für die Richter Liste
        if st.button("🐈 RICHTER LISTE"):
            st.query_params.update({"view": "judge-list", "auth": "true", "role": "Admin"})
            set_view("Judge_List")
            st.rerun()
        if st.button("🖨️ NOMINATION LABELS DRUCK"):
            st.query_params.update({"view": "nom-labels", "auth": "true", "role": "Admin"})
            set_view("Nomination_Labels")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("⚙️ System-Einstellungen (Admin-Steuerung)")
    
    # 1. Richter-Fixierung
    if "steward_lock" not in st.session_state:
        st.session_state.steward_lock = True
    st.session_state.steward_lock = st.toggle(
        "Richter-Auswahl für Stewards sperren (Lockdown)", 
        value=st.session_state.steward_lock
    )

    # Initialisiere den sicheren Speicher, falls er beim allerersten Start noch leer ist
    if "admin_selected_day" not in st.session_state:
        st.session_state.admin_selected_day = "Tag 1"

    # HIER IST JETZT DIE FUNKTION: Sauber eingerückt auf der Modulebene des Admin-Panels
    def save_admin_day():
        st.session_state.admin_selected_day = st.session_state.admin_radio_widget

    st.subheader("⚙️ Globaler Event-Status")
    st.radio(
        "Aktiven Tag für die gesamte Ausstellung festlegen:", 
        ["Tag 1", "Tag 2"], 
        key="admin_radio_widget",
        index=0 if st.session_state.admin_selected_day == "Tag 1" else 1,
        on_change=save_admin_day
    )

# BIS ADMIN CONTROL
# BIS ADMIN CONTROL
elif st.session_state.view == "BIS_Admin_Control":
    display_header_with_logo("👑 BIS Admin Control")
    df_full = load_labels()
    
    if df_full is not None:
        # --- HIER DIE NEUE RADIO-BOX FÜR DIE TAGE EINFÜGEN ---
        admin_tag = st.radio("Ausstellungstag verwalten:", ["Tag 1", "Tag 2"], horizontal=True, key="admin_day_selector").upper()
        
        # Spaltenname dynamisch bestimmen (SELECTION 1 oder SELECTION 2)
        sel_col = f"SELECTION {admin_tag.replace('TAG ', '')}"
        
        # Wir überschreiben temporär im geladenen Dataframe die 'SELECTION' Spalte,
        # damit alle nachfolgenden Filter im originalen Code (pool = df_full[df_full['SELECTION']...]) unverändert weiterlaufen!
        if sel_col in df_full.columns:
            df_full['SELECTION'] = df_full[sel_col]
        # -----------------------------------------------------

    if df_full is not None:
        # Auch die Kategorie-Auswahl braucht einen tagesabhängigen Key
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()), key=f"admin_sel_cat_{admin_tag}")
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        
        for label, klassen, geschl in bis_defs:
            # Der Expander-Key wird tagesabhängig, damit der Auf-/Zuklapp-Status nicht vermischt wird
            with st.expander(f"KLASSE: {label} ({admin_tag})", expanded=True):
                c_ctrl, c_votes = st.columns([1, 1.2])
                
                # Der v_prefix enthält jetzt den Tag, damit die Stimmen von Tag 1 und Tag 2 getrennt gesucht werden
                v_prefix = f"v_{admin_tag}_{sel_cat}_{label}_"
                
                with c_ctrl:
                    st.markdown("**Steuerung**")
                    
                    # Die Datenschlüssel im store.data erhalten den Tag, damit Werte getrennt gespeichert werden
                    key_reveal = f"reveal_{admin_tag}_{sel_cat}_{label}"
                    key_winner_reveal = f"winner_reveal_{admin_tag}_{sel_cat}_{label}"
                    key_override = f"override_{admin_tag}_{sel_cat}_{label}"
                    
                    # Die Widget-Keys (key=...) erhalten ebenfalls das admin_tag, was Streamlit zum sauberen Reset zwingt
                    store.data[key_reveal] = st.checkbox("Nominationen anzeigen", value=store.data.get(key_reveal, False), key=f"cb1_{key_reveal}")
                    store.data[key_winner_reveal] = st.checkbox("BIS Gewinner anzeigen", value=store.data.get(key_winner_reveal, False), key=f"cb2_{key_winner_reveal}")
                    
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    options = ["Automatisch (Stimmen)"] + sorted(pool['KAT_STR'].unique().tolist())
                    
                    store.data[key_override] = st.selectbox(f"Gewinner festlegen:", options, index=options.index(store.data.get(key_override, "Automatisch (Stimmen)")) if store.data.get(key_override) in options else 0, key=f"sb_{key_override}")
                    
                    final_nr = None
                    if store.data[key_override] != "Automatisch (Stimmen)": 
                        final_nr = store.data[key_override]
                    elif "votes" in store.data:
                        vts = [v for k, v in store.data["votes"].items() if k.startswith(v_prefix) and v != "Keine Wahl"]
                        if vts: 
                            final_nr = pd.Series(vts).value_counts().index[0]
                            
                    if final_nr and st.button(f"🏆 OVERLAY ZEIGEN (#{final_nr})", key=f"btn_ov_{admin_tag}_{sel_cat}_{label}"):
                        w_match = df_full[df_full['KAT_STR'] == str(final_nr)]
                        if not w_match.empty:
                            store.active_overlay = w_match.iloc[0].to_dict()
                            store.overlay_start_time = time.time()
                            if "local_overlay_end" in st.session_state:
                                st.session_state.local_overlay_end = 0
                        st.success(f"Overlay für #{final_nr} wurde gestartet!")
        
                with c_votes:
                    st.markdown("**Stimmen-Details**")
                    if "votes" in store.data:
                        current_votes = {k.replace(v_prefix, ""): v for k, v in store.data["votes"].items() if k.startswith(v_prefix) and v != "Keine Wahl"}
                        if current_votes:
                            vote_df = pd.DataFrame([{"Richter": r, "Wahl (Kat Nr.)": f"#{v}"} for r, v in current_votes.items()])
                            st.table(vote_df)
                            summary = pd.Series(current_votes.values()).value_counts()
                            st.write("**Zwischenstand:**")
                            for nr, count in summary.items(): 
                                st.write(f"Katze #{nr}: {count} Stimme(n)")
                                
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_bisadmin"):
        set_view("Home")

# BIS PUBLIC VIEW
# BIS PUBLIC VIEW NEW
# BIS PUBLIC VIEW NEW

elif st.session_state.view == "BIS_Public":
    # --- SCHALTWEICHE 1: OVERLAY AKTIVIERUNG PRÜFEN ---
    is_overlay_active = hasattr(store, 'active_overlay') and store.active_overlay is not None

    if is_overlay_active:
        if time.time() - store.overlay_start_time < 20:
            st.markdown(render_overlay_html(store.active_overlay), unsafe_allow_html=True)
            time.sleep(1)
            st.rerun() 
        else: 
            store.active_overlay = None
            st.rerun()

    def get_initials(name):
        parts = str(name).split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return str(name)[:2].upper()

    display_header_with_logo("🏆 Best in Show")
    df_full = load_labels()
    
    if df_full is not None:
        df_full = df_full.drop_duplicates() # Füge dies hinzu, um Geisterzeilen zu vermeiden
        # --- ANFANG DER ÄNDERUNG: AUTOMATISCHE TAGES-SYNCHRONISATION FÜR DAS PUBLIKUM ---
        # WIR HOLEN DEN GLOBALEN TAG VOM ADMIN ("Tag 1" ODER "Tag 2")
        global_admin_day = st.session_state.get("admin_selected_day", "Tag 1")
        current_tag = global_admin_day.upper()
        
        # WIR ÜBERSCHREIBEN DEINEN STABILEN TAG-SCHLÜSSEL AUTOMATISCH MIT DEM ADMIN-WERT
        st.session_state['bis_stable_tag'] = current_tag
        # --- ENDE DER ÄNDERUNG ---
		
		
		# --- STABILE WIDGET-INITIALISIERUNG ---
		# Holt den exakten Zustand vor dem Rerun ab, damit nichts zurückspringt
        # current_tag = st.session_state.get('bis_stable_tag', 'TAG 1')
        available_cats = sorted(df_full['KATEGORIE'].unique())
        current_cat = st.session_state.get('bis_stable_cat', available_cats[0])

        # Indices berechnen (Fallback auf 0, falls Werte beim Datenladen variieren)
        tag_index = ["TAG 1", "TAG 2"].index(current_tag) if current_tag in ["TAG 1", "TAG 2"] else 0
        cat_index = available_cats.index(current_cat) if current_cat in available_cats else 0

        # --- ANFANG DER ÄNDERUNG: ENTFERNUNG DES INTERAKTIVEN RADIO-BUTTONS ---
        # DIE MANUELLE AUSWAHL PER RADIO-BUTTON WURDE ENTFERNT. 
        # STATTDESTESSEN WIRBT EIN SCHREIBGESCHÜTZTER HINWEIS IN DER SIDEBAR FÜR KLARHEIT.
        st.sidebar.info(f"📅 Aktiver Ausstellungstag: {current_tag}")
        tag = current_tag
        # --- ENDE DER ÄNDERUNG ---
		

        # Widgets erzwingen den Zustand über den Index
        # tag_selection = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"], index=tag_index)
        # tag = tag_selection.upper()
        sel_cat = st.selectbox("Kategorie:", available_cats, index=cat_index)
        
        # Zustand sofort für den nächsten Durchlauf einfrieren
        st.session_state['bis_stable_tag'] = tag
        st.session_state['bis_stable_cat'] = sel_cat
        # --------------------------------------

        # --- DYNAMISCHE SPALTEN-WEICHE FÜR DIE 2 TAGE ---
        sel_col = f"SELECTION {tag.replace('TAG ', '')}"
        if sel_col in df_full.columns:
            df_full['SELECTION'] = df_full[sel_col]
        # ------------------------------------------------

        bis_defs = [
            ("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), 
            ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), 
            ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), 
            ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")
        ]
        
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])

        # --- PRÜFEN, OB ES IN DIESER KATEGORIE ÜBERHAUPT NOMINIERTE KATZEN GIBT ---
        cats_in_this_cat = df_full[
            (df_full['SELECTION'].astype(str).str.upper() == 'X') & 
            (df_full['KATEGORIE'] == sel_cat)
        ]

        # Wenn keine einzige Katze ein 'X' in dieser Kategorie hat, Tabelle ausblenden
        if cats_in_this_cat.empty:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info(f"ℹ️ In der Kategorie {sel_cat} sind für {tag} aktuell keine Katzen für die Best in Show nominiert.")
            
            # Verhindert, dass das restliche Layout/Footer nach oben springt
            st.markdown("<div style='min-height: 400px;'></div>", unsafe_allow_html=True)

        # --- CSS-LOGIK FÜR GRÜNE RICHTER IM HEADER ---
        style_rules = ""
        for label, klassen, geschl in bis_defs:
            if not store.data.get(f"winner_reveal_{tag}_{sel_cat}_{label}", False):
                prefix = f"v_{tag}_{sel_cat}_{label}_"
                abgestimmte = []
                for key, val in store.data.get("votes", {}).items():
                    if key.startswith(prefix) and val != "Keine Wahl" and val != "Keine Wahl/Not chosen yet":
                        # Weiche für Dictionary- oder String-Struktur
                        if isinstance(val, dict):
                            if val.get("katze") not in ["Keine Wahl", "Keine Wahl/Not chosen yet"]:
                                abgestimmte.append(key.replace(prefix, ""))
                        elif str(val) not in ["Keine Wahl", "Keine Wahl/Not chosen yet"]:
                            abgestimmte.append(key.replace(prefix, ""))
                
                for j in abgestimmte:
                    style_rules += f".judge-{str(j).replace(' ', '_')} {{ background-color: #28a745 !important; }}"

	    # --- HIER DIE FARBE DER GEWINNER-KARTE ANPASSEN ---
        style_rules += """
        .winner-card {
            background-color: #ffd700 !important;  /* Hintergrundfarbe (z.B. Gold) */
            border: 2px solid #d4af37 !important;  /* Rahmenfarbe */
            color: #000000 !important;             /* Textfarbe für Details */
        }
        .winner-card .cat-number {
            color: #000000 !important;             /* Textfarbe für die Startnummer */
            font-weight: bold !important;
        }
        """
        
        # Da style_rules jetzt niemals leer ist, rendern wir das Stylesheet direkt
        st.markdown(f"<style>{style_rules}</style>", unsafe_allow_html=True)

        # --- STATISCHER HEADER (oben, einmalig) ---
        cols = st.columns([0.8] + [1.2]*len(judges) + [0.8])
        cols[0].empty()
        for i, j in enumerate(judges):
            clean_id = str(j).replace(" ", "_")
            cols[i+1].markdown(f"<div class='judge-header-box judge-{clean_id}'>{j}</div>", unsafe_allow_html=True)
        cols[-1].markdown("<div class='judge-header-box' style='background-color:#b21f2d;'>BIS</div>", unsafe_allow_html=True)

        # --- KATZEN-ZEILEN ---
        for label, klassen, geschl in bis_defs:
            r_cols = st.columns([0.8] + [1.2]*len(judges) + [0.8])
            r_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
            
            show_noms = store.data.get(f"reveal_{tag}_{sel_cat}_{label}", False)
            winner_revealed = store.data.get(f"winner_reveal_{tag}_{sel_cat}_{label}", False)
            
            for i, j in enumerate(judges):
                with r_cols[i+1]:
                    if show_noms:
                        m = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not m.empty:
                            kat_nr = m.iloc[0]['KAT_STR']
                            circles_html = ""
                            if winner_revealed:
                                prefix = f"v_{tag}_{sel_cat}_{label}_"
                                all_votes = store.data.get("votes", {})
                                voters = []
                                for v_key, v_val in all_votes.items():
                                    if v_key.startswith(prefix):
                                        # Auslesen der Katalognummer aus Dict oder Plain-String
                                        voted_cat = v_val.get("katze") if isinstance(v_val, dict) else v_val
                                        if str(voted_cat) == str(kat_nr):
                                            voters.append(v_key.replace(prefix, ""))
                                if voters:
                                    circles = "".join([f"<div class='judge-circle' title='{v}'>{get_initials(v)}</div>" for v in voters])
                                    circles_html = f"<div class='judge-initials-container'>{circles}</div>"

                            st.markdown(f"<div class='cat-card'><div class='cat-number'>{kat_nr}</div><div class='cat-details'>{get_full_label(m.iloc[0])}</div>{circles_html}</div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
            
            with r_cols[-1]:
                if winner_revealed:
                    prefix = f"v_{tag}_{sel_cat}_{label}_"
                    winner_nr = store.data.get(f"override_{tag}_{sel_cat}_{label}", "Automatisch (Stimmen)")
                    if winner_nr == "Automatisch (Stimmen)" and "votes" in store.data:
                        vts = []
                        for k, v in store.data["votes"].items():
                            if k.startswith(prefix) and v != "Keine Wahl" and v != "Keine Wahl/Not chosen yet":
                                # Wir werten für das öffentliche Endergebnis nur bestätigte Stimmen!
                                if isinstance(v, dict):
                                    if v.get("status") == "bestaerkt":
                                        vts.append(v.get("katze"))
                                else:
                                    vts.append(v)
                        if vts: winner_nr = pd.Series(vts).value_counts().index[0]
                    if winner_nr and winner_nr != "Automatisch (Stimmen)":
                        m_w = df_full[df_full['KAT_STR'] == str(winner_nr)]
                        if not m_w.empty: st.markdown(f"<div class='cat-card winner-card'><div class='cat-number'>{winner_nr}</div><div class='cat-details'>{get_full_label(m_w.iloc[0])}</div></div>", unsafe_allow_html=True)
                else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)

    # --- SCHALTWEICHE 2: REFRESH NUR LADEN, WENN KEIN OVERLAY ZEIGT ---
    if not is_overlay_active:
        st_autorefresh(interval=3000, key="bis_refresh")


# LIVE DASHBOARD
elif st.session_state.view == "Dashboard":
    display_header_with_logo("📢 Live-Aufruf & Status")
    
    # Holt sich den vom Admin festgesetzten Tag (völlig immun gegen das st_autorefresh)
    admin_day = st.session_state.get("admin_selected_day", "Tag 1")
    tag = "TAG 2" if "2" in str(admin_day) else "TAG 1"
    
    # Passive Info-Anzeige in der Seitenleiste
    st.sidebar.info(f"📅 Aktiver Ausstellungstag: {tag}")
    
    df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"
        
        # Filtert das Excel NUR auf Zeilen, die am aktuellen Tag ein 'X' haben
        df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy()
        
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        if judges:
            cols = st.columns(len(judges))
            for i, j in enumerate(judges):
                with cols[i]:
                    st.markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
                    
                    judge_entries = []
                    for k, v in store.data.items():
                        if "|" in k and k.split("|")[1] == j:
                            kat_nr = k.split("|")[0]
                            
                            # PRÜFUNG: Existiert die Katze am aktuellen Tag bei diesem Richter?
                            m = df_tag[(df_tag['KAT_STR'] == kat_nr) & (df_tag[r_col] == j)]
                            
                            if not m.empty:  # Nur verarbeiten, wenn sie zum aktuellen Tag gehört!
                                flags = v.get("flags", {}) if isinstance(v, dict) else {}
                                beim_richten = flags.get("Zum Richten", False) and not flags.get("Gerichtet", False)
                                
                                # --- NEU: HOLE DEN STATUS OB DIE KATZE GERADE AUF DEM TISCH IST ---
                                wird_gerichtet = flags.get("Wird gerichtet", False) and not flags.get("Gerichtet", False)
                                # -----------------------------------------------------------------
                                
                                nominiert = flags.get("NOM", False)
                                biv = flags.get("BIV", False)
                                
                                # --- ÄNDERUNG: ERWEITERT UM "WIRD_GERICHTET", DAMIT DIE KARTE GEZEIGT WIRD ---
                                if beim_richten or wird_gerichtet or nominiert or biv:
                                    judge_entries.append({
                                        "key": k, 
                                        "data": v if isinstance(v, dict) else {"flags": {}},
                                        "row_data": m.iloc[0]  # Daten merken fürs spätere Anzeigen
                                    })
                    
                    judge_entries.sort(key=lambda x: x["data"].get("timestamp", 0))
                    
                    for entry in judge_entries:
                        kat_nr = entry["key"].split("|")[0]
                        flags = entry["data"].get("flags", {})
                        m_row = entry["row_data"]
                        
                        # --- NEU: DESIGN-WEICHE FÜR DAS ORANGE BLINKEN AUF DEM DASHBOARD ---
                        rendered_tags = []
                        for t, val in flags.items():
                            if val and t != "Gerichtet":
                                # LOGIK: FALLS "WIRD GERICHTET" AKTIV IST, BLENDEN WIR DAS BLAUE "ZUM RICHTEN" AUS
                                if t == "Zum Richten" and flags.get("Wird gerichtet"):
                                    continue
                                
                                # ENTFERNT LEERZEICHEN FÜR DEN CSS-KLASSENNAMEN (AUS "Wird gerichtet" WIRD "wirdgerichtet")
                                class_suffix = t.lower().replace(" ", "")
                                rendered_tags.append(f"<span class='tag tag-{class_suffix}'>{t}</span>")
                        
                        tags_html = "".join(rendered_tags)
                        # --------------------------------------------------------------------
                        
                        if tags_html: 
                            st.markdown(f"""
                                <div class='cat-card'>
                                    <div class='cat-number'>{kat_nr}</div>
                                    <div class='cat-details'>{get_full_label(m_row)}</div>
                                    <div class='tag-container'>{tags_html}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
    st_autorefresh(interval=10000, key="dash_refresh")

elif st.session_state.view == "Steward_Panel":
    display_header_with_logo("📝 Steward-Pult")
    df_full = load_labels()
    
    if df_full is not None:
        # 1. Prüfen, ob ein Richter via QR-Code übergeben wurde
        url_judge_name = st.session_state.get("url_judge", "--")
        
        # 2. Automatisch ermitteln, welcher Tag gilt (Standard ist der sichere ADMIN-TAG)
        admin_day = st.session_state.get("admin_selected_day", "Tag 1")
        calculated_tag = "TAG 2" if "2" in str(admin_day) else "TAG 1"
        
        # Falls in der URL explizit ein Tag steht (?day=2), überschreibt dieser den Admin-Tag
        url_day = st.query_params.get("day", None)
        if url_day == "1":
            calculated_tag = "TAG 1"
        elif url_day == "2":
            calculated_tag = "TAG 2"
        
        # 3. Wenn ein Richtername übergeben wurde, deine originale Logik prüfen:
        if url_judge_name != "--":
            j_t1 = [r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"] if 'RICHTER TAG 1' in df_full.columns else []
            j_t2 = [r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"] if 'RICHTER TAG 2' in df_full.columns else []
            
            if url_judge_name in j_t2 and url_judge_name not in j_t1:
                calculated_tag = "TAG 2"
        
        # Finale Zuweisung an die Variable tag für die Spaltennamen
        tag = calculated_tag.upper()
        
        # Nur noch eine passive Info-Anzeige in der Sidebar statt einem störenden Radio-Button
        st.sidebar.info(f"📅 Aktiver Ausstellungstag: {tag}")
        
        r_col = f"RICHTER {tag}"
        all_j = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        # Berechnen des Default-Index für die Richter-Selectbox
        default_idx = 0
        if url_judge_name in all_j:
            default_idx = all_j.index(url_judge_name) + 1 # +1 wegen dem "--" Eintrag
            
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j, index=default_idx)

        # --- WARNHINWEIS FÜR ABWEICHENDEN RICHTER ---
        if url_judge_name != "--" and mein_richter != "--" and mein_richter != url_judge_name:
            st.error(
                f"🚨 **ACHTUNG! Sie verlassen gerade Ihren zugewiesenen Richter!**\n\n"
                f"Sie sind ursprünglich eingeloggt für **{url_judge_name}**, "
                f"steuern aber aktuell die Katzenliste für **{mein_richter}**."
            )

        if mein_richter != "--":
            df_richter_alle = df_full[(df_full[tag].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)]
            verfuegbare_kategorien = sorted(list(set([str(cat).replace('.0', '') for cat in df_richter_alle['KATEGORIE'].unique() if pd.notna(cat)])))
            meine_kategorie = st.selectbox("Kategorie wählen:", verfuegbare_kategorien)
            
            df_j = df_richter_alle[df_richter_alle['KATEGORIE'].astype(str).str.replace('.0', '') == meine_kategorie].sort_values('KATALOG-NR')
            st.divider()
            
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']
                k = f"{nr}|{mein_richter}"
                
                # Spalten flexibel auslesen
                klasse = row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', 'N/A')))
                fg_cols = [c for c in row.index if "FARBGRUPPE" in c or "FARB-GRUPPE" in c]
                farbgruppe = row[fg_cols[0]] if fg_cols else row.get('FARBGRUPPE', 'N/A')
                if pd.isna(farbgruppe) or str(farbgruppe).strip().lower() == "nan": farbgruppe = "N/A"
                
                geschlecht = row.get('GESCHLECHT', 'N/A')
                geb_cols = [c for c in row.index if "GEB" in c or "GEBURT" in c]
                geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', 'N/A')
                if isinstance(geb_datum, pd.Timestamp): geb_datum = geb_datum.strftime('%d.%m.%Y')
                elif pd.isna(geb_datum) or str(geb_datum).strip().lower() == "nan": geb_datum = "N/A"
                
                # --- STRUKTUR INITIALISIEREN UND LOKALEN ZUSTAND HOLEN ---
                cat_state = {
                    "flags": {"Zum Richten": False, "Wird gerichtet": False, "BIV": False, "NOM": False, "Gerichtet": False},
                    "timestamp": 0
                }
                
                if k in store.data and isinstance(store.data[k], dict):
                    old_state = store.data[k]
                    if "flags" in old_state and isinstance(old_state["flags"], dict):
                        for flag_name in cat_state["flags"].keys():
                            cat_state["flags"][flag_name] = old_state["flags"].get(flag_name, False)
                    if "timestamp" in old_state:
                        cat_state["timestamp"] = old_state["timestamp"]
                # -----------------------------------------------------------------
                
                flags = cat_state["flags"]
                card_class = "steward-card-wrapper gerichtet" if flags.get("Gerichtet") else "steward-card-wrapper"
                
                # START DES GRAUEN RECHTECKS
                st.markdown(f"""
                <div class="{card_class}">
                    <div class="card-header-row">
                        <span class="card-cat-number">Nr. {nr}</span>
                        <span class="card-meta-main">{get_full_label(row)}</span>
                    </div>
                    <div class="grid-container">
                        <span class="card-meta-sub"><span class="meta-label">Klasse:</span> {klasse}</span>
                        <span class="card-meta-sub"><span class="meta-label">Farbgruppe:</span> {farbgruppe}</span>
                        <span class="card-meta-sub"><span class="meta-label">Geschlecht:</span> {geschlecht}</span>
                        <span class="card-meta-sub"><span class="meta-label">Geboren:</span> {geb_datum}</span>
                    </div>
                    <div style="border-top: 1px solid #e2e2e2; padding-top: 10px; margin-top: 12px; margin-bottom: 8px;"></div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4, c5 = st.columns(5, vertical_alignment="center")
                
                # BUTTON 1: AUFRUFEN (Blau)
                is_rich = flags.get("Zum Richten")
                with c1:
                    if is_rich and not flags.get("Wird gerichtet"): st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⚠️ [ AKTIV ] AUFGERUFEN ⚠️" if (is_rich and not flags.get("Wird gerichtet")) else "AUFRUFEN", key=f"btn_rich_{k}"):
                        cat_state["flags"]["Zum Richten"] = not is_rich
                        if cat_state["flags"]["Zum Richten"]:
                            cat_state["flags"]["Gerichtet"] = False
                            cat_state["timestamp"] = time.time()
                        else:
                            cat_state["flags"]["Wird gerichtet"] = False
                        
                        # ÄNDERUNG: DIREKTE ZUWEISUNG UND VERWENDUNG DER GARANTIERT EXISTIERENDEN METHODE
                        store.data[k] = cat_state
                        store.save_backup()
                        st.rerun()
                    if is_rich and not flags.get("Wird gerichtet"): st.markdown('</div>', unsafe_allow_html=True)
                
                # BUTTON 2: WIRD GERICHTET (Orange)
                is_busy = flags.get("Wird gerichtet")
                with c2:
                    if is_busy: st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⏳ TISCH / RICHTEN ⏳" if is_busy else "WIRD GERICHTET", key=f"btn_busy_{k}"):
                        cat_state["flags"]["Wird gerichtet"] = not is_busy
                        if cat_state["flags"]["Wird gerichtet"]:
                            cat_state["flags"]["Zum Richten"] = True 
                            cat_state["flags"]["Gerichtet"] = False
                            cat_state["timestamp"] = time.time()
                        
                        # ÄNDERUNG: DIREKTE ZUWEISUNG UND VERWENDUNG DER GARANTIERT EXISTIERENDEN METHODE
                        store.data[k] = cat_state
                        store.save_backup()
                        st.rerun()
                    if is_busy: st.markdown('</div>', unsafe_allow_html=True)

                # BUTTON 3: BIV (Grün)
                is_biv = flags.get("BIV")
                with c3:
                    if is_biv: st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⚠️ [ AKTIV ] BIV ⚠️" if is_biv else "BIV", key=f"btn_biv_{k}"):
                        cat_state["flags"]["BIV"] = not is_biv
                        cat_state["timestamp"] = time.time()
                        
                        # ÄNDERUNG: DIREKTE ZUWEISUNG UND VERWENDUNG DER GARANTIERT EXISTIERENDEN METHODE
                        store.data[k] = cat_state
                        store.save_backup()
                        st.rerun()
                    if is_biv: st.markdown('</div>', unsafe_allow_html=True)
                
                # BUTTON 4: NOMINIEREN (Gelb)
                is_nom = flags.get("NOM")
                with c4:
                    if is_nom: st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⚠️ [ AKTIV ] NOM ⚠️" if is_nom else "NOM", key=f"btn_nom_{k}"):
                        cat_state["flags"]["NOM"] = not is_nom
                        if cat_state["flags"]["NOM"]:
                            cat_state["timestamp"] = time.time()
                        
                        # ÄNDERUNG: DIREKTE ZUWEISUNG UND VERWENDUNG DER GARANTIERT EXISTIERENDEN METHODE
                        store.data[k] = cat_state
                        store.save_backup()
                        st.rerun()
                    if is_nom: st.markdown('</div>', unsafe_allow_html=True)
                
                # BUTTON 5: GERICHTET (Grau)
                is_done = flags.get("Gerichtet")
                with c5:
                    if st.button("[ ERLEDIGT ] GERICHTET" if is_done else "GERICHTET", key=f"btn_done_{k}"):
                        if not is_done:
                            cat_state["flags"]["Zum Richten"] = False
                            cat_state["flags"]["Wird gerichtet"] = False
                            cat_state["flags"]["Gerichtet"] = True
                        else:
                            cat_state["flags"]["Gerichtet"] = False
                        
                        # ÄNDERUNG: DIREKTE ZUWEISUNG UND VERWENDUNG DER GARANTIERT EXISTIERENDEN METHODE
                        store.data[k] = cat_state
                        store.save_backup()
                        st.rerun()
                                
                # ENDE DES GRAUEN RECHTECKS
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('<hr style="border: none; border-top: 2px solid #000; margin-top: 0px; margin-bottom: 30px;">', unsafe_allow_html=True)

# JUDGE VOTING
elif st.session_state.view == "Judge_Voting":
    display_header_with_logo("🗳️ Richter Abstimmung/Judges Votes")
    df_full = load_labels()
    if df_full is not None:
        # --- ANFANG DER ÄNDERUNG: AUTOMATISCHE TAGES-SYNCHRONISATION STATT MANUELLER AUSWAHL ---
        # WIR HOLEN DEN GLOBALEN TAG, DEN DER ADMIN IN SEINER HOME-FUNKTION GEWÄHLT HAT
        global_admin_day = st.session_state.get("admin_selected_day", "Tag 1")
        
        # WIR ZWINGEN DEINEN EXISTIERENDEN SELECTOR-KEY AUF DEN GLOBALEN ADMIN-TAG.
        # DADURCH BLEIBT DEINE KOMPLETTE FILTER-LOGIK IN 'load_labels()' ZU 100% ERHALTEN, 
        # ABER DER RICHTER KANN SICH NICHT MEHR VERKLICKEN.
        st.session_state["judge_day_selector"] = global_admin_day
        
        # STATT DES INTERAKTIVEN RADIO-BUTTONS ZEIGEN WIR DEN TAG NUR NOCH SCHREIBGESCHÜTZT AN
        st.sidebar.info(f"📅 Aktiver Ausstellungstag: {global_admin_day}")
        
        # DIE VARIABLE 'tag' WIRD HIER FÜR DIE UNTEREN SPALTENNAMEN DIREKT AUSGELESEN
        tag = global_admin_day.upper()
        # --- ENDE DER ÄNDERUNG ---
		
        r_col = f"RICHTER {tag}"
        all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        
        c1, c2 = st.columns(2)
        
                # PRÜFUNG: Wurde ein Richter in der URL mitgegeben? (Ignorieren, wenn Admin am Werk ist)
        url_judge_name = st.session_state.get("url_judge", "--")
        
        if url_judge_name in all_judges and st.session_state.user_role != "Admin":
            # Fixierung NUR für echte Richter-Direktlinks
            active_j = url_judge_name
            c1.markdown(f"<div style='padding-top:25px;'><b>Eingeloggt als Richter:</b> <span style='color:#1a4a9e; font-size:18px;'>{active_j}</span></div>", unsafe_allow_html=True)
        else:
            # Admins (oder wenn kein Richter in URL steht) sehen immer die volle Auswahlbox!
            active_j = c1.selectbox("Identität/Identity:", ["--"] + all_judges)

        active_cat = c2.selectbox("Kategorie/Category:", sorted(df_full['KATEGORIE'].unique()))
        
        # ... ab hier läuft dein originaler Code für das Voting unverändert weiter ...

        if active_j != "--":
            if "votes" not in store.data: store.data["votes"] = {}
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
            for label, klassen, geschl in bis_defs:
                with st.expander(f"Wahl für/Choice for {label}"):
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == active_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    if not pool.empty:
                        opts = {f"#{r['KAT_STR']} - {get_full_label(r)}": r['KAT_STR'] for _, r in pool.iterrows()}
                        # TAG wird hier in den Schlüssel eingebaut, damit Tag 1 und Tag 2 getrennt gespeichert und resettet werden
                        v_key = f"v_{tag}_{active_cat}_{label}_{active_j}"
                        curr = store.data["votes"].get(v_key, "Keine Wahl")
                        sel = st.radio("Favorit:", ["Keine Wahl/Not chosen yet"] + list(opts.keys()), index=(list(opts.values()).index(curr)+1) if curr in opts.values() else 0, key=f"r_{v_key}")
                        store.data["votes"][v_key] = opts[sel] if sel != "Keine Wahl/Not chosen yet" else "Keine Wahl/Not chosen yet"



# --- NEUER MENÜPUNKT: QR CODES ---
elif st.session_state.view == "QR_Codes":
    display_header_with_logo("📱 QR-Code Login Zentrale")
    st.write("Lass die Richter und Mitarbeiter diesen QR-Code scannen, um sich sofort ohne Passwort einzuloggen.")
    
    df_full = load_labels()
    
    # Basis-URL deiner App
    base_url = "https://kecb2026.streamlit.app/"
    
    # 1. Hilfsfunktion zum Zeichnen der QR-Codes für die Streamlit-UI
    def generate_qr_image(url_to_encode):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # 2. PDF-Generierungsfunktion (Getrennter Admin-Block & Emoji-frei)
    def generate_pdf_download(df):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, spaceAfter=15, textColor=colors.HexColor("#1A365D"), alignment=1)
        section_style = ParagraphStyle('DocSection', parent=styles['Heading2'], fontSize=12, leading=15, spaceBefore=15, spaceAfter=6, textColor=colors.HexColor("#2B6CB0"))
        label_style = ParagraphStyle('DocLabel', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor("#2D3748"))
        
        story = []
        story.append(Paragraph("QR-Code Login Zentrale - Burgdorf 2026", title_style))
        story.append(Spacer(1, 10))
        
        # --- FIX: ADMIN DIREKT ZEICHNEN (Nicht im 3er-Raster der Richter!) ---
        story.append(Paragraph("1. Allgemeine Logins und Admins", section_style))
        adm_url = f"{base_url}?view=admin&auth=true&role=Admin"
        
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(adm_url)
        qr.make(fit=True)
        img_pil = qr.make_image(fill_color="black", back_color="white")
        img_buf = BytesIO()
        img_pil.save(img_buf, format="PNG")
        img_buf.seek(0)
        
        # Platziert den Admin zentriert als Einzelelement
        admin_table = Table([[Paragraph("<b>ADMIN MAIN HOME</b>", label_style)], [Image(img_buf, width=90, height=90)]], colWidths=[180])
        admin_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(admin_table)
        story.append(Spacer(1, 15))
        
        # --- AB HIER NUR NOCH DIE LISTEN FÜR STUFENWEISE RASTER SAMMELN ---
        all_qr_items = []
        
        # --- Daten sammeln: Tag 1 ---
        if df is not None and 'RICHTER TAG 1' in df.columns:
            judges_t1 = sorted([r for r in df['RICHTER TAG 1'].unique() if str(r) != "nan"])
            for judge in judges_t1:
                # Stewards Tag 1
                stew_url = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=1"
                all_qr_items.append((f"Steward fuer: {judge}", stew_url, "2. Steward-Links fuer TAG 1 (Samstag)"))
                
                # Richter Direkt Tag 1
                j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                all_qr_items.append((f"Richter: {judge} (Tag 1)", j_url, "3. Richter-Direkt-Links fuer TAG 1 (Samstag)"))
                
        # --- Daten sammeln: Tag 2 ---
        if df is not None and 'RICHTER TAG 2' in df.columns:
            judges_t2 = sorted([r for r in df['RICHTER TAG 2'].unique() if str(r) != "nan"])
            for judge in judges_t2:
                # Stewards Tag 2
                stew_url = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=2"
                all_qr_items.append((f"Steward fuer: {judge}", stew_url, "4. Steward-Links fuer TAG 2 (Sonntag)"))
                
                # Richter Direkt Tag 2
                j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=2"
                all_qr_items.append((f"Richter: {judge} (Tag 2)", j_url, "5. Richter-Direkt-Links fuer TAG 2 (Sonntag)"))
        
        # --- Grid im PDF generieren ---
        unique_sections = list(dict.fromkeys([item[2] for item in all_qr_items]))
        for current_section in unique_sections:
            story.append(Paragraph(current_section, section_style))
            story.append(Spacer(1, 4))
            
            section_items = [item for item in all_qr_items if item[2] == current_section]
            cells = []
            
            for label, url, _ in section_items:
                qr = qrcode.QRCode(version=1, box_size=4, border=1)
                qr.add_data(url)
                qr.make(fit=True)
                img_pil = qr.make_image(fill_color="black", back_color="white")
                
                img_buf = BytesIO()
                img_pil.save(img_buf, format="PNG")
                img_buf.seek(0)
                
                rl_img = Image(img_buf, width=90, height=90)
                
                cell_content = [
                    Paragraph(f"<b>{label}</b>", label_style),
                    Spacer(1, 3),
                    rl_img,
                    Spacer(1, 10)
                ]
                cells.append(cell_content)
            
            grid_data = []
            row = []
            for i, cell in enumerate(cells):
                row.append(cell)
                if (i + 1) % 3 == 0 or (i + 1) == len(cells):
                    while len(row) < 3:
                        row.append(Paragraph("", label_style)) # Saubere leere Zelle
                    grid_data.append(row)
                    row = []
            
            if grid_data:
                table_grid = Table(grid_data, colWidths=[180, 180, 180])
                table_grid.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(table_grid)
                story.append(Spacer(1, 5))

        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # ---------------- DYNAMIC DOWNLOAD BUTTON ----------------
    st.write("### 🖨️ Druckansicht & Export")
    try:
        pdf_data = generate_pdf_download(df_full)
        st.download_button(
            label="📄 ALLE QR-Codes (Admins, Stewards & Richter) als PDF herunterladen",
            data=pdf_data,
            file_name="Alle_QR_Codes_Burgdorf_2026.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Fehler bei der PDF-Erstellung: {e}")
    
    st.divider()

    # Registerkarten für die Übersichtlichkeit (Web-Ansicht)
    tab1, tab2, tab3 = st.tabs(["🤵 Stewards & Admins", "👨‍⚖️ Richter (Tag 1)", "👨‍⚖️ Richter (Tag 2)"])
    
    # ---------------- TAB 1: STEWARDS & ADMINS ----------------
    with tab1:
        st.subheader("Allgemeine Logins")
        col_adm, _ = st.columns(2)
        with col_adm:
            st.warning("⚙️ ADMIN MAIN HOME")
            adm_url = f"{base_url}?view=admin&auth=true&role=Admin"
            st.image(generate_qr_image(adm_url), width=230)
            st.caption(f"[Link kopieren]({adm_url})")
            
        st.divider()
        
        if df_full is not None:
            # --- SEKTION: TAG 1 ---
            st.markdown("### 📝 Steward-Links für TAG 1 (Samstag)")
            st.write("Diese QR-Codes filtern fest auf die Richter von Tag 1:")
            
            if 'RICHTER TAG 1' in df_full.columns:
                judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
                if judges_t1:
                    s_cols_t1 = st.columns(3)
                    for idx, judge in enumerate(judges_t1):
                        with s_cols_t1[idx % 3]:
                            st.info(f"Steward für: {judge}")
                            stew_url_t1 = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=1"
                            st.image(generate_qr_image(stew_url_t1), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 1 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 1' fehlt in den Daten!")
                
            st.write("") 
            st.divider()
            st.write("") 
            
            # --- SEKTION: TAG 2 ---
            st.markdown("### 📝 Steward-Links für TAG 2 (Sonntag)")
            st.write("Diese QR-Codes filtern fest auf die Richter von Tag 2:")
            
            if 'RICHTER TAG 2' in df_full.columns:
                judges_t2 = sorted([r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"])
                if judges_t2:
                    s_cols_t2 = st.columns(3)
                    for idx, judge in enumerate(judges_t2):
                        with s_cols_t2[idx % 3]:
                            st.info(f"Steward für: {judge}")
                            stew_url_t2 = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=2"
                            st.image(generate_qr_image(stew_url_t2), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 2 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 2' fehlt in den Daten!")
                
    # ---------------- TAB 2: RICHTER TAG 1 ----------------
    with tab2:
        st.subheader("Richter-Direkt-Links für TAG 1")
        if df_full is not None:
            if 'RICHTER TAG 1' in df_full.columns:
                judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
                if judges_t1:
                    j_cols = st.columns(3)
                    for idx, judge in enumerate(judges_t1):
                        with j_cols[idx % 3]:
                            st.success(f"Richter: {judge}")
                            j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                            st.image(generate_qr_image(j_url), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 1 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 1' fehlt in den Daten!")

    # ---------------- TAB 3: RICHTER TAG 2 ----------------
    with tab3:
        st.subheader("Richter-Direkt-Links für TAG 2")
        if df_full is not None:
            if 'RICHTER TAG 2' in df_full.columns:
                judges_t2 = sorted([r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"])
                if judges_t2:
                    j_cols = st.columns(3)
                    for idx, judge in enumerate(judges_t2):
                        with j_cols[idx % 3]:
                            st.success(f"Richter: {judge}")
                            j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=2"
                            st.image(generate_qr_image(j_url), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 2 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 2' fehlt in den Daten!")
                
    # --- ZURÜCK NAVI ---
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_qrcode"):
        set_view("Home")

# --- NEU NEU NEUER MENÜPUNKT: QR CODES GENERIEREN---
elif st.session_state.view == "QR_Codes_Gen":
    display_header_with_logo("📱 QR-Code Login Generator")
    st.write("Lass die Richter und Mitarbeiter diesen QR-Code scannen, um sich sofort ohne Passwort einzuloggen.")
    
    df_full = load_labels()
    
    # Basis-URL deiner App
    base_url = "https://kecb2026.streamlit.app/"
    
    # 1. Hilfsfunktion zum Zeichnen der QR-Codes für die Streamlit-UI
    def generate_qr_image(url_to_encode):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # 2. PDF-Generierungsfunktion (Getrennter Admin-Block & Emoji-frei)
    def generate_pdf_download(df):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, spaceAfter=15, textColor=colors.HexColor("#1A365D"), alignment=1)
        section_style = ParagraphStyle('DocSection', parent=styles['Heading2'], fontSize=12, leading=15, spaceBefore=15, spaceAfter=6, textColor=colors.HexColor("#2B6CB0"))
        label_style = ParagraphStyle('DocLabel', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor("#2D3748"))
        
        story = []
        story.append(Paragraph("QR-Code Login Zentrale - Burgdorf 2026", title_style))
        story.append(Spacer(1, 10))
        
        # --- FIX: ADMIN DIREKT ZEICHNEN (Nicht im 3er-Raster der Richter!) ---
        story.append(Paragraph("1. Allgemeine Logins und Admins", section_style))
        adm_url = f"{base_url}?view=admin&auth=true&role=Admin"
        
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(adm_url)
        qr.make(fit=True)
        img_pil = qr.make_image(fill_color="black", back_color="white")
        img_buf = BytesIO()
        img_pil.save(img_buf, format="PNG")
        img_buf.seek(0)
        
        # Platziert den Admin zentriert als Einzelelement
        admin_table = Table([[Paragraph("<b>ADMIN MAIN HOME</b>", label_style)], [Image(img_buf, width=90, height=90)]], colWidths=[180])
        admin_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(admin_table)
        story.append(Spacer(1, 15))
        
        # --- AB HIER NUR NOCH DIE LISTEN FÜR STUFENWEISE RASTER SAMMELN ---
        all_qr_items = []
        
        # --- Daten sammeln: Tag 1 ---
        if df is not None and 'RICHTER TAG 1' in df.columns:
            judges_t1 = sorted([r for r in df['RICHTER TAG 1'].unique() if str(r) != "nan"])
            for judge in judges_t1:
                # Stewards Tag 1
                stew_url = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=1"
                all_qr_items.append((f"Steward fuer: {judge}", stew_url, "2. Steward-Links fuer TAG 1 (Samstag)"))
                
                # Richter Direkt Tag 1
                j_url = f"{base_url}?view=test-live-voting&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                all_qr_items.append((f"Richter: {judge} (Tag 1)", j_url, "3. Richter-Direkt-Links fuer TAG 1 (Samstag)"))
                
        # --- Daten sammeln: Tag 2 ---
        if df is not None and 'RICHTER TAG 2' in df.columns:
            judges_t2 = sorted([r for r in df['RICHTER TAG 2'].unique() if str(r) != "nan"])
            for judge in judges_t2:
                # Stewards Tag 2
                stew_url = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=2"
                all_qr_items.append((f"Steward fuer: {judge}", stew_url, "4. Steward-Links fuer TAG 2 (Sonntag)"))
                
                # Richter Direkt Tag 2
                j_url = f"{base_url}?view=test-live-voting&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=2"
                all_qr_items.append((f"Richter: {judge} (Tag 2)", j_url, "5. Richter-Direkt-Links fuer TAG 2 (Sonntag)"))
        
        # --- Grid im PDF generieren ---
        unique_sections = list(dict.fromkeys([item[2] for item in all_qr_items]))
        for current_section in unique_sections:
            story.append(Paragraph(current_section, section_style))
            story.append(Spacer(1, 4))
            
            section_items = [item for item in all_qr_items if item[2] == current_section]
            cells = []
            
            for label, url, _ in section_items:
                qr = qrcode.QRCode(version=1, box_size=4, border=1)
                qr.add_data(url)
                qr.make(fit=True)
                img_pil = qr.make_image(fill_color="black", back_color="white")
                
                img_buf = BytesIO()
                img_pil.save(img_buf, format="PNG")
                img_buf.seek(0)
                
                rl_img = Image(img_buf, width=90, height=90)
                
                cell_content = [
                    Paragraph(f"<b>{label}</b>", label_style),
                    Spacer(1, 3),
                    rl_img,
                    Spacer(1, 10)
                ]
                cells.append(cell_content)
            
            grid_data = []
            row = []
            for i, cell in enumerate(cells):
                row.append(cell)
                if (i + 1) % 3 == 0 or (i + 1) == len(cells):
                    while len(row) < 3:
                        row.append(Paragraph("", label_style)) # Saubere leere Zelle
                    grid_data.append(row)
                    row = []
            
            if grid_data:
                table_grid = Table(grid_data, colWidths=[180, 180, 180])
                table_grid.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(table_grid)
                story.append(Spacer(1, 5))

        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # ---------------- DYNAMIC DOWNLOAD BUTTON ----------------
    st.write("### 🖨️ Druckansicht & Export")
    try:
        pdf_data = generate_pdf_download(df_full)
        st.download_button(
            label="📄 ALLE QR-Codes (Admins, Stewards & Richter) als PDF herunterladen",
            data=pdf_data,
            file_name="Alle_QR_Codes_Burgdorf_2026.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Fehler bei der PDF-Erstellung: {e}")
    
    st.divider()

    # Registerkarten für die Übersichtlichkeit (Web-Ansicht)
    tab1, tab2, tab3 = st.tabs(["🤵 Stewards & Admins", "👨‍⚖️ Richter (Tag 1)", "👨‍⚖️ Richter (Tag 2)"])
    
    # ---------------- TAB 1: STEWARDS & ADMINS ----------------
    with tab1:
        st.subheader("Allgemeine Logins")
        col_adm, _ = st.columns(2)
        with col_adm:
            st.warning("⚙️ ADMIN MAIN HOME")
            adm_url = f"{base_url}?view=admin&auth=true&role=Admin"
            st.image(generate_qr_image(adm_url), width=230)
            st.caption(f"[Link kopieren]({adm_url})")
            
        st.divider()
        
        if df_full is not None:
            # --- SEKTION: TAG 1 ---
            st.markdown("### 📝 Steward-Links für TAG 1 (Samstag)")
            st.write("Diese QR-Codes filtern fest auf die Richter von Tag 1:")
            
            if 'RICHTER TAG 1' in df_full.columns:
                judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
                if judges_t1:
                    s_cols_t1 = st.columns(3)
                    for idx, judge in enumerate(judges_t1):
                        with s_cols_t1[idx % 3]:
                            st.info(f"Steward für: {judge}")
                            stew_url_t1 = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=1"
                            st.image(generate_qr_image(stew_url_t1), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 1 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 1' fehlt in den Daten!")
                
            st.write("") 
            st.divider()
            st.write("") 
            
            # --- SEKTION: TAG 2 ---
            st.markdown("### 📝 Steward-Links für TAG 2 (Sonntag)")
            st.write("Diese QR-Codes filtern fest auf die Richter von Tag 2:")
            
            if 'RICHTER TAG 2' in df_full.columns:
                judges_t2 = sorted([r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"])
                if judges_t2:
                    s_cols_t2 = st.columns(3)
                    for idx, judge in enumerate(judges_t2):
                        with s_cols_t2[idx % 3]:
                            st.info(f"Steward für: {judge}")
                            stew_url_t2 = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=2"
                            st.image(generate_qr_image(stew_url_t2), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 2 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 2' fehlt in den Daten!")
                
    # ---------------- TAB 2: RICHTER TAG 1 ----------------
    with tab2:
        st.subheader("Richter-Direkt-Links für TAG 1")
        if df_full is not None:
            if 'RICHTER TAG 1' in df_full.columns:
                judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
                if judges_t1:
                    j_cols = st.columns(3)
                    for idx, judge in enumerate(judges_t1):
                        with j_cols[idx % 3]:
                            st.success(f"Richter: {judge}")
                            j_url = f"{base_url}?view=test-live-voting&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                            st.image(generate_qr_image(j_url), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 1 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 1' fehlt in den Daten!")

    # ---------------- TAB 3: RICHTER TAG 2 ----------------
    with tab3:
        st.subheader("Richter-Direkt-Links für TAG 2")
        if df_full is not None:
            if 'RICHTER TAG 2' in df_full.columns:
                judges_t2 = sorted([r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"])
                if judges_t2:
                    j_cols = st.columns(3)
                    for idx, judge in enumerate(judges_t2):
                        with j_cols[idx % 3]:
                            st.success(f"Richter: {judge}")
                            j_url = f"{base_url}?view=test-live-voting&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=2"
                            st.image(generate_qr_image(j_url), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 2 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 2' fehlt in den Daten!")
                
    # --- ZURÜCK NAVI ---
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_qrcode"):
        set_view("Home")
                

# VIEW: NOMINATED CATS (DEIN KOMPLETTES ADMIN-KONTROLLZENTRUM + INTEGRIERTER PDF-DRUCK)
# ==============================================================================
elif st.session_state.view == "Nominated_Cats":
    display_header_with_logo("🏅 Nominierte Katzen (Admin-Zentrale)")

    def get_show_class(row):
        kl = str(row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', '')))).replace('.0', '')
        geschlecht = str(row.get('GESCHLECHT', '')).upper()
        if kl in ['1','3','5','7','9']: return f"Adult {geschlecht}"
        if kl in ['2','4','6','8','10']: return f"Neuter {geschlecht}"
        if kl == '11': return f"Junior 8-12 {geschlecht}"
        if kl == '12': return f"Kitten 4-8 {geschlecht}"
        return "Unbekannt"    
    
    df_full = load_labels()
        
    if df_full is not None:
        data_tag1 = []
        data_tag2 = []
        
        for _, row in df_full.iterrows():
            kat_nr = row.get('KAT_STR', str(row.get('KATALOG-NR', ''))).replace('.0', '')
            klasse = row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', '-')))
            
            # Farb- und Spalten-Ermittlung komplett unzensiert
            fg_cols = [c for c in row.index if "FARBGRUPPE" in c or "FARB-GRUPPE" in c]
            farbgruppe = row[fg_cols[0]] if fg_cols else row.get('FARBGRUPPE', '-')
            
            geb_cols = [c for c in row.index if "GEB" in c or "GEBURT" in c]
            geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', '-')
            if isinstance(geb_datum, pd.Timestamp): 
                geb_datum = geb_datum.strftime('%d.%m.%Y')

            # Echte Trennung nach SELECTION 1
            if str(row.get('SELECTION 1', '')).upper() == 'X':
                richter_t1 = row.get('RICHTER TAG 1', row.get('RICHTER 1', ''))
                data_tag1.append({
                    "Katalog-Nr.": kat_nr,
                    "Rasse": row.get('RASSE', '-'),
                    "Farbcode": row.get('FARBE', '-'),
                    "Farbgruppe": farbgruppe,
                    "Geburtsdatum": geb_datum,
                    "Geschlecht": row.get('GESCHLECHT', '-'),
                    "Kategorie": row.get('KATEGORIE', '-'),
                    "Klasse": klasse,
                    "Show-Klasse": get_show_class(row),
                    "Richter": richter_t1 if pd.notna(richter_t1) and str(richter_t1) != "nan" else "-",
                    "Tag": "Tag 1 (Sa)"
                })
                
            # Echte Trennung nach SELECTION 2
            if str(row.get('SELECTION 2', '')).upper() == 'X':
                richter_t2 = row.get('RICHTER TAG 2', row.get('RICHTER 2', ''))
                data_tag2.append({
                    "Katalog-Nr.": kat_nr,
                    "Rasse": row.get('RASSE', '-'),
                    "Farbcode": row.get('FARBE', '-'),
                    "Farbgruppe": farbgruppe,
                    "Geburtsdatum": geb_datum,
                    "Geschlecht": row.get('GESCHLECHT', '-'),
                    "Kategorie": row.get('KATEGORIE', '-'),
                    "Klasse": klasse,
                    "Show-Klasse": get_show_class(row),
                    "Richter": richter_t2 if pd.notna(richter_t2) and str(richter_t2) != "nan" else "-",
                    "Tag": "Tag 2 (So)"
                })

        # Drei Reiter: Deine beiden Original-Tage + das neue Druckzentrum
        tab_t1, tab_t2, tab_pdf_druck = st.tabs(["Tag 1 (Samstag)", "Tag 2 (Sonntag)", "🖨️ PDF Richter-Druckzentrum"])

        # --- SEITE FÜR TAG 1 (DEIN ORIGINAL CODE) ---
        with tab_t1:
            if data_tag1:
                df_nom_t1 = pd.DataFrame(data_tag1)
                
                # --- ADMIN-KONTROLLZENTRUM TAG 1 ---
                st.markdown("### 🛡️ Admin-Kontrollzentrum (Samstag)")
                df_valid_t1 = df_nom_t1[df_nom_t1['Richter'] != "-"].copy()
                
                dups_t1 = df_nom_t1[df_nom_t1.duplicated(subset=['Katalog-Nr.'], keep=False)]
                if not dups_t1.empty:
                    st.error(f"❌ {len(dups_t1['Katalog-Nr.'].unique())} Katze(n) sind mehrfach nominiert!")
                    st.dataframe(dups_t1[['Katalog-Nr.', 'Richter']], hide_index=True)
                else:
                    st.success("✅ Katalog-Nummern für Samstag sind eindeutig.")
                
                if not df_valid_t1.empty:
                    richter_load_t1 = df_valid_t1.groupby(['Richter', 'Kategorie']).size().reset_index(name='Anzahl')
                    overloaded_t1 = richter_load_t1[richter_load_t1['Anzahl'] > 8]
                    if not overloaded_t1.empty:
                        st.warning(f"⚠️ {len(overloaded_t1)} Richter-Kategorie-Kombination(en) über Limit (8)!")
                        st.dataframe(overloaded_t1, hide_index=True)
                    else:
                        st.success("✅ Richter-Kapazität für Samstag eingehalten.")
                        
                    violation_t1 = df_valid_t1.groupby(['Richter', 'Kategorie', 'Show-Klasse']).filter(lambda x: len(x) > 1)
                    if not violation_t1.empty:
                        st.error(f"❌ {len(violation_t1['Richter'].unique())} Richter hat Klassen-Verstöße!")
                        st.dataframe(violation_t1[['Richter', 'Kategorie', 'Show-Klasse', 'Katalog-Nr.']], hide_index=True)
                    else:
                        st.success("✅ Klassen-Regel für Samstag eingehalten.")
                
                st.divider()

                # --- FILTER & SORTIERUNG TAG 1 ---
                st.markdown("### 🔍 Filter & Sortierung (Samstag)")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    r_opt_t1 = ["Alle Richter"] + sorted([r for r in df_nom_t1['Richter'].unique() if r != "-"])
                    w_richter_t1 = st.selectbox("Nach Richter filtern:", r_opt_t1, key="r_t1")
                with c_f2:
                    k_opt_t1 = ["Alle Kategorien"] + sorted([str(k) for k in df_nom_t1['Kategorie'].unique() if k != "-"])
                    w_kat_t1 = st.selectbox("Nach Kategorie filtern:", k_opt_t1, key="k_t1")
                    
                c_f3, c_f4 = st.columns(2)
                with c_f3:
                    reihenfolge = ["Kitten 4-8 M", "Kitten 4-8 W", "Junior 8-12 M", "Junior 8-12 W", "Neuter M", "Neuter W", "Adult M", "Adult W"]
                    vorhandene_sk_t1 = [sk for sk in reihenfolge if sk in df_nom_t1['Show-Klasse'].unique()]
                    w_sk_t1 = st.selectbox("Nach Show-Klasse filtern:", ["Alle Show-Klassen"] + vorhandene_sk_t1, key="sk_t1")
                with c_f4:
                    g_opt_t1 = ["Alle Geschlechter"] + sorted([str(g) for g in df_nom_t1['Geschlecht'].unique() if g != "-"])
                    w_geschlecht_t1 = st.selectbox("Nach Geschlecht filtern:", g_opt_t1, key="g_t1")

                sort_options = {"Katalog-Nr.": "Katalog-Nr.", "Rasse": "Rasse", "Kategorie": "Kategorie", "Klasse": "Klasse", "Geschlecht": "Geschlecht", "Richter": "Richter"}
                w_sort_t1 = st.selectbox("Primär sortieren nach:", list(sort_options.keys()), key="s_t1")

                if w_richter_t1 != "Alle Richter": df_nom_t1 = df_nom_t1[df_nom_t1['Richter'] == w_richter_t1]
                if w_kat_t1 != "Alle Kategorien": df_nom_t1 = df_nom_t1[df_nom_t1['Kategorie'].astype(str) == w_kat_t1]
                if w_sk_t1 != "Alle Show-Klassen": df_nom_t1 = df_nom_t1[df_nom_t1['Show-Klasse'].astype(str) == w_sk_t1]
                if w_geschlecht_t1 != "Alle Geschlechter": df_nom_t1 = df_nom_t1[df_nom_t1['Geschlecht'] == w_geschlecht_t1]

                if w_sort_t1 == "Katalog-Nr.":
                    df_nom_t1 = df_nom_t1.sort_values(by="Katalog-Nr.", key=lambda x: pd.to_numeric(x, errors='coerce'))
                else:
                    df_nom_t1 = df_nom_t1.sort_values(by=sort_options[w_sort_t1])

                st.success(f"Gefunden: {len(df_nom_t1)} nominierte Katze(n) für Samstag.")
                st.dataframe(df_nom_t1, use_container_width=True, hide_index=True)
                
                csv_t1 = df_nom_t1.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Liste Tag 1 als CSV herunterladen", data=csv_t1, file_name="nominated_samstag.csv", mime="text/csv", key="dl_t1")
            else:
                st.info("Keine Nominationen für Tag 1 (Spalte 'SELECTION 1') vorhanden.")

        # --- SEITE FÜR TAG 2 (DEIN ORIGINAL CODE) ---
        with tab_t2:
            if data_tag2:
                df_nom_t2 = pd.DataFrame(data_tag2)
                
                # --- ADMIN-KONTROLLZENTRUM TAG 2 ---
                st.markdown("### 🛡️ Admin-Kontrollzentrum (Sonntag)")
                df_valid_t2 = df_nom_t2[df_nom_t2['Richter'] != "-"].copy()
                
                dups_t2 = df_nom_t2[df_nom_t2.duplicated(subset=['Katalog-Nr.'], keep=False)]
                if not dups_t2.empty:
                    st.error(f"❌ {len(dups_t2['Katalog-Nr.'].unique())} Katze(n) sind mehrfach nominiert!")
                    st.dataframe(dups_t2[['Katalog-Nr.', 'Richter']], hide_index=True)
                else:
                    st.success("✅ Katalog-Nummern für Sonntag sind eindeutig.")
                
                if not df_valid_t2.empty:
                    richter_load_t2 = df_valid_t2.groupby(['Richter', 'Kategorie']).size().reset_index(name='Anzahl')
                    overloaded_t2 = richter_load_t2[richter_load_t2['Anzahl'] > 8]
                    if not overloaded_t2.empty:
                        st.warning(f"⚠️ {len(overloaded_t2)} Richter-Kategorie-Kombination(en) über Limit (8)!")
                        st.dataframe(overloaded_t2, hide_index=True)
                    else:
                        st.success("✅ Richter-Kapazität für Sonntag eingehalten.")
                        
                    violation_t2 = df_valid_t2.groupby(['Richter', 'Kategorie', 'Show-Klasse']).filter(lambda x: len(x) > 1)
                    if not violation_t2.empty:
                        st.error(f"❌ {len(violation_t2['Richter'].unique())} Richter hat Klassen-Verstöße!")
                        st.dataframe(violation_t2[['Richter', 'Kategorie', 'Show-Klasse', 'Katalog-Nr.']], hide_index=True)
                    else:
                        st.success("✅ Klassen-Regel für Sonntag eingehalten.")
                
                st.divider()

                # --- FILTER & SORTIERUNG TAG 2 ---
                st.markdown("### 🔍 Filter & Sortierung (Sonntag)")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    r_opt_t2 = ["Alle Richter"] + sorted([r for r in df_nom_t2['Richter'].unique() if r != "-"])
                    w_richter_t2 = st.selectbox("Nach Richter filtern:", r_opt_t2, key="r_t2")
                with c_f2:
                    k_opt_t2 = ["Alle Kategorien"] + sorted([str(k) for k in df_nom_t2['Kategorie'].unique() if k != "-"])
                    w_kat_t2 = st.selectbox("Nach Kategorie filtern:", k_opt_t2, key="k_t2")
                    
                c_f3, c_f4 = st.columns(2)
                with c_f3:
                    reihenfolge = ["Kitten 4-8 M", "Kitten 4-8 W", "Junior 8-12 M", "Junior 8-12 W", "Neuter M", "Neuter W", "Adult M", "Adult W"]
                    vorhandene_sk_t2 = [sk for sk in reihenfolge if sk in df_nom_t2['Show-Klasse'].unique()]
                    w_sk_t2 = st.selectbox("Nach Show-Klasse filtern:", ["Alle Show-Klassen"] + vorhandene_sk_t2, key="sk_t2")
                with c_f4:
                    g_opt_t2 = ["Alle Geschlechter"] + sorted([str(g) for g in df_nom_t2['Geschlecht'].unique() if g != "-"])
                    w_geschlecht_t2 = st.selectbox("Nach Geschlecht filtern:", g_opt_t2, key="g_t2")

                w_sort_t2 = st.selectbox("Primär sortieren nach:", list(sort_options.keys()), key="s_t2")

                if w_richter_t2 != "Alle Richter": df_nom_t2 = df_nom_t2[df_nom_t2['Richter'] == w_richter_t2]
                if w_kat_t2 != "Alle Kategorien": df_nom_t2 = df_nom_t2[df_nom_t2['Kategorie'].astype(str) == w_kat_t2]
                if w_sk_t2 != "Alle Show-Klassen": df_nom_t2 = df_nom_t2[df_nom_t2['Show-Klasse'].astype(str) == w_sk_t2]
                if w_geschlecht_t2 != "Alle Geschlechter": df_nom_t2 = df_nom_t2[df_nom_t2['Geschlecht'] == w_geschlecht_t2]

                if w_sort_t2 == "Katalog-Nr.":
                    df_nom_t2 = df_nom_t2.sort_values(by="Katalog-Nr.", key=lambda x: pd.to_numeric(x, errors='coerce'))
                else:
                    df_nom_t2 = df_nom_t2.sort_values(by=sort_options[w_sort_t2])

                st.success(f"Gefunden: {len(df_nom_t2)} nominierte Katze(n) für Sonntag.")
                st.dataframe(df_nom_t2, use_container_width=True, hide_index=True)
                
                csv_t2 = df_nom_t2.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Liste Tag 2 als CSV herunterladen", data=csv_t2, file_name="nominated_sonntag.csv", mime="text/csv", key="dl_t2")
            else:
                st.info("Keine Nominationen für Tag 2 (Spalte 'SELECTION 2') vorhanden.")

        # --- REITER 3: DER NEUE DRUCK-BEREICH FÜR DAS REVOLUTIONÄRE RICHTER-PDF ---
        with tab_pdf_druck:
            st.markdown("### 🖨️ Offizielle Richter-Nominationsliste (PDF)")
            st.write("Wähle den Ausstellungstag und den Richter aus, um das personalisierte Deckblatt mit der Gesamtliste aller Nominationen inklusive Nominierungs-Richter zu drucken.")
            
            selected_day_label = st.selectbox("📅 Ausstellungstag für PDF wählen:", ["Tag 1 (Samstag)", "Tag 2 (Sonntag)"], key="pdf_day_sel")
            day_num = 1 if "Tag 1" in selected_day_label else 2
            tag_key = f"TAG {day_num}"
            selection_col = f"SELECTION {day_num}"
            judge_col = f"RICHTER TAG {day_num}"
            
            if selection_col in df_full.columns and judge_col in df_full.columns:
                available_judges = sorted([r for r in df_full[judge_col].unique() if pd.notna(r) and str(r).strip() != "" and str(r).lower() != "nan" and str(r) != "-"])
                
                if available_judges:
                    selected_judge = st.selectbox("👨‍⚖️ Richter für PDF wählen (für Deckblatt & QR-Code):", available_judges, key="pdf_judge_sel")
                    st.write("")
                    
                    if st.button(f"🖨️ PDF für {selected_judge} ({tag_key}) generieren", use_container_width=True, key="btn_gen_pdf_nominated"):
                        
                        # Alle nominierten Katzen des Tages holen
                        df_nominated = df_full[df_full[selection_col].astype(str).str.upper() == 'X'].copy()
                        
                        # Sprechende Übersetzungen der Klassen (z.B. Kitten 4-8 Female)
                        def get_pdf_show_class_label(row):
                            kl = str(row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', ''))).replace('.0', '').strip()
                            geschlecht_raw = str(row.get('GESCHLECHT', '')).strip().lower()
                            geschlecht_str = "Male" if geschlecht_raw in ['m', '1,0', 'male'] else "Female"
                            
                            if kl in ['1','3','5','7','9']: return f"Adult {geschlecht_str}"
                            if kl in ['2','4','6','8','10']: return f"Neuter {geschlecht_str}"
                            if kl == '11': return f"Junior 8-12 {geschlecht_str}"
                            if kl == '12': return f"Kitten 4-8 {geschlecht_str}"
                            return f"Class {kl} {geschlecht_str}"

                        if not df_nominated.empty:
                            pdf_buffer = BytesIO()
                            doc = SimpleDocTemplate(
                                pdf_buffer, pagesize=A4,
                                leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
                            )
                            
                            styles = getSampleStyleSheet()
                            title_style = ParagraphStyle(
                                'CoverTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
                                fontSize=26, leading=32, alignment=1, textColor=colors.HexColor('#1a4a9e'), spaceAfter=30
                            )
                            cat_header_style = ParagraphStyle(
                                'CategoryHeader', parent=styles['Heading2'], fontName='Helvetica-Bold',
                                fontSize=22, leading=26, textColor=colors.HexColor('#1a4a9e'), spaceBefore=15, spaceAfter=15, keepWithNext=True
                            )
                            class_header_style = ParagraphStyle(
                                'ClassHeader', parent=styles['Heading3'], fontName='Helvetica-Bold',
                                fontSize=14, leading=18, textColor=colors.HexColor('#333333'), spaceBefore=12, spaceAfter=6, keepWithNext=True
                            )
                            
                            # Farb-Styles
                            cell_header_text = ParagraphStyle('CellHeaderText', fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=1, textColor=colors.white)
                            cell_text_bold = ParagraphStyle('CellTextBold', fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=1, textColor=colors.black)
                            cell_text_normal = ParagraphStyle('CellTextNormal', fontName='Helvetica', fontSize=10, leading=13, alignment=0, textColor=colors.black)
                            
                            story = []
                            
                            # ======================================================
                            # SEITE 1: COVERSHEET
                            # ======================================================
                            story.append(Spacer(1, 40))
                            if os.path.exists(LOGO_URL):
                                story.append(Image(LOGO_URL, width=120, height=120))
                                story.append(Spacer(1, 20))
                                
                            story.append(Paragraph(f"Nominated Cats List<br/>Burgdorf Day {day_num} - {selected_judge}", title_style))
                            story.append(Spacer(1, 30))
                            
                            # Reines Ersetzen der Leerzeichen durch ein + (Sonderzeichen bleiben wie sie sind)
                            base_url = "https://kecb2026.streamlit.app/"
                            judge_param = str(selected_judge).replace(' ', '+')
                            test_live_url = f"{base_url}?view=test-live-voting&auth=true&role=Richter&judge={judge_param}&day={day_num}"

                            qr = qrcode.QRCode(version=1, box_size=10, border=4)
                            qr.add_data(test_live_url)
                            qr.make(fit=True)
                            img_qr = qr.make_image(fill_color="black", back_color="white")
                            
                            qr_buffer = BytesIO()
                            img_qr.save(qr_buffer, format="PNG")
                            qr_buffer.seek(0)
                            
                            story.append(Image(qr_buffer, width=200, height=200))
                            story.append(Spacer(1, 15))
                            story.append(Paragraph(
                                f"<font color='#1a4a9e'><b>SCAN FOR LIVE VOTING</b></font><br/>"
                                f"<font size='8' color='#666666'>{test_live_url}</font>", 
                                ParagraphStyle('QR_Sub', fontName='Helvetica', fontSize=10, alignment=1, leading=14)
                            ))
                            
                            from reportlab.platypus import PageBreak
                            story.append(PageBreak())
                            
                            # ======================================================
                            # SEITE 2+: DIE GESAMTLISTE MIT NEUER SORTIERUNG
                            # ======================================================
                            categories = sorted(df_nominated['KATEGORIE'].unique(), key=lambda x: str(x))
                            
                            for idx_cat, cat in enumerate(categories):
                                if idx_cat > 0:
                                    story.append(PageBreak())
                                    
                                story.append(Paragraph(f"Category {cat}", cat_header_style))
                                df_cat = df_nominated[df_nominated['KATEGORIE'] == cat].copy()
                                df_cat['PDF_SHOW_CLASS'] = df_cat.apply(get_pdf_show_class_label, axis=1)
                                
                                # EXAKTE REIHNENFOLGE NACH DEINER VORGABE: (Zuerst Female vor Male!)
                                klassen_reihenfolge = [
                                    "Kitten 4-8 Female", "Kitten 4-8 Male", 
                                    "Junior 8-12 Female", "Junior 8-12 Male", 
                                    "Neuter Female", "Neuter Male", 
                                    "Adult Female", "Adult Male"
                                ]
                                
                                # Nur die Klassen herausfiltern, die auch tatsächlich Katzen enthalten
                                vorhandene_klassen = [sk for sk in klassen_reihenfolge if sk in df_cat['PDF_SHOW_CLASS'].unique()]
                                for sk in df_cat['PDF_SHOW_CLASS'].unique():
                                    if sk not in vorhandene_klassen:
                                        vorhandene_klassen.append(sk)
                                        
                                # Durchlaufe die Klassen in der exakten Wunsch-Reihenfolge
                                for s_klasse in vorhandene_klassen:
                                    df_class = df_cat[df_cat['PDF_SHOW_CLASS'] == s_klasse].copy()
                                    df_class['SORT_KEY'] = pd.to_numeric(df_class['KATALOG-NR'], errors='coerce')
                                    df_class = df_class.sort_values('SORT_KEY')
                                    
                                    if not df_class.empty:
                                        story.append(Paragraph(s_klasse, class_header_style))
                                        
                                        # Tabellen-Header
                                        table_data = [[
                                            Paragraph("<b>Number</b>", cell_header_text), 
                                            Paragraph("<b>EMS/Group</b>", cell_header_text), 
                                            Paragraph("<b>Date of Birth</b>", cell_header_text), 
                                            Paragraph("<b>Sex</b>", cell_header_text),
                                            Paragraph("<b>Nominated by</b>", cell_header_text)
                                        ]]
                                        
                                        for _, row in df_class.iterrows():
                                            kat_nr = str(row.get('KAT_STR', row.get('KATALOG-NR', ''))).replace('.0', '')
                                            rasse_name = row.get('RASSE', '-')
                                            farbcode = row.get('FARBE', '-')
                                            
                                            fg_cols = [c for c in row.index if "FARBGRUPPE" in str(c) or "FARB-GRUPPE" in str(c)]
                                            farbgruppe = row[fg_cols[0]] if fg_cols else row.get('FARBGRUPPE', '')
                                            gruppe_clean = roman_to_numeric(farbgruppe) if 'roman_to_numeric' in globals() else farbgruppe
                                            
                                            if gruppe_clean and str(gruppe_clean).strip() != "-":
                                                details_text = f"<b>{rasse_name} {farbcode}</b><br/>Group {gruppe_clean}"
                                            else:
                                                details_text = f"<b>{rasse_name} {farbcode}</b>"
                                                
                                            geb_cols = [c for c in row.index if "GEB" in str(c) or "GEBURT" in str(c)]
                                            geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', '-')
                                            if isinstance(geb_datum, pd.Timestamp):
                                                geb_datum = geb_datum.strftime('%d.%m.%Y')
                                            elif pd.isna(geb_datum) or str(geb_datum).strip().lower() == "nan":
                                                geb_datum = "–"
                                                
                                            geschl_raw = str(row.get('GESCHLECHT', '-')).strip().upper()
                                            geschl_text = "MALE (1.0)" if geschl_raw in ['M', '1,0', 'MALE'] else "FEMALE (0.1)"
                                            
                                            nominating_judge = row.get(judge_col, row.get(f'RICHTER {day_num}', '-'))
                                            if pd.isna(nominating_judge) or str(nominating_judge).strip().lower() == "nan" or str(nominating_judge).strip() == "":
                                                nominating_judge = "-"
                                            
                                            table_data.append([
                                                Paragraph(f"<font size='14'><b>{kat_nr}</b></font>", cell_text_bold),
                                                Paragraph(details_text, cell_text_normal),
                                                Paragraph(str(geb_datum), cell_text_bold),
                                                Paragraph(geschl_text, cell_text_bold),
                                                Paragraph(str(nominating_judge), cell_text_bold)
                                            ])
                                            
                                        cat_table = Table(table_data, colWidths=[55, 175, 80, 88, 125])
                                        cat_table.setStyle(TableStyle([
                                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4a9e')),
                                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                                        ]))
                                        
                                        story.append(cat_table)
                                        story.append(Spacer(1, 10))
                                        
                            doc.build(story)
                            pdf_buffer.seek(0)
                            
                            st.success(f"🎉 PDF-Kompilierung für Richter {selected_judge} erfolgreich abgeschlossen!")
                            st.download_button(
                                label=f"📥 PDF-Datei herunterladen und drucken",
                                data=pdf_buffer,
                                file_name=f"Nominated_Cats_Day{day_num}_{selected_judge.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.warning(f"Für {selected_day_label} wurden generell keine nominierten Katzen gefunden.")
                else:
                    st.info("Es wurden am gewählten Tag keine gültigen Richternamen gefunden.")
            else:
                st.error(f"Fehler: Spaltenstrukturen '{selection_col}' oder '{judge_col}' fehlen in der Datei.")

    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_nom"):
        set_view("Home")


# ADMIN PANEL
elif st.session_state.view == "Admin_Panel":
    display_header_with_logo("⚙️ Admin-Konsole")
    
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        store.active_overlay = None
        st.success("Speicher geleert!")

    # --- HIER IST DER NEUE BUTTON SAUBER EINIGERÜCKT ---
    st.markdown("---")  # Eine kleine Trennlinie für die Optik
    st.subheader("🔄 Excel-Cache")
    st.write("Die Excel-Datei wird automatisch alle 10 Minuten neu eingelesen. Hier kannst du das Laden sofort erzwingen:")
    
    if st.button("🔥 Excel-Daten JETZT sofort neu einlesen", key="clear_cache_button"):
        load_labels.clear()  # Löscht den 10-Minuten-Cache sofort
        st.success("Der Cache wurde geleert! Die Excel-Datei wird beim nächsten Aufruf frisch geladen.")
        st.rerun()
    st.markdown("---")
        
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_admin"):
        set_view("Home")


		
# --- NEUER MENÜPUNKT: JUDGE LIST ---
elif st.session_state.view == "Judge_List" or st.session_state.view == "Judge List":
    display_header_with_logo("📊 Judge Book")
    st.write("Sieh sofort, welche Katzen in den jeweiligen Klassen direkt gegeneinander antreten.")
    
    df_full = load_labels()
    
    if df_full is not None:
        # Funktion zur Tabellen-Generierung, damit kein Code doppelt existiert oder gekürzt wird
        def render_judge_table(tag_key, r_col, suffix):
            # Alle Richter holen, die an diesem Tag aktiv sind
            all_j = sorted([r for r in df_full[df_full[tag_key].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
            
            c1, c2 = st.columns(2)
            mein_richter = c1.selectbox("Richter filtern:", ["--"] + all_j, key=f"jl_judge_{suffix}")
            
            if mein_richter != "--":
                # Kategorien für diesen Richter ermitteln
                df_richter_alle = df_full[(df_full[tag_key].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)]
                verfuegbare_kategorien = sorted(list(set([str(cat).replace('.0', '') for cat in df_richter_alle['KATEGORIE'].unique() if pd.notna(cat)])))
                meine_kategorie = c2.selectbox("Kategorie filtern:", verfuegbare_kategorien, key=f"jl_cat_{suffix}")
                
                # Daten filtern und sortieren nach Katalog-Nr
                df_filtered = df_richter_alle[df_richter_alle['KATEGORIE'].astype(str).str.replace('.0', '') == meine_kategorie].sort_values('KATALOG-NR')
                
                st.divider()
                
                # --- ANZAHL DER KATZEN ANZEIGEN ---
                anzahl_katzen = len(df_filtered)
                st.markdown(f"**Gemeldete Katzen in dieser Auswahl:** {anzahl_katzen}")
                
                # Vorbereitung der Tabellendaten
                table_rows = []
                
                for _, row in df_filtered.iterrows():
                    nr = row['KAT_STR']
                    ems = row.get('RASSE_KURZ', row.get('RASSE', '')) + " " + row.get('FARBE', '')
                    sex = row.get('GESCHLECHT', 'N/A')
                    klasse = str(row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', 'N/A')))).replace('.0', '')
                    
                    # Geburtsdatum formatieren
                    geb_cols = [c for c in row.index if "GEB" in c or "GEBURT" in c]
                    geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', 'N/A')
                    if isinstance(geb_datum, pd.Timestamp): 
                        geb_datum = geb_datum.strftime('%d.%m.%Y')
                    elif pd.isna(geb_datum) or str(geb_datum).strip().lower() == "nan": 
                        geb_datum = "–"
                    
                    # 8-Spalten Logik initialisieren
                    x_cols = {"Ad ♂": "", "Ad ♀": "", "K ♂": "", "K ♀": "", "11 ♂": "", "11 ♀": "", "12 ♂": "", "12 ♀": ""}
                    
                    # Automatische Zuordnung basierend auf Klasse und Geschlecht (Sex)
                    try:
                        kl_num = int(klasse)
                        
                        sex_clean = str(sex).strip().lower()
                        is_male = (sex_clean == "1,0" or sex_clean == "m")
                        
                        if kl_num in [1, 3, 5, 7, 9]:
                            x_cols["Ad ♂" if is_male else "Ad ♀"] = "X"
                        elif kl_num in [2, 4, 6, 8, 10]:
                            x_cols["K ♂" if is_male else "K ♀"] = "X"
                        elif kl_num == 11:
                            x_cols["11 ♂" if is_male else "11 ♀"] = "X"
                        elif kl_num == 12:
                            x_cols["12 ♂" if is_male else "12 ♀"] = "X"
                    except ValueError:
                        pass
                    
                    # Zeile zusammensetzen
                    row_entry = {
                        "Nr.": nr,
                        "EMS-Code": ems,
                        "Sex": sex,
                        "Kl.": klasse,
                        "Geboren": geb_datum,
                        **x_cols
                    }
                    table_rows.append(row_entry)
                
                if table_rows:
                    df_display = pd.DataFrame(table_rows)
                    
                    # Darstellung als sortierbare Streamlit-Tabelle
                    st.dataframe(
                        df_display, 
                        use_container_width=True, 
                        hide_index=True,
                        height=650,
                        column_config={
                            "Nr.": st.column_config.TextColumn(width="small"),
                            "Sex": st.column_config.TextColumn(width="small"),
                            "Kl.": st.column_config.TextColumn(width="small"),
                            "Ad ♂": st.column_config.TextColumn(alignment="center"),
                            "Ad ♀": st.column_config.TextColumn(alignment="center"),
                            "K ♂": st.column_config.TextColumn(alignment="center"),
                            "K ♀": st.column_config.TextColumn(alignment="center"),
                            "11 ♂": st.column_config.TextColumn(alignment="center"),
                            "11 ♀": st.column_config.TextColumn(alignment="center"),
                            "12 ♂": st.column_config.TextColumn(alignment="center"),
                            "12 ♀": st.column_config.TextColumn(alignment="center"),
                        }
                    )
                    
                    st.caption("💡 Tipp: Klicke auf die Spaltenköpfe (z.B. '12 ♀'), um die Katzen zu sortieren und Konkurrenten direkt im Blick zu haben!")
                else:
                    st.info("Keine Katzen für diese Auswahl gemeldet.")
            else:
                st.info("Bitte wähle einen Richter aus der Liste aus, um die Judge List anzuzeigen.")

        # Hier werden die Tabs generiert
        tab_tag1, tab_tag2 = st.tabs(["Tag 1 (Samstag)", "Tag 2 (Sonntag)"])
        
        with tab_tag1:
            render_judge_table("TAG 1", "RICHTER TAG 1", "t1")
            
        with tab_tag2:
            render_judge_table("TAG 2", "RICHTER TAG 2", "t2")
            
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_judgebook"):
        set_view("Home")




# --- EIGENSTÄNDIGE VIEW: NOMINATION LABELS DRUCK ---
elif st.session_state.view in ["Nomination_Labels", "Nomination Labels"]:
    display_header_with_logo("🖨️ Nomination Labels Druckzentrale")
    st.write("Generiere hier die exakten Druck-Labels (8 Stück pro A4-Seite). Jede Klasse beginnt ein neues Blatt.")

    df_full = load_labels()
    
    if df_full is not None:
        # 1. Spaltennamen radikal säubern
        df_full.columns = [str(c).strip().upper() for c in df_full.columns]
        
        # 2. Hilfsspalte für eine korrekte numerische Sortierung erstellen
        # Verhindert, dass 100 vor 11 kommt
        if 'KAT_STR' in df_full.columns:
            df_full['_sort_nr_helper'] = pd.to_numeric(
                df_full['KAT_STR'].astype(str).str.replace('.0', '', regex=False).str.strip(), 
                errors='coerce'
            ).fillna(9999).astype(int)
        else:
            df_full['_sort_nr_helper'] = 0

        # 3. Präzise Filterung & direkte Sortierung (Kategorie -> Klasse -> Kat.-Nr.)
        sort_spalten = []
        if 'KATEGORIE' in df_full.columns: sort_spalten.append('KATEGORIE')
        if 'KLASSE_INTERNAL' in df_full.columns: sort_spalten.append('KLASSE_INTERNAL')
        sort_spalten.append('_sort_nr_helper')

        if 'SELECTION 1' in df_full.columns:
            df_samstag_daten = df_full[df_full['SELECTION 1'].astype(str).str.upper() == 'X'].sort_values(by=sort_spalten).copy()
        elif 'SELECTION' in df_full.columns:
            df_samstag_daten = df_full[df_full['SELECTION'].astype(str).str.upper() == 'X'].sort_values(by=sort_spalten).copy()
        else:
            df_samstag_daten = pd.DataFrame(columns=df_full.columns)
            
        if 'SELECTION 2' in df_full.columns:
            df_sonntag_daten = df_full[df_full['SELECTION 2'].astype(str).str.upper() == 'X'].sort_values(by=sort_spalten).copy()
        else:
            df_sonntag_daten = pd.DataFrame(columns=df_full.columns)

        # Aufräumen der Hilfsspalte, damit sie nicht in der App stört
        if not df_samstag_daten.empty: df_samstag_daten.drop(columns=['_sort_nr_helper'], errors='ignore', inplace=True)
        if not df_sonntag_daten.empty: df_sonntag_daten.drop(columns=['_sort_nr_helper'], errors='ignore', inplace=True)


    
    

        # DEINE PDF-FUNKTION (KOMPLETT UNBERÜHRT UND UNVERÄNDERT)
        def generate_avery_labels(df):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            mm = 2.83464
            label_width = 99.1 * mm
            label_height = 67.7 * mm
            margin_left = 5.9 * mm
            margin_top = 13.1 * mm
            
            color_map = {
                "AM": colors.HexColor("#ffff00"),
                "AW": colors.HexColor("#ff99cc"),
                "KM": colors.HexColor("#99cc00"),
                "KW": colors.HexColor("#33ccff"),
                "JM": colors.HexColor("#cc99ff"),
                "JW": colors.HexColor("#e60073"),
                "KiM": colors.HexColor("#ffbf00"),
                "KiW": colors.HexColor("#ff6600")
            }
            
            sorted_rows = []
            for idx, row in df.iterrows():
                klasse_val = row.get('KLASSE_INTERNAL', row.get('KLASSE', ''))
                klasse_str = str(klasse_val).replace('.0', '')
                sex = str(row.get('GESCHLECHT', '')).strip().upper()
                kat_nr_str = str(row.get('KAT_STR', '')).replace('.0', '')
                
                try:
                    kat_nr_sort = int(kat_nr_str)
                except:
                    kat_nr_sort = 9999
                
                badge_key = "AM"
                badge_label = "Adult M"
                sort_order = 0
                
                try:
                    kl_num = int(klasse_str)
                    is_male = (sex in ["1,0", "M", "MALE"])
                    if kl_num in [1, 3, 5, 7, 9]:
                        badge_key = "AM" if is_male else "AW"
                        badge_label = "Adult M" if is_male else "Adult W"
                        sort_order = 0 if is_male else 1
                    elif kl_num in [2, 4, 6, 8, 10]:
                        badge_key = "KM" if is_male else "KW"
                        badge_label = "Kastrat M" if is_male else "Kastrat W"
                        sort_order = 2 if is_male else 3
                    elif kl_num == 11:
                        badge_key = "JM" if is_male else "JW"
                        badge_label = "8-12 M" if is_male else "8-12 W"
                        sort_order = 4 if is_male else 5
                    elif kl_num == 12:
                        badge_key = "KiM" if is_male else "KiW"
                        badge_label = "4-8 M" if is_male else "4-8 W"
                        sort_order = 6 if is_male else 7
                except:
                    if "K" in sex or "N" in sex:
                        badge_key = "KM" if "M" in sex else "KW"
                        badge_label = "MN" if "M" in sex else "FN"
                        sort_order = 2 if "M" in sex else 3
                    else:
                        badge_key = "AM"
                        badge_label = f"{klasse_str} {sex}"
                        sort_order = 8
                
                row_data = row.to_dict()
                row_data['_sort_kat'] = str(row.get('KATEGORIE', '9')).replace('.0', '')
                row_data['_sort_class'] = sort_order
                row_data['_sort_kat_nr'] = kat_nr_sort
                row_data['_badge_key'] = badge_key
                row_data['_badge_label'] = badge_label
                row_data['_clean_kat_nr'] = kat_nr_str
                row_data['_clean_klasse'] = klasse_str
                sorted_rows.append(row_data)
            
            df_sorted = pd.DataFrame(sorted_rows)
            if not df_sorted.empty:
                df_sorted = df_sorted.sort_values(by=['_sort_kat', '_sort_class', '_sort_kat_nr']).reset_index(drop=True)
                grouped = df_sorted.groupby(['_sort_kat', '_sort_class'])
                
                is_first_page = True
                for (kat_name, class_idx), group in grouped:
                    if not is_first_page:
                        c.showPage()
                    is_first_page = False
                    
                    count = 0
                    for _, row in group.iterrows():
                        if count > 0 and count % 8 == 0:
                            c.showPage()
                            
                        page_idx = count % 8
                        col = page_idx % 2
                        row_idx = page_idx // 2
                        
                        x = margin_left + (col * label_width)
                        y = (297 * mm) - margin_top - ((row_idx + 1) * label_height)
                        
                        kat_nr = row['_clean_kat_nr']
                        kategorie = row['_sort_kat']
                        badge_label = row['_badge_label']
                        badge_bg = color_map.get(row['_badge_key'], colors.HexColor("#99cc00"))
                        
                        rasse = str(row.get('RASSE', ''))
                        farbe = str(row.get('FARBE', ''))
                        ems_code = f"{rasse} {farbe}".strip()
                        
                        geb_cols = [col for col in row.index if "GEB" in col or "GEBURT" in col]
                        geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', '-')
                        if isinstance(geb_datum, pd.Timestamp):
                            geb_datum = geb_datum.strftime('%d.%m.%Y')
                        
                        c.saveState()
                        c.setStrokeColor(colors.HexColor("#e5e5e5"))
                        c.setLineWidth(0.2)
                        c.rect(x, y, label_width, label_height)
                        
                        c.setFont("Helvetica", 14)
                        c.setFillColor(colors.black)
                        c.drawString(x + 6*mm, y + label_height - 10*mm, kategorie)
                        
                        badge_w = 22 * mm
                        badge_h = 6 * mm
                        bx = x + label_width - badge_w - 6*mm
                        by = y + label_height - 11*mm
                        
                        c.setFillColor(badge_bg)
                        c.rect(bx, by, badge_w, badge_h, fill=1, stroke=0)
                        
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica-Bold", 11)
                        c.drawCentredString(bx + (badge_w / 2), by + 1.8*mm, badge_label)
                        
                        c.setFont("Helvetica", 46)
                        c.drawCentredString(x + (label_width / 2), y + (label_height / 2) - 4*mm, kat_nr)
                        
                        c.setFont("Helvetica", 12)
                        c.drawString(x + 6*mm, y + 10*mm, ems_code)
                        
                        c.setFont("Helvetica", 12)
                        c.drawRightString(x + label_width - 6*mm, y + 10*mm, str(geb_datum))
                        c.restoreState()
                        count += 1
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()

        # Tabs für die Tagestrennung
        tab_tag1, tab_tag2 = st.tabs(["Tag 1 (Samstag)", "Tag 2 (Sonntag)"])
        
        # =====================================================================
        # TAB FÜR TAG 1 (SAMSTAG)
        # =====================================================================
        with tab_tag1:
            if not df_samstag_daten.empty:
                st.info(f"Aktuell sind **{len(df_samstag_daten)}** Katzen für den Labeldruck an Tag 1 bereit.")
                
                pdf_labels_t1 = generate_avery_labels(df_samstag_daten.copy())
                st.download_button(
                    label="📥 Avery Zweckform PDF generieren & herunterladen (Tag 1)",
                    data=pdf_labels_t1,
                    file_name="KECB_Nomination_Labels_Sorted_Tag1.pdf",
                    mime="application/pdf",
                    key="dl_btn_t1"
                )
                
                st.write("### Vorschau der enthaltenen Katzen (Tag 1):")
                spalten_t1 = [c for c in ['KAT_STR', 'KATEGORIE', 'KLASSE_INTERNAL', 'GESCHLECHT', 'RASSE', 'FARBE'] if c in df_samstag_daten.columns]
                namen_t1 = {"KAT_STR": "Kat.-Nr.", "KATEGORIE": "Kategorie", "KLASSE_INTERNAL": "Klasse", "GESCHLECHT": "Geschlecht", "RASSE": "Rasse", "FARBE": "Farbe"}
                config_t1 = {c: namen_t1[c] for c in spalten_t1 if c in namen_t1}
                
                # Hier sortieren wir die Daten direkt im Aufruf mit reinen Leerzeichen für die Einrückung
                st.dataframe(df_samstag_daten[spalten_t1].sort_values(by='KAT_STR', key=lambda x: pd.to_numeric(x, errors='coerce')), column_config=config_t1, use_container_width=True, hide_index=True, key="preview_table_samstag_final")
                
            else:
                st.info("Aktuell sind keine Katzen für den Labeldruck an Tag 1 (Spalte 'SELECTION 1') bereit.")

        # =====================================================================
        # TAB FÜR TAG 2 (SONNTAG)
        # =====================================================================
        with tab_tag2:
            if not df_sonntag_daten.empty:
                st.info(f"Aktuell sind **{len(df_sonntag_daten)}** Katzen für den Labeldruck an Tag 2 bereit.")
                
                pdf_labels_t2 = generate_avery_labels(df_sonntag_daten.copy())
                st.download_button(
                    label="📥 Avery Zweckform PDF generieren & herunterladen (Tag 2)",
                    data=pdf_labels_t2,
                    file_name="KECB_Nomination_Labels_Sorted_Tag2.pdf",
                    mime="application/pdf",
                    key="dl_btn_t2"
                )
                
                st.write("### Vorschau der enthaltenen Katzen (Tag 2):")
                
                # --- AB HIER ERSETZEN ---
                spalten_t2 = [c for c in ['KAT_STR', 'KATEGORIE', 'KLASSE_INTERNAL', 'GESCHLECHT', 'RASSE', 'FARBE'] if c in df_sonntag_daten.columns]
                namen_t2 = {"KAT_STR": "Kat.-Nr.", "KATEGORIE": "Kategorie", "KLASSE_INTERNAL": "Klasse", "GESCHLECHT": "Geschlecht", "RASSE": "Rasse", "FARBE": "Farbe"}
                config_t2 = {c: namen_t2[c] for c in spalten_t2 if c in namen_t2}
                
                # Wir erstellen die Struktur für die Anzeige (die künstliche Spalte 'TAG' wurde hier entfernt!)
                df_sonntag_vorschau = df_sonntag_daten[spalten_t2].copy()
                                
                # Hier sortieren wir die fertige Sonntag-Vorschau direkt beim Anzeigen
                st.dataframe(
                    df_sonntag_vorschau.sort_values(by='KAT_STR', key=lambda x: pd.to_numeric(x, errors='coerce')), 
                    column_config=config_t2, 
                    use_container_width=True, 
                    hide_index=True, 
                    key="voneinander_getrennte_sonntags_tabelle"
                )
                # --- BIS HIER ERSETZEN ---

                
            

                
            else:
                st.info("Aktuell sind keine Katzen für den Labeldruck an Tag 2 (Spalte 'SELECTION 2') bereit.")

            
        if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_labels"):
            set_view("Home")


# ADMIN PANEL
elif st.session_state.view == "Admin_Panel":
    display_header_with_logo("⚙️ Admin-Konsole")
    
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        store.active_overlay = None
        st.success("Speicher geleert!")

    # --- HIER IST DER NEUE BUTTON SAUBER EINIGERÜCKT ---
    st.markdown("---")  # Eine kleine Trennlinie für die Optik
    st.subheader("🔄 Excel-Cache")
    st.write("Die Excel-Datei wird automatisch alle 10 Minuten neu eingelesen. Hier kannst du das Laden sofort erzwingen:")
    
    if st.button("🔥 Excel-Daten JETZT sofort neu einlesen", key="clear_cache_button"):
        load_labels.clear()  # Löscht den 10-Minuten-Cache sofort
        st.success("Der Cache wurde geleert! Die Excel-Datei wird beim nächsten Aufruf frisch geladen.")
        st.rerun()
    st.markdown("---")
        
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_admin"):
        set_view("Home")

		



# ==============================================================================
# NEUER MENÜPUNKT: TEST LIVE-VOTING (RICHTER)
# ==============================================================================
elif st.session_state.view == "Test_Live_Voting":
    display_header_with_logo("🗳️  Judge Live Voting")
   
    df_full = load_labels()
    if df_full is not None:
        # AUTOMATISCHE TAGES-SYNCHRONISATION
        global_admin_day = st.session_state.get("admin_selected_day", "Tag 1")
        st.session_state["judge_day_selector"] = global_admin_day
        st.sidebar.info(f"📅 Aktiver Ausstellungstag: {global_admin_day}")
        tag = global_admin_day.upper()
        
        r_col = f"RICHTER {tag}"
        all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        
        # 1. LIVE-WERTE AUS DEM TEST-ADMIN AUSLESEN
        active_cat = store.data.get("test_live_cat")
        active_label = store.data.get("test_live_label")
        
        # 2. WENN NOCH KEIN HÄKCHEN IM TEST-ADMIN GESETZT WURDE -> WARTE-BILDSCHIRM
        if not active_cat or not active_label:
            st.info("⏳ **Bitte warten...** Die Ausstellungsleitung hat für den Test aktuell noch keine Abstimmungsrunde freigeschaltet. Please wait, the Admin will release the voting shortly.")
            st.stop()
            
        # 3. GELBER LIVE-BANNER FÜR DEN RICHTER
        st.markdown(
            f"<div style='background-color:#fff3cd; padding:15px; border-radius:8px; border-left:5px solid #ffc107; margin-bottom:20px;'>"
            f"📢 <b>AKTIVE RUNDE - ACTIVE ROUND:</b><br>"
            f"<span style='font-size:20px; color:#856404;'><b>Kategorie - Category {active_cat} — {active_label}</b></span>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        # Richter-Identität ermitteln (entweder via URL oder Box)
        c1, _ = st.columns([2, 2])
        url_judge_name = st.session_state.get("url_judge", "--")
        
        if url_judge_name in all_judges and st.session_state.user_role != "Admin":
            active_j = url_judge_name
            c1.markdown(f"<div><b>Eingeloggt als Richter - Logged in as:</b> <span style='color:#1a4a9e; font-size:18px;'>{active_j}</span></div>", unsafe_allow_html=True)
        else:
            active_j = c1.selectbox("Identität/Identity wählen:", ["--"] + all_judges, key="test_live_vote_j_box")

        # Wenn ein Richter gewählt/eingeloggt ist, zeigen wir EXKLUSIV die eine aktive Klasse
        if active_j != "--":
            # ÄNDERUNG: SICHERSTELLEN, DASS DER VOTES-KEY IM SPEICHER EXISTIERT
            if "votes" not in store.data or not isinstance(store.data["votes"], dict): 
                store.data["votes"] = {}
                
            bis_defs = [
                ("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), 
                ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), 
                ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), 
                ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")
            ]
            
            for label, klassen, geschl in bis_defs:
                # DIE MAGISCHE WEICHE: NUR WENN ES DIE VOM TEST-ADMIN FREIGEGEBENE KLASSE IST!
                if label == active_label:
                    with st.expander(f"Wahl für/Choice for {label}", expanded=True):
                        pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == active_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        
                        if not pool.empty:
                            # --------------------------------------------------
                            # 1. DETAIL-ERMITTLUNG (SCHLEIFE FÜR DATUM & GESCHLECHT)
                            # --------------------------------------------------
                            opts = {}
                            for _, r in pool.iterrows():
                                # Geburtsdatum-Spalte flexibel ermitteln
                                geb_cols = [c for c in r.index if "GEB" in str(c) or "GEBURT" in str(c)]
                                geb_datum = r[geb_cols[0]] if geb_cols else r.get('GEB_DATUM', 'N/A')
                                
                                # Datum formatieren, falls es ein Timestamp ist
                                if isinstance(geb_datum, pd.Timestamp):
                                    geb_datum = geb_datum.strftime('%d.%m.%Y')
                                elif pd.isna(geb_datum) or str(geb_datum).strip().lower() == "nan":
                                    geb_datum = "N/A"
                                
                                geschlecht_val = r.get('GESCHLECHT', 'N/A')
                                rasse_gruppe = get_full_label(r)
                                
                                # Label für den Radio-Button zusammenbauen
                                full_option_text = f"#{r['KAT_STR']} - {rasse_gruppe} [{geschlecht_val}, *{geb_datum}]"
                                
                                # Strukturiert speichern für die spätere Anzeige in der Box
                                opts[full_option_text] = {
                                    "kat_nr": r['KAT_STR'],
                                    "details": f"{rasse_gruppe} [{geschlecht_val}, *{geb_datum}]"
                                }
                            
                            v_key = f"v_{tag}_{active_cat}_{label}_{active_j}"
                            curr_raw = store.data["votes"].get(v_key, "Keine Wahl")
                            
                            # Extrahiere die reine Kat-Nummer, egal ob Dict oder String geliefert wird
                            if isinstance(curr_raw, dict):
                                curr = curr_raw.get("katze", "Keine Wahl")
                            else:
                                curr = curr_raw
                            
                            # --------------------------------------------------
                            # 2. DEINE ABSTURZ-SICHERUNG
                            # --------------------------------------------------
                            default_index = 0
                            current_option_text = "Keine Wahl/Not chosen yet"
                            
                            try:
                                # Reine Katalognummern für die Index-Suche extrahieren
                                pure_numbers = [info["kat_nr"] for info in opts.values()]
                                if curr in pure_numbers:
                                    default_index = pure_numbers.index(curr) + 1
                                    current_option_text = list(opts.keys())[default_index - 1]
                            except (ValueError, IndexError):
                                default_index = 0
                                current_option_text = "Keine Wahl/Not chosen yet"

                            # --------------------------------------------------
                            # 4. RADIO-BUTTON & SPEICHER-LOGIK
                            # --------------------------------------------------
                            # Hilfsfunktion: Feuert live bei Klick und setzt den Status zurück!
                            def on_radio_change():
                                current_radio_val = st.session_state[f"r_test_{v_key}"]
                                if current_radio_val != "Keine Wahl/Not chosen yet":
                                    kat_nummer = opts[current_radio_val]["kat_nr"]
                                    # Bei jeder Änderung überschreiben wir die Bestätigung und setzen zurück auf "wählt"
                                    store.data["votes"][v_key] = {
                                        "katze": kat_nummer,
                                        "status": "wählt"
                                    }
                                else:
                                    store.data["votes"][v_key] = "Keine Wahl/Not chosen yet"
                                store.save_backup()
                                # ÄNDERUNG: Sofortiger Rerun, damit Admin und Banner die Änderung live registrieren!
                                st.rerun()

                            # Radio-Button steuert den Live-Zustand an
                            sel = st.radio(
                                "Favorit wählen / Choose favorite:", 
                                ["Keine Wahl/Not chosen yet"] + list(opts.keys()), 
                                index=default_index, 
                                key=f"r_test_{v_key}",
                                on_change=on_radio_change
                            )

                            # --------------------------------------------------
                            # 3. GEWÄHLTE KATZE GROSS ANZEIGEN (REAKTIV)
                            # --------------------------------------------------
                            if sel != "Keine Wahl/Not chosen yet" and sel in opts:
                                selected_data = opts[sel]
                                
                                # Status ermitteln
                                current_status = "wählt"
                                if isinstance(store.data["votes"].get(v_key), dict):
                                    current_status = store.data["votes"][v_key].get("status", "wählt")
                                
                                if current_status == "bestaerkt":
                                    banner_title = "✅ BESTÄTIGTE STIMME / CONFIRMED VOTE:"
                                    bg_color = "#d4edda" # Grün
                                    border_color = "#28a745"
                                    text_color = "#155724"
                                else:
                                    banner_title = "⏳ AUSGEWÄHLT (NOCH NICHT BESTÄTIGT) / SELECTED (NOT CONFIRMED YET):"
                                    bg_color = "#fff3cd" # Gelb/Orange
                                    border_color = "#ffc107"
                                    text_color = "#856404"

                                st.markdown(
                                    f"<div style='background-color:{bg_color}; padding:15px; border-radius:8px; border-left:5px solid {border_color}; margin-bottom:20px; text-align:center; color:{text_color};'>"
                                    f"<div style='font-size:14px; text-transform:uppercase; letter-spacing:1px; font-weight:bold;'>{banner_title}</div>"
                                    f"<div style='font-size:54px; font-weight:900; line-height:1; margin:10px 0;'>#{selected_data['kat_nr']}</div>"
                                    f"<div style='font-size:16px; font-weight:500;'>{selected_data['details']}</div>"
                                    f"</div>", 
                                    unsafe_allow_html=True
                                )
                            else:
                                # Neutrale Graubox, wenn noch nichts gewählt wurde
                                st.markdown(
                                    f"<div style='background-color:#e2e3e5; padding:12px; border-radius:8px; border-left:5px solid #6c757d; margin-bottom:20px; text-align:center; color:#383d41; font-style:italic;'>"
                                    f"Noch keine Stimme abgegeben / No vote cast yet."
                                    f"</div>", 
                                    unsafe_allow_html=True
                                )
                            
                            # Bestätigungs-Button wird nur eingeblendet, wenn eine Katze gewählt ist
                            if sel != "Keine Wahl/Not chosen yet":
                                st.write("") 
                                if st.button("🚀 Stimme offiziell bestätigen / Confirm Vote", key=f"btn_confirm_{v_key}", use_container_width=True):
                                    finale_katze = opts[sel]["kat_nr"]
                                    
                                    store.data["votes"][v_key] = {
                                        "katze": finale_katze,
                                        "status": "bestaerkt"
                                    }
                                    store.save_backup()
                                    st.success(f"Katze #{finale_katze} erfolgreich bestätigt!")
                                    st.rerun()
                        else:
                            st.info("ℹ️ Keine nominierten Katzen in dieser Klasse vorhanden.")

# ==============================================================================
# NEUER SEPARATER MENÜPUNKT: 🎛️ [Test] Live-Admin
# ==============================================================================
elif st.session_state.view == "Test_Live_Admin":
    # --- AUTOMATISCHER REFRESH FÜR ECHTEZEIT-ANZEIGE ---
    # Aktualisiert das Admin-Panel alle 2000 Millisekunden (2 Sekunden) von selbst.
    # Da wir nur das RAM abfragen, ist das extrem performant und flackerfrei!
    st_autorefresh(interval=2000, key="live_admin_auto_refresh")

    display_header_with_logo("👑 BIS Admin Control")
    df_full = load_labels()
    
    if df_full is not None:
        # --- HIER DIE NEUE RADIO-BOX FÜR DIE TAGE EINFÜGEN ---
        admin_tag = st.radio("Ausstellungstag verwalten:", ["Tag 1", "Tag 2"], horizontal=True, key="admin_day_selector").upper()
        
        # Spaltenname dynamisch bestimmen (SELECTION 1 oder SELECTION 2)
        sel_col = f"SELECTION {admin_tag.replace('TAG ', '')}"
        
        # Wir überschreiben temporär im geladenen Dataframe die 'SELECTION' Spalte,
        # damit alle nachfolgenden Filter im originalen Code (pool = df_full[df_full['SELECTION']...]) unverändert weiterlaufen!
        if sel_col in df_full.columns:
            df_full['SELECTION'] = df_full[sel_col]
        # -----------------------------------------------------

    if df_full is not None:
        # Auch die Kategorie-Auswahl braucht einen tagesabhängigen Key
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()), key=f"admin_sel_cat_{admin_tag}")
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        
        for label, klassen, geschl in bis_defs:
            # Der Expander-Key wird tagesabhängig, damit der Auf-/Zuklapp-Status nicht vermischt wird
            with st.expander(f"KLASSE: {label} ({admin_tag})", expanded=True):
                c_ctrl, c_votes = st.columns([1, 1.2])
                
                # Der v_prefix enthält jetzt den Tag, damit die Stimmen von Tag 1 und Tag 2 getrennt gesucht werden
                v_prefix = f"v_{admin_tag}_{sel_cat}_{label}_"
                
                with c_ctrl:
                    st.markdown("**Steuerung**")
                    
                    # Die Datenschlüssel im store.data erhalten den Tag, damit Werte getrennt gespeichert werden
                    key_reveal = f"reveal_{admin_tag}_{sel_cat}_{label}"
                    key_winner_reveal = f"winner_reveal_{admin_tag}_{sel_cat}_{label}"
                    key_override = f"override_{admin_tag}_{sel_cat}_{label}"
                    
                    # Die Widget-Keys (key=...) erhalten ebenfalls das admin_tag, was Streamlit zum sauberen Reset zwingt
                    store.data[key_reveal] = st.checkbox("Nominationen anzeigen", value=store.data.get(key_reveal, False), key=f"cb1_{key_reveal}")
                    store.data[key_winner_reveal] = st.checkbox("BIS Gewinner anzeigen", value=store.data.get(key_winner_reveal, False), key=f"cb2_{key_winner_reveal}")
                    
                    # --- ANFANG DER NEUEN ZUSÄTZLICHEN CHECKBOX ---
                    # HIER PRÜFEN WIR, OB DIESE KLASSE GERADE ALS AKTIVE TEST-RUNDE GESPEICHERT IST
                    is_live_now = (store.data.get("test_live_cat") == sel_cat) and (store.data.get("test_live_label") == label) and (store.data.get("test_live_tag") == admin_tag)
                    
                    activate_voting = st.checkbox("🟢 Diese Klasse für Richter freischalten (Live-Voting)", value=is_live_now, key=f"live_vote_{admin_tag}_{sel_cat}_{label}")
                    
                    if activate_voting:
                        store.data["test_live_cat"] = sel_cat
                        store.data["test_live_label"] = label
                        store.data["test_live_tag"] = admin_tag
                    elif is_live_now and not activate_voting:
                        store.data["test_live_cat"] = None
                        store.data["test_live_label"] = None
                        store.data["test_live_tag"] = None
                    # --- ENDE DER NEUEN ZUSÄTZLICHEN CHECKBOX ---
                    
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    options = ["Automatisch (Stimmen)"] + sorted(pool['KAT_STR'].unique().tolist())
                    
                    store.data[key_override] = st.selectbox(f"Gewinner festlegen:", options, index=options.index(store.data.get(key_override, "Automatisch (Stimmen)")) if store.data.get(key_override) in options else 0, key=f"sb_{key_override}")
                    
                    final_nr = None
                    if store.data[key_override] != "Automatisch (Stimmen)": 
                        final_nr = store.data[key_override]
                    elif "votes" in store.data:
                        # Für die automatische Ermittlung des Gewinners zählen NUR "bestaerkt" (bestätigte) Stimmen!
                        vts = []
                        for k, v in store.data["votes"].items():
                            if k.startswith(v_prefix) and v != "Keine Wahl" and v != "Keine Wahl/Not chosen yet":
                                if isinstance(v, dict) and v.get("status") == "bestaerkt":
                                    vts.append(v.get("katze"))
                                elif isinstance(v, str): # Kompatibilität für alte Plain-Strings
                                    vts.append(v)
                        if vts: 
                            final_nr = pd.Series(vts).value_counts().index[0]
                            
                    if final_nr and st.button(f"🏆 OVERLAY ZEIGEN (#{final_nr})", key=f"btn_ov_{admin_tag}_{sel_cat}_{label}"):
                        w_match = df_full[df_full['KAT_STR'] == str(final_nr)]
                        if not w_match.empty:
                            store.active_overlay = w_match.iloc[0].to_dict()
                            store.overlay_start_time = time.time()
                            if "local_overlay_end" in st.session_state:
                                st.session_state.local_overlay_end = 0
                        st.success(f"Overlay für #{final_nr} wurde gestartet!")
        
                with c_votes:
                    st.markdown("**Stimmen-Details**")
                    if "votes" in store.data:
                        rows = []
                        confirmed_votes_for_summary = []
                        
                        for k, v in store.data["votes"].items():
                            if k.startswith(v_prefix) and v != "Keine Wahl" and v != "Keine Wahl/Not chosen yet":
                                r_name = k.replace(v_prefix, "")
                                
                                # Struktur aufdröseln (Dict vs. Alt-String)
                                if isinstance(v, dict):
                                    kat_nr = v.get("katze", "N/A")
                                    status = v.get("status", "wählt")
                                else:
                                    kat_nr = v
                                    status = "bestaerkt" # Alte Einträge werten wir direkt als bestätigt
                                
                                # Status-Emoji bestimmen
                                status_emoji = "✅ Bestätigt" if status == "bestaerkt" else "⏳ Wählt..."
                                
                                rows.append({
                                    "Richter": r_name, 
                                    "Wahl (Kat Nr.)": f"#{kat_nr}",
                                    "Status": status_emoji
                                })
                                
                                # Für die mathematische Zusammenfassung zählen nur bestätigte Stimmen
                                if status == "bestaerkt":
                                    confirmed_votes_for_summary.append(kat_nr)
                        
                        if rows:
                            vote_df = pd.DataFrame(rows)
                            
                            # Schickes farbliches Highlight-Styling für die Tabelle (Grün für Bestätigt, Gelb für Entwurf)
                            def highlight_status(row):
                                if "✅" in str(row["Status"]):
                                    return ['background-color: #d4edda; color: #155724'] * len(row)
                                return ['background-color: #fff3cd; color: #856404'] * len(row)
                            
                            styled_df = vote_df.style.apply(highlight_status, axis=1)
                            st.dataframe(styled_df, use_container_width=True, hide_index=True)
                            
                            st.write("**Gezählte Zwischenstände (Nur bestätigte Stimmen):**")
                            if confirmed_votes_for_summary:
                                summary = pd.Series(confirmed_votes_for_summary).value_counts()
                                for nr, count in summary.items(): 
                                    st.write(f"Katze #{nr}: **{count} Stimme(n)**")
                            else:
                                st.info("Es wurden noch keine Stimmen final bestätigt.")
                                
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_bisadmin"):
        set_view("Home")
				
