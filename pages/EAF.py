import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Fonction pour charger un onglet spécifique depuis Google Sheets
@st.cache_data
def load_sheet(file_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    return df

# Charger chaque onglet dans un DataFrame
file_id = st.secrets["google_sheets"]["file_id"]
sheets = {
    "philosophie": "776936543",
    "eds": "455744397",
    "go": "1814626375",
    "dnb":"1644783757",
    "eaf":"1206285985"
}

# Charger l'onglet EAF dans un DataFrame
eaf_df = load_sheet(file_id, sheets["eaf"])
eaf_df.columns = eaf_df.columns.str.strip()  # Supprimer les espaces dans les noms de colonnes

# Fonction pour filtrer les données par année
@st.cache_data
def filter_data_by_year(df, year):
    return df[df['session'] == year]

# Sélectionner un établissement pour le mettre en surbrillance dans la barre latérale
with st.sidebar:
    highlighted_etablissement_eaf = st.selectbox(
        "Choisissez un établissement pour les épreuves anticipées de français (EAF) :",
        sorted(eaf_df['établissement'].unique())
    )

# Filtrer les données par année pour EAF
eaf_df_year_2024 = filter_data_by_year(eaf_df, 2024)
eaf_df_year_2023 = filter_data_by_year(eaf_df, 2023)

# Calcul des moyennes pour les épreuves EAF
@st.cache_data
def create_summary_eaf(eaf_df_year_2023, eaf_df_year_2024):
    summary_data_eaf = pd.DataFrame({
        'Épreuve': ['Écrit', 'Oral'],
        '2023': [
            eaf_df_year_2023['écrit'].mean(),
            eaf_df_year_2023['oral'].mean()
        ],
        '2024': [
            eaf_df_year_2024['écrit'].mean(),
            eaf_df_year_2024['oral'].mean()
        ]
    })
    return summary_data_eaf

# Fonction pour créer des couleurs conditionnelles pour la surbrillance
def color_based_on_highlight(df):
    return ['#ff6347' if highlight else '#80c9e0' for highlight in df['highlight']]

# Définir une palette de couleurs pour chaque année
colors = {
    "2023": "#ff7f0e",  # Orange pour 2023
    "2024": "#1f77b4",  # Bleu pour 2024
}


# Fonction pour afficher un graphique en barres
def display_bar_chart(summary_df, title):
    summary_df = summary_df.melt(id_vars="Épreuve", var_name="Année", value_name="Moyenne")
    fig = px.bar(
        summary_df,
        x="Épreuve",
        y="Moyenne",
        color="Année",
        barmode="group",
        color_discrete_map=colors,
        title=title
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text='',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Créer le résumé pour les épreuves anticipées de français
summary_df_eaf = create_summary_eaf(eaf_df_year_2023, eaf_df_year_2024)

# Affichage des résultats EAF en bar chart
st.subheader("Résultats des épreuves anticipées de français (EAF)")
display_bar_chart(summary_df_eaf, "Épreuves anticipées sur 20")

# Fonction pour calculer la moyenne et la variation pour EAF
@st.cache_data
def calculate_metrics_eaf(df_2024, df_2023, highlighted_etablissement, subject):
    mean_2024 = df_2024[df_2024['établissement'] == highlighted_etablissement][subject].mean()
    mean_2023 = df_2023[df_2023['établissement'] == highlighted_etablissement][subject].mean()
    variation = ((mean_2024 - mean_2023) / mean_2023 * 100) if mean_2023 != 0 else 0
    return mean_2024, variation

# Affichage des résultats spécifiques pour l'établissement sélectionné
st.subheader(f"Résultats pour l'établissement : {highlighted_etablissement_eaf} (EAF)")

# Création de la disposition à trois colonnes
col1, col2, col3 = st.columns(3)

# Colonne 1 : Épreuve "Écrit" - Affichage des métriques et du classement
with col1:
    mean_2024_ecrit, variation_ecrit = calculate_metrics_eaf(eaf_df_year_2024, eaf_df_year_2023, highlighted_etablissement_eaf, "écrit")
    with st.container(border=True):
        st.write("**Écrit**")
        st.metric(label="Moyenne 2024", value=f"{mean_2024_ecrit:.2f}", delta=f"{variation_ecrit:.2f}%")

        # Préparer les données de classement pour "Écrit"
        ecrit_summary = eaf_df_year_2024[['établissement', 'écrit']].copy()
        ecrit_summary = ecrit_summary.rename(columns={'écrit': 'moyenne'})
        ecrit_summary = ecrit_summary.sort_values(by='moyenne', ascending=False).reset_index(drop=True)
        ecrit_summary['rang'] = ecrit_summary.index + 1
        ecrit_summary['highlight'] = ecrit_summary['établissement'] == highlighted_etablissement_eaf

        # Graphique de classement pour "Écrit"
        fig_ecrit = px.bar(
            ecrit_summary,
            x="moyenne",
            y="établissement",
            orientation="h",
            text="rang",
            labels={"moyenne": "Moyenne", "établissement": "Établissement"}
        )
        fig_ecrit.update_traces(marker_color=color_based_on_highlight(ecrit_summary), textposition='outside')
        fig_ecrit.update_layout(yaxis=dict(autorange="reversed"))
        fig_ecrit.update_layout(xaxis_title=None, yaxis_title=None)

        st.plotly_chart(fig_ecrit, use_container_width=True)

# Colonne 2 : Épreuve "Oral" - Affichage des métriques et du classement
with col2:

    mean_2024_oral, variation_oral = calculate_metrics_eaf(eaf_df_year_2024, eaf_df_year_2023, highlighted_etablissement_eaf, "oral")
    with st.container(border=True):
        st.write("**Oral**")
        st.metric(label="Moyenne 2024", value=f"{mean_2024_oral:.2f}", delta=f"{variation_oral:.2f}%")

        # Préparer les données de classement pour "Oral"
        oral_summary = eaf_df_year_2024[['établissement', 'oral']].copy()
        oral_summary = oral_summary.rename(columns={'oral': 'moyenne'})
        oral_summary = oral_summary.sort_values(by='moyenne', ascending=False).reset_index(drop=True)
        oral_summary['rang'] = oral_summary.index + 1
        oral_summary['highlight'] = oral_summary['établissement'] == highlighted_etablissement_eaf

        # Graphique de classement pour "Oral"
        fig_oral = px.bar(
            oral_summary,
            x="moyenne",
            y="établissement",
            orientation="h",
            text="rang",
            labels={"moyenne": "Moyenne", "établissement": "Établissement"}
        )
        fig_oral.update_traces(marker_color=color_based_on_highlight(oral_summary), textposition='outside')
        fig_oral.update_layout(yaxis=dict(autorange="reversed"))
        fig_oral.update_layout(xaxis_title=None, yaxis_title=None)

        st.plotly_chart(fig_oral, use_container_width=True)

# Colonne 3 : Scatter plot comparant les scores Écrit vs Oral
with col3:
    with st.container(border=True,height=633):
        st.write('**Écrit vs Oral**')
        eaf_df_year_2024['highlight'] = eaf_df_year_2024['établissement'] == highlighted_etablissement_eaf

        fig_scatter = px.scatter(
            eaf_df_year_2024,
            x="écrit",
            y="oral",
            color='highlight',
            color_discrete_map={True: '#ff6347', False: '#80c9e0'},
            hover_name="établissement"
        )
        fig_scatter.update_layout(showlegend=False)

        st.plotly_chart(fig_scatter, use_container_width=True)
