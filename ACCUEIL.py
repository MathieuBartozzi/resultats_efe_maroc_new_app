import streamlit as st

# Configuration de la mise en page
st.set_page_config(
    page_title='Résultats EFE Maroc')

st.sidebar.success("Selectionner une page.")

# Titre de l'application
st.title("Analyse des Résultats des Épreuves - EFE Maroc")

# Introduction
st.markdown("""
Cette application permet d'analyser les résultats des épreuves du Baccalauréat et du Diplôme National du Brevet (DNB) pour les établissements EFE Maroc.
Cette interface vous permet de naviguer et d'explorer les données de performance des établissement par épreuve pour les années 2023 et 2024.

Chaque section présente des graphiques interactifs et des classements qui permettent de visualiser les moyennes des différents établissements, ainsi que les variations d'une année à l'autre. Un filtrage par établissement de votre choix pour comparer ses résultats aux autres établissements dans des épreuves spécifiques.

""")

st.write('**Bonne navigation !**')

st.divider()
