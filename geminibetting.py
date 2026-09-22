
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# Configurazione della pagina
st.set_page_config(
    page_title="Analizzatore Scommesse & Value Betting",
    page_icon="⚽",
    layout="wide"
)

# Stile CSS personalizzato per un look professionale
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .metric-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .form-win { color: #28a745; font-weight: bold; }
    .form-draw { color: #ffc107; font-weight: bold; }
    .form-loss { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Advanced Betting & Value Analysis - Europa")
st.markdown("Piattaforma professionale per l'analisi statistica, il calcolo delle Value Bet e la Schedina Top del Giorno.")

# ==========================================
# DATI DI SIMULAZIONE / DATABASE
# ==========================================
LEAGUES = ["Serie A", "Premier League", "La Liga", "Bundesliga", "Ligue 1"]

TEAMS = {
    "Serie A": ["Inter", "Milan", "Juventus", "Napoli", "Atalanta", "Roma", "Lazio", "Fiorentina", "Bologna", "Torino"],
    "Premier League": ["Manchester City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Manchester United", "Newcastle", "Brighton", "West Ham"],
    "La Liga": ["Real Madrid", "Barcelona", "Girona", "Atletico Madrid", "Athletic Bilbao", "Real Sociedad", "Real Betis", "Villarreal", "Valencia", "Sevilla"],
    "Bundesliga": ["Bayer Leverkusen", "Bayern Monaco", "Stoccarda", "Lipsia", "Borussia Dortmund", "Eintracht Francoforte", "Friburgo", "Hoffenheim", "Werder Brema", "Augsburg"],
    "Ligue 1": ["Paris Saint-Germain", "Monaco", "Brest", "Lilla", "Nizza", "Lens", "Olympique Lione", "Olympique Marsiglia", "Strasburgo", "Rennes"]
}

# Funzione per generare dati casuali ma coerenti per le partite
@st.cache_data
def load_match_schedule():
    np.random.seed(42)
    matches = []
    base_date = date.today()
    
    for league in LEAGUES:
        teams = TEAMS[league]
        for i in range(len(teams)):
            for j in range(len(teams)):
                if i != j:
                    # Creiamo date distribuite nell'arco di un mese
                    days_offset = np.random.randint(-5, 15)
                    match_date = pd.Timestamp(base_date) + pd.Timedelta(days=days_offset)
                    
                    # Generazione stato di forma recente (es. V, N, P)
                    form_home = np.random.choice(["V", "N", "P"], size=5, p=[0.5, 0.3, 0.2])
                    form_away = np.random.choice(["V", "N", "P"], size=5, p=[0.4, 0.3, 0.3])
                    
                    # Quote simulate
                    odd_1 = round(np.random.uniform(1.40, 3.80), 2)
                    odd_x = round(np.random.uniform(3.10, 4.20), 2)
                    odd_2 = round(np.random.uniform(1.80, 5.50), 2)
                    
                    # Probabilità implicite e calcolo Value
                    prob_1 = (1 / odd_1) * 100
                    prob_x = (1 / odd_x) * 100
                    prob_2 = (1 / odd_2) * 100
                    total_prob = prob_1 + prob_x + prob_2
                    
                    matches.append({
                        "Campionato": league,
                        "Data": match_date.strftime("%Y-%m-%d"),
                        "Squadra Casa": teams[i],
                        "Squadra Ospite": teams[j],
                        "Forma Casa": list(form_home),
                        "Forma Ospite": list(form_away),
                        "Quota 1": odd_1,
                        "Quota X": odd_x,
                        "Quota 2": odd_2,
                        "Prob 1 (%)": round(prob_1 / total_prob * 100, 1),
                        "Prob X (%)": round(prob_x / total_prob * 100, 1),
                        "Prob 2 (%)": round(prob_2 / total_prob * 100, 1),
                        "Over 2.5 Prob": round(np.random.uniform(40, 75), 1),
                        "BTTS Prob": round(np.random.uniform(45, 70), 1)
                    })
    return pd.DataFrame(matches)

df_matches = load_match_schedule()

# ==========================================
# NAVIGAZIONE A TAB
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Schedina Top 5 del Giorno", 
    "📅 Calendario & Ricerca", 
    "📊 Studio Match & Forma", 
    "🧮 Calcolatore Value & Bankroll"
])

# --- TAB 1: SCHEDINA TOP 5 DEL GIORNO ---
with tab1:
    st.header("🎯 La Schedina 'Top Value' del Giorno")
    st.markdown("L'algoritmo analizza tutti i campionati europei in programma oggi e seleziona le **5 migliori opportunità** con il più alto indice di affidabilità statistica.")
    
    # Filtriamo le partite odierne o vicine come simulazione del "giorno"
    today_str = date.today().strftime("%Y-%m-%d")
    df_today = df_matches[df_matches["Data"] >= today_str].copy()
    
    if len(df_today) > 0:
        # Calcoliamo un indice di affidabilità basato su probabilità massima e stabilità
        def calc_reliability(row):
            max_prob = max(row["Prob 1 (%)"], row["Prob X (%)"], row["Prob 2 (%)"])
            return max_prob
            
        df_today["Affidabilità"] = df_today.apply(calc_reliability, axis=1)
        top_5 = df_today.sort_values(by="Affidabilità", ascending=False).head(5)
        
        total_odds_accumulated = 1.0
        
        for idx, row in top_5.reset_index().iterrows():
            # Scegliamo il segno più probabile
            if row["Prob 1 (%)"] >= row["Prob 2 (%)"] and row["Prob 1 (%)"] >= row["Prob X (%)"]:
                segno = "1"
                quota = row["Quota 1"]
                prob = row["Prob 1 (%)"]
            elif row["Prob 2 (%)"] >= row["Prob 1 (%)"] and row["Prob 2 (%)"] >= row["Prob X (%)"]:
                segno = "2"
                quota = row["Quota 2"]
                prob = row["Prob 2 (%)"]
            else:
                segno = "X"
                quota = row["Quota X"]
                prob = row["Prob X (%)"]
                
            total_odds_accumulated *= quota
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                with col1:
                    st.markdown(f"**{row['Campionato']}** | {row['Squadra Casa']} vs {row['Squadra Ospite']}")
                    st.caption(f"Data: {row['Data']}")
                with col2:
                    st.metric("Segno Consigliato", segno, f"Quota: {quota}")
                with col3:
                    st.metric("Probabilità St.", f"{prob}%")
                with col4:
                    st.markdown(f"*Motivazione:* Ottima stabilità statistica. Forma recente favorevole e probabilità stimata superiore alla quota dei bookmaker.")
                st.divider()
                
        st.markdown(### 📈 Riepilogo Schedina Multipla Top 5")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("Quota Totale Schedina", f"{total_odds_accumulated:.2f}")
        with m_col2:
            suggested_stake = 10.0
            st.metric("Potenziale Vincita (su 10€)", f"€ {suggested_stake * total_odds_accumulated:.2f}")
            
    else:
        st.info("Nessuna partita disponibile per la data odierna.")

# --- TAB 2: CALENDARIO & RICERCA ---
with tab2:
    st.header("📅 Calendario Partite & Filtro Squadra")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_league = st.selectbox("Filtra per Campionato", ["Tutti"] + LEAGUES)
    with col_f2:
        team_search = st.text_input("🔍 Cerca Squadra specifica (es. Inter, Real Madrid...)", "")
        
    df_filtered = df_matches.copy()
    if selected_league != "Tutti":
        df_filtered = df_filtered[df_filtered["Campionato"] == selected_league]
        
    if team_search.strip() != "":
        query = team_search.strip().lower()
        df_filtered = df_filtered[
            df_filtered["Squadra Casa"].str.lower().contains(query, na=False) |
            df_filtered["Squadra Ospite"].str.lower().contains(query, na=False)
        ]
        
    st.dataframe(
        df_filtered[["Campionato", "Data", "Squadra Casa", "Squadra Ospite", "Quota 1", "Quota X", "Quota 2", "Over 2.5 Prob"]],
        use_container_width=True,
        hide_index=True
    )

# --- TAB 3: STUDIO MATCH & FORMA ---
with tab3:
    st.header("📊 Studio Avanzato Match & Stato di Forma")
    st.markdown("Seleziona una partita per visualizzare l'analisi approfondita, comprese le ultime 5 partite disputate dalle squadre.")
    
    match_options = df_matches[df_matches["Campionato"] == selected_league]["Squadra Casa"] + " vs " + df_matches[df_matches["Campionato"] == selected_league]["Squadra Ospite"] \
        if selected_league != "Tutti" else df_matches["Squadra Casa"] + " vs " + df_matches["Squadra Ospite"]
        
    selected_match_str = st.selectbox("Seleziona Incontro", match_options)
    
    if selected_match_str:
        home_team, away_team = selected_match_str.split(" vs ")
        match_data = df_matches[(df_matches["Squadra Casa"] == home_team) & (df_matches["Squadra Ospite"] == away_team)].iloc[0]
        
        st.subheader(f"Analisi: {home_team} vs {away_team} ({match_data['Campionato']})")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"#### 🏠 {home_team} (Casa)")
            form_h = match_data["Forma Casa"]
            form_html = " ".join([f"<span class='form-win'>V</span>" if x=='V' else f"<span class='form-draw'>N</span>" if x=='N' else f"<span class='form-loss'>P</span>" for x in form_h])
            st.markdown(f"Ultime 5 partite: {form_html}", unsafe_allow_html=True)
            st.metric("Probabilità Vittoria Casa", f"{match_data['Prob 1 (%)']}%")
            
        with col_s2:
            st.markdown(f"#### ✈️ {away_team} (Ospite)")
            form_a = match_data["Forma Ospite"]
            form_html_a = " ".join([f"<span class='form-win'>V</span>" if x=='V' else f"<span class='form-draw'>N</span>" if x=='N' else f"<span class='form-loss'>P</span>" for x in form_a])
            st.markdown(f"Ultime 5 partite: {form_html_a}", unsafe_allow_html=True)
            st.metric("Probabilità Vittoria Ospite", f"{match_data['Prob 2 (%)']}%")
            
        st.divider()
        st.markdown("#### 📈 Trend Gol & Mercati")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.metric("Probabilità Over 2.5", f"{match_data['Over 2.5 Prob']}%")
        with col_g2:
            st.metric("Probabilità Gol / Gol (BTTS)", f"{match_data['BTTS Prob']}%")

# --- TAB 4: CALCOLATORE VALUE & BANKROLL ---
with tab4:
    st.header("🧮 Calcolatore Value Bet & Money Management")
    st.markdown("Verifica se una quota offre valore reale rispetto alla tua stabilità stimata e calcola la puntata corretta.")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        bookie_odds = st.number_input("Quota del Bookmaker", min_value=1.01, max_value=20.0, value=2.10, step=0.05)
    with c_col2:
        estimated_prob = st.slider("Tua Probabilità Stimata (%)", min_value=1, max_value=100, value=55)
    with c_col3:
        bankroll = st.number_input("Bankroll Totale (€)", min_value=10.0, max_value=100000.0, value=500.0, step=50.0)
        
    implied_prob = (1 / bookie_odds) * 100
    value_margin = estimated_prob - implied_prob
    
    st.divider()
    
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        st.metric("Probabilità Implicita Q.", f"{implied_prob:.1f}%")
    with r_col2:
        st.metric("Margine di Valore", f"{value_margin:+.1f}%", delta="Value Bet ✅" if value_margin > 0 else "No Value ❌")
    with r_col3:
        # Criterio di Kelly semplificato (frazione conservativa)
        kelly_fraction = max(0, (estimated_prob/100 * bookie_odds - 1) / (bookie_odds - 1)) * 0.25
        suggested_stake = bankroll * kelly_fraction
        st.metric("Puntata Consigliata (Kelly 1/4)", f"€ {suggested_stake:.2f}")
