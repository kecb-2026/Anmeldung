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
from dateutil.relativedelta import relativedelta

# Dateiname für das Speichern der Anmeldungen
EXCEL_FILE = "ausstellung_anmeldungen.xlsx"

# Unterstützt sowohl den Dateinamen deiner hochgeladenen CSV als auch Excel-Varianten
STAMMDATEN_DATEIEN = [
    "2026.xlsx - Sheet1.csv",
    "2026.xlsx",
    "katzen_stammdaten.xlsx"
]

# Seite konfigurieren
st.set_page_config(
    page_title="FFH Ausstellungs-Anmeldung",
    layout="centered"
)

# --- INITIALISIERUNG SESSION STATE FÜR ADRESSEN & KATZEN-AUTOFILL ---
session_defaults = {
    'a_nachname': "",
    'a_vorname': "",
    'a_strasse': "",
    'a_plz_ort': "",
    'a_land': "Schweiz",
    'k_name': "",
    'k_ems': "",
    'k_gruppe': "",
    'k_rasse': "",
    'k_zuchtbuch': "",
    'k_chip': "",
    'k_geboren': date(2025, 1, 1),
    'k_geschlecht': "1.0 Männlich",
    'k_kastriert': "Nein",
    'v_name': "",
    'v_ems': "",
    'v_zuchtbuch': "",
    'm_name': "",
    'm_ems': "",
    'm_zuchtbuch': "",
    'z_zuechter': ""
}

for key, val in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

def safe_str(wert):
    if pd.isna(wert):
        return ""
    text = str(wert).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text

def extrahiere_ziffern(wert):
    if pd.isna(wert):
        return ""
    text = str(wert).strip()
    if text.endswith(".0"):
        text = text[:-2]
    elif "." in text:
        text = text.split(".")[0]
    return "".join(filter(str.isdigit, text))

def lade_stammdaten():
    for d in STAMMDATEN_DATEIEN:
        if os.path.exists(d):
            if d.endswith(".xlsx"):
                try:
                    return pd.read_excel(d), d
                except Exception as e:
                    print(f"Fehler: {e}")
            elif d.endswith(".csv"):
                for sep in [";", ","]:
                    try:
                        return pd.read_csv(d, sep=sep, encoding="utf-8"), d
                    except:
                        try:
                            return pd.read_csv(d, sep=sep, encoding="latin-1"), d
                        except:
                            pass
    dateien = os.listdir(".")
    for d in dateien:
        if d.startswith("2026") or "stammdaten" in d.lower():
            if d.endswith(".xlsx") and d not in STAMMDATEN_DATEIEN:
                try:
                    return pd.read_excel(d), d
                except:
                    pass
            elif d.endswith(".csv") and d not in STAMMDATEN_DATEIEN:
                for sep in [";", ","]:
                    try:
                        return pd.read_csv(d, sep=sep, encoding="utf-8"), d
                    except:
                        pass
    return None, None

def suche_adresse(query):
    if not query or len(query) < 4:
        return []
    try:
        clean_query = query.replace(",", " ").strip()
        while "  " in clean_query:
            clean_query = clean_query.replace("  ", " ")
        encoded_query = urllib.parse.quote(clean_query)
        url = f"https://photon.komoot.io/api/?q={encoded_query}&limit=5&lang=de"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get('features', [])
            suggestions = []
            for item in results:
                props = item.get('properties', {})
                street = props.get('street', '')
                hnr = props.get('housenumber', '')
                pc = props.get('postcode', '')
                city = props.get('city', '')
                country = props.get('country', '')
                if street:
                    suggestions.append({
                        "label": f"{street} {hnr}, {pc} {city}, {country}".strip(", "),
                        "strasse_nr": f"{street} {hnr}".strip(),
                        "plz_ort": f"{pc} {city}".strip(),
                        "land": country
                    })
            return suggestions
    except Exception as e:
        print(f"Fehler: {e}")
    return []

def pruefe_alter_warnung(geb, kl, datum_sa, datum_so, samstag_aktiv, sonntag_aktiv):
    if kl == "-" or kl == "15. Ausser Konkurrenz":
        return None, ""

    def get_monate(tag):
        monate = (tag.year - geb.year) * 12 + (tag.month - geb.month)
        if tag.day < geb.day:
            monate -= 1
        return monate

    monate_sa = get_monate(datum_sa) if samstag_aktiv else None
    monate_so = get_monate(datum_so) if sonntag_aktiv else None
    
    hinweis_umwertung = ""

    # Erwachsenenklassen (1-10): Punktgenau ab dem 12. Geburtstag (12 Monate)
    erwachsenen_klassen = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    if any(kl.startswith(prefix) for prefix in erwachsenen_klassen):
        if samstag_aktiv and monate_sa < 12:
            return f"Die Katze ist am Samstag erst {monate_sa} Monate alt. In die Erwachsenenklassen (1-10) darf sie erst ab exakt 12 Monaten gemeldet werden.", ""
        if sonntag_aktiv and monate_so < 12:
            return f"Die Katze ist am Sonntag erst {monate_so} Monate alt. In die Erwachsenenklassen (1-10) darf sie erst ab exakt 12 Monaten gemeldet werden.", ""

    # Klasse 11 (Jugendklasse 8-12 Monate)
    if "11." in kl:
        if samstag_aktiv and monate_sa < 8:
            return f"Die Katze ist am Samstag erst {monate_sa} Monate alt. Mindestalter für Klasse 11 ist 8 Monate.", ""
        if samstag_aktiv and monate_sa >= 12:
            return f"Die Katze ist am Samstag bereits 12 Monate alt. Sie muss in eine Erwachsenenklasse gemeldet werden.", ""
        
        # Weiche für Geburtstag am Sonntag während des Ausstellungswochenendes
        if samstag_aktiv and sonntag_aktiv and monate_sa == 11 and monate_so >= 12:
            hinweis_umwertung = "HINWEIS: Katze vollendet am Sonntag das 12. Lebensmonat und MUSS für den Sonntag in die Erwachsenenklasse (Klasse 9) umgewertet werden!"

        if sonntag_aktiv and not samstag_aktiv and monate_so >= 12:
            return f"Die Katze ist am Sonntag bereits 12 Monate alt. Sie muss in eine Erwachsenenklasse gemeldet werden.", ""

    # Klasse 12 (Kittenklasse 4-8 Monate)
    if "12." in kl:
        if samstag_aktiv and monate_sa < 4:
            return f"Die Katze ist am Samstag erst {monate_sa} Monate alt. Mindestalter für Klasse 12 ist 4 Monate.", ""
        if samstag_aktiv and monate_sa >= 8:
            return f"Die Katze ist am Samstag bereits 8 Monate alt. Sie muss in die Klasse 11 gemeldet werden.", ""
        
        # Weiche für Geburtstag am Sonntag während des Ausstellungswochenendes
        if samstag_aktiv and sonntag_aktiv and monate_sa == 7 and monate_so >= 8:
            hinweis_umwertung = "HINWEIS: Katze vollendet am Sonntag das 8. Lebensmonat und MUSS für den Sonntag in die Klasse 11 umgewertet werden!"

        if sonntag_aktiv and not samstag_aktiv and monate_so >= 8:
            return f"Die Katze ist am Sonntag bereits 8 Monate alt. Sie muss in die Klasse 11 gemeldet werden.", ""

    return None, hinweis_umwertung

def sende_bestaetigungs_email(daten):
    try:
        smtp_server = st.secrets["smtp"]["server"]
        smtp_port = int(st.secrets["smtp"]["port"])
        smtp_user = st.secrets["smtp"]["user"]
        smtp_password = st.secrets["smtp"]["password"]
        sender_email = st.secrets["smtp"]["sender"]
    except Exception:
        return False
    
    empfaenger = daten.get("Email")
    if not empfaenger:
        return False
    kopie_verein = sender_email
    betreff = f"Anmeldebestätigung: {daten.get('Ausstellungsort', 'Ausstellung')} 2026 - {daten.get('Katze_Name', 'Katze')}"
    
    inhalt = (
        f"Guten Tag {daten.get('Aussteller_Vorname', '')} {daten.get('Aussteller_Nachname', '')}\n\n"
        f"Vielen Dank für Ihre Anmeldung. Hier sind die eingegebenen Daten:\n\n"
        f"--- KATZENDETAILS ---\n"
        f"Name: {daten.get('Katze_Name', '')} ({daten.get('Katze_EMS', '')})\n"
        f"Zuchtbuch-Nr: {daten.get('Zuchtbuch_Nr', '')}\n"
        f"Geburtsdatum: {daten.get('Geburtsdatum', '')}\n"
        f"Geschlecht: {daten.get('Geschlecht', '')}\n"
        f"Kastriert: {daten.get('Kastrat', '')}\n"
        f"Klasse: {daten.get('Angemeldete_Klasse', '')}\n"
        f"Gewicht: {daten.get('Gewicht', '')} kg\n\n"
        f"--- AUSSTELLUNGSDETAILS ---\n"
        f"Datum/Tage: {daten.get('Angemeldete_Tage', '')}\n"
        f"Doppelkäfig mit: {daten.get('Doppelkafig', 'Keine Angabe')}\n\n"
        f"--- WICHTIGE HINWEISE & BEMERKUNGEN ---\n"
        f"Umgruppierung: {daten.get('Hinweis_Umwertung', 'Keine automatische Umwertung nötig.')}\n"
        f"Deine Bemerkungen: {daten.get('Bemerkungen', 'Keine Bemerkungen hinterlegt.')}\n\n"
        f"Freundliche Grüsse\nIhr KECB-Ausstellungsteam"
    )
    try:
        msg = MIMEText(inhalt, 'plain', 'utf-8')
        msg['Subject'] = Header(betreff, 'utf-8')
        msg['From'] = sender_email
        msg['To'] = empfaenger
        msg['Cc'] = kopie_verein
        
        server = smtplib.SMTP_SSL(smtp_server, smtp_port) if smtp_port == 465 else smtplib.SMTP(smtp_server, smtp_port)
        if smtp_port != 465:
            server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, [empfaenger, kopie_verein], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Fehler beim E-Mail-Versand: {e}")
        return False

st.title("🐾 Anmeldung zur Katzenausstellung Burgdorf 2026")
st.markdown("### Fédération Féline Helvétique (FFH) / FIFe")

# --- 1. AUSSTELLUNGSDETAILS ---
st.subheader("1. Ausstellungsdetails")
ausstellungsort = st.text_input("Ausstellung in *", value="Burgdorf")

col_sat_chk, col_sat_date = st.columns([1, 2])
with col_sat_chk:
    st.write("")
    st.write("")
    samstag_aktiv = st.checkbox("Samstag", value=False)
with col_sat_date:
    datum_samstag = st.date_input("Ausstellungstermin Samstag", value=date(2026, 10, 10), format="DD.MM.YYYY", disabled=not samstag_aktiv)

col_sun_chk, col_sun_date = st.columns([1, 2])
with col_sun_chk:
    st.write("")
    st.write("")
    sonntag_aktiv = st.checkbox("Sonntag", value=False)
with col_sun_date:
    datum_sonntag = st.date_input("Ausstellungstermin Sonntag", value=date(2026, 10, 11), format="DD.MM.YYYY", disabled=not sonntag_aktiv)

gewaehlte_tage = []
if samstag_aktiv:
    gewaehlte_tage.append(f"Samstag ({datum_samstag.strftime('%d.%m.%Y')})")
if sonntag_aktiv:
    gewaehlte_tage.append(f"Sonntag ({datum_sonntag.strftime('%d.%m.%Y')})")
wochentag_export = ", ".join(gewaehlte_tage)

# --- 2. AUTOMATISCHER KATZEN- & AUSSTELLER-SUCHFILTER ---
st.subheader("2. Angaben zur Katze")
df_stamm, gefundener_dateiname = lade_stammdaten()

if df_stamm is not None:
    st.markdown("🔐 **Eintrag aus Datenbank laden (Sichere Suche)**")
    col_search_nr, col_search_name = st.columns(2)
    with col_search_nr:
        suche_zuchtbuch = st.text_input("Stammbuch-Nummer:", placeholder="z.B. 123456")
    with col_search_name:
        suche_nachname = st.text_input("Nachname des Besitzers:", placeholder="z.B. Müller")
        
    if st.button("🔍 Daten suchen"):
        if suche_zuchtbuch and suche_nachname:
            such_ziffern = extrahiere_ziffern(suche_zuchtbuch)
            such_nachname_str = str(suche_nachname).strip().lower()
            
            such_spalte_nr = 'Stammbuch-Nummer' if 'Stammbuch-Nummer' in df_stamm.columns else ('Zuchtbuch_Nr' if 'Zuchtbuch_Nr' in df_stamm.columns else None)
            such_spalte_name = 'Besitzer Nachname' if 'Besitzer Nachname' in df_stamm.columns else None
            
            if such_spalte_nr and such_spalte_name:
                df_stamm['Ziffern_Suche'] = df_stamm[such_spalte_nr].apply(extrahiere_ziffern)
                match = df_stamm[
                    (df_stamm['Ziffern_Suche'] == such_ziffern) & 
                    (df_stamm[such_spalte_name].astype(str).str.lower().str.contains(such_nachname_str, na=False))
                ]
                
                if not match.empty:
                    row = match.iloc[0]
                    st.session_state.k_name = safe_str(row.get('Name', ''))
                    rasse = safe_str(row.get('Rasse', ''))
                    farbe = safe_str(row.get('Farbe', ''))
                    st.session_state.k_ems = f"{rasse} {farbe}".strip() if rasse and farbe else rasse
                    st.session_state.k_gruppe = safe_str(row.get('Farbgruppe', ''))
                    st.session_state.k_rasse = rasse
                    st.session_state.k_zuchtbuch = safe_str(row.get(such_spalte_nr, ''))
                    st.session_state.k_chip = safe_str(row.get('Chip-Nummer', ''))
                    
                    geb_datum = row.get('Geburtsdatum', '')
                    if pd.notna(geb_datum):
                        try:
                            if isinstance(geb_datum, str):
                                st.session_state.k_geboren = datetime.strptime(geb_datum.strip(), "%d.%m.%Y").date()
                            else:
                                st.session_state.k_geboren = pd.to_datetime(geb_datum).date()
                        except:
                            pass
                    
                    geschlecht_raw = str(row.get('Geschlecht', '')).lower().strip()
                    st.session_state.k_geschlecht = "0.1 Weiblich" if any(x in geschlecht_raw for x in ["w", "f", "0.1"]) else "1.0 Männlich"
                    kastriert_raw = str(row.get('Kastriert', '')).lower().strip()
                    st.session_state.k_kastriert = "Ja" if kastriert_raw in ["x", "ja", "yes", "1", "true", "kastrat", "k"] else "Nein"
                    
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
                    st.session_state.z_zuechter = safe_str(row.get('Züchter', ''))
                    
                    st.success(f"✅ Daten für '{st.session_state.k_name}' geladen!")
                    st.rerun()
                else:
                    st.warning("Keine Übereinstimmung gefunden.")
            else:
                st.error("Fehler bei den Spaltennamen!")
        else:
            st.error("Bitte füllen Sie beide Suchfelder aus!")

# --- Eingabefelder für die Katze ---
col3, col4 = st.columns([2, 1])
katze_name = col3.text_input("Titel + Name der Katze *", value=st.session_state.k_name)
katze_ems = col4.text_input("EMS-Code *", value=st.session_state.k_ems)

col5, col6 = st.columns([1, 2])
katze_gruppe = col5.text_input("Gruppe / Farbgruppe", value=st.session_state.k_gruppe)
katze_rasse_farbe = col6.text_input("Rasse + Farbe *", value=st.session_state.k_rasse)

col7, col8 = st.columns(2)
katze_zuchtbuch = col7.text_input("Zuchtbuch-Nr. / Pedigree-No. *", value=st.session_state.k_zuchtbuch)
katze_chip = col8.text_input("Chip-Nr.", value=st.session_state.k_chip)

col9, col10, col11 = st.columns([2, 2, 1])
with col9:
    katze_geboren = st.date_input("Geburtsdatum *", value=st.session_state.k_geboren, format="DD.MM.YYYY")
with col10:
    g_index = 0 if "Männlich" in st.session_state.k_geschlecht else 1
    katze_geschlecht = st.radio("Geschlecht *", ["1.0 Männlich", "0.1 Weiblich"], index=g_index)
with col11:
    kast_index = 0 if st.session_state.k_kastriert == "Ja" else 1
    katze_kastriert = st.radio("Kastrat? *", ["Ja", "Nein"], index=kast_index)

# --- KLASSEN-LISTE ---
gemeinsame_klassen = [
    "11. Klasse 8-12 Monate",
    "12. Klasse 4-8 Monate",
    "13a. Novizenklasse",
    "13b. Kontrollklasse",
    "13c. Bestimmungsklasse",
    "14. Hauskatze",
    "15. Ausser Konkurrenz"
]

if katze_kastriert == "Ja":
    klassen_optionen = [
        "-",
        "2. Supreme Premior - PH",
        "4. Gr. Int. Premior - CAPS",
        "6. International Premior - CAGPIB",
        "8. Premior - CAPIB",
        "10. Kastraten (Neuter) - CAP"
    ] + gemeinsame_klassen
else:
    klassen_optionen = [
        "-",
        "1. Supreme Champion - PH",
        "3. Gr. Int. Champion - CACS",
        "5. International Champion - CAGCIB",
        "7. Champion - CACIB",
        "9. Offene Klasse (Open) - CAC"
    ] + gemeinsame_klassen

ausstellungsklasse = st.selectbox("Klasse für die gemeldet wird *", klassen_optionen)

# --- ALTERS-WARNUNG & AUTOMATISCHE UMWERTUNGS-PRÜFUNG ---
warnung_text, hinweis_umwertung = pruefe_alter_warnung(
    katze_geboren,
    ausstellungsklasse,
    datum_samstag,
    datum_sonntag,
    samstag_aktiv,
    sonntag_aktiv
)

if warnung_text:
    st.error(f"❌ {warnung_text}")
if hinweis_umwertung:
    st.warning(f"⚠️ {hinweis_umwertung}")

katze_gewicht = st.text_input("Gewicht der Katze (kg)")

# --- STAMMBAUM & ZÜCHTER ---
if not st.session_state.k_zuchtbuch:
    with st.container():
        st.subheader("3. Stammbaum (Eltern)")
        vater_name = st.text_input("Name des Vaters *", value=st.session_state.v_name)
        vater_ems = st.text_input("EMS-Code Vater *", value=st.session_state.v_ems)
        vater_zuchtbuch = st.text_input("Zuchtbuch-Nr. Vater *", value=st.session_state.v_zuchtbuch)
        mutter_name = st.text_input("Name der Mutter *", value=st.session_state.m_name)
        mutter_ems = st.text_input("EMS-Code Mutter *", value=st.session_state.m_ems)
        mutter_zuchtbuch = st.text_input("Zuchtbuch-Nr. Mutter *", value=st.session_state.m_zuchtbuch)
        zuechter_name_land = st.text_input("Züchter + Land *", key="zuechter_input_1")
else:
    vater_name = st.session_state.v_name
    vater_ems = st.session_state.v_ems
    vater_zuchtbuch = st.session_state.v_zuchtbuch
    mutter_name = st.session_state.m_name
    mutter_ems = st.session_state.m_ems
    mutter_zuchtbuch = st.session_state.m_zuchtbuch
    zuechter_name_land = st.session_state.z_zuechter

# --- AUSSTELLER ---
st.subheader("4. Aussteller & Züchter")
if not st.session_state.a_strasse:
    suchanfrage = st.text_input("Suchen Sie nach Ihrer Adresse...", placeholder="z.B. Musterweg 7 Zürich")
    if len(suchanfrage) >= 4:
        ergebnisse = suche_adresse(suchanfrage)
        if ergebnisse:
            auswahl_label = st.selectbox("Gefundene Adressen:", ["-- Bitte wählen --"] + [r["label"] for r in ergebnisse])
            if auswahl_label != "-- Bitte wählen --":
                gewaehlt = next(item for item in ergebnisse if item["label"] == auswahl_label)
                st.session_state.a_strasse = gewaehlt["strasse_nr"]
                st.session_state.a_plz_ort = gewaehlt["plz_ort"]
                st.session_state.a_land = gewaehlt["land"]
                st.rerun()

col12, col13 = st.columns(2)
aussteller_nachname = col12.text_input("Nachname *", value=st.session_state.a_nachname)
aussteller_vorname = col13.text_input("Vorname *", value=st.session_state.a_vorname)
col14, col15 = st.columns([2, 1])
aussteller_strasse = col14.text_input("Strasse, Nr. *", value=st.session_state.a_strasse)
aussteller_ort = col15.text_input("PLZ + Ort *", value=st.session_state.a_plz_ort)
col16, col17 = st.columns(2)
aussteller_land = col16.text_input("Land *", value=st.session_state.a_land)
aussteller_telefon = col17.text_input("Telefon *")
aussteller_email = st.text_input("E-Mail-Adresse *")
col18, col19 = st.columns([2, 1])
aussteller_verein = col18.text_input("Verein *")
aussteller_mitgliedsnr = col19.text_input("Mitglieds-Nr.")

# --- BEMERKUNGEN & ABSENDEN ---
st.subheader("5. Bemerkungen & Einverständnis")
doppelkafig = st.text_input("Doppelkäfig zusammen mit:")
bemerkungen = st.text_area("Bemerkungen")
agb_akzeptiert = st.checkbox("Ich akzeptiere die FIFé/FFH Regeln. *")

if st.button("Anmeldung verbindlich absenden", type="primary"):
    if not (ausstellungsort and katze_name and aussteller_nachname and aussteller_email and agb_akzeptiert):
        st.error("Bitte füllen Sie alle Pflichtfelder (*) aus.")
    elif ausstellungsklasse == "-":
        st.error("Bitte wählen Sie eine Ausstellungsklasse!")
    elif warnung_text:
        st.error(f"Absenden blockiert aufgrund eines schweren Altersfehlers: {warnung_text}")
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
            "Email": aussteller_email,
            "Verein": aussteller_verein,
            "MitgliedsNr": aussteller_mitgliedsnr,
            "Zuechter": zuechter_name_land,
            "Doppelkafig": doppelkafig,
            "Hinweis_Umwertung": hinweis_umwertung if hinweis_umwertung else "Keine automatische Umwertung nötig.",
            "Bemerkungen": bemerkungen if bemerkungen else "Keine"
        }
        df_neu = pd.DataFrame([neue_anmeldung])
        if os.path.exists(EXCEL_FILE):
            df_gesamt = pd.concat([pd.read_excel(EXCEL_FILE), df_neu], ignore_index=True)
        else:
            df_gesamt = df_neu
        df_gesamt.to_excel(EXCEL_FILE, index=False)
        sende_bestaetigungs_email(neue_anmeldung)
        st.success("Erfolgreich!")
        st.balloons()

# --- ADMIN ---
with st.expander("🔐 Admin-Bereich"):
    if st.text_input("Passwort", type="password") == "ffh2026":
        if os.path.exists(EXCEL_FILE):
            with open(EXCEL_FILE, "rb") as f:
                st.download_button("📥 Excel herunterladen", f.read(), "ausstellung_anmeldungen.xlsx")
            st.dataframe(pd.read_excel(EXCEL_FILE))
