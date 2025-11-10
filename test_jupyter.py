#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📓 FICHIER D'EXPLORATION ET VALIDATION RAPIDE - APIs JudiLibre et Légifrance

⚠️ CE FICHIER UTILISE LE FORMAT JUPYTER NOTEBOOK (cellules #%%)
   Pour l'utiliser, ouvrez-le dans:
   - VSCode avec l'extension Jupyter
   - PyCharm Professional avec support Jupyter
   - JupyterLab ou Jupyter Notebook
   - Ou tout IDE supportant les cellules interactives Python

🎯 OBJECTIF:
   Permet d'explorer rapidement les APIs et de valider les réponses
   sans avoir à exécuter des tests complets. Idéal pour:
   - Tester rapidement une requête API
   - Explorer les structures de données retournées
   - Valider les taxonomies disponibles
   - Débugger des problèmes d'API

💡 UTILISATION:
   1. Ouvrir ce fichier dans un IDE supportant Jupyter
   2. Exécuter les cellules une par une avec Shift+Enter
   3. Modifier les paramètres selon vos besoins
   4. Observer les résultats directement dans la cellule

📝 NOTES:
   - Chaque cellule (#%%) peut être exécutée indépendamment
   - Les variables sont partagées entre les cellules
   - Nécessite des credentials valides dans le fichier .env
   - Mode sandbox activé par défaut

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License
"""

# %%
# ============================================================================
# IMPORTS ET INITIALISATION
# ============================================================================

from api_judilibre import JudiLibreAPI
from api_legifrance import LegiFranceAPI

# %%
# ============================================================================
# INITIALISATION API JUDILIBRE (SANDBOX)
# ============================================================================
# Crée une instance de l'API JudiLibre en mode sandbox
# Le token OAuth sera récupéré automatiquement lors de la première requête

api = JudiLibreAPI(sandbox=True)

# %%
# ============================================================================
# TEST 1: Récupération des sièges de cours d'appel
# ============================================================================
# Exemple: Récupérer les informations sur la Cour d'appel de Rouen
# context_value="ca" indique qu'on cherche dans les cours d'appel

api.taxonomy("location", key="ca_rouen", context_value="ca")

# %%
# ============================================================================
# TEST 2: Lister tous les sièges de tribunaux de commerce
# ============================================================================
# Récupère la liste complète des tribunaux de commerce (tcom)
# Utile pour connaître tous les codes de localisation disponibles

api.taxonomy("location", context_value="tcom")


# %%
# ============================================================================
# TEST 3: Récupérer toutes les juridictions disponibles
# ============================================================================
# Retourne la liste complète des juridictions:
# cc (Cour de cassation), ca (Cours d'appel), tj (Tribunaux judiciaires), etc.

api.taxonomy("jurisdiction")

# %%
# ============================================================================
# TEST 4: Récupérer les chambres des tribunaux de commerce
# ============================================================================
# Liste les chambres spécifiques aux tribunaux de commerce
# context_value="tcom" filtre sur les tribunaux de commerce uniquement

api.taxonomy("chamber", context_value="tcom")

# %%
# ============================================================================
# EXEMPLES SUPPLÉMENTAIRES - Décommenter pour tester
# ============================================================================

# Recherche simple dans la jurisprudence
results = api.search(
    query="responsabilité contractuelle", jurisdiction=["cc"], chamber=["civ1"], page_size=10
)

# Récupération d'une décision spécifique
decision = api.decision("60794cff9ba5988459c47bf2")

# Explorer toutes les taxonomies disponibles
# all_taxonomies = api.taxonomy()
# for tax in all_taxonomies:
#     print(f"{tax['key']}: {tax['description']}")

# %%
# ============================================================================
# TESTS API LÉGIFRANCE - Décommenter pour tester
# ============================================================================

api_lf = LegiFranceAPI(sandbox=True)

# Recherche dans le Code civil
results = api_lf.search(query="mariage", fond="CODE_ETAT", code_name="Code civil", page_size=5)

# %%
# Recherche article
article = api_lf.article("LEGIARTI000006422334")
# %%
