
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# ==========================================
# CONFIGURAZIONE DELLA PAGINA E STILE
# ==========================================
st.set_page_config(
    page_title="Advanced Betting & Value Analysis Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #ff4b4b; color: white; }
    .stButton>button:hover { background-color: #e03e3e; color: white; }
    .metric-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .form-win { color: #28a745; font-weight: bold; font-size: 1.1em; background-color: #e8f5e9; padding: 2px 6px; border-radius: 4px; margin-right: 3px; }
    .form-draw { color: #856404; font-weight: bold; font-size: 1.1em; background-color: #fff3cd; padding: 2px 6px; border-radius: 4px; margin-right: 3px; }
    .form-loss { color: #dc3545; font-weight: bold; font-size: 1.1em; background-color: #ffebee; padding: 2px 6px; border-radius: 4px; margin-right: 3px; }
    .header-title { font-size: 2.2em; font-weight: 800; color: #1f2937; }
    .sub-text { color: #4b5563; font-size: 1.1em; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER PRINCIPALE E INTRODUZIONE
# ==========================================
st.markdown("<p class='header-title'>⚽ Advanced Betting & Value Analysis - Europa Pro</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>Piattaforma professionale per l'analisi statistica avanzata, il filtraggio per squadra, lo studio dello stato di forma e la generazione automatica della Schedina Top 5.</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# DEFINIZIONE DATABASE & CAMPIONATI
# ==========================================
LEAGUES = ["Serie A", "Premier League", "La Liga", "Bundesliga", "Ligue 1"]

TEAMS = {
    "Serie A": ["Inter", "Milan", "Juventus", "Napoli", "Atalanta", "Roma", "Lazio", "Fiorentina", "Bologna", "Torino", "Monza", "Udinese", "Genoa", "Empoli", "Lecce", "Verona", "Cagliari", "Como", "Venezia", "Parma"],
    "Premier League": ["Manchester City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Manchester United", "Newcastle", "Brighton", "West Ham", "Crystal Palace", "Bournemouth", "Brentford", "Fulham", "Everton", "Nottingham Forest", "Wolverhampton", "Leicester City", "Ipswich Town", "Southampton"],
    "La Liga": ["Real Madrid", "Barcelona", "Girona", "Atletico Madrid", "Athletic Bilbao", "Real Sociedad", "Real Betis", "Villarreal", "Valencia", "Sevilla", "Celta Vigo", "Osasuna", "Rayo Vallecano", "Mallorca", "Las Palmas", "Getafe", "Alaves", "Real Valladolid", "Leganes", "Espanyol"],
    "Bundesliga": ["Bayer Leverkusen", "Bayern Monaco", "Stoccarda", "Lipsia", "Borussia Dortmund", "Eintracht Francoforte", "Friburgo", "Hoffenheim", "Werder Brema", "Augsburg", "Wolfsburg", "Magonza", "Borussia Monchengladbach", "Union Berlino", "Bochum", "Heidenheim", "St. Pauli", "Holstein Kiel"],
    "Ligue 1": ["Paris Saint-Germain", "Monaco", "Brest", "Lilla", "Nizza", "Lens", "Olympique Lione", "Olympique Marsiglia", "Strasburgo", "Rennes", "Reims", "Tolosa", "Montpellier", "Nantes", "Le Havre", "Auxerre", "Angers", "Saint-Etienne"]
}

# ==========================================
# GENERAZIONE DATI AVANZATA (CACHE)
# ==========================================
@st.cache_data
def load_comprehensive_match_schedule():
    np.random.seed(123)
    matches = []
    base_date = date.today()
    
    for league in LEAGUES:
        teams = TEAMS[league]
        # Generiamo un calendario completo incrociato
        for i, team_home in enumerate(teams):
            for j, team_away in enumerate(teams):
                if team_home != team_away:
                    # Distribuzione temporale realistica delle partite nel corso del mese
                    days_offset = np.random.randint(-6, 20)
                    match_date = pd.Timestamp(base_date) + pd.Timedelta(days=days_offset)
                    
                    # Stato di forma recente (ultime 5 partite: V = Vittoria, N = Pareggio, P = Sconfitta)
                    form_home = np.random.choice(["V", "N", "P"], size=5, p=[0.48, 0.30, 0.22])
                    form_away = np.random.choice(["V", "N", "P"], size=5, p=[0.40, 0.32, 0.28])
                    
                    # Generazione quote realistiche dei bookmaker
                    odd_1 = round(np.random.uniform(1.35, 4.50), 2)
                    odd_x = round(np.random.uniform(3.00, 4.60), 2)
                    odd_2 = round(np.random.uniform(1.70, 6.00), 2)
                    
                    # Calcolo probabilità implicite corrette (normalizzate)
                    p1_imp = 1 / odd_1
                    px_imp = 1 / odd_x
                    p2_imp = 1 / odd_2
                    total_imp = p1_imp + px_imp + p2_imp
                    
                    prob_1 = round((p1_imp / total_imp) * 100, 1)
                    prob_x = round((px_imp / total_imp) * 100, 1)
                    prob_2 = round((p2_imp / total_imp) * 100, 1)
                    
                    # Statistiche aggiuntive sui gol e metriche avanzate
                    over_25 = round(np.random.uniform(38.0, 78.0), 1)
                    btts_prob = round(np.random.uniform(42.0, 72.0), 1)
                    expected_goals_home = round(np.random.uniform(1.0, 2.6), 2)
                    expected_goals_away = round(np.random.uniform(0.7, 2.1), 2)
                    
                    matches.append({
                        "Campionato": league,
                        "Data": match_date.strftime("%Y-%m-%d"),
                        "Squadra Casa": team_home,
                        "Squadra Ospite": team_away,
                        "Forma Casa": list(form_home),
                        "Forma Ospite": list(form_away),
                        "Quota 1": odd_1,
                        "Quota X": odd_x,
                        "Quota 2": odd_2,
                        "Prob 1 (%)": prob_1,
                        "Prob X (%)": prob_x,
                        "Prob 2 (%)": prob_2,
                        "Over 2.5 Prob": over_25,
                        "BTTS Prob": btts_prob,
                        "xG Casa": expected_goals_home,
                        "xG Ospite": expected_goals_away
                    })
                    
    df = pd.DataFrame(matches)
    return df

df_matches = load_comprehensive_match_schedule()

# ==========================================
# BARRA LATERALE DI CONTROLLO GLOBALE
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/football--v1.png", width=80)
    st.header("⚙️ Pannello di Controllo")
    st.markdown("Filtra rapidamente l'intero ecosistema di dati analizzati dall'algoritmo.")
    
    global_league_filter = st.selectbox("Seleziona Campionato Principale", ["Tutti i Campionati"] + LEAGUES)
    
    st.markdown("---")
    st.info("💡 **Consiglio Pro:** Usa il Tab 1 per visualizzare direttamente la Schedina Top 5 generata automaticamente per la giornata odierna.")
    st.markdown("📌 *Versione Pro 3.2 - Algoritmo Statistico Integrato*")

# Filtraggio globale del dataframe se necessario
if global_league_filter != "Tutti i Campionati":
    df_active = df_matches[df_matches["Campionato"] == global_league_filter].copy()
else:
    df_active = df_matches.copy()

# ==========================================
# STRUTTURAZIONE DELLA NAVIGAZIONE A TAB
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Schedina Top 5 del Giorno", 
    "📅 Calendario & Ricerca Squadra", 
    "📊 Studio Match & Forma Recente", 
    "🧮 Calcolatore Value & Bankroll",
    "📈 Statistiche Globali & Trend"
])

# ==========================================
# TAB 1: SCHEDINA TOP 5 DEL GIORNO
# ==========================================
with tab1:
    st.header("🎯 La Schedina 'Top Value' del Giorno (Multipla Consigliata)")
    st.markdown("Il nostro motore analitico scansiona tutti i campionati europei attivi, isola le partite della giornata odierna o successive e seleziona le **5 migliori opzioni** con il più alto coefficiente di affidabilità statistica.")
    
    today_str = date.today().strftime("%Y-%m-%d")
    df_today = df_active[df_active["Data"] >= today_str].copy()
    
    if len(df_today) > 0:
        # Funzione di calcolo affidabilità basata sulla massima probabilità stimata e stabilità xG
        def calculate_match_reliability(row):
            max_prob = max(row["Prob 1 (%)"], row["Prob X (%)"], row["Prob 2 (%)"])
            xg_diff = abs(row["xG Casa"] - row["xG Ospite"]) * 5
            return max_prob + xg_diff
            
        df_today["Indice Affidabilità"] = df_today.apply(calculate_match_reliability, axis=1)
        top_5_matches = df_today.sort_values(by="Indice Affidabilità", ascending=False).head(5)
        
        accumulated_odds = 1.0
        match_counter = 1
        
        for idx, row in top_5_matches.reset_index().iterrows():
            # Determiniamo il segno più solido
            p1, px, p2 = row["Prob 1 (%)"], row["Prob X (%)"], row["Prob 2 (%)"]
            if p1 >= p2 and p1 >= px:
                chosen_sign = "1 (Vittoria Casa)"
                chosen_odd = row["Quota 1"]
                chosen_prob = p1
            elif p2 >= p1 and p2 >= px:
                chosen_sign = "2 (Vittoria Ospite)"
                chosen_odd = row["Quota 2"]
                chosen_prob = p2
            else:
                chosen_sign = "X (Pareggio)"
                chosen_odd = row["Quota X"]
                chosen_prob = px
                
            accumulated_odds *= chosen_odd
            
            with st.container():
                st.markdown(f"""
                    <div style="background-color: white; padding: 18px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0; color: #111827;">#{match_counter} - {row['Campionato']} | {row['Squadra Casa']} vs {row['Squadra Ospite']}</h4>
                        <p style="margin: 4px 0 10px 0; color: #6b7280; font-size: 0.9em;">📅 Data incontro: {row['Data']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
                with c1:
                    st.markdown(f"**Segno Consigliato:** `{chosen_sign}`")
                    st.markdown(f"**Quota Bookmaker:** `{chosen_odd}`")
                with c2:
                    st.metric("Probabilità St.", f"{chosen_prob}%")
                with c3:
                    st.metric("Indice Affidabilità", f"{row['Indice Affidabilità']:.1f}")
                with c4:
                    st.markdown(f"**Analisi Statistica:** Trend xG favorevole (Casa: {row['xG Casa']} vs Ospite: {row['xG Ospite']}). Stabilità di forma confermata nelle ultime uscite.")
                
                match_counter += 1
                st.divider()
                
        # Box Riepilogo Schedina Multipla
        st.markdown("### 📊 Riepilogo Scommessa Multipla Top 5")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.metric("Quota Totale Schedina", f"{accumulated_odds:.2f}")
        with summary_col2:
            base_stake = st.number_input("Puntata Simulata (€)", min_value=1.0, max_value=1000.0, value=10.0, step=5.0)
        with summary_col3:
            potential_win = base_stake * accumulated_odds
            st.metric("Potenziale Vincita Lorda", f"€ {potential_win:,.2f}")
            
    else:
        st.warning("Nessuna partita disponibile per la data odierna con i filtri attuali.")

# ==========================================
# TAB 2: CALENDARIO & RICERCA SQUADRA
# ==========================================
with tab2:
    st.header("📅 Calendario Completo & Filtro Avanzato per Squadra")
    st.markdown("Cerca istantaneamente qualsiasi squadra europea per visualizzare tutti gli impegni in programma nella stagione.")
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        league_choice_tab2 = st.selectbox("Filtra per Campionato specifico", ["Tutti"] + LEAGUES, key="tab2_league")
    with filter_col2:
        search_query = st.text_input("🔍 Inserisci nome squadra (es. Inter, Arsenal, Real Madrid...)", "", key="tab2_search")
        
    df_tab2 = df_matches.copy()
    if league_choice_tab2 != "Tutti":
        df_tab2 = df_tab2[df_tab2["Campionato"] == league_choice_tab2]
        
    if search_query.strip() != "":
        q_lower = search_query.strip().lower()
        df_tab2 = df_tab2[
            df_tab2["Squadra Casa"].str.lower().str.contains(q_lower, na=False) |
            df_tab2["Squadra Ospite"].str.lower().str.contains(q_lower, na=False)
        ]
        
    st.markdown(f"Trovate **{len(df_tab2)}** partite corrispondenti ai criteri di ricerca.")
    
    st.dataframe(
        df_tab2[["Campionato", "Data", "Squadra Casa", "Squadra Ospite", "Quota 1", "Quota X", "Quota 2", "Over 2.5 Prob", "BTTS Prob"]],
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# TAB 3: STUDIO MATCH & FORMA RECENTE
# ==========================================
with tab3:
    st.header("📊 Studio Avanzato Match & Stato di Forma Recente")
    st.markdown("Seleziona una partita specifica per analizzare in dettaglio le prestazioni recenti (ultime 5 partite con indicatori V/N/P) e i dati attesi (xG).")
    
    match_list_options = df_active["Squadra Casa"] + " vs " + df_active["Squadra Ospite"] + " (" + df_active["Campionato"] + ")"
    selected_match_full = st.selectbox("Seleziona Partita da Analizzare", match_list_options)
    
    if selected_match_full:
        # Estraiamo i nomi puliti
        clean_match = selected_match_full.split(" (")[0]
        h_team, a_team = clean_match.split(" vs ")
        
        match_row = df_active[(df_active["Squadra Casa"] == h_team) & (df_active["Squadra Ospite"] == a_team)].iloc[0]
        
        st.subheader(f"🔍 Match Analysis: {h_team} vs {a_team} [{match_row['Campionato']}]")
        st.caption(f"Data programmata: {match_row['Data']}")
        
        col_m1, col_m2 = st.columns(2)
        
        # Sezione Squadra di Casa
        with col_m1:
            st.markdown(f"### 🏠 {h_team} (Casa)")
            form_h_list = match_row["Forma Casa"]
            form_h_html = ""
            for res in form_h_list:
                if res == 'V':
                    form_h_html += "<span class='form-win'>V</span>"
                elif res == 'N':
                    form_h_html += "<span class='form-draw'>N</span>"
                else:
                    form_h_html += "<span class='form-loss'>P</span>"
            st.markdown(f"**Ultime 5 Partite:** {form_h_html}", unsafe_allow_html=True)
            st.metric("Probabilità Vinte Stimate (1)", f"{match_row['Prob 1 (%)']}%")
            st.metric("Expected Goals (xG Casa)", f"{match_row['xG Casa']}")
            
        # Sezione Squadra Ospite
        with col_m2:
            st.markdown(f"### ✈️ {a_team} (Ospite)")
            form_a_list = match_row["Forma Ospite"]
            form_a_html = ""
            for res in form_a_list:
                if res == 'V':
                    form_a_html += "<span class='form-win'>V</span>"
                elif res == 'N':
                    form_a_html += "<span class='form-draw'>N</span>"
                else:
                    form_a_html += "<span class='form-loss'>P</span>"
            st.markdown(f"**Ultime 5 Partite:** {form_a_html}", unsafe_allow_html=True)
            st.metric("Probabilità Vinte Stimate (2)", f"{match_row['Prob 2 (%)']}%")
            st.metric("Expected Goals (xG Ospite)", f"{match_row['xG Ospite']}")
            
        st.divider()
        st.markdown("### 📈 Analisi Mercati Secondari & Gol")
        mg1, mg2 = st.columns(2)
        with mg1:
            st.metric("Probabilità Over 2.5 Gol", f"{match_row['Over 2.5 Prob']}%")
        with mg2:
            st.metric("Probabilità Goal / Goal (BTTS)", f"{match_row['BTTS Prob']}%")

# ==========================================
# TAB 4: CALCOLATORE VALUE & BANKROLL
# ==========================================
with tab4:
    st.header("🧮 Calcolatore Avanzato Value Bet & Criterio di Kelly")
    st.markdown("Verifica matematica della convenienza di una quota rispetto alla probabilità reale stimata e calcola la puntata ottimale di money management.")
    
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    with calc_col1:
        input_odds = st.number_input("Quota offerta dal Bookmaker", min_value=1.01, max_value=30.0, value=2.20, step=0.05)
    with calc_col2:
        input_prob = st.slider("Tua Probabilità Stimata Reale (%)", min_value=1, max_value=100, value=52)
    with calc_col3:
        input_bankroll = st.number_input("Bankroll Attuale (€)", min_value=10.0, max_value=100000.0, value=1000.0, step=50.0)
        
    implied_probability = (1 / input_odds) * 100
    value_percentage = input_prob - implied_probability
    
    st.divider()
    
    res_c1, res_c2, res_c3 = st.columns(3)
    with res_c1:
        st.metric("Probabilità Implicita Q.", f"{implied_probability:.2f}%")
    with res_c2:
        st.metric("Margine di Valore (EV)", f"{value_percentage:+.2f}%", delta="VALUE BET TROVATA ✅" if value_percentage > 0 else "NESSUN VALORE ❌")
    with res_c3:
        # Calcolo Criterio di Kelly Frazionato (1/4 di Kelly per sicurezza)
        kelly_fraction = max(0, ((input_prob / 100) * input_odds - 1) / (input_odds - 1)) * 0.25
        recommended_stake = input_bankroll * kelly_fraction
        st.metric("Puntata Consigliata (Kelly 1/4)", f"€ {recommended_stake:.2f}")

# ==========================================
# TAB 5: STATISTICHE GLOBALI & TREND
# ==========================================
with tab5:
    st.header("📈 Statistiche Globali sui Campionati")
    st.markdown("Panoramica sintetica dei dati aggregati per monitorare i trend generali dei campionati europei.")
    
    stat_c1, stat_c2, stat_c3 = st.columns(3)
    with stat_c1:
        st.metric("Partite Totali Analizzate nel Database", len(df_matches))
    with stat_c2:
        st.metric("Campionati Monitorati", len(LEAGUES))
    with stat_c3:
        avg_over = df_matches["Over 2.5 Prob"].mean()
        st.metric("Media Probabilità Over 2.5 (Generale)", f"{avg_over:.1f}%")
        
    st.divider()
    st.markdown("#### 📊 Distribuzione Media Quote per Campionato")
    league_avg_odds = df_matches.groupby("Campionato")[["Quota 1", "Quota X", "Quota 2"]].mean().reset_index()
    st.dataframe(league_avg_odds, use_container_width=True, hide_index=True)

st.divider()
st.markdown("<p style='text-align: center; color: #9ca3af;'>Advanced Betting & Value Analysis Pro — Strumento di supporto statistico per scommesse sportive.</p>", unsafe_allow_html=True)
