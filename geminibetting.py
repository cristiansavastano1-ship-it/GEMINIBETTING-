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

# Stile CSS avanzato per leggibilità perfetta
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    .match-card { background-color: #111827; padding: 16px; border-radius: 12px; border: 1px solid #1f2937; margin-bottom: 12px; }
    .analysis-container { background-color: #111827; padding: 24px; border-radius: 14px; border: 1px solid #374151; margin-top: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    .metric-box { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; text-align: center; }
    .value-box { background-color: #064e3b; border-left: 6px solid #10b981; padding: 18px; border-radius: 10px; margin-top: 15px; color: #ecfdf5; }
    .no-value-box { background-color: #7f1d1d; border-left: 6px solid #ef4444; padding: 18px; border-radius: 10px; margin-top: 15px; color: #fef2f2; }
    
    div.row-widget.stRadio div[role="radiogroup"] label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    div.row-widget.stRadio div[role="radiogroup"] label {
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚽ Pro Betting Studio & Deep Match Analytics")
st.markdown(
    "Piattaforma multi-campionato avanzata con modello di Poisson, grafici interattivi ed export dati."
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

# Sidebar
st.sidebar.header("⚙️ Configurazione")
api_key = st.sidebar.text_input(
    "Inserisci API Key (football-data.org)", type="password"
)
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


# Funzione di Poisson per calcolo esatto gol
def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)


# Funzione per estrarre la forma recente (ultime 5 partite) dalle partite concluse
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
    # Prendi le ultime 5
    ultime = partite_squadra[-5:] if len(partite_squadra) >= 5 else partite_squadra
    return "".join(ultime) if ultime else "N/D"


# --- TAB 1: CALENDARIO E STUDIO STATISTICO ---
with tab_calendario:
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
                            "forma": calcola_forma_recente(
                                matches_raw, nome_sq
                            ),
                        }

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
                giornata_sel = st.selectbox(
                    "📅 Seleziona Giornata di Campionato",
                    giornate,
                    index=min(len(giornate) - 1, 0),
                )
                partite_filtrate = df[df["giornata"] == giornata_sel]

                st.markdown(
                    f"### 📌 Partite in programma - Giornata {int(giornata_sel)}"
                )

                for idx, row in partite_filtrate.iterrows():
                    with st.container():
                        st.markdown(
                            '<div class="match-card">', unsafe_allow_html=True
                        )
                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.markdown(
                                f"**{row['casa']} vs {row['trasferta']}**<br><span style='color:#94a3b8; font-size:13px;'>📅 {row['data']} - {row['ora']}</span>",
                                unsafe_allow_html=True,
                            )
                        with c2:
                            st.markdown(
                                f"Risultato: **{row['gol_casa']} - {row['gol_trasf']}** <span style='font-size:12px; color:#94a3b8;'>({row['stato']})</span>",
                                unsafe_allow_html=True,
                            )
                        with c3:
                            if st.button(
                                "📊 Studio Avanzato (Poisson)",
                                key=f"btn_match_{idx}",
                            ):
                                st.session_state["match_attivo"] = row
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(
                "Impossibile scaricare i dati. Verifica la correttezza della chiave API."
            )
    else:
        st.warning(
            "👈 Inserisci la tua API Key gratuita nella barra laterale per caricare i campionati."
        )

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

        # Calcolo Matrice Poisson per esiti e risultati esatti
        max_gol = 5
        matrice_prob = [[0.0] * (max_gol + 1) for _ in range(max_gol + 1)]
        p_casa, p_pareggio, p_trasferta = 0.0, 0.0, 0.0

        for r_c in range(max_gol + 1):
            for r_t in range(max_gol + 1):
                prob = poisson_prob(lam_c, r_c) * poisson_prob(lam_t, r_t)
                matrice_prob[r_c][r_t] = prob
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

        # Trova top 3 risultati esatti
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

        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown(
            f"<h2>🔬 Studio Matematico (Poisson): {sq_casa} vs {sq_trasf}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Forma Recente (Ultime 5):** 🏠 {sq_casa} `[{forma_casa}]` | ✈️ {sq_trasf} `[{forma_trasf}]`"
        )

        focus_mercato = st.radio(
            "🎯 Seleziona il Focus di Analisi",
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
                st.markdown(
                    f'<div class="metric-box"><b>Lambda Casa (xG)</b><br><span style="font-size:24px; color:#38bdf8;">{lam_c:.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-box"><b>Lambda Trasf (xG)</b><br><span style="font-size:24px; color:#38bdf8;">{lam_t:.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="metric-box"><b>xG Totali Match</b><br><span style="font-size:24px; color:#38bdf8;">{xg_stimati}</span></div>',
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(
                    f'<div class="metric-box"><b>Over 2.5 (Poisson)</b><br><span style="font-size:24px; color:#38bdf8;">{over_25_rate}%</span></div>',
                    unsafe_allow_html=True,
                )

        elif focus_mercato == "1X2 & Doppia Chance":
            st.markdown(
                "#### ⚖️ Probabilità Reali calcolate con Legge di Poisson"
            )
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f'<div class="metric-box"><b>Segno 1</b><br><span style="font-size:22px; color:#38bdf8;">{p_c_1x2}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-box"><b>Segno X</b><br><span style="font-size:22px; color:#38bdf8;">{p_p_1x2}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="metric-box"><b>Segno 2</b><br><span style="font-size:22px; color:#38bdf8;">{p_t_1x2}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col4:
                dc = (
                    "1X"
                    if p_c_1x2 >= p_t_1x2
                    else ("X2" if p_t_1x2 > p_c_1x2 else "12")
                )
                st.markdown(
                    f'<div class="metric-box"><b>Doppia Chance Consigliata</b><br><span style="font-size:22px; color:#10b981;">{dc}</span></div>',
                    unsafe_allow_html=True,
                )

        elif focus_mercato == "Gol / No Gol & Over/Under":
            st.markdown("#### ⚽ Mercati dei Gol (Poisson)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f'<div class="metric-box"><b>BTTS (Gol / Gol)</b><br><span style="font-size:22px; color:#38bdf8;">{btts_rate}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-box"><b>Over 2.5 Gol</b><br><span style="font-size:22px; color:#38bdf8;">{over_25_rate}%</span></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="metric-box"><b>Under 2.5 Gol</b><br><span style="font-size:22px; color:#38bdf8;">{round(100 - over_25_rate, 1)}%</span></div>',
                    unsafe_allow_html=True,
                )

        elif focus_mercato == "Risultati Esatti":
            st.markdown(
                "#### 🎯 Top 4 Risultati Esatti più probabili secondo Poisson"
            )
            col1, col2, col3, col4 = st.columns(4)
            for i in range(4):
                res_str, prob_val = risultati_esatti_list[i]
                with [col1, col2, col3, col4][i]:
                    st.markdown(
                        f'<div class="metric-box"><b>{i+1}° Scelta</b><br><span style="font-size:22px; color:#10b981;">{res_str}</span><br><span style="font-size:12px; color:#94a3b8;">{prob_val:.1f}% prob.</span></div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: CLASSIFICA & EXPORT ---
with tab_classifica:
    st.subheader(f"🏆 Classifica Ufficiale ed Export Dati - {campionato_scelto}")

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

                # Pulsante di export CSV
                csv_data = df_classifica.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Scarica Classifica in formato CSV",
                    data=csv_data,
                    file_name=f"classifica_{codice_lega}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("Classifica non disponibile.")
        else:
            st.error("Impossibile scaricare la classifica.")
    else:
        st.warning("👈 Inserisci la tua API Key nella barra laterale.")

# --- TAB 3: CALCOLATORE VALUE BET ---
with tab_value:
    st.subheader("🔍 Analizzatore di Valore delle Quote (Value Bet)")
    st.markdown(
        "Confronta la percentuale di probabilità calcolata con i dati o con Poisson rispetto alla quota del bookmaker."
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
                    <p>La quota del bookmaker (<b>{quota_bookmaker}</b>) è superiore alla quota equa stimata (<b>{quota_equa:.2f}</b>). 
                    Esiste un vantaggio matematico di valore atteso positivo.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
                <div class="no-value-box">
                    <h4>❌ NESSUN VALORE (SCONSIGLIATO)</h4>
                    <p>La quota offerta è inferiore alla soglia di valore equo.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

# --- TAB 4: GRAFICI & TREND ---
with tab_grafici:
    st.subheader(
        f"📊 Analisi Grafica e Trend di Campionato - {campionato_scelto}"
    )

    if api_key and "df_classifica" in locals() and not df_classifica.empty:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("##### 📈 Punti per Squadra in Classifica")
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
                height=400,
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
                margin=dict(l=10, r=10, t=10, b=10), height=400
            )
            st.plotly_chart(fig_gol, use_container_width=True)
    else:
        st.warning(
            "Carica prima la classifica nel Tab 2 inserendo la chiave API per sbloccare i grafici interattivi."
        )
