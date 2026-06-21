# -*- coding: utf-8 -*-

"""
Projekt: Cat Show Anmeldung des KECB Katzenausstellung
Copyright (c) 2026 Brigitte Portner
Alle Rechte vorbehalten
"""



```python
import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime, date

# Dateiname für die Excel-Datenbank
EXCEL_FILE = "ausstellung_anmeldungen.xlsx"

# Seite konfigurieren (für ein professionelles und sauberes Layout)
st.set_page_config(page_title="FFH Ausstellungs-Anmeldung", layout="centered")

# --- INITIALISIERUNG SESSION STATE FÜR ADRESSEN ---
# Wird benötigt, um die Felder nach der Autocomplete-Suche automatisch zu beschreiben
if 'strasse_nr' not in st.session_state:
    st.session_state.strasse_nr = ""
if 'plz_ort' not in st.session_state:
    st.session_state.plz_ort = ""
if 'land' not in st.session_state:
    st.session_state.land = "Schweiz"

# Hilfsfunktion für die kostenlose Adresssuche (Photon API von Komoot / OpenStreetMap)
def suche_adresse(query):
    if not query or len(query) < 4:
        return []
    try:
        url = f"https://photon.komoot.io/api/?q={requests.utils.quote(query)}&limit=5&lang=de"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            results = response.json().get('features', [])
            suggestions = []
            for item in results:
                props = item.get('properties', {})
                street = props.get('street', '')
                housenumber = props.get('housenumber', '')
                postcode = props.get('postcode', '')
                city = props.get('city', '')
                country = props.get('country', '')
                
                # Nur brauchbare Adressen mit Strassenname vorschlagen
                if street:
                    label_parts = [f"{street} {housenumber}".strip()]
                    if postcode or city:
                        label_parts.append(f"{postcode} {city}".strip())
                    if country:
                        label_parts.append(country)
                    
                    label = ", ".join(label_parts)
                    suggestions.append({
                        "label": label,
                        "strasse_nr": f"{street} {housenumber}".strip(),
                        "plz_ort": f"{postcode} {city}".strip(),
                        "land": country
                    })
            return suggestions
    except Exception:
        pass
    return []

st.title("🐾 Anmeldung zur Katzenausstellung")
st.markdown("### Fédération Féline Helvétique (FFH) / FIFe")
st.write("Bitte füllen Sie das Formular vollständig aus.")

# --- 1. AUSSTELLUNGSDETAILS ---
st.subheader("1. Ausstellungsdetails")

# Ausstellungsort über die volle Breite
ausstellungsort = st.text_input("Ausstellung in *", placeholder="z.B. Burgdorf")

# Zeile für Samstag mit Checkbox und Datum direkt dahinter
col_sat_chk, col_sat_date = st.columns([1, 2])
with col_sat_chk:
    st.write("") # Optische Ausrichtung
    st.write("") 
    samstag_aktiv = st.checkbox("Samstag", value=True)
with col_sat_date:
    datum_samstag = st.date_input(
        "Ausstellungstermin Samstag", 
        value=date(2026, 10, 10),
        format="DD.MM.YYYY",
        disabled=not samstag_aktiv
    )

# Zeile für Sonntag mit Checkbox und Datum direkt dahinter
col_sun_chk, col_sun_date = st.columns([1, 2])
with col_sun_chk:
    st.write("") # Optische Ausrichtung
    st.write("")
    sonntag_aktiv = st.checkbox("Sonntag", value=False)
with col_sun_date:
    datum_sonntag = st.date_input(
        "Ausstellungstermin Sonntag", 
        value=date(2026, 10, 11),
        format="DD.MM.YYYY",
        disabled=not sonntag_aktiv
    )

# Werte für den Excel-Export aufbereiten
gewaehlte_tage = []
if samstag_aktiv:
    gewaehlte_tage.append(f"Samstag ({datum_samstag.strftime('%d.%m.%Y')})")
if sonntag_aktiv:
    gewaehlte_tage.append(f"Sonntag ({datum_sonntag.strftime('%d.%m.%Y')})")
wochentag_export = ", ".join(gewaehlte_tage)


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
    katze_geboren = st.date_input(
        "Geburtsdatum *", 
        value=date(2025, 1, 1),
        max_value=datetime.today(),
        format="DD.MM.YYYY"
    )
with col10:
    katze_geschlecht = st.radio("Geschlecht *", ["1.0 Männlich", "0.1 Weiblich"])
with col11:
    katze_kastriert = st.radio("Kastrat? *", ["Ja", "Nein"])

# Dynamische Klassenfilterung
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
        "2. Supreme Premior - PH",
        "4. Gr. Int. Premior - CAPS",
        "6. International Premior - CAGPIB",
        "8. Premior - CAPIB",
        "10. Kastraten (Neuter) - CAP"
    ] + gemeinsame_klassen
else:
    klassen_optionen = [
        "1. Supreme Champion - PH",
        "3. Gr. Int. Champion - CACS",
        "5. International Champion - CAGCIB",
        "7. Champion - CACIB",
        "9. Offene Klasse (Open) - CAC"
    ] + gemeinsame_klassen

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

# --- START ADRESS-SUCHE (AUTOCOMPLETE) ---
st.markdown("🔍 **Schnell-Eingabe der Adresse**")
suchanfrage = st.text_input("Suchen Sie nach Ihrer Strasse, PLZ oder Ort...", placeholder="z.B. Birkenweg 12 Bern")

if len(suchanfrage) >= 4:
    ergebnisse = suche_adresse(suchanfrage)
    if ergebnisse:
        options = ["-- Bitte wählen --"] + [r["label"] for r in ergebnisse]
        auswahl_label = st.selectbox("Gefundene Adressen (Bitte anklicken zum Ausfüllen):", options)
        
        if auswahl_label != "-- Bitte wählen --":
            # Passenden Eintrag heraussuchen und Session-State setzen
            gewaehlt = next(item for item in ergebnisse if item["label"] == auswahl_label)
            st.session_state.strasse_nr = gewaehlt["strasse_nr"]
            st.session_state.plz_ort = gewaehlt["plz_ort"]
            st.session_state.land = gewaehlt["land"]
            st.success("Adresse wurde unten eingetragen!")
    else:
        st.info("Keine direkte Adresse gefunden. Tippen Sie einfach weiter oder tragen Sie sie manuell unten ein.")
# --- ENDE ADRESS-SUCHE ---

st.markdown("---") # Trennlinie zur optischen Abgrenzung

col12, col13 = st.columns(2)
aussteller_nachname = col12.text_input("Nachname (Aussteller) *")
aussteller_vorname = col13.text_input("Vorname (Aussteller) *")

# Adressfelder nutzen nun die Werte aus dem Session State
col14, col15 = st.columns([2, 1])
aussteller_strasse = col14.text_input("Strasse, Nr. *", value=st.session_state.strasse_nr)
aussteller_ort = col15.text_input("PLZ + Ort *", value=st.session_state.plz_ort)

col16, col17 = st.columns(2)
aussteller_land = col16.text_input("Land *", value=st.session_state.land)
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
    if not (ausstellungsort and katze_name and aussteller_nachname and aussteller_email and agb_akzeptiert):
        st.error("Bitte füllen Sie alle Pflichtfelder (*) aus und akzeptieren Sie die Bedingungen.")
    elif not (samstag_aktiv or sonntag_aktiv):
        st.error("Bitte wählen Sie mindestens einen Ausstellungstag (Samstag und/oder Sonntag) aus.")
    else:
        # Daten sammeln
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
            "Email": aussteller_email,
            "Verein": aussteller_verein,
            "MitgliedsNr": aussteller_mitgliedsnr,
            "Zuechter": zuechter_name_land,
            "Doppelkafig": doppelkafig,
            "Bemerkungen": bemerkungen
        }
        
        df_neu = pd.DataFrame([neue_anmeldung])
        
        # In Excel-Datei abspeichern
        if os.path.exists(EXCEL_FILE):
            df_alt = pd.read_excel(EXCEL_FILE)
            df_gesamt = pd.concat([df_alt, df_neu], ignore_index=True)
        else:
            df_gesamt = df_neu
            
        df_gesamt.to_excel(EXCEL_FILE, index=False)
        
        st.success("🎉 Vielen Dank! Die Anmeldung wurde erfolgreich gespeichert.")
        st.balloons()

```
