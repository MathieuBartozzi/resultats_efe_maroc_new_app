
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

philo_df = load_sheet(file_id, sheets["philosophie"])
eds_df = load_sheet(file_id, sheets["eds"])
go_df = load_sheet(file_id, sheets["go"])


# Définir une palette de couleurs pour chaque année
colors = {
    "2023": "#ff7f0e",  # Orange pour 2023
    "2024": "#1f77b4",  # Bleu pour 2024
}

# Fonction pour filtrer les données par année
@st.cache_data
def filter_data_by_year(df, year):
    return df[df['session'] == year]

# Fonction pour créer un résumé des moyennes par épreuve pour une année donnée
@st.cache_data
def create_summary(year, philo_df, eds_df, go_df):
    return pd.DataFrame({
        'Épreuve': ['Philosophie', 'EDS', 'Grand Oral'],
        'Année': str(year),
        'Moyenne': [
            philo_df['moyenne'].mean(),
            eds_df['moyenne'].mean(),
            go_df['moyenne'].mean()
        ]
    })

# Fonction pour créer et afficher le graphique de comparaison des moyennes par épreuve et par année
def display_summary_chart(summary_df):
    fig = px.bar(
        summary_df,
        x="Épreuve",
        y="Moyenne",
        color="Année",
        title="Moyenne par épreuve (2023 vs 2024)",
        barmode="group",
        color_discrete_map=colors
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text='',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig)

# Fonction pour créer et afficher le graphique des moyennes par spécialité pour l'EDS
def display_speciality_chart(eds_speciality_df):
    fig = px.bar(
        eds_speciality_df,
        x="moyenne",
        y="spécialité",
        orientation="h",
        text="moyenne",
        title="Classement des spécialités",
        labels={"moyenne": "Moyenne des Notes", "spécialité": "Spécialité"}
    )
    fig.update_traces(marker_color=colors["2024"], textposition="outside")
    fig.update_layout(
        xaxis=dict(range=[10, 20]),
        yaxis=dict(categoryorder="total ascending"),
        xaxis_title=None,
        yaxis_title=None
    )
    st.plotly_chart(fig, use_container_width=True)


# Fonction pour créer un DataFrame de moyennes globales par établissement pour l'année 2024
def create_overall_summary_2024(philo_df, eds_df, go_df):
    # Filtrer les données pour l'année 2024
    philo_df_2024 = philo_df[philo_df['session'] == 2024]
    eds_df_2024 = eds_df[eds_df['session'] == 2024]
    go_df_2024 = go_df[go_df['session'] == 2024]

    # Calculer les moyennes par établissement pour chaque épreuve pour 2024
    philo_avg = philo_df_2024.groupby('établissement')['moyenne'].mean().reset_index()
    eds_avg = eds_df_2024.groupby('établissement')['moyenne'].mean().reset_index()
    go_avg = go_df_2024.groupby('établissement')['moyenne'].mean().reset_index()

    # Renommer les colonnes pour éviter les conflits lors de la fusion
    philo_avg.rename(columns={'moyenne': 'philo_moyenne'}, inplace=True)
    eds_avg.rename(columns={'moyenne': 'eds_moyenne'}, inplace=True)
    go_avg.rename(columns={'moyenne': 'go_moyenne'}, inplace=True)

    # Fusionner les moyennes pour obtenir un DataFrame global
    overall_df = philo_avg.merge(eds_avg, on='établissement', how='outer').merge(go_avg, on='établissement', how='outer')

    # Calculer la moyenne globale par établissement en ignorant les NaN
    overall_df['Moyenne'] = overall_df[['philo_moyenne', 'eds_moyenne', 'go_moyenne']].mean(axis=1, skipna=True).round(2)

    return overall_df

def display_overall_average_chart_2024(overall_df, highlighted_etablissement):
    # Ajouter une colonne pour surbriller l'établissement sélectionné
    overall_df['highlight'] = overall_df['établissement'] == highlighted_etablissement

    # Trier par moyenne décroissante
    overall_df = overall_df.sort_values(by='Moyenne', ascending=False).reset_index(drop=True)
    overall_df['Rang'] = overall_df.index + 1  # Ajouter le rang



    # Créer le graphique en barres verticales avec Plotly
    fig = px.bar(
        overall_df,
        x="établissement",
        y="Moyenne",
        text="Moyenne",
        title="Classement des moyennes globales (EDS, GO, Philo) par établissement pour 2024",
        labels={"Moyenne": "Moyenne globale", "établissement": "Établissement"}
    )

    # Appliquer la couleur pour l'établissement mis en surbrillance
    colors = ['#ff6347' if highlight else '#80c9e0' for highlight in overall_df['highlight']]
    fig.update_traces(marker_color=colors, textposition='outside', texttemplate='%{text:.2f}')

    colors = ['#ff6347' if highlight else '#80c9e0' for highlight in overall_df['highlight']]
    fig.update_traces(marker_color=colors, textposition='outside')
    fig.update_layout(
        yaxis=dict(range=[0, 15]),
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(tickangle=45))

    st.plotly_chart(fig)

# Sélectionner un établissement pour le mettre en surbrillance dans la barre latérale
with st.sidebar:
    highlighted_etablissement = st.selectbox(
        "Choisissez un établissement à mettre en surbrillance :",
        sorted(philo_df['établissement'].unique())
        )

# Chargement et filtration des données
st.title("Résultats Baccalauréat - EFE Maroc")
st.divider()

philo_df_year_2024 = filter_data_by_year(philo_df, 2024)
eds_df_year_2024 = filter_data_by_year(eds_df, 2024)
go_df_year_2024 = filter_data_by_year(go_df, 2024)
philo_df_year_2023 = filter_data_by_year(philo_df, 2023)
eds_df_year_2023 = filter_data_by_year(eds_df, 2023)
go_df_year_2023 = filter_data_by_year(go_df, 2023)

# Création du résumé des moyennes par année
summary_2023 = create_summary(2023, philo_df_year_2023, eds_df_year_2023, go_df_year_2023)
summary_2024 = create_summary(2024, philo_df_year_2024, eds_df_year_2024, go_df_year_2024)
summary_df = pd.concat([summary_2023, summary_2024])

# Préparation des moyennes par spécialité pour l'EDS (2024)
eds_speciality_average = eds_df_year_2024.groupby('spécialité').agg({'moyenne': 'mean'}).reset_index()
eds_speciality_average['moyenne'] = eds_speciality_average['moyenne'].round(1)  # Arrondir à 1 chiffre
eds_speciality_average = eds_speciality_average.sort_values(by="moyenne", ascending=False)

# Affichage des sous-titres et des graphiques
st.subheader('Résultats tout établissements')

# Créer deux colonnes pour les graphiques
# Créer deux colonnes pour les graphiques
# Créer les deux colonnes principales
col1, col2 = st.columns(2)

# Dans la première colonne principale, créer deux sous-colonnes
with col1:
    sub_col1, sub_col2 = st.columns(2)

    with sub_col1:
        # Afficher le graphique de comparaison des moyennes par épreuve et par année
        display_summary_chart(summary_df)

    with sub_col2:
        # Afficher le graphique des moyennes par spécialité pour l'EDS
        display_speciality_chart(eds_speciality_average)

# Dans la deuxième colonne principale, afficher le graphique du classement
with col2:
    # Création du résumé des moyennes par établissement pour l'année 2024
    overall_df_2024 = create_overall_summary_2024(philo_df, eds_df, go_df)
    # Appel de la fonction pour afficher le graphique pour l'année 2024 avec l'établissement mis en surbrillance
    display_overall_average_chart_2024(overall_df_2024, highlighted_etablissement)





######################################
# Section : Classements par Épreuve
st.subheader(f'Résultats pour : {highlighted_etablissement}')

philo_summary = philo_df_year_2024[['établissement', 'moyenne']].copy()
eds_summary = eds_df_year_2024[['établissement', 'spécialité', 'moyenne']].copy()
go_summary = go_df_year_2024[['établissement', 'moyenne']].copy()
philo_summary['épreuve'] = 'Philosophie'
eds_summary['épreuve'] = 'EDS'
go_summary['épreuve'] = 'Grand Oral'

# # Sélectionner un établissement pour le mettre en surbrillance
# highlighted_etablissement = st.selectbox(
#     "Choisissez un établissement :",
#     sorted(philo_summary['établissement'].unique()),
#     key="highlighted_etablissement_2"
# )

# Préparer les données de classement pour Philosophie avec surbrillance
philo_summary = philo_summary.sort_values(by='moyenne', ascending=False).reset_index(drop=True)
philo_summary['rang'] = philo_summary.index + 1
philo_summary['highlight'] = philo_summary['établissement'] == highlighted_etablissement

# Préparer les données de classement pour le Grand Oral avec surbrillance
go_summary = go_summary.sort_values(by='moyenne', ascending=False).reset_index(drop=True)
go_summary['rang'] = go_summary.index + 1
go_summary['highlight'] = go_summary['établissement'] == highlighted_etablissement


# Fonction pour créer des couleurs conditionnelles
def color_based_on_highlight(df):
    colors = ['#ff6347' if highlight else '#80c9e0' for highlight in df['highlight']]
    return colors

# Fonction pour calculer les métriques
@st.cache_data
def calculate_metrics(df_2024, df_2023, highlighted_etablissement, speciality=None):
    if speciality:
        mean_2024 = df_2024[(df_2024['établissement'] == highlighted_etablissement) & (df_2024['spécialité'] == speciality)]['moyenne'].mean()
        mean_2023 = df_2023[(df_2023['établissement'] == highlighted_etablissement) & (df_2023['spécialité'] == speciality)]['moyenne'].mean()
    else:
        mean_2024 = df_2024[df_2024['établissement'] == highlighted_etablissement]['moyenne'].mean()
        mean_2023 = df_2023[df_2023['établissement'] == highlighted_etablissement]['moyenne'].mean()

    variation = ((mean_2024 - mean_2023) / mean_2023 * 100) if mean_2023 != 0 else 0
    return mean_2024, variation

# Calcul des métriques pour chaque épreuve
philo_mean_2024, philo_variation = calculate_metrics(philo_df_year_2024, philo_df_year_2023, highlighted_etablissement)
# eds_mean_2024, eds_variation = calculate_metrics(eds_df_year_2024, eds_df_year_2023, highlighted_etablissement, selected_speciality)
go_mean_2024, go_variation = calculate_metrics(go_df_year_2024, go_df_year_2023, highlighted_etablissement)


# Filtrer les données EDS pour les établissements sélectionnés
filtered_eds_df_year_2024 = eds_df_year_2024[eds_df_year_2024['établissement']==highlighted_etablissement]
filtered_eds_df_year_2023 = eds_df_year_2023[eds_df_year_2023['établissement']==highlighted_etablissement]

# Calcul des statistiques pour chaque spécialité en 2024 et 2023
speciality_stats = []
for speciality in filtered_eds_df_year_2024['spécialité'].unique():
    # Filtrer les données pour highlighted_etablissement et la spécialité en 2024 et 2023
    speciality_2024 = eds_df_year_2024[eds_df_year_2024['spécialité'] == speciality]
    speciality_2023 = eds_df_year_2023[eds_df_year_2023['spécialité'] == speciality]

    # Calculer la moyenne pour highlighted_etablissement uniquement
    mean_2024 = filtered_eds_df_year_2024[filtered_eds_df_year_2024['spécialité'] == speciality]['moyenne'].mean()
    mean_2023 = filtered_eds_df_year_2023[filtered_eds_df_year_2023['spécialité'] == speciality]['moyenne'].mean()

    # Calcul de la variation entre 2023 et 2024
    variation = ((mean_2024 - mean_2023) / mean_2023 * 100) if mean_2023 != 0 else 0

    # Calcul du rang de highlighted_etablissement parmi les établissements ayant cette spécialité en 2024
    speciality_2024_sorted = speciality_2024.sort_values(by='moyenne', ascending=False).reset_index(drop=True)
    highlighted_rank = speciality_2024_sorted[speciality_2024_sorted['établissement'] == highlighted_etablissement].index[0] + 1 if highlighted_etablissement in speciality_2024_sorted['établissement'].values else None

    #Ajouter les informations de cette spécialité pour highlighted_etablissement
    speciality_stats.append({
        "Spécialité": speciality,
        "Moyenne 2024": round(mean_2024, 2),
        "Variation (%)": round(variation, 2),
        "Rang (2024)": highlighted_rank
    })


# Conversion en DataFrame pour l'affichage
speciality_stats_df = pd.DataFrame(speciality_stats)





# Afficher les classements dans trois colonnes
col1, col2, col3= st.columns(3)

with col1:

    with st.container(border=True):
        st.write("**Philosophie**")
        st.metric(label="Moyenne 2024", value=f"{philo_mean_2024:.2f}", delta=f"{philo_variation:.2f}%")

        fig_philo = px.bar(
            philo_summary,
            x="moyenne",
            y="établissement",
            orientation="h",
            text="rang",
            labels={"moyenne": "Moyenne", "établissement": "Établissement"}
            )
        fig_philo.update_traces(marker_color=color_based_on_highlight(philo_summary), textposition='outside')
        fig_philo.update_layout(yaxis=dict(autorange="reversed"))  # Trier de haut en bas
        fig_philo.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_philo, use_container_width=True)

with col2:

    with st.container(border=True):
        st.write("**Grand Oral**")
        st.metric(label="Moyenne 2024", value=f"{go_mean_2024:.2f}", delta=f"{go_variation:.2f}%")

        fig_go = px.bar(
            go_summary,
            x="moyenne",
            y="établissement",
            orientation="h",
            text="rang",
            labels={"moyenne": "Moyenne", "établissement": "Établissement"}
            )
        fig_go.update_traces(marker_color=color_based_on_highlight(go_summary), textposition='outside')
        fig_go.update_layout(yaxis=dict(autorange="reversed"))  # Trier de haut en bas
        fig_go.update_layout(xaxis_title=None, yaxis_title=None)

        st.plotly_chart(fig_go, use_container_width=True)

with col3:
    with st.container(border=True,height=633):
        st.write("**Spécialités**")
        st.dataframe(speciality_stats_df, use_container_width=True)
