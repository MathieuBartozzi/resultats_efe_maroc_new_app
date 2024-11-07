import streamlit as st

# Configuration de la mise en page
st.set_page_config(
    page_title='Résultats EFE Maroc')

st.sidebar.success("Selectionner une page.")

# Titre de l'application
st.title("Analyse des Résultats des Épreuves - EFE Maroc")

# Introduction
st.markdown("""
Bienvenue sur l'application d'analyse des résultats des épreuves du Baccalauréat et du Diplôme National du Brevet (DNB) pour les établissements EFE Maroc.
Cette interface vous permet de naviguer et d'explorer les données de performance des élèves par épreuve, par spécialité, et par établissement pour les années 2023 et 2024.

Chaque section présente des graphiques interactifs et des classements qui permettent de visualiser les moyennes des différents établissements, ainsi que les variations d'une année à l'autre. Vous pouvez également mettre en surbrillance un établissement de votre choix pour comparer ses résultats aux autres établissements dans des épreuves spécifiques. En plus, une analyse des corrélations entre les épreuves est disponible, vous offrant un aperçu des tendances et des performances comparatives des élèves.

Explorez les différents onglets et visualisations pour découvrir en détail les résultats académiques de chaque épreuve, et n'hésitez pas à utiliser les options de filtrage pour personnaliser votre analyse.
""")

st.write('**Bonne navigation !**')

st.divider()
