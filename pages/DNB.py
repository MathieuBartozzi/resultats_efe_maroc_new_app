
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

dnb_df = load_sheet(file_id, sheets["dnb"])
dnb_df.columns = dnb_df.columns.str.strip()


# Sélectionner un établissement pour le mettre en surbrillance dans la barre latérale
with st.sidebar:
    highlighted_etablissement = st.selectbox(
        "Choisissez un établissement à mettre en surbrillance :",
        sorted(dnb_df['établissement'].unique())
    )

# Définir une palette de couleurs pour chaque année
colors = {
    "2023": "#ff7f0e",  # Orange pour 2023
    "2024": "#1f77b4",  # Bleu pour 2024
}

# Fonction pour filtrer les données par année
@st.cache_data
def filter_data_by_year(df, year):
    return df[df['session'] == year]

dnb_df_year_2024 = filter_data_by_year(dnb_df, 2024)
dnb_df_year_2023 = filter_data_by_year(dnb_df, 2023)


# Fonction pour créer un résumé des moyennes pour les épreuves séparées
@st.cache_data
def create_summary(dnb_df_year_2023, dnb_df_year_2024):
    summary_data_100 = pd.DataFrame({
        'Épreuve': [
            'Français', 'Mathématiques', 'SO de projet'
        ],
        '2023': [
            dnb_df_year_2023['Français (sur 100)'].mean(),
            dnb_df_year_2023['Mathématiques (sur 100)'].mean(),
            dnb_df_year_2023['SO de projet (sur 100)'].mean()
        ],
        '2024': [
            dnb_df_year_2024['Français (sur 100)'].mean(),
            dnb_df_year_2024['Mathématiques (sur 100)'].mean(),
            dnb_df_year_2024['SO de projet (sur 100)'].mean()
        ]
    })

    summary_data_50 = pd.DataFrame({
        'Épreuve': [
            'Hist. Géo.EMC', 'Sciences',
            'DNL Hist. Géo. arabe', 'Langue de la section'
        ],
        '2023': [
            dnb_df_year_2023['Hist. Géo.EMC (sur 50)'].mean(),
            dnb_df_year_2023['Sciences (sur 50)'].mean(),
            dnb_df_year_2023['DNL Hist. Géo. arabe (sur 50)'].mean(),
            dnb_df_year_2023['Langue de la section (sur 50)'].mean()
        ],
        '2024': [
            dnb_df_year_2024['Hist. Géo.EMC (sur 50)'].mean(),
            dnb_df_year_2024['Sciences (sur 50)'].mean(),
            dnb_df_year_2024['DNL Hist. Géo. arabe (sur 50)'].mean(),
            dnb_df_year_2024['Langue de la section (sur 50)'].mean()
        ]
    })

    summary_data_socle = pd.DataFrame({
        'Épreuve': ['Socle Commun'],
        '2023': [dnb_df_year_2023['Socle Commun (sur 400)'].mean()],
        '2024': [dnb_df_year_2024['Socle Commun (sur 400)'].mean()]
    })

    return summary_data_100, summary_data_50, summary_data_socle

# Créer les résumés de données pour les trois graphiques
summary_df_100, summary_df_50, summary_df_socle = create_summary(dnb_df_year_2023, dnb_df_year_2024)

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


st.title("Résultats DNB - EFE Maroc")
st.divider()


# Affichage des graphiques avec trois colonnes

st.subheader("Résultats tout établissements")

col1, col2, col3 = st.columns(3)

with col1:
    display_bar_chart(summary_df_100, "Épreuves finales sur 100")

with col2:
    display_bar_chart(summary_df_50, "Épreuves finales sur 50")

with col3:
    display_bar_chart(summary_df_socle, "Socle Commun")




# Fonction pour créer des couleurs conditionnelles pour la surbrillance
def color_based_on_highlight(df):
    return ['#ff6347' if highlight else '#80c9e0' for highlight in df['highlight']]

# Liste des épreuves
subjects = [
    "Français (sur 100)", "Hist. Géo.EMC (sur 50)", "Mathématiques (sur 100)",
    "Sciences (sur 50)", "SO de projet (sur 100)", "Socle Commun (sur 400)",
    "DNL Hist. Géo. arabe (sur 50)", "Langue de la section (sur 50)"
]



# Fonction pour calculer la moyenne et la variation
@st.cache_data
def calculate_metrics(df_2024, df_2023, highlighted_etablissement, subject):
    mean_2024 = df_2024[df_2024['établissement'] == highlighted_etablissement][subject].mean()
    mean_2023 = df_2023[df_2023['établissement'] == highlighted_etablissement][subject].mean()
    variation = ((mean_2024 - mean_2023) / mean_2023 * 100) if mean_2023 != 0 else 0
    return mean_2024, variation

st.subheader(f'Résultats pour : {highlighted_etablissement}')

# Affichage des informations pour chaque épreuve dans une grille 4x2
rows = [subjects[:4], subjects[4:]]  # Diviser les épreuves en deux lignes de 4

for row in rows:
    cols = st.columns(4)
    for idx, subject in enumerate(row):
        with cols[idx]:
            # Calculer les métriques pour l'épreuve
            mean_2024, variation = calculate_metrics(dnb_df_year_2024, dnb_df_year_2023, highlighted_etablissement, subject)

            # Préparer les données de classement pour l'épreuve avec surbrillance
            subject_summary = dnb_df_year_2024[['établissement', subject]].copy()
            subject_summary = subject_summary.rename(columns={subject: 'moyenne'})  # Renommer pour uniformité
            subject_summary = subject_summary.sort_values(by='moyenne', ascending=False).reset_index(drop=True)
            subject_summary['rang'] = subject_summary.index + 1
            subject_summary['highlight'] = subject_summary['établissement'] == highlighted_etablissement

            # Afficher le titre, la métrique et la variation
            with st.container(border=True):
                st.write(subject)
                st.metric(label="Moyenne 2024", value=f"{mean_2024:.2f}", delta=f"{variation:.2f}%")

                # Créer le graphique de classement pour l'épreuve
                fig = px.bar(
                    subject_summary,
                    x="moyenne",
                    y="établissement",
                    orientation="h",
                    text="rang",
                    labels={"moyenne": "Moyenne", "établissement": "Établissement"}
                )
                fig.update_traces(marker_color=color_based_on_highlight(subject_summary), textposition='outside')
                fig.update_layout(yaxis=dict(autorange="reversed"))  # Trier de haut en bas
                fig.update_layout(xaxis_title=None, yaxis_title=None)

                st.plotly_chart(fig, use_container_width=True)





# Calcul de la matrice de corrélation
correlation_matrix = dnb_df_year_2024[subjects].corr()

# Trouver les deux paires d'épreuves les plus corrélées
correlated_pairs = []
for i in range(len(subjects)):
    for j in range(i + 1, len(subjects)):
        corr_value = correlation_matrix.iloc[i, j]
        correlated_pairs.append((subjects[i], subjects[j], corr_value))

# Trier les paires par valeur absolue de corrélation et prendre les deux plus élevées
top_two_pairs = sorted(correlated_pairs, key=lambda x: abs(x[2]), reverse=True)[:2]


st.subheader("Épreuves les plus corrélées")
col1, col2 = st.columns(2)

for idx, (subj1, subj2, corr_value) in enumerate(top_two_pairs):
    # Créer une nouvelle colonne pour la surbrillance de l'établissement
    dnb_df_year_2024['highlight'] = dnb_df_year_2024['établissement'] == highlighted_etablissement

    # Créer le scatter plot pour la paire d'épreuves
    fig = px.scatter(
        dnb_df_year_2024,
        x=subj1,
        y=subj2,
        hover_name="établissement",  # Afficher le nom de l'établissement au survol
        labels={"highlight": "Établissement sélectionné"},
        title=f"{subj1} vs {subj2}",
    )

    # Mettre à jour la légende et l'affichage
    fig.update_layout(showlegend=False)
    fig.update_traces(marker=dict(color=color_based_on_highlight(dnb_df_year_2024)))
    fig.update_traces(marker=dict(size=10 if dnb_df_year_2024['highlight'].any() else 6))

    # Afficher le graphique dans la colonne appropriée
    if idx == 0:
        col1.plotly_chart(fig, use_container_width=True)
    else:
        col2.plotly_chart(fig, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    with st.popover("Comprendre la visualisation"):
        st.write("Dans les graphiques ci-dessus, le point rouge représente l'établissement que vous avez sélectionné, tandis que les points bleus représentent les autres établissements. Ce positionnement permet de situer les performances de l'établissement choisi par rapport aux autres dans chaque paire d'épreuves corrélées. Si le point rouge se trouve vers le haut ou la droite du graphique, cela indique que cet établissement a des performances supérieures dans l'épreuve correspondante. Inversement, un point rouge en bas ou à gauche signifie que les scores de l'établissement sont inférieurs à ceux de la plupart des autres établissements.")

with col2:
    with st.popover('Voir les autres corréaltions'):
        correlation_matrix = dnb_df_year_2024[subjects].corr()
        subjects = [
        "Français (sur 100)", "Hist. Géo.EMC (sur 50)", "Mathématiques (sur 100)",
        "Sciences (sur 50)", "SO de projet (sur 100)", "Socle Commun (sur 400)",
        "DNL Hist. Géo. arabe (sur 50)", "Langue de la section (sur 50)"
    ]

        # Calcul de la matrice de corrélation
        correlation_matrix = dnb_df_year_2024[subjects].corr()

        # Affichage de la matrice de corrélation sous forme de carte de chaleur
        st.subheader("Corrélations entre les épreuves du DNB - 2024")

        # Créer la figure de la heatmap avec des annotations
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale="Viridis",
            colorbar=dict(title="Corrélation"),
            zmin=-1, zmax=1,  # Plage de valeurs pour la corrélation
            text=correlation_matrix.round(2).values,  # Texte des valeurs arrondies à 2 décimales
            texttemplate="%{text}",  # Affiche les valeurs dans chaque cellule
        ))

        # Mettre à jour la mise en page pour clarifier les étiquettes
        fig.update_layout(
            title="Matrice de corrélation entre les épreuves",
            xaxis_title=None,
            yaxis_title=None,
            xaxis=dict(tickangle=-45)  # Incline les noms des épreuves pour plus de lisibilité
        )

        st.plotly_chart(fig, use_container_width=True)
