import math
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Pro Football Betting & Deep Analytics",
    layout="wide",
    page_icon="⚽",
)

# --- GESTIONE DINAMICA TEMA (DARK / LIGHT MODE) ---
st.sidebar.markdown("### ⚙️ Pannello di Controllo", unsafe_allow_html=True)

tema_selezionato = st.sidebar.radio(
    "🎨 Tema Grafico", ["🌙 Dark Mode", "☀️ Light Mode"], horizontal=True
)

if tema_selezionato == "🌙 Dark Mode":
    bg_app = "#0b0f19"
    text_app = "#f8fafc"
    card_bg = "linear-gradient(135deg, #111827 0%, #1f2937 100%)"
    card_border = "#374151"
    analysis_bg = "#111827"
    metric_bg = "#1f2937"
    metric_border = "#4b5563"
    text_muted = "#94a3b8"
    plotly_template = "plotly_dark"
    radio_bg = "#1f2937"
    radio_text = "#ffffff"
else:
    bg_app = "#f8fafc"
    text_app = "#0f172a"
    card_bg = "linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)"
    card_border = "#cbd5e1"
    analysis_bg = "#ffffff"
    metric_bg = "#f1f5f9"
    metric_border = "#e2e8f0"
    text_muted = "#64748b"
    plotly_template = "plotly"
    radio_bg = "#e2e8f0"
    radio_text = "#0f172a"

# Iniezione Stile CSS Dinamico
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {text_app}; }}
    
    .match-card {{ 
        background: {card_bg}; 
        padding: 20px; 
        border-radius: 14px; 
        border: 1px solid {card_border}; 
        margin-bottom: 14px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease;
    }}
    .match-card:hover {{
        border-color: #38bdf8;
    }}
    
    .analysis-container {{ 
        background-color: {analysis_bg}; 
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid {card_border}; 
        margin-top: 25px; 
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); 
    }}
    
    .metric-box {{ 
        background: {metric_bg}; 
        padding: 18px; 
        border-radius: 12px; 
        border: 1px solid {metric_border}; 
        text-align: center; 
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.02);
    }}
    
    .value-box {{ 
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); 
        border-left: 6px solid #10b981; 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 20px; 
        color: #ecfdf5; 
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }}
    .no-value-box {{ 
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); 
        border-left: 6px solid #ef4444; 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 20px; 
        color: #fef2f2; 
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
    }}
    
    div.row-widget.stRadio div[role="radiogroup"] label p {{
        color: {radio_text} !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }}
    div.row-widget.stRadio div[role="radiogroup"] label {{
        background-color: {radio_bg};
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid {card_border};
        margin-right: 8px;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# Header principale
st.markdown(
    f"<h1 style='text-align: center; color: {text_app}; font-weight: 800;'>⚽ PRO BETTING STUDIO & ANALYTICS</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align: center; color: {text_muted}; font-size: 16px; margin-bottom: 30px;'>Piattaforma professionale di analisi statistica calcistica basata su Poisson, xG, Value Betting, AI Smart Acca & Simulazioni Monte Carlo.</p>",
    unsafe_allow_html=True,
)

LEAGUES = {
    "Serie A (Italia) [Club]": ("SA", "football-data"),
    "Premier League (Inghilterra) [Club]": ("PL", "football-data"),
    "La Liga (Spagna) [Club]": ("PD", "football-data"),
    "Bundesliga (Germania) [Club]": ("BL1", "football-data"),
    "Ligue 1 (Francia) [Club]": ("FL1", "football-data"),
    "Eredivisie (Olanda) [Club]": ("DED", "football-data"),
    "Champions League [Club]": ("CL", "football-data"),
    "UEFA Nations League [Nazionali]": ("10", "api-football"), # ID 10 tipicamente associato alla Nations League su API-Football
}

api_key = st.sidebar.text_input(
    "🔑 API Key (football-data.org - Club)", type="password"
)
api_key_nazionali = st.sidebar.text_input(
    "🔑 API Key (API-Football - Nazionali)", type="password"
)

st.sidebar.markdown("---")
campionato_scelto = st.sidebar.selectbox(
    "🏆 Seleziona Campionato / Torneo", list(LEAGUES.keys())
)
codice_lega, tipo_fonte = LEAGUES[campionato_scelto]

tab_calendario, tab_classifica, tab_value, tab_grafici, tab_ai_schedine, tab_value_finder, tab_monte_carlo = st.tabs([
    "📅 Calendario & Studio Match",
    "🏆 Classifica & Export",
    "🔍 Calcolatore Value Bet",
    "📊 Grafici & Trend",
    "🤖 Schedine Smart & AI",
    "⚡ Value Finder",
    "🎲 Simulatore Monte Carlo"
])


@st.cache_data(ttl=3600)
def scarica_dati_club(chiave, league_code):
    if not chiave:
        return None
    url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"
    headers = {"X-Auth-Token": chiave}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)
def scarica_classifica_club(chiave, league_code):
    if not chiave:
        return None
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": chiave}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)
def scarica_dati_nazionali(chiave, league_id):
    if not chiave:
        return None
    # Endpoint ufficiale API-Football (v3) per le partite della stagione corrente
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season=2026"
    headers = {
        "x-rapidapi-key": chiave,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)
def scarica_classifica_nazionali(chiave, league_id):
    if not chiave:
        return None
    url = f"https://v3.football.api-sports.io/standings?league={league_id}&season=2026"
    headers = {
        "x-rapidapi-key": chiave,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)


def calcola_forma_recente(matches_list, nome_squadra, is_api_football=False):
    partite_squadra = []
    for m in matches_list:
        if not is_api_football:
            if m["status"] == "FINISHED":
                h = m["homeTeam"]["name"]
                a = m["awayTeam"]["name"]
                if h == nome_squadra or a == nome_squadra:
                    gh = m["score"]["fullTime"].get("home", 0)
                    ga = m["score"]["fullTime"].get("away", 0)
                    if gh is not None and ga is not None:
                        if h == nome_squadra:
                            res = "V" if gh > ga else ("P" if gh == ga else "S")
                        else:
                            res = "V" if ga > gh else ("P" if ga == gh else "S")
                        partite_squadra.append(res)
        else:
            if m.get("fixture", {}).get("status", {}).get("short") == "FT":
                h = m["teams"]["home"]["name"]
                a = m["teams"]["away"]["name"]
                if h == nome_squadra or a == nome_squadra:
                    gh = m["goals"]["home"]
                    ga = m["goals"]["away"]
                    if gh is not None and ga is not None:
                        if h == nome_squadra:
                            res = "V" if gh > ga else ("P" if gh == ga else "S")
                        else:
                            res = "V" if ga > gh else ("P" if ga == gh else "S")
                        partite_squadra.append(res)
    ultime = partite_squadra[-5:] if len(partite_squadra) >= 5 else partite_squadra
    return "".join(ultime) if ultime else "N/D"


statistiche_squadre = {}
matches_raw = []

# Caricamento dati in base alla fonte selezionata
if tipo_fonte == "football-data" and api_key:
    dati = scarica_dati_club(api_key, codice_lega)
    dati_classifica = scarica_classifica_club(api_key, codice_lega)

    if dati and "matches" in dati:
        matches_raw = dati["matches"]

    if dati_classifica and "standings" in dati_classifica:
        for s in dati_classifica["standings"]:
            table_data = s.get("table", [])
            for riga in table_data:
                nome_sq = riga["team"]["name"]
                giocate = max(riga["playedGames"], 1)
                gf = riga["goalsFor"]
                gs = riga["goalsAgainst"]
                statistiche_squadre[nome_sq] = {
                    "media_gf": gf / giocate,
                    "media_gs": gs / giocate,
                    "punti": riga["points"],
                    "forma": calcola_forma_recente(matches_raw, nome_sq, is_api_football=False),
                }

elif tipo_fonte == "api-football" and api_key_nazionali:
    dati_naz = scarica_dati_nazionali(api_key_nazionali, codice_lega)
    dati_classifica_naz = scarica_classifica_nazionali(api_key_nazionali, codice_lega)

    if dati_naz and "response" in dati_naz:
        matches_raw = dati_naz["response"]

    if dati_classifica_naz and "response" in dati_classifica_naz:
        for item in dati_classifica_naz["response"]:
            for standing_group in item.get("league", {}).get("standings", []):
                for riga in standing_group:
                    nome_sq = riga["team"]["name"]
                    all_p = riga.get("all", {})
                    giocate = max(all_p.get("played", 1), 1)
                    gf = all_p.get("goals", {}).get("for", 0)
                    gs = all_p.get("goals", {}).get("against", 0)
                    statistiche_squadre[nome_sq] = {
                        "media_gf": gf / giocate,
                        "media_gs": gs / giocate,
                        "punti": riga.get("points", 0),
                        "forma": calcola_forma_recente(matches_raw, nome_sq, is_api_football=True),
                    }


# --- TAB 1: CALENDARIO E STUDIO STATISTICO ---
with tab_calendario:
    chiave_attiva = api_key if tipo_fonte == "football-data" else api_key_nazionali
    if chiave_attiva:
        if matches_raw:
            lista = []
            for m in matches_raw:
                if tipo_fonte == "football-data":
                    g_casa = m["score"]["fullTime"].get("home") if m.get("score") and m["score"].get("fullTime") else None
                    g_trasf = m["score"]["fullTime"].get("away") if m.get("score") and m["score"].get("fullTime") else None
                    lista.append({
                        "giornata": m.get("matchday", 0),
                        "casa": m["homeTeam"]["name"],
                        "trasferta": m["awayTeam"]["name"],
                        "data": m["utcDate"][:10],
                        "ora": m["utcDate"][11:16],
                        "gol_casa": g_casa if g_casa is not None else "-",
                        "gol_trasf": g_trasf if g_trasf is not None else "-",
                        "stato": m["status"],
                    })
                else:
                    fixture_info = m.get("fixture", {})
                    teams_info = m.get("teams", {})
                    goals_info = m.get("goals", {})
                    
                    g_casa = goals_info.get("home")
                    g_trasf = goals_info.get("away")
                    
                    data_utc = fixture_info.get("date", "2026-01-01T00:00:00")
                    lista.append({
                        "giornata": 1, # API-Football raggruppa spesso per round testuale
                        "casa": teams_info.get("home", {}).get("name", "Casa"),
                        "trasferta": teams_info.get("away", {}).get("name", "Ospiti"),
                        "data": data_utc[:10],
                        "ora": data_utc[11:16],
                        "gol_casa": g_casa if g_casa is not None else "-",
                        "gol_trasf": g_trasf if g_trasf is not None else "-",
                        "stato": fixture_info.get("status", {}).get("short", "NS"),
                    })

            df = pd.DataFrame(lista)
            giornate = sorted(df["giornata"].unique())

            if len(giornate) > 0:
                col_g1, col_g2 = st.columns([2, 2])
                with col_g1:
                    giornata_sel = st.selectbox(
                        "📅 Seleziona Giornata / Turno",
                        giornate,
                        index=min(len(giornate) - 1, 0),
                    )
                st.markdown("<br>", unsafe_allow_html=True)

                partite_filtrate = df[df["giornata"] == giornata_sel]

                st.markdown(f"### 📌 Match in Programma")

                for idx, row in partite_filtrate.iterrows():
                    with st.container():
                        st.markdown('<div class="match-card">', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.markdown(
                                f"🏠 **{row['casa']}**<br>✈️ **{row['trasferta']}**<br><span style='color:{text_muted}; font-size:12px;'>📅 {row['data']} ore {row['ora']}</span>",
                                unsafe_allow_html=True,
                            )
                        with c2:
                            st.markdown(
                                f"<br>Risultato: <b style='font-size:18px; color:#38bdf8;'>{row['gol_casa']} - {row['gol_trasf']}</b><br><span style='font-size:11px; color:{text_muted};'>Stato: {row['stato']}</span>",
                                unsafe_allow_html=True,
                            )
                        with c3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("📊 Studio Poisson", key=f"btn_match_{idx}"):
                                st.session_state["match_attivo"] = row
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Nessun match trovato o chiave API non valida.")
    else:
        st.info("👈 Inserisci la chiave API corrispondente nella barra laterale per sbloccare i calendari.")

    if "match_attivo" in st.session_state:
        m = st.session_state["match_attivo"]
        sq_casa = m["casa"]
        sq_trasf = m["trasferta"]

        if sq_casa in statistiche_squadre and sq_trasf in statistiche_squadre:
            lam_c = statistiche_squadre[sq_casa]["media_gf"]
            lam_t = statistiche_squadre[sq_trasf]["media_gf"]
            forma_casa = statistiche_squadre[sq_casa]["forma"]
            forma_trasf = statistiche_squadre[sq_trasf]["forma"]
        else:
            lam_c, lam_t = 1.4, 1.1
            forma_casa, forma_trasf = "N/D", "N/D"

        max_gol = 5
        p_casa, p_pareggio, p_trasferta = 0.0, 0.0, 0.0

        for r_c in range(max_gol + 1):
            for r_t in range(max_gol + 1):
                prob = poisson_prob(lam_c, r_c) * poisson_prob(lam_t, r_t)
                if r_c > r_t:
                    p_casa += prob
                elif r_c == r_t:
                    p_pareggio += prob
                else:
                    p_trasferta += prob

        tot_1x2 = p_casa + p_pareggio + p_trasferta
        p_c_1x2 = round((p_casa / tot_1x2) * 100, 1)
        p_p_1x2 = round((p_pareggio / tot_1x2) * 100, 1)
        p_t_1x2 = round((p_trasferta / tot_1x2) * 100, 1)

        xg_stimati = round(lam_c + lam_t, 2)

        risultati_esatti_list = []
        for r_c in range(4):
            for r_t in range(4):
                p_res = poisson_prob(lam_c, r_c) * poisson_prob(lam_t, r_t) / tot_1x2
                risultati_esatti_list.append((f"{r_c} - {r_t}", p_res * 100))
        risultati_esatti_list.sort(key=lambda x: x[1], reverse=True)

        btts_rate = round(
            sum(
                poisson_prob(lam_c, r_c) * poisson_prob(lam_t, r_t)
                for r_c in range(1, 5)
                for r_t in range(1, 5)
            )
            * 100,
            1,
        )
        over_25_rate = round(
            sum(
                poisson_prob(lam_c, r_c) * poisson_prob(lam_t, r_t)
                for r_c in range(6)
                for r_t in range(6)
                if r_c + r_t > 2.5
            )
            * 100,
            1,
        )

        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown(f"<h2>🔬 Analisi Scientifica: {sq_casa} vs {sq_trasf}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color: {text_muted};'>Forma Recente (Ultime 5): 🏠 <b>{sq_casa}</b> [{forma_casa}] &nbsp;|&nbsp; ✈️ <b>{sq_trasf}</b> [{forma_trasf}]</p>",
            unsafe_allow_html=True,
        )

        focus_mercato = st.radio(
            "🎯 Scegli l'Ambito di Analisi",
            [
                "Panoramica Poisson",
                "1X2 & Doppia Chance",
                "Gol / No Gol & Over/Under",
                "Risultati Esatti",
            ],
            horizontal=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if focus_mercato == "Panoramica Poisson":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="metric-box"><b>xG Casa (Lambda)</b><br><span style="font-size:24px; color:#38bdf8;">{lam_c:.2f}</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box"><b>xG Trasf (Lambda)</b><br><span style="font-size:24px; color:#38bdf8;">{lam_t:.2f}</span></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box"><b>xG Totali Match</b><br><span style="font-size:24px; color:#38bdf8;">{xg_stimati}</span></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="metric-box"><b>Over 2.5 Prob.</b><br><span style="font-size:24px; color:#38bdf8;">{over_25_rate}%</span></div>', unsafe_allow_html=True)

        elif focus_mercato == "1X2 & Doppia Chance":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="metric-box"><b>Segno 1</b><br><span style="font-size:22px; color:#38bdf8;">{p_c_1x2}%</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box"><b>Segno X</b><br><span style="font-size:22px; color:#38bdf8;">{p_p_1x2}%</span></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box"><b>Segno 2</b><br><span style="font-size:22px; color:#38bdf8;">{p_t_1x2}%</span></div>', unsafe_allow_html=True)
            with col4:
                dc = "1X" if p_c_1x2 >= p_t_1x2 else ("X2" if p_t_1x2 > p_c_1x2 else "12")
                st.markdown(f'<div class="metric-box"><b>Doppia Chance</b><br><span style="font-size:22px; color:#10b981;">{dc}</span></div>', unsafe_allow_html=True)

        elif focus_mercato == "Gol / No Gol & Over/Under":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-box"><b>BTTS (Gol / Gol)</b><br><span style="font-size:22px; color:#38bdf8;">{btts_rate}%</span></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box"><b>Over 2.5</b><br><span style="font-size:22px; color:#38bdf8;">{over_25_rate}%</span></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box"><b>Under 2.5</b><br><span style="font-size:22px; color:#38bdf8;">{round(100 - over_25_rate, 1)}%</span></div>', unsafe_allow_html=True)

        elif focus_mercato == "Risultati Esatti":
            col1, col2, col3, col4 = st.columns(4)
            for i in range(4):
                res_str, prob_val = risultati_esatti_list[i]
                with [col1, col2, col3, col4][i]:
                    st.markdown(f'<div class="metric-box"><b>Top {i+1}</b><br><span style="font-size:22px; color:#10b981;">{res_str}</span><br><span style="font-size:12px; color:{text_muted};">{prob_val:.1f}%</span></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: CLASSIFICA & EXPORT ---
with tab_classifica:
    st.subheader(f"🏆 Classifica / Gironi - {campionato_scelto}")
    if chiave_attiva:
        if statistiche_squadre:
            lista_classifica = []
            for sq, dati_sq in sorted(statistiche_squadre.items(), key=lambda x: x[1]["punti"], reverse=True):
                lista_classifica.append({
                    "Squadra": sq,
                    "Punti": dati_sq["punti"],
                    "Media GF": round(dati_sq["media_gf"], 2),
                    "Media GS": round(dati_sq["media_gs"], 2),
                    "Forma": dati_sq["forma"]
                })
            df_classifica = pd.DataFrame(lista_classifica)
            st.dataframe(df_classifica, use_container_width=True, hide_index=True)
            
            csv_data = df_classifica.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Scarica Classifica / Statistiche - CSV",
                data=csv_data,
                file_name=f"classifica_{codice_lega}.csv",
                mime="text/csv",
            )
        else:
            st.warning("Classifica non disponibile per questa competizione.")
    else:
        st.info("👈 Inserisci la chiave API nella barra laterale.")

# --- TAB 3: CALCOLATORE VALUE BET ---
with tab_value:
    st.subheader("🔍 Analizzatore di Valore delle Quote (Value Bet)")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        probabilita_stimata = st.slider("Probabilità stimata (%)", 1.0, 100.0, 50.0, 0.5)
    with col_v2:
        quota_bookmaker = st.number_input("Quota offerta dal bookmaker", 1.01, 50.0, 2.00, 0.01)

    quota_equa = 100 / probabilita_stimata
    valore_atteso = ((probabilita_stimata / 100) * quota_bookmaker) - 1

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric(label="Quota Statistica Equa", value=f"{quota_equa:.2f}")
    with col_res2:
        st.metric(label="Valore Atteso (EV)", value=f"{valore_atteso * 100:+.2f}%")

    if quota_bookmaker > quota_equa:
        st.markdown(
            f"""
                <div class="value-box">
                    <h4>🔥 OTTIMA VALUE BET TROVATA!</h4>
                    <p>La quota (<b>{quota_bookmaker}</b>) è superiore alla quota equa stimata (<b>{quota_equa:.2f}</b>).</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
                <div class="no-value-box">
                    <h4>❌ NESSUN VALORE (SCONSIGLIATO)</h4>
                    <p>La quota offerta non compensa il rischio stimato.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

# --- TAB 4: GRAFICI & TREND ---
with tab_grafici:
    st.subheader(f"📊 Trend & Panoramica - {campionato_scelto}")
    if chiave_attiva and statistiche_squadre:
        lista_grafico = [{"Squadra": k, "Punti": v["punti"], "Gol Fatti (Medio)": v["media_gf"]} for k, v in statistiche_squadre.items()]
        df_g = pd.DataFrame(lista_grafico)
        fig_punti = px.bar(df_g, x="Squadra", y="Punti", color="Punti", color_continuous_scale="Viridis", template=plotly_template)
        fig_punti.update_layout(xaxis_tickangle=-45, margin=dict(l=10, r=10, t=10, b=10), height=420)
        st.plotly_chart(fig_punti, use_container_width=True)
    else:
        st.info("Carica i dati tramite chiave API per visualizzare i grafici.")


def genera_dataset_valore(matches_list, stats_dict):
    righe_valore = []
    if not matches_list or not stats_dict:
        return pd.DataFrame()
    for m in matches_list:
        if "homeTeam" in m:
            h = m["homeTeam"]["name"]
            a = m["awayTeam"]["name"]
            giornata = m.get("matchday", 1)
            data_m = m["utcDate"][:10]
        else:
            h = m["teams"]["home"]["name"]
            a = m["teams"]["away"]["name"]
            giornata = 1
            data_m = m.get("fixture", {}).get("date", "2026-01-01")[:10]

        if h in stats_dict and a in stats_dict:
            lam_c = stats_dict[h]["media_gf"]
            lam_t = stats_dict[a]["media_gf"]
            
            max_g = 4
            pc, pp, pt = 0.0, 0.0, 0.0
            for rc in range(max_g + 1):
                for rt in range(max_g + 1):
                    pr = poisson_prob(lam_c, rc) * poisson_prob(lam_t, rt)
                    if rc > rt: pc += pr
                    elif rc == rt: pp += pr
                    else: pt += pr
            tot = pc + pp + pt
            pc, pp, pt = (pc/tot, pp/tot, pt/tot) if tot > 0 else (0.33, 0.33, 0.34)

            over_prob = sum(poisson_prob(lam_c, rc) * poisson_prob(lam_t, rt) for rc in range(5) for rt in range(5) if rc + rt > 2.5)
            
            if pc >= pt and pc >= 0.45:
                mercato, selezione, prob_mod = "1X2", f"1 ({h})", pc
            elif pt > pc and pt >= 0.40:
                mercato, selezione, prob_mod = "1X2", f"2 ({a})", pt
            elif over_prob > 0.55:
                mercato, selezione, prob_mod = "Over/Under", "Over 2.5", over_prob
            else:
                mercato, selezione, prob_mod = "1X2", "X (Pareggio)", pp

            quota_book = round(1.05 / max(prob_mod, 0.1), 2)
            edge = round(((prob_mod * quota_book) - 1) * 100, 1)
            rischio = "Basso" if quota_book < 1.50 and prob_mod > 0.65 else ("Medio" if 1.50 <= quota_book <= 2.20 else "Alto")

            righe_valore.append({
                "Partita": f"{h} - {a}",
                "Giornata": giornata,
                "Mercato": mercato,
                "Selezione": selezione,
                "Prob_Modello": round(prob_mod * 100, 1),
                "Quota_Book": quota_book,
                "Edge": edge,
                "Rischio": rischio,
                "Data": data_m
            })
    return pd.DataFrame(righe_valore)

df_valore_generato = genera_dataset_valore(matches_raw, statistiche_squadre)

# --- TAB 5: SCHEDINE SMART & AI ---
with tab_ai_schedine:
    st.subheader("🤖 Generatore Automatico di Schedine & Accumulatori Smart")
    if not df_valore_generato.empty:
        giornate_disponibili = sorted(df_valore_generato["Giornata"].unique())
        giornata_scelta = st.selectbox("📅 Seleziona Turno / Giornata", giornate_disponibili)
        
        df_giornata = df_valore_generato[df_valore_generato["Giornata"] == giornata_scelta]
        num_eventi = st.slider("🔢 Numero di eventi in combo", 2, 5, min(3, max(2, len(df_giornata))))
        
        subset_smart = df_giornata.head(num_eventi)
        if not subset_smart.empty:
            quota_totale_combo = np.prod(subset_smart["Quota_Book"].values)
            prob_complessiva_stimata = np.prod(subset_smart["Prob_Modello"].values / 100.0) * 100

            m1, m2, m3 = st.columns(3)
            m1.metric("Eventi in Combo", len(subset_smart))
            m2.metric("Quota Totale Stimata", f"{quota_totale_combo:.2f}")
            m3.metric("Probabilità Combinata Modello", f"{prob_complessiva_stimata:.1f}%")

            for idx, row in subset_smart.iterrows():
                st.markdown(
                    f"""<div style='background:{metric_bg}; padding:12px 18px; border-radius:10px; margin-bottom:8px; border:1px solid {card_border};'>
                    <b>{row['Partita']}</b> &nbsp;|&nbsp; Pronostico: <span style='color:#38bdf8;'><b>{row['Selezione']}</b></span> 
                    &nbsp;|&nbsp; Quota: <b>{row['Quota_Book']}</b> &nbsp;|&nbsp; Edge: <span style='color:#10b981;'><b>+{row['Edge']}%</b></span>
                    </div>""",
                    unsafe_allow_html=True
                )
    else:
        st.info("⚠️ Carica i dati tramite API Key per generare le schedine smart.")

# --- TAB 6: VALUE FINDER AUTOMATICO ---
with tab_value_finder:
    st.subheader("⚡ Scanner Value Finder Automatico")
    if not df_valore_generato.empty:
        filtro_edge_min = st.slider("Filtro Edge Statistico Minimo (%)", -5.0, 25.0, 2.0, 0.5)
        df_vf_filtrato = df_valore_generato[df_valore_generato["Edge"] >= filtro_edge_min].sort_values(by="Edge", ascending=False)
        st.dataframe(df_vf_filtrato, use_container_width=True, hide_index=True)
    else:
        st.info("⚠️ Carica i dati tramite API Key per avviare lo scanner.")

# --- TAB 7: SIMULATORE MONTE CARLO & PLAYER IMPACT ---
with tab_monte_carlo:
    st.subheader("🎲 Simulatore Stocastico Monte Carlo, Player Impact & Match Flow (Angoli & Tiri)")
    if statistiche_squadre:
        nomi_squadre = sorted(list(statistiche_squadre.keys()))
        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            sq_c_sim = st.selectbox("🏠 Squadra di Casa", nomi_squadre, index=0, key="sim_casa")
        with col_mc2:
            sq_t_sim = st.selectbox("✈️ Squadra Ospite", nomi_squadre, index=min(1, len(nomi_squadre)-1), key="sim_trasf")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            num_iterazioni = st.selectbox("Numero di Simulazioni", [1000, 5000, 10000], index=1)
        with col_p2:
            impatto_assenza_casa = st.slider(f"Modificatore Offensivo {sq_c_sim}", -30, 30, 0, 5, format="%d%%", key="imp_c")
        with col_p3:
            impatto_assenza_trasf = st.slider(f"Modificatore Offensivo {sq_t_sim}", -30, 30, 0, 5, format="%d%%", key="imp_t")

        if st.button("🚀 Avvia Simulazione Monte Carlo Avanzata"):
            lam_base_c = statistiche_squadre[sq_c_sim]["media_gf"]
            lam_base_t = statistiche_squadre[sq_t_sim]["media_gf"]

            lam_effettiva_c = max(0.1, lam_base_c * (1 + impatto_assenza_casa / 100.0))
            lam_effettiva_t = max(0.1, lam_base_t * (1 + impatto_assenza_trasf / 100.0))

            tiri_base_c = max(2.5, lam_effettiva_c * 3.2)
            tiri_base_t = max(2.0, lam_effettiva_t * 3.0)

            corner_base_c = max(3.0, 4.2 + (lam_effettiva_c - 1.2) * 1.5)
            corner_base_t = max(2.5, 3.8 + (lam_effettiva_t - 1.1) * 1.4)

            np.random.seed(42)
            gol_casa_sim = np.random.poisson(lam_effettiva_c, num_iterazioni)
            gol_trasf_sim = np.random.poisson(lam_effettiva_t, num_iterazioni)

            tiri_casa_sim = np.random.poisson(tiri_base_c, num_iterazioni)
            tiri_trasf_sim = np.random.poisson(tiri_base_t, num_iterazioni)

            corner_casa_sim = np.random.poisson(corner_base_c, num_iterazioni)
            corner_trasf_sim = np.random.poisson(corner_base_t, num_iterazioni)

            vittorie_casa = np.sum(gol_casa_sim > gol_trasf_sim)
            pareggi = np.sum(gol_casa_sim == gol_trasf_sim)
            vittorie_trasf = np.sum(gol_casa_sim < gol_trasf_sim)

            prob_c = (vittorie_casa / num_iterazioni) * 100
            prob_p = (pareggi / num_iterazioni) * 100
            prob_t = (vittorie_trasf / num_iterazioni) * 100

            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric(f"Vittoria {sq_c_sim} (1)", f"{prob_c:.1f}%")
            mc2.metric("Pareggio (X)", f"{prob_p:.1f}%")
            mc3.metric(f"Vittoria {sq_t_sim} (2)", f"{prob_t:.1f}%")

            matrice_risultati = np.zeros((5, 5))
            for gc, gt in zip(gol_casa_sim, gol_trasf_sim):
                if gc <= 4 and gt <= 4:
                    matrice_risultati[gc, gt] += 1
            matrice_risultati_perc = (matrice_risultati / num_iterazioni) * 100

            fig_heatmap = px.imshow(
                matrice_risultati_perc[:5, :5],
                labels=dict(x=f"Gol {sq_t_sim}", y=f"Gol {sq_c_sim}", color="Probabilità (%)"),
                x=["0", "1", "2", "3", "4+"],
                y=["0", "1", "2", "3", "4+"],
                text_auto=".1f",
                color_continuous_scale="Teal",
                template=plotly_template
            )
            fig_heatmap.update_layout(height=430, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_heatmap, use_container_width=True)

            tot_tiri_match = np.mean(tiri_casa_sim) + np.mean(tiri_trasf_sim)
            tot_corner_match = np.mean(corner_casa_sim) + np.mean(corner_trasf_sim)

            st.markdown(
                f"""
                <div class="analysis-container">
                    <h4>💡 Insight di Sintesi dell'IA (Monte Carlo & Match Flow)</h4>
                    <ul>
                        <li><b>Aspettativa Gol Corretta ({sq_c_sim}):</b> {lam_effettiva_c:.2f}</li>
                        <li><b>Aspettativa Gol Corretta ({sq_t_sim}):</b> {lam_effettiva_t:.2f}</li>
                        <li><b>Volume Offensivo Stimato:</b> Circa <b>{tot_tiri_match:.1f} tiri nello specchio</b> e <b>{tot_corner_match:.1f} calci d'angolo</b> complessivi.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("⚠️ Carica i dati delle squadre per avviare le simulazioni Monte Carlo.")
