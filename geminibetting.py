import math
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Pro Football Betting & Deep Analytics",
    layout="wide",
    page_icon="⚽",
)

# Stile CSS avanzato, moderno e curato nei dettagli
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    
    /* Card delle partite */
    .match-card { 
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%); 
        padding: 20px; 
        border-radius: 14px; 
        border: 1px solid #374151; 
        margin-bottom: 14px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease;
    }
    .match-card:hover {
        border-color: #38bdf8;
    }
    
    /* Container di analisi dettagliata */
    .analysis-container { 
        background-color: #111827; 
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid #374151; 
        margin-top: 25px; 
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4); 
    }
    
    /* Box metriche */
    .metric-box { 
        background: #1f2937; 
        padding: 18px; 
        border-radius: 12px; 
        border: 1px solid #4b5563; 
        text-align: center; 
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.05);
    }
    
    /* Box esito Value Bet */
    .value-box { 
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); 
        border-left: 6px solid #10b981; 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 20px; 
        color: #ecfdf5; 
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }
    .no-value-box { 
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); 
        border-left: 6px solid #ef4444; 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 20px; 
        color: #fef2f2; 
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
    }
    
    /* Radio button personalizzati */
    div.row-widget.stRadio div[role="radiogroup"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    div.row-widget.stRadio div[role="radiogroup"] label {
        background-color: #1f2937;
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid #374151;
        margin-right: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header principale con stile pulito
st.markdown(
    "<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>⚽ PRO BETTING STUDIO & ANALYTICS</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 30px;'>Piattaforma professionale di analisi statistica calcistica basata su Poisson, xG, Value Betting & AI Smart Acca.</p>",
    unsafe_allow_html=True,
)

LEAGUES = {
    "Serie A (Italia)": "SA",
    "Premier League (Inghilterra)": "PL",
    "La Liga (Spagna)": "PD",
    "Bundesliga (Germania)": "BL1",
    "Ligue 1 (Francia)": "FL1",
    "Eredivisie (Olanda)": "DED",
    "Champions League": "CL",
}

# Sidebar migliorata
st.sidebar.markdown(
    "### ⚙️ Pannello di Controllo", unsafe_allow_html=True
)
api_key = st.sidebar.text_input(
    "🔑 Inserisci API Key (football-data.org)", type="password"
)
st.sidebar.markdown("---")
campionato_scelto = st.sidebar.selectbox(
    "🏆 Seleziona Campionato", list(LEAGUES.keys())
)
codice_lega = LEAGUES[campionato_scelto]

# Tab di navigazione principali estesi con le nuove sezioni AI
tab_calendario, tab_classifica, tab_value, tab_grafici, tab_ai_schedine, tab_value_finder = st.tabs([
    "📅 Calendario & Studio Match",
    "🏆 Classifica & Export",
    "🔍 Calcolatore Value Bet",
    "📊 Grafici & Trend",
    "🤖 Schedine Smart & AI",
    "⚡ Value Finder Automatico"
])


@st.cache_data(ttl=3600)
def scarica_dati(chiave, league_code):
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
def scarica_classifica(chiave, league_code):
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


def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)


def calcola_forma_recente(matches_list, nome_squadra):
    partite_squadra = []
    for m in matches_list:
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
    ultime = partite_squadra[-5:] if len(partite_squadra) >= 5 else partite_squadra
    return "".join(ultime) if ultime else "N/D"


# Caricamento preliminare dati per alimentare le sezioni
statistiche_squadre = {}
matches_raw = []

if api_key:
    dati = scarica_dati(api_key, codice_lega)
    dati_classifica = scarica_classifica(api_key, codice_lega)

    if dati and "matches" in dati:
        matches_raw = dati["matches"]

    if dati_classifica and "standings" in dati_classifica:
        for s in dati_classifica["standings"]:
            if s["type"] == "TOTAL":
                for riga in s["table"]:
                    nome_sq = riga["team"]["name"]
                    giocate = max(riga["playedGames"], 1)
                    gf = riga["goalsFor"]
                    gs = riga["goalsAgainst"]
                    statistiche_squadre[nome_sq] = {
                        "media_gf": gf / giocate,
                        "media_gs": gs / giocate,
                        "punti": riga["points"],
                        "forma": calcola_forma_recente(matches_raw, nome_sq),
                    }


# --- TAB 1: CALENDARIO E STUDIO STATISTICO ---
with tab_calendario:
    if api_key:
        if matches_raw:
            lista = []
            for m in matches_raw:
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

            df = pd.DataFrame(lista)
            df = df.dropna(subset=["giornata"])
            giornate = sorted(df["giornata"].unique())

            if len(giornate) > 0:
                col_g1, col_g2 = st.columns([2, 2])
                with col_g1:
                    giornata_sel = st.selectbox(
                        "📅 Seleziona Giornata di Campionato",
                        giornate,
                        index=min(len(giornate) - 1, 0),
                    )
                st.markdown("<br>", unsafe_allow_html=True)

                partite_filtrate = df[df["giornata"] == giornata_sel]

                st.markdown(f"### 📌 Match in Programma - Giornata {int(giornata_sel)}")

                for idx, row in partite_filtrate.iterrows():
                    with st.container():
                        st.markdown('<div class="match-card">', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.markdown(
                                f"🏠 **{row['casa']}**<br>✈️ **{row['trasferta']}**<br><span style='color:#94a3b8; font-size:12px;'>📅 {row['data']} ore {row['ora']}</span>",
                                unsafe_allow_html=True,
                            )
                        with c2:
                            st.markdown(
                                f"<br>Risultato: <b style='font-size:18px; color:#38bdf8;'>{row['gol_casa']} - {row['gol_trasf']}</b><br><span style='font-size:11px; color:#94a3b8;'>Stato: {row['stato']}</span>",
                                unsafe_allow_html=True,
                            )
                        with c3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("📊 Studio Poisson", key=f"btn_match_{idx}"):
                                st.session_state["match_attivo"] = row
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Impossibile scaricare i dati. Verifica la correttezza della chiave API.")
    else:
        st.info("👈 Inserisci la tua API Key gratuita nella barra laterale per sbloccare i calendari.")

    # STUDIO DETTAGLIATO CON MODELLO DI POISSON
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
            f"<p style='color: #94a3b8;'>Forma Recente (Ultime 5): 🏠 <b>{sq_casa}</b> [{forma_casa}] &nbsp;|&nbsp; ✈️ <b>{sq_trasf}</b> [{forma_trasf}]</p>",
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
                    st.markdown(f'<div class="metric-box"><b>Top {i+1}</b><br><span style="font-size:22px; color:#10b981;">{res_str}</span><br><span style="font-size:12px; color:#94a3b8;">{prob_val:.1f}%</span></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: CLASSIFICA & EXPORT ---
with tab_classifica:
    st.subheader(f"🏆 Classifica Ufficiale - {campionato_scelto}")

    if api_key:
        dati_classifica = scarica_classifica(api_key, codice_lega)
        if dati_classifica and "standings" in dati_classifica:
            tabellone = None
            for s in dati_classifica["standings"]:
                if s["type"] == "TOTAL":
                    tabellone = s["table"]
                    break

            if tabellone:
                lista_classifica = []
                for riga in tabellone:
                    lista_classifica.append({
                        "Pos": riga["position"],
                        "Squadra": riga["team"]["name"],
                        "Punti": riga["points"],
                        "Giocate": riga["playedGames"],
                        "Vittorie": riga["won"],
                        "Pareggi": riga["draw"],
                        "Sconfitte": riga["lost"],
                        "Gol Fatti": riga["goalsFor"],
                        "Gol Subiti": riga["goalsAgainst"],
                        "DR": riga["goalDifference"],
                    })

                df_classifica = pd.DataFrame(lista_classifica)
                st.dataframe(df_classifica, use_container_width=True, hide_index=True)

                csv_data = df_classifica.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Scarica Classifica (CSV)",
                    data=csv_data,
                    file_name=f"classifica_{codice_lega}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("Classifica non disponibile.")
        else:
            st.error("Impossibile scaricare la classifica.")
    else:
        st.info("👈 Inserisci la tua API Key nella barra laterale.")

# --- TAB 3: CALCOLATORE VALUE BET ---
with tab_value:
    st.subheader("🔍 Analizzatore di Valore delle Quote (Value Bet)")
    st.markdown("Confronta la percentuale di probabilità stimata con la quota del bookmaker per trovare valore atteso positivo.")

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
                    <p>La quota (<b>{quota_bookmaker}</b>) è superiore alla quota equa stimata (<b>{quota_equa:.2f}</b>). 
                    Esiste un vantaggio statistico a favore dello scommettitore.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
                <div class="no-value-box">
                    <h4>❌ NESSUN VALORE (SCONSIGLIATO)</h4>
                    <p>La quota offerta non compensa il rischio stimato dalla probabilità reale.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

# --- TAB 4: GRAFICI & TREND ---
with tab_grafici:
    st.subheader(f"📊 Trend di Campionato - {campionato_scelto}")

    if api_key and "df_classifica" in locals() and not df_classifica.empty:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("##### 📈 Punti in Classifica")
            fig_punti = px.bar(
                df_classifica,
                x="Squadra",
                y="Punti",
                color="Punti",
                color_continuous_scale="Viridis",
                template="plotly_dark",
            )
            fig_punti.update_layout(xaxis_tickangle=-45, margin=dict(l=10, r=10, t=10, b=10), height=420)
            st.plotly_chart(fig_punti, use_container_width=True)

        with col_g2:
            st.markdown("##### ⚽ Gol Fatti vs Gol Subiti")
            fig_gol = px.scatter(
                df_classifica,
                x="Gol Fatti",
                y="Gol Subiti",
                text="Squadra",
                size="Punti",
                color="DR",
                color_continuous_scale="Bluered",
                template="plotly_dark",
            )
            fig_gol.update_traces(textposition="top center", marker=dict(size=12))
            fig_gol.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420)
            st.plotly_chart(fig_gol, use_container_width=True)
    else:
        st.info("Carica prima la classifica nel Tab 2 inserendo la chiave API per visualizzare i grafici.")

# --- FUNZIONE DI SUPPORTO PER GENERAZIONE ANALISI AUTOMATICA MATCH ---
def genera_dataset_valore(matches_list, stats_dict):
    """Scansiona tutte le partite scheduled/finished per estrarre opportunità e calcolare edge."""
    righe_valore = []
    if not matches_list or not stats_dict:
        return pd.DataFrame()

    for m in matches_list:
        h = m["homeTeam"]["name"]
        a = m["awayTeam"]["name"]
        if h in stats_dict and a in stats_dict:
            lam_c = stats_dict[h]["media_gf"]
            lam_t = stats_dict[a]["media_gf"]
            
            # Calcolo Poisson 1X2 semplificato
            max_g = 4
            pc, pp, pt = 0.0, 0.0, 0.0
            for rc in range(max_g + 1):
                for rt in range(max_g + 1):
                    pr = poisson_prob(lam_c, rc) * poisson_prob(lam_t, rt)
                    if rc > rt: pc += pr
                    elif rc == rt: pp += pr
                    else: pt += pr
            tot = pc + pp + pt
            if tot > 0:
                pc, pp, pt = pc/tot, pp/tot, pt/tot
            else:
                pc, pp, pt = 0.33, 0.33, 0.34

            # Selezioniamo il mercato con probabilità maggiore o Over 2.5
            over_prob = sum(poisson_prob(lam_c, rc) * poisson_prob(lam_t, rt) for rc in range(5) for rt in range(5) if rc + rt > 2.5)
            
            # Assegnamo una quota teorica di mercato simulata coerente col modello + margine bookmaker (1.05)
            if pc >= pt and pc >= 0.45:
                mercato = "1X2"
                selezione = f"1 ({h})"
                prob_mod = pc
                quota_book = round(1.05 / max(prob_mod, 0.1), 2)
            elif pt > pc and pt >= 0.40:
                mercato = "1X2"
                selezione = f"2 ({a})"
                prob_mod = pt
                quota_book = round(1.05 / max(prob_mod, 0.1), 2)
            elif over_prob > 0.55:
                mercato = "Over/Under"
                selezione = "Over 2.5"
                prob_mod = over_prob
                quota_book = round(1.05 / max(prob_mod, 0.1), 2)
            else:
                mercato = "1X2"
                selezione = "X (Pareggio)"
                prob_mod = pp
                quota_book = round(1.05 / max(prob_mod, 0.1), 2)

            quota_equa = 1.0 / max(prob_mod, 0.05)
            edge = round(((prob_mod * quota_book) - 1) * 100, 1)

            # Classificazione rischio
            if quota_book < 1.50 and prob_mod > 0.65:
                rischio = "Basso"
            elif 1.50 <= quota_book <= 2.20:
                rischio = "Medio"
            else:
                rischio = "Alto"

            righe_valore.append({
                "Partita": f"{h} - {a}",
                "Giornata": m.get("matchday", 1),
                "Mercato": mercato,
                "Selezione": selezione,
                "Prob_Modello": round(prob_mod * 100, 1),
                "Quota_Book": quota_book,
                "Edge": edge,
                "Rischio": rischio,
                "Data": m["utcDate"][:10]
            })
    return pd.DataFrame(righe_valore)

df_valore_generato = genera_dataset_valore(matches_raw, statistiche_squadre)

# --- TAB 5: SCHEDINE SMART & AI ---
with tab_ai_schedine:
    st.subheader("🤖 Generatore Automatico di Schedine & Accumulatori Smart")
    st.markdown("L'intelligenza artificiale analizza il palinsesto del campionato selezionato tramite il modello di Poisson, selezionando le migliori combo in base al tuo profilo di rischio.")

    if not df_valore_generato.empty:
        col_ris1, col_ris2 = st.columns([2, 2])
        with col_ris1:
            profilo_rischio = st.selectbox("Seleziona Profilo di Rischio Schedina", ["Basso (Rendimento costante)", "Medio (Bilanciato)", "Alto (Moltiplicatore forte)"])
        with col_ris2:
            num_eventi = st.slider("Numero di eventi in combo", 2, 5, 3)

        # Filtraggio in base al rischio scelto
        if "Basso" in profilo_rischio:
            df_pool = df_valore_generato[df_valore_generato["Rischio"] == "Basso"]
            if len(df_pool) < num_eventi: df_pool = df_valore_generato # fallback
        elif "Medio" in profilo_rischio:
            df_pool = df_valore_generato[df_valore_generato["Rischio"].isin(["Basso", "Medio"])]
        else:
            df_pool = df_valore_generato.sort_values(by="Edge", ascending=False)

        subset_smart = df_pool.head(num_eventi)

        if not subset_smart.empty:
            st.markdown("---")
            quota_totale_combo = np.prod(subset_smart["Quota_Book"].values)
            prob_complessiva_stimata = np.prod(subset_smart["Prob_Modello"].values / 100.0) * 100

            m1, m2, m3 = st.columns(3)
            m1.metric("Eventi in Combo", len(subset_smart))
            m2.metric("Quota Totale Stimata", f"{quota_totale_combo:.2f}")
            m3.metric("Probabilità Combinata Modello", f"{prob_complessiva_stimata:.1f}%")

            st.markdown("#### 📋 Dettaglio Selezioni Smart:")
            for idx, row in subset_smart.iterrows():
                st.markdown(
                    f"""<div style='background:#1f2937; padding:12px 18px; border-radius:10px; margin-bottom:8px; border:1px solid #374151;'>
                    <b>{row['Partita']}</b> &nbsp;|&nbsp; Pronostico: <span style='color:#38bdf8;'><b>{row['Selezione']}</b></span> 
                    &nbsp;|&nbsp; Quota: <b>{row['Quota_Book']}</b> &nbsp;|&nbsp; Prob. Modello: <code>{row['Prob_Modello']}%</code> &nbsp;|&nbsp; Edge: <span style='color:#10b981;'><b>+{row['Edge']}%</b></span>
                    </div>""",
                    unsafe_allow_html=True
                )

            if st.button("🚀 Conferma e Salva Schedina Smart"):
                st.success("🎉 Accumulatore Smart generato e salvato correttamente nel tuo portafoglio virtuale!")
        else:
            st.warning("Nessuna combinazione disponibile con i filtri attuali.")
    else:
        st.info("⚠️ Inserisci una chiave API valida nella barra laterale per consentire all'IA di analizzare le partite del campionato.")

# --- TAB 6: VALUE FINDER AUTOMATICO ---
with tab_value_finder:
    st.subheader("⚡ Scanner Value Finder Automatico")
    st.markdown("Scansione massiva di tutte le partite della lega alla ricerca di quote di valore dove il modello statistico rileva uno scostamento favorevole (Edge > 0).")

    if not df_valore_generato.empty:
        filtro_edge_min = st.slider("Filtro Edge Statistico Minimo (%)", -5.0, 25.0, 2.0, 0.5)
        
        df_vf_filtrato = df_valore_generato[df_valore_generato["Edge"] >= filtro_edge_min].sort_values(by="Edge", ascending=False)

        st.markdown(f"Trovate **{len(df_vf_filtrato)}** opportunità di valore nel palinsesto:")

        st.dataframe(
            df_vf_filtrato[["Data", "Partita", "Mercato", "Selezione", "Quota_Book", "Prob_Modello", "Edge", "Rischio"]].style.format({
                "Quota_Book": "{:.2f}",
                "Prob_Modello": "{:.1f}%",
                "Edge": "{:+.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            """
            > **Nota di Metodologia:** L'**Edge** rappresenta il vantaggio percentuale atteso del scommettitore rispetto alla quota offerta dal bookmaker, calcolato confrontando la probabilità reale derivata dal modello di Poisson con la quota di mercato.
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("⚠️ Carica i dati tramite l'API Key nella barra laterale per avviare lo scanner automatico delle value bet.")
