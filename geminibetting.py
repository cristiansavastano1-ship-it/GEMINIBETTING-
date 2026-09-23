import math
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Pro Football Betting & Deep Analytics",
    layout="wide",
    page_icon="⚽",
)

# Stile CSS avanzato
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    
    .match-card { 
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%); 
        padding: 20px; 
        border-radius: 14px; 
        border: 1px solid #374151; 
        margin-bottom: 14px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease;
    }
    .match-card:hover { border-color: #38bdf8; }
    
    .analysis-container { 
        background-color: #111827; 
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid #374151; 
        margin-top: 25px; 
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4); 
    }
    
    .metric-box { 
        background: #1f2937; 
        padding: 18px; 
        border-radius: 12px; 
        border: 1px solid #4b5563; 
        text-align: center; 
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.05);
    }
    
    .value-box { 
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); 
        border-left: 6px solid #10b981; 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 20px; 
        color: #ecfdf5; 
    }
    .no-value-box { 
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); 
        border-left: 6px solid #ef4444; 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 20px; 
        color: #fef2f2; 
    }
    
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

st.markdown(
    "<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>⚽ PRO BETTING STUDIO & ANALYTICS</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 30px;'>Piattaforma professionale con Poisson, Fattore Campo, Clean Sheet e H2H.</p>",
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

tab_calendario, tab_classifica, tab_value, tab_grafici = st.tabs([
    "📅 Calendario & Studio Match",
    "🏆 Classifica & Export",
    "🔍 Calcolatore Value Bet",
    "📊 Grafici & Trend",
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


# Funzione avanzata per calcolare statistiche dettagliate (Fattore Campo, Clean Sheet, Fail to Score)
def calcola_statistiche_avanzate(matches_list, nome_squadra):
    giocate_casa = 0
    gol_fatti_casa = 0
    gol_subiti_casa = 0
    clean_sheet_casa = 0
    fail_to_score_casa = 0

    giocate_trasf = 0
    gol_fatti_trasf = 0
    gol_subiti_trasf = 0
    clean_sheet_trasf = 0
    fail_to_score_trasf = 0

    partite_squadra_tot = []

    for m in matches_list:
        if m["status"] == "FINISHED":
            h = m["homeTeam"]["name"]
            a = m["awayTeam"]["name"]
            gh = m["score"]["fullTime"].get("home", 0)
            ga = m["score"]["fullTime"].get("away", 0)

            if gh is not None and ga is not None:
                # Tracciamento forma recente
                if h == nome_squadra or a == nome_squadra:
                    res = (
                        "V"
                        if (h == nome_squadra and gh > ga)
                        or (a == nome_squadra and ga > gh)
                        else ("P" if gh == ga else "S")
                    )
                    partite_squadra_tot.append(res)

                # Statistiche Casa
                if h == nome_squadra:
                    giocate_casa += 1
                    gol_fatti_casa += gh
                    gol_subiti_casa += ga
                    if ga == 0:
                        clean_sheet_casa += 1
                    if gh == 0:
                        fail_to_score_casa += 1

                # Statistiche Trasferta
                if a == nome_squadra:
                    giocate_trasf += 1
                    gol_fatti_trasf += ga
                    gol_subiti_trasf += gh
                    if gh == 0:
                        clean_sheet_trasf += 1
                    if ga == 0:
                        fail_to_score_trasf += 1

    # Medie
    med_gf_c = gol_fatti_casa / max(giocate_casa, 1)
    med_gs_c = gol_subiti_casa / max(giocate_casa, 1)
    cs_c_pct = (
        round((clean_sheet_casa / giocate_casa) * 100, 1)
        if giocate_casa > 0
        else 0
    )
    fts_c_pct = (
        round((fail_to_score_casa / giocate_casa) * 100, 1)
        if giocate_casa > 0
        else 0
    )

    med_gf_t = gol_fatti_trasf / max(giocate_trasf, 1)
    med_gs_t = gol_subiti_trasf / max(giocate_trasf, 1)
    cs_t_pct = (
        round((clean_sheet_trasf / giocate_trasf) * 100, 1)
        if giocate_trasf > 0
        else 0
    )
    fts_t_pct = (
        round((fail_to_score_trasf / giocate_trasf) * 100, 1)
        if giocate_trasf > 0
        else 0
    )

    ultime = (
        "".join(partite_squadra_tot[-5:])
        if len(partite_squadra_tot) >= 5
        else "".join(partite_squadra_tot)
    )

    return {
        "casa": {
            "media_gf": med_gf_c,
            "media_gs": med_gs_c,
            "cs_pct": cs_c_pct,
            "fts_pct": fts_c_pct,
            "giocate": giocate_casa,
        },
        "trasferta": {
            "media_gf": med_gf_t,
            "media_gs": med_gs_t,
            "cs_pct": cs_t_pct,
            "fts_pct": fts_t_pct,
            "giocate": giocate_trasf,
        },
        "forma": ultime if ultime else "N/D",
    }


# Funzione per estrarre lo storico H2H (Testa a Testa)
def estrai_h2h(matches_list, sq_casa, sq_trasf):
    precedenti = []
    for m in matches_list:
        if m["status"] == "FINISHED":
            h = m["homeTeam"]["name"]
            a = m["awayTeam"]["name"]
            if (h == sq_casa and a == sq_trasf) or (
                h == sq_trasf and a == sq_casa
            ):
                gh = m["score"]["fullTime"].get("home", "-")
                ga = m["score"]["fullTime"].get("away", "-")
                precedenti.append({
                    "data": m["utcDate"][:10],
                    "casa": h,
                    "trasferta": a,
                    "risultato": f"{gh} - {ga}",
                })
    return precedenti[:5]  # Ultimi 5 precedenti


# --- TAB 1: CALENDARIO E STUDIO STATISTICO ---
with tab_calendario:
    statistiche_squadre = {}
    matches_raw = []

    if api_key:
        dati = scarica_dati(api_key, codice_lega)
        if dati and "matches" in dati:
            matches_raw = dati["matches"]
            # Prepara le statistiche avanzate per ogni squadra trovata nel campionato
            squadre_uniche = set()
            for m in matches_raw:
                squadre_uniche.add(m["homeTeam"]["name"])
                squadre_uniche.add(m["awayTeam"]["name"])

            for sq in squadre_uniche:
                statistiche_squadre[sq] = calcola_statistiche_avanzate(
                    matches_raw, sq
                )

        if matches_raw:
            lista = []
            for m in matches_raw:
                g_casa = (
                    m["score"]["fullTime"].get("home")
                    if m.get("score") and m["score"].get("fullTime")
                    else None
                )
                g_trasf = (
                    m["score"]["fullTime"].get("away")
                    if m.get("score") and m["score"].get("fullTime")
                    else None
                )

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
                st.markdown(
                    f"### 📌 Match in Programma - Giornata {int(giornata_sel)}"
                )

                for idx, row in partite_filtrate.iterrows():
                    with st.container():
                        st.markdown(
                            '<div class="match-card">', unsafe_allow_html=True
                        )
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
                            if st.button(
                                "📊 Studio Avanzato", key=f"btn_match_{idx}"
                            ):
                                st.session_state["match_attivo"] = row
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(
                "Impossibile scaricare i dati. Verifica la correttezza della chiave API."
            )
    else:
        st.info(
            "👈 Inserisci la tua API Key gratuita nella barra laterale per sbloccare i calendari."
        )

    # STUDIO DETTAGLIATO CON FATTORE CAMPO, CLEAN SHEET E H2H
    if "match_attivo" in st.session_state:
        m = st.session_state["match_attivo"]
        sq_casa = m["casa"]
        sq_trasf = m["trasferta"]

        if sq_casa in statistiche_squadre and sq_trasf in statistiche_squadre:
            # Sfruttiamo le performance reali in base al fattore campo!
            lam_c = statistiche_squadre[sq_casa]["casa"]["media_gf"]
            lam_t = statistiche_squadre[sq_trasf]["trasferta"]["media_gf"]

            cs_casa = statistiche_squadre[sq_casa]["casa"]["cs_pct"]
            fts_casa = statistiche_squadre[sq_casa]["casa"]["fts_pct"]

            cs_trasf = statistiche_squadre[sq_trasf]["trasferta"]["cs_pct"]
            fts_trasf = statistiche_squadre[sq_trasf]["trasferta"]["fts_pct"]

            forma_casa = statistiche_squadre[sq_casa]["forma"]
            forma_trasf = statistiche_squadre[sq_trasf]["forma"]
        else:
            lam_c, lam_t = 1.4, 1.1
            cs_casa, fts_casa, cs_trasf, fts_trasf = 30, 20, 25, 30
            forma_casa, forma_trasf = "N/D", "N/D"

        # Modello Poisson basato sul fattore campo
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
                p_res = (
                    poisson_prob(lam_c, r_c)
                    * poisson_prob(lam_t, r_t)
                    / tot_1x2
                )
                risultati_esatti_list.append(
                    (f"{r_c} - {r_t}", p_res * 100)
                )
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

        h2h_list = estrai_h2h(matches_raw, sq_casa, sq_trasf)

        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown(
            f"<h2>🔬 Studio Avanzato: {sq_casa} vs {sq_trasf}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='color: #94a3b8;'>Forma Recente: 🏠 <b>{sq_casa}</b> [{forma_casa}] &nbsp;|&nbsp; ✈️ <b>{sq_trasf}</b> [{forma_trasf}]</p>",
            unsafe_allow_html=True,
        )

        focus_mercato = st.radio(
            "🎯 Scegli l'Ambito di Analisi",
            [
                "Panoramica & Fattore Campo",
                "Clean Sheet & Fail to Score",
                "1X2 & Risultati Esatti",
                "Precedenti (H2H)",
            ],
            horizontal=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if focus_mercato == "Panoramica & Fattore Campo":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f'<div class="metric-box"><b>xG Casa (In Casa)</b><br><span style="font-size:24px; color:#38bdf8;">{lam_c:.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-box"><b>xG Trasf (Fuori)</b><br><span style="font-size:24px; color:#38bdf8;">{lam_t:.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="metric-box"><b>xG Totali Match</b><br><span style="font-size:24px; color:#38bdf8;">{xg_stimati}</span></div>',
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(
                    f'<div class="metric-box"><b>Over 2.5 Prob.</b><br><span style="font-size:24px; color:#38bdf8;">{over_25_rate}%</span></div>',
                    unsafe_allow_html=True,
                )

        elif focus_mercato == "Clean Sheet & Fail to Score":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f'<div class="metric-box"><b>Clean Sheet ({sq_casa})</b><br><span style="font-size:22px; color:#38bdf8;">{cs_casa}%</span><br><span style="font-size:11px; color:#94a3b8;">partite interne</span></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-box"><b>Fail to Score ({sq_casa})</b><br><span style="font-size:22px; color:#f87171;">{fts_casa}%</span><br><span style="font-size:11px; color:#94a3b8;">partite interne</span></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="metric-box"><b>Clean Sheet ({sq_trasf})</b><br><span style="font-size:22px; color:#38bdf8;">{cs_trasf}%</span><br><span style="font-size:11px; color:#94a3b8;">partite esterne</span></div>',
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(
                    f'<div class="metric-box"><b>Fail to Score ({sq_trasf})</b><br><span style="font-size:22px; color:#f87171;">{fts_trasf}%</span><br><span style="font-size:11px; color:#94a3b8;">partite esterne</span></div>',
                    unsafe_allow_html=True,
                )

        elif focus_mercato == "1X2 & Risultati Esatti":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f'<div class="metric-box"><b>Segno 1</b><br><span style="font-size:20px; color:#38bdf8;">{p_c_1x2}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-box"><b>Segno X</b><br><span style="font-size:20px; color:#38bdf8;">{p_p_1x2}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="metric-box"><b>Segno 2</b><br><span style="font-size:20px; color:#38bdf8;">{p_t_1x2}%</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<br>##### 🎯 Top Risultati Esatti (Poisson)")
            r1, r2, r3, r4 = st.columns(4)
            for i in range(4):
                res_str, prob_val = risultati_esatti_list[i]
                with [r1, r2, r3, r4][i]:
                    st.markdown(
                        f'<div class="metric-box"><b>Top {i+1}</b><br><span style="font-size:18px; color:#10b981;">{res_str}</span><br><span style="font-size:11px; color:#94a3b8;">{prob_val:.1f}%</span></div>',
                        unsafe_allow_html=True,
                    )

        elif focus_mercato == "Precedenti (H2H)":
            st.markdown("##### 📜 Ultimi Precedenti Diretti (H2H)")
            if h2h_list:
                for match_h2h in h2h_list:
                    st.markdown(
                        f"📅 **{match_h2h['data']}** &nbsp;|&nbsp; {match_h2h['casa']} vs {match_h2h['trasferta']} &nbsp;➔&nbsp; Risultato: **{match_h2h['risultato']}**"
                    )
            else:
                st.info(
                    "Nessun precedente diretto recente registrato nei dati disponibili di questo campionato."
                )

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
                st.dataframe(
                    df_classifica, use_container_width=True, hide_index=True
                )

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
    st.markdown(
        "Confronta la percentuale di probabilità stimata con la quota del bookmaker per trovare valore atteso positivo."
    )

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        probabilita_stimata = st.slider(
            "Probabilità stimata (%)", 1.0, 100.0, 50.0, 0.5
        )
    with col_v2:
        quota_bookmaker = st.number_input(
            "Quota offerta dal bookmaker", 1.01, 50.0, 2.00, 0.01
        )

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
            fig_punti.update_layout(
                xaxis_tickangle=-45,
                margin=dict(l=10, r=10, t=10, b=10),
                height=420,
            )
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
            fig_gol.update_traces(
                textposition="top center", marker=dict(size=12)
            )
            fig_gol.update_layout(
                margin=dict(l=10, r=10, t=10, b=10), height=420
            )
            st.plotly_chart(fig_gol, use_container_width=True)
    else:
        st.info(
            "Carica prima la classifica nel Tab 2 inserendo la chiave API per visualizzare i grafici."
        )
