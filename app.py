# -*- coding: utf-8 -*-

"""
Projekt: Cat Show Anmeldung des KECB Katzenausstellung
Copyright (c) 2026 Brigitte Portner
Alle Rechte vorbehalten
"""




import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Dateiname für die Excel-Datenbank
EXCEL_FILE = "ausstellung_anmeldungen.xlsx"

# Seite konfigurieren (für ein professionelles Layout)
st.set_page_config(page_title="FFH Ausstellungs-Anmeldung", layout="centered")

st.title("🐾 Anmeldung zur Katzenausstellung")
st.markdown("### Fédération Féline Helvétique (FFH) / FIFe")
st.write("Bitte füllen Sie das Formular vollständig aus.")

# --- 1. AUSSTELLUNGSDETAILS ---
st.subheader("1. Ausstellungsdetails")
col1, col2 = st.columns(2)
with col1:
    ausstellungsort = st.text_input("Ausstellung in *", placeholder="z.B. Bern")
    wochentag = st.radio("Wochentag *", ["Samstag", "Sonntag"])
with col2:
    ausstellungsdatum = st.date_input("Ausstellungstermin *", min_value=datetime.today())
    bewertungstyp = st.radio("Bewertung / Judgement *", ["Bewertung 1", "Bewertung 2", "Beide"])

# --- 2. ANGABEN ZUR KATZE ---
st.subheader("2. Angaben zur Katze")
col3, col4 = st.columns([2, 1])
with col3:
    katze_name = st.text_input("Titel + Name der Katze *")
with col4:
    katze_ems = st.text_input("EMS-Code *", placeholder="z.B. NFO n 22")

col5, col6 = st.columns([1, 2])
with col5:
    katze_gruppe = st.text_input("Gruppe")
with col6:
    katze_rasse_farbe = st.text_input("Rasse + Farbe *", placeholder="z.B. Norwegische Waldkatze")

col7, col8 = st.columns(2)
with col7:
    katze_zuchtbuch = st.text_input("Zuchtbuch-Nr. / Pedigree-No. *")
with col8:
    katze_chip = st.text_input("Chip-Nr. (falls vor 1.1.23 geboren)")

col9, col10, col11 = st.columns([2, 2, 1])
with col9:
    katze_geboren = st.date_input("Geburtsdatum *", max_value=datetime.today())
with col10:
    katze_geschlecht = st.radio("Geschlecht *", ["1.0 Männlich", "0.1 Weiblich"])
with col11:
    katze_kastriert = st.radio("Kastrat? *", ["Ja", "Nein"])

klassen_optionen = [
    "1. Supreme Champion - PH", "2. Supreme Premior - PH", "3. Gr. Int. Champion - CACS",
    "4. Gr. Int. Premior - CAPS", "5. International Champion - CAGCIB", "6. International Premior - CAGPIB",
    "7. Champion - CACIB", "8. Premior - CAPIB", "9. Offene Klasse (Open) - CAC",
    "10. Kastraten (Neuter) - CAP", "11. Klasse 8-12 Monate", "12. Klasse 4-8 Monate",
    "13a. Novizenklasse", "13b. Kontrollklasse", "13c. Bestimmungsklasse",
    "14. Hauskatze", "15. Ausser Konkurrenz", "16. Wurfklasse (mind. 3 Welpen)", "17. Veteranenklasse"
]
ausstellungsklasse = st.selectbox("Klasse für die gemeldet wird *", klassen_optionen)
katze_gewicht = st.text_input("Gewicht der Katze (kg)", placeholder="z.B. 4.5")
bereits_erhalten = st.text_input("Bereits erhalten in / Point obtenu à l'exposition de")

# --- 3. STAMMBAUM (ELTERN) ---
st.subheader("3. Stammbaum (Eltern)")
st.markdown("**Vater**")
col_v1, col_v2, col_v3 = st.columns([2, 1, 1])
vater_name = col_v1.text_input("Name des Vaters *")
vater_ems = col_v2.text_input("EMS-Code Vater *")
vater_zuchtbuch = col_v3.text_input("Zuchtbuch-Nr. Vater *")

st.markdown("**Mutter**")
col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
mutter_name = col_m1.text_input("Name der Mutter *")
mutter_ems = col_m2.text_input("EMS-Code Mutter *")
mutter_zuchtbuch = col_m3.text_input("Zuchtbuch-Nr. Mutter *")

# --- 4. AUSSTELLER & ZÜCHTER ---
st.subheader("4. Aussteller & Züchter")
col12, col13 = st.columns(2)
aussteller_nachname = col12.text_input("Nachname (Aussteller) *")
aussteller_vorname = col13.text_input("Vorname (Aussteller) *")

col14, col15 = st.columns([2, 1])
aussteller_strasse = col14.text_input("Strasse, Nr. *")
aussteller_ort = col15.text_input("PLZ + Ort *")

col16, col17 = st.columns(2)
aussteller_land = col16.text_input("Land *", value="Schweiz")
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

agb_akzeptiert = st.checkbox("Ich bestätige, dass die obigen Angaben wahrheitsgetreu sind und ich die Ausstellungsregeln der FIFé/FFH akzeptiere. *")

# --- ABSENDEN LOGIK ---
if st.button("Anmeldung verbindlich absenden", type="primary"):
    # Einfache Validierung der wichtigsten Pflichtfelder
    if not (ausstellungsort and katze_name and aussteller_nachname and aussteller_email and agb_akzeptiert):
        st.error("Bitte füllen Sie alle Pflichtfelder (*) aus und akzeptieren Sie die Bedingungen.")
    else:
        # Daten in ein Dictionary packen
        neue_anmeldung = {
            "Eingangsdatum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ort": ausstellungsort, "Datum": str(ausstellungsdatum), "Wochentag": wochentag, "Bewertung": bewertungstyp,
            "Katze_Name": katze_name, "Katze_EMS": katze_ems, "Gruppe": katze_gruppe, "Rasse_Farbe": katze_rasse_farbe,
            "Zuchtbuch_Nr": katze_zuchtbuch, "Chip_Nr": katze_chip, "Geburtsdatum": str(katze_geboren),
            "Geschlecht": katze_geschlecht, "Kastrat": katze_kastriert, "Klasse": ausstellungsklasse,
            "Gewicht": katze_gewicht, "Bereits_Erhalten": bereits_erhalten,
            "Vater_Name": vater_name, "Vater_EMS": vater_ems, "Vater_Zuchtbuch": vater_zuchtbuch,
            "Mutter_Name": mutter_name, "Mutter_EMS": mutter_ems, "Mutter_Zuchtbuch": mutter_zuchtbuch,
            "Aussteller_Nachname": aussteller_nachname, "Aussteller_Vorname": aussteller_vorname,
            "Strasse": aussteller_strasse, "PLZ_Ort": aussteller_ort, "Land": aussteller_land,
            "Telefon": aussteller_telefon, "Email": aussteller_email, "Verein": aussteller_verein,
            "MitgliedsNr": aussteller_mitgliedsnr, "Zuechter": zuechter_name_land,
            "Doppelkafig": doppelkafig, "Bemerkungen": bemerkungen
        }
        
        # In DataFrame umwandeln
        df_neu = pd.DataFrame([neue_anmeldung])
        
        # Wenn Datei existiert, anhängen, sonst neu erstellen
        if os.path.exists(EXCEL_FILE):
            df_alt = pd.read_excel(EXCEL_FILE)
            df_gesamt = pd.concat([df_alt, df_neu], ignore_index=True)
        else:
            df_gesamt = df_neu
            
        # Zurück in Excel schreiben
        df_gesamt.to_excel(EXCEL_FILE, index=False)
        
        st.success("🎉 Vielen Dank! Die Anmeldung wurde erfolgreich gespeichert.")
