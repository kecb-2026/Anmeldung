# -*- coding: utf-8 -*-

"""
Projekt: Cat Show Anmeldung des KECB Katzenausstellung
Copyright (c) 2026 Brigitte Portner
Alle Rechte vorbehalten
"""


import streamlit as st
import pandas as pd
import os
import requests
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, date

# Dateiname für das Speichern der Anmeldungen
EXCEL_FILE = "ausstellung_anmeldungen.xlsx"

# Unterstützt sowohl den Dateinamen deiner hochgeladenen CSV als auch Excel-Varianten
STAMMDATEN_DATEIEN = ["2026.xlsx - Sheet1.csv", "2026.xlsx", "katzen_stammdaten.xlsx"]

# Seite konfigurieren
st.set_page_config(page_title="FFH Ausstellungs-Anmeldung", layout="centered")

# --- INITIALISIERUNG SESSION STATE FÜR ADRESSEN & KATZEN-AUTOFILL ---
session_defaults = {
    # Aussteller / Besitzer
    'a_nachname': "",
    'a_vorname': "",
    'a_strasse': "",
    'a_plz_ort': "",
    'a_land': "Schweiz",
    # Katze
    'k_name': "",
    'k_ems': "",
    'k_gruppe': "",
    'k_rasse': "",
    'k_zuchtbuch': "",
    'k_chip': "",
    'k_geboren': date(2025, 1, 1),
    'k_geschlecht': "1.0 Männlich",
    'k_kastriert': "Nein",
    # Eltern
    'v_name': "", 'v_ems': "", 'v_zuchtbuch': "",
    'm_name': "", 'm_ems': "", 'm_zuchtbuch': ""
}

for key, val in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Hilfsfunktion: Wandelt NaN-Werte aus der Excel/CSV in saubere Leerstrings um
def safe_str(wert):
    if pd.isna(wert):
        return ""
    text = str(wert).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text

# Extrem robuste Hilfsfunktion zum Extrahieren von reinen Ziffern
def extrahiere_ziffern(wert):
    if pd.isna(wert):
        return ""
    text = str(wert).strip()
    if text.endswith(".0"):
        text = text[:-2]
    elif "." in text:
        text = text.split(".")[0]
    return "".join(filter(str.isdigit, text))

# Automatischer Stammdaten-Lader (unterstützt Excel und CSV flexibel)
def lade_stammdaten():
    # Zuerst in der definierten Liste suchen
    for d in STAMMDATEN_DATEIEN:
        if os.path.exists(d):
            if d.endswith(".xlsx"):
                try:
                    return pd.read_excel(d), d
                except Exception as e:
                    print(f"Fehler beim Laden der Excel {d}: {e}")
            elif d.endswith(".csv"):
                for sep in [";", ","]:
                    try:
                        return pd.read_csv(d, sep=sep, encoding="utf-8"), d
                    except:
                        try:
                            return pd.read_csv(d, sep=sep, encoding="latin-1"), d
                        except:
                            pass
                            
    # Falls nicht in der Liste, das Verzeichnis scannen
    dateien = os.listdir(".")
    for d in dateien:
        if d.startswith("2026") or "stammdaten" in d.lower():
            if d.endswith(".xlsx") and d not in STAMMDATEN_DATEIEN:
                try:
                    return pd.read_excel(d), d
                except Exception as e:
                    print(f"Fehler beim Laden der Excel {d}: {e}")
            elif d.endswith(".csv") and d not in STAMMDATEN_DATEIEN:
                for sep in [";", ","]:
                    try:
                        return pd.read_csv(d, sep=sep, encoding="utf-8"), d
                    except:
                        try:
                            return pd.read_csv(d, sep=sep, encoding="latin-1"), d
                        except:
                            pass
    return None, None

# Hilfsfunktion: Adresssuche
def suche_adresse(query):
    if not query or len(query) < 4: return []
    try:
        clean_query = query.replace(",", " ").strip()
        while "  " in clean_query: clean_query = clean_query.replace("  ", " ")
        encoded_query = urllib.parse.quote(clean_query)
        url = f"https://photon.komoot.io/api/?q={encoded_query}&limit=5&lang=de"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get('features', [])
            suggestions = []
            for item in results:
                props = item.get('properties', {})
                street, hnr, pc, city, country = props.get('street', ''), props.get('housenumber', ''), props.get('postcode', ''), props.get('city', ''), props.get('country', '')
                if street:
                    suggestions.append({
                        "label": f"{street} {hnr}, {pc} {city}, {country}".strip(", "),
                        "strasse_nr": f"{street} {hnr}".strip(),
                        "plz_ort": f"{pc} {city}".strip(),
                        "land": country
                    })
            return suggestions
    except Exception as e: print(f"Fehler bei Adresssuche: {e}")
    return []

# Hilfsfunktion: E-Mail-Versand
def sende_bestaetigungs_email(daten):
    try:
        smtp_server = st.secrets["smtp"]["server"]
        smtp_port = int(st.secrets["smtp"]["port"])
        smtp_user = st.secrets["smtp"]["user"]
        smtp_password = st.secrets["smtp"]["password"]
        sender_email = st.secrets["smtp"]["sender"]
    except Exception:
        st.warning("⚠️ E-Mail-Bestätigung konnte nicht gesendet werden (Secrets fehlen). Die Anmeldung wurde trotzdem gespeichert!")
        return False

    empfaenger = daten["Email"]
    kopie_verein = sender_email
    betreff = f"Anmeldebestätigung: {daten['Ausstellungsort']} - {daten['Katze_Name']}"
    
    inhalt = f"Guten Tag {daten['Aussteller_Vorname']} {daten['Aussteller_Nachname']}\n\nVielen Dank für Ihre Anmeldung. Hier sind Ihre Daten:\n\nKatze: {daten['Katze_Name']} ({daten['Katze_EMS']})\nKlasse: {daten['Angemeltete_Klasse']}\nZuchtbuch-Nr: {daten['Zuchtbuch_Nr']}\n\nFreundliche Grüsse\nIhr Ausstellungsteam"

    try:
        msg = MIMEText(inhalt, 'plain', 'utf-8')
        msg['Subject'] = Header(betreff, 'utf-8')
        msg['From'] = sender_email
        msg['To'] = empfaenger
        msg['Cc'] = kopie_verein
        server = smtplib.SMTP_SSL(smtp_server, smtp_port) if smtp_port == 465 else smtplib.SMTP(smtp_server, smtp_port)
        if smtp_port != 465: server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, [empfaenger, kopie_verein], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Senden der E-Mail: {e}")
        return False


st.title("🐾 Anmeldung zur Katzenausstellung")
st.markdown("### Fédération Féline Helvétique (FFH) / FIFe")

# --- 1. AUSSTELLUNGSDETAILS ---
st.subheader("1. Ausstellungsdetails")
ausstellungsort = st.text_input("Ausstellung in *", placeholder="z.B. Bern")

col_sat_chk, col_sat_date = st.columns([1, 2])
with col_sat_chk:
    st.write(""); st.write("")
    samstag_aktiv = st.checkbox("Samstag", value=True)
with col_sat_date:
    datum_samstag = st.date_input("Ausstellungstermin Samstag", value=date(2026, 10, 10), format="DD.MM.YYYY", disabled=not samstag_aktiv)

col_sun_chk, col_sun_date = st.columns([1, 2])
with col_sun_chk:
    st.write(""); st.write("")
    sonntag_aktiv = st.checkbox("Sonntag", value=False)
with col_sun_date:
    datum_sonntag = st.date_input("Ausstellungstermin Sonntag", value=date(2026, 10, 11), format="DD.MM.YYYY", disabled=not sonntag_aktiv)

gewaehlte_tage = []
if samstag_aktiv: gewaehlte_tage.append(f"Samstag ({datum_samstag.strftime('%d.%m.%Y')})")
if sonntag_aktiv: gewaehlte_tage.append(f"Sonntag ({datum_sonntag.strftime('%d.%m.%Y')})")
wochentag_export = ", ".join(gewaehlte_tage)


# --- 2. AUTOMATISCHER KATZEN- & AUSSTELLER-SUCHFILTER ---
st.subheader("2. Angaben zur Katze")

df_stamm, gefundener_dateiname = lade_stammdaten()

if df_stamm is not None:
    st.markdown("🔐 **Eintrag aus Vereinsdatenbank laden (Sichere Suche)**")
    st.info("Geben Sie Stammbuch-Nummer UND Nachname des Besitzers ein und klicken Sie auf 'Daten suchen'.")
    
    col_search_nr, col_search_name = st.columns(2)
    with col_search_nr:
        suche_zuchtbuch = st.text_input("Stammbuch-Nummer:", placeholder="z.B. 111951")
    with col_search_name:
        suche_nachname = st.text_input("Nachname des Besitzers:", placeholder="z.B. Ammann")
        
    if st.button("🔍 Daten suchen"):
        if suche_zuchtbuch and suche_nachname:
            such_ziffern = extrahiere_ziffern(suche_zuchtbuch)
            clean_nachname = str(suche_nachname).strip().lower()
            
            such_spalte_nr = 'Stammbuch-Nummer' if 'Stammbuch-Nummer' in df_stamm.columns else ('Zuchtbuch_Nr' if 'Zuchtbuch_Nr' in df_stamm.columns else None)
            such_spalte_name = 'Besitzer Nachname' if 'Besitzer Nachname' in df_stamm.columns else None
            
            if such_spalte_nr and such_spalte_name:
                df_stamm['Ziffern_Suche'] = df_stamm[such_spalte_nr].apply(extrahiere_ziffern)
                
                match = df_stamm[
                    (df_stamm['Ziffern_Suche'] == such_ziffern) & 
                    (df_stamm[such_spalte_name].astype(str).str.strip().str.lower() == clean_nachname)
                ]
                
                if not match.empty:
                    row = match.iloc[0]
                    neue_nr = safe_str(row.get(such_spalte_nr, ''))
                    
                    st.session_state.k_name = safe_str(row.get('Name', ''))
                    
                    rasse = safe_str(row.get('Rasse', ''))
                    farbe = safe_str(row.get('Farbe', ''))
                    st.session_state.k_ems = f"{rasse} {farbe}".strip() if rasse and farbe else rasse
                    
                    st.session_state.k_gruppe = safe_str(row.get('Farbgruppe', ''))
                    st.session_state.k_rasse = rasse
                    st.session_state.k_zuchtbuch = neue_nr
                    st.session_state.k_chip = safe_str(row.get('Chip-Nummer', ''))
                    
                    geb_datum = row.get('Geburtsdatum', '')
                    if pd.notna(geb_datum):
                        try:
                            if isinstance(geb_datum, str):
                                st.session_state.k_geboren = datetime.strptime(geb_datum.strip(), "%d.%m.%Y").date()
                            else:
                                st.session_state.k_geboren = pd.to_datetime(geb_datum).date()
                        except:
                            try:
                                st.session_state.k_geboren = pd.to_datetime(geb_datum).date()
                            except: pass
                    
                    geschlecht_raw = str(row.get('Geschlecht', '')).lower().strip()
                    if "w" in geschlecht_raw or "f" in geschlecht_raw or "0.1" in geschlecht_raw:
                        st.session_state.k_geschlecht = "0.1 Weiblich"
                    else:
                        st.session_state.k_geschlecht = "1.0 Männlich"
                        
                    kastriert_raw = str(row.get('Kastriert', '')).lower().strip()
                    if kastriert_raw in ["x", "ja", "yes", "1", "true", "kastrat", "k"]:
                        st.session_state.k_kastriert = "Ja"
                    else:
                        st.session_state.k_kastriert = "Nein"
                        
                    st.session_state.a_nachname = safe_str(row.get('Besitzer Nachname', ''))
                    st.session_state.a_vorname = safe_str(row.get('Besitzer Vorname', ''))
                    st.session_state.a_strasse = safe_str(row.get('Besitzer Adresse 1', ''))
                    
                    plz = safe_str(row.get('Besitzer PLZ', ''))
                    ort = safe_str(row.get('Besitzer Ort', ''))
                    st.session_state.a_plz_ort = f"{plz} {ort}".strip()
                    st.session_state.a_land = safe_str(row.get('Besitzer Land', 'Schweiz'))
                    
                    st.session_state.v_name = safe_str(row.get('Vater_Name', ''))
                    st.session_state.v_ems = safe_str(row.get('Vater_EMS', ''))
                    st.session_state.v_zuchtbuch = safe_str(row.get('Vater_Zuchtbuch', ''))
                    st.session_state.m_name = safe_str(row.get('Mutter_Name', ''))
                    st.session_state.m_ems = safe_str(row.get('Mutter_EMS', ''))
                    st.session_state.m_zuchtbuch = safe_str(row.get('Mutter_Zuchtbuch', ''))
                    
                    st.success(f"✅ Daten für '{st.session_state.k_name}' erfolgreich geladen!")
                    st.rerun()
                else:
                    st.warning("Keine Übereinstimmung für diese Stammbuch-Nummer und diesen Nachnamen gefunden.")
            else:
                st.error("Fehler bei den Spaltennamen der geladenen Datei!")
        else:
            st.error("Bitte füllen Sie beide Suchfelder aus!")
else:
    st.info("Hinweis: Laden Sie Ihre '2026.xlsx - Sheet1.csv' oder '2026.xlsx' auf GitHub hoch, um die automatische Ausfüll-Funktion freizuschalten.")

# --- Eingabefelder für die Katze ---
col3, col4 = st.columns([2, 1])
katze_name = col3.text_input("Titel + Name der Katze *", value=st.session_state.k_name)
katze_ems = col4.text_input("EMS-Code *", value=st.session_state.k_ems, placeholder="z.B. NFO n 22")

col5, col6 = st.columns([1, 2])
katze_gruppe = col5.text_input("Gruppe / Farbgruppe", value=st.session_state.k_gruppe)
katze_rasse_farbe = col6.text_input("Rasse + Farbe *", value=st.session_state.k_rasse, placeholder="z.B. Norwegische Waldkatze")

col7, col8 = st.columns(2)
katze_zuchtbuch = col7.text_input("Zuchtbuch-Nr. / Pedigree-No. *", value=st.session_state.k_zuchtbuch)
katze_chip = col8.text_input("Chip-Nr. (falls vor 1.1.23 geboren)", value=st.session_state.k_chip)

col9, col10, col11 = st.columns([2, 2, 1])
with col9:
    katze_geboren = st.date_input("Geburtsdatum *", value=st.session_state.k_geboren, max_value=datetime.today(), format="DD.MM.YYYY")
with col10:
    g_index = 0 if "Männlich" in st.session_state.k_geschlecht else 1
    katze_geschlecht = st.radio("Geschlecht *", ["1.0 Männlich", "0.1 Weiblich"], index=g_index)
with col11:
    kast_index = 0 if st.session_state.k_kastriert == "Ja" else 1
    katze_kastriert = st.radio("Kastrat? *", ["Ja", "Nein"], index=kast_index)

# Dynamische Klassenfilterung mit "-" als standardmäßigen Platzhalter
gemeinsame_klassen = ["11. Klasse 8-12 Monate", "12. Klasse 4-8 Monate", "13a. Novizenklasse", "13b. Kontrollklasse", "13c. Bestimmungsklasse", "14. Hauskatze", "15. Ausser Konkurrenz"]
if katze_kastriert == "Ja":
    klassen_optionen = ["-", "2. Supreme Premior - PH", "4. Gr. Int. Premior - CAPS", "6. International Premior - CAGPIB", "8. Premior - CAPIB", "10. Kastraten (Neuter) - CAP"] + gemeinsame_klassen
else:
    klassen_optionen = ["-", "1. Supreme Champion - PH", "3. Gr. Int. Champion - CACS", "5. International Champion - CAGCIB", "7. Champion - CACIB", "9. Offene Klasse (Open) - CAC"] + gemeinsame_klassen

ausstellungsklasse = st.selectbox("Klasse für die gemeldet wird *", klassen_optionen)
katze_gewicht = st.text_input("Gewicht der Katze (kg)", placeholder="z.B. 4.5")
bereits_erhalten = st.text_input("Bereits erhalten in / Point obtenu à l'exposition de")


# --- 3. STAMMBAUM (ELTERN) ---
# Bereich wird ausgeblendet, wenn bereits eine Zuchtbuch-Nr im Session State existiert
if not st.session_state.k_zuchtbuch:
    with st.container():
        st.subheader("3. Stammbaum (Eltern)")
        st.markdown("**Vater**")
        col_v1, col_v2, col_v3 = st.columns([2, 1, 1])
        vater_name = col_v1.text_input("Name des Vaters *", value=st.session_state.v_name)
        vater_ems = col_v2.text_input("EMS-Code Vater *", value=st.session_state.v_ems)
        vater_zuchtbuch = col_v3.text_input("Zuchtbuch-Nr. Vater *", value=st.session_state.v_zuchtbuch)

        st.markdown("**Mutter**")
        col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
        mutter_name = col_m1.text_input("Name der Mutter *", value=st.session_state.m_name)
        mutter_ems = col_m2.text_input("EMS-Code Mutter *", value=st.session_state.m_ems)
        mutter_zuchtbuch = col_m3.text_input("Zuchtbuch-Nr. Mutter *", value=st.session_state.m_zuchtbuch)
else:
    # Falls Daten geladen wurden, müssen die Variablen für den Absende-Prozess trotzdem existieren
    vater_name = st.session_state.v_name
    vater_ems = st.session_state.v_ems
    vater_zuchtbuch = st.session_state.v_zuchtbuch
    mutter_name = st.session_state.m_name
    mutter_ems = st.session_state.m_ems
    mutter_zuchtbuch = st.session_state.m_zuchtbuch


# --- 4. AUSSTELLER & ZÜCHTER ---
st.subheader("4. Aussteller & Züchter")

if not st.session_state.a_strasse:
    st.markdown("🔍 **Schnell-Eingabe der Adresse**")
    suchanfrage = st.text_input("Suchen Sie nach Ihrer Strasse, PLZ oder Ort...", placeholder="z.B. Schulhausstrasse 22 Moosseedorf")
    if len(suchanfrage) >= 4:
        ergebnisse = suche_adresse(suchanfrage)
        if ergebnisse:
            options = ["-- Bitte wählen --"] + [r["label"] for r in ergebnisse]
            auswahl_label = st.selectbox("Gefundene Adressen:", options)
            if auswahl_label != "-- Bitte wählen --":
                gewaehlt = next(item for item in ergebnisse if item["label"] == auswahl_label)
                st.session_state.a_strasse = gewaehlt["strasse_nr"]
                st.session_state.a_plz_ort = gewaehlt["plz_ort"]
                st.session_state.a_land = gewaehlt["land"]
                st.success("Adresse wurde eingetragen!")

st.markdown("---")
col12, col13 = st.columns(2)
aussteller_nachname = col12.text_input("Nachname (Aussteller) *", value=st.session_state.a_nachname)
aussteller_vorname = col13.text_input("Vorname (Aussteller) *", value=st.session_state.a_vorname)

col14, col15 = st.columns([2, 1])
aussteller_strasse = col14.text_input("Strasse, Nr. *", value=st.session_state.a_strasse)
aussteller_ort = col15.text_input("PLZ + Ort *", value=st.session_state.a_plz_ort)

col16, col17 = st.columns(2)
aussteller_land = col16.text_input("Land *", value=st.session_state.a_land)
aussteller_telefon = col17.text_input("Telefon *")
aussteller_email = st.text_input("E-Mail-Adresse *")

col18, col19 = st.columns([2, 1])
aussteller_verein = col18.text_input("Mitglied bei (Katzclub/Verein) *")
aussteller_mitgliedsnr = col19.text_input("Mitglieds-Nr.")
zuechter_name_land = st.text_input("Züchter + Land *")


# --- 5. BEMERKUNGEN & BESTÄTIGUNG ---
st.subheader("5. Bemerkungen & Einverständnis")
doppelkafig = st.text_input("Doppelkäfig zusammen mit folgenden Katze(n)")
bemerkungen = st.text_area("Bemerkungen / Commentaires")
agb_akzeptiert = st.checkbox("Ich bestätige die Richtigkeit der Angaben und akzeptiere die FIFé/FFH Regeln. *")


# --- ABSENDEN LOGIK ---
if st.button("Anmeldung verbindlich absenden", type="primary"):
    if not (ausstellungsort and katze_name and aussteller_nachname and aussteller_email and agb_akzeptiert):
        st.error("Bitte füllen Sie alle Pflichtfelder (*) aus.")
    elif ausstellungsklasse == "-":
        # Blockiert das Absenden, wenn die Klasse nicht gewählt wurde
        st.error("Bitte wählen Sie eine Ausstellungsklasse für Ihre Katze aus!")
    elif not (samstag_aktiv or sonntag_aktiv):
        st.error("Bitte wählen Sie mindestens einen Ausstellungstag aus.")
        else:
        neue_anmeldung = {
            "Eingangsdatum": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "Ausstellungsort": ausstellungsort, 
            "Angemeldete_Tage": wochentag_export,
            "Katze_Name": katze_name, 
            "Katze_EMS": katze_ems, 
            "Gruppe": katze_gruppe, 
            "Rasse_Farbe": katze_rasse_farbe,
            "Zuchtbuch_Nr": katze_zuchtbuch, 
            "Chip_Nr": katze_chip, 
            "Geburtsdatum": katze_geboren.strftime("%d.%m.%Y"),
            "Geschlecht": katze_geschlecht, 
            "Kastrat": katze_kastriert, 
            "Angemeldete_Klasse": ausstellungsklasse,
            "Gewicht": katze_gewicht, 
            "Bereits_Erhalten": bereits_erhalten,
            "Vater_Name": vater_name, 
            "Vater_EMS": vater_ems, 
            "Vater_Zuchtbuch": vater_zuchtbuch,
            "Mutter_Name": mutter_name, 
            "Mutter_EMS": mutter_ems, 
            "Mutter_Zuchtbuch": mutter_zuchtbuch,
            "Aussteller_Nachname": aussteller_nachname, 
            "Aussteller_Vorname": aussteller_vorname,
            "Strasse": aussteller_strasse, 
            "PLZ_Ort": aussteller_ort, 
            "Land": aussteller_land,
            "Telefon": aussteller_telefon, 
            "Email": aussteller_email, # <--- WICHTIG: Das hier ist der Key, den die E-Mail-Funktion sucht
            "Verein": aussteller_verein,
            "MitgliedsNr": aussteller_mitgliedsnr, 
            "Zuechter": zuechter_name_land, 
            "Doppelkafig": doppelkafig, 
            "Bemerkungen": bemerkungen
        }
        
        # ... Rest des Codes bleibt gleich

        df_neu = pd.DataFrame([neue_anmeldung])
        if os.path.exists(EXCEL_FILE):
            df_gesamt = pd.concat([pd.read_excel(EXCEL_FILE), df_neu], ignore_index=True)
        else:
            df_gesamt = df_neu
        df_gesamt.to_excel(EXCEL_FILE, index=False)
        
        sende_bestaetigungs_email(neue_anmeldung)
        st.success("🎉 Anmeldung erfolgreich gespeichert und Bestätigung versendet!")
        st.balloons()


# --- 6. ADMIN-BEREICH ---
st.markdown("---")
with st.expander("🔐 Admin-Bereich (Anmeldungen herunterladen)"):
    admin_passwort = st.text_input("Admin-Passwort eingeben", type="password")
    if admin_passwort == "ffh2026":
        if os.path.exists(EXCEL_FILE):
            with open(EXCEL_FILE, "rb") as f:
                st.download_button(label="📥 Excel-Tabelle herunterladen (.xlsx)", data=f.read(), file_name="ausstellung_anmeldungen.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.dataframe(pd.read_excel(EXCEL_FILE))
        else: st.info("Keine Anmeldungen vorhanden.")
    elif admin_passwort: st.error("Ungültiges Passwort!")
