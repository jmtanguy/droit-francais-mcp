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

from time import sleep

from api_judilibre import JudilibreAPI
from api_legifrance import LegifranceAPI

# %%
# ============================================================================
# INITIALISATION API JUDILIBRE (SANDBOX)
# ============================================================================
# Crée une instance de l'API JudiLibre en mode sandbox
# Le token OAuth sera récupéré automatiquement lors de la première requête

api = JudilibreAPI(sandbox=True)

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
api.search(
    query="responsabilité contractuelle", jurisdiction=["cc"], chamber=["civ1"], page_size=2
)

# %%
# ============================================================================
# EXEMPLES SUPPLÉMENTAIRES - Décommenter pour tester
# ============================================================================

# Recherche simple dans la jurisprudence sur toutes les juridictions
api.search(
    query="responsabilité contractuelle",  page_size=5
)


#%%
# Récupération d'une décision spécifique
decision = api.consult("60c993fe7c5a5b81c05bdfc3")

# Explorer toutes les taxonomies disponibles
# all_taxonomies = api.taxonomy()
# for tax in all_taxonomies:
#     print(f"{tax['key']}: {tax['description']}")

# %%
# ============================================================================
# TESTS API LÉGIFRANCE - Décommenter pour tester
# ============================================================================
from api_legifrance import LegifranceAPI
api_lf = LegifranceAPI(sandbox=False)
# %%
# Recherche dans le Code civil
results = api_lf.search(query="mariage", fond="CODE_ETAT", code="Code civil" ,page_size=5)

#%%
# Recherche dans le fond JORF
results = api_lf.search(query="crédit", fond="JORF",   page_size=5)

# %%
# Recherche article
article = api_lf.consult("LEGIARTI000006422500")
text = api_lf.consult("LEGITEXT000006075116")
text_date = api_lf.consult("LEGITEXT000006069565_31-12-2006")

#%%
text = api_lf.consult("JURITEXT000045940024")

#%%
api_lf.search(query="télétravail", fond="KALI", page_size=3)

# %%
# Test
from api_legifrance import LegifranceAPI
from time import sleep

api_lf = LegifranceAPI(sandbox=True)

#%%
api_lf.search(query="crédit consommateur 2025",fond= "JORF", page_size=2, clean=True)

#%%
api_lf.search(query="responsabilité du courtier en crédit sur un montage in fine",fond= "ALL", page_size=2, clean=True)

#%%
api_lf.search(query="Cour d'appel de Paris 2 avril 2025",fond= "ALL", page_size=2, clean=True)


#%%
# Test
result = api_lf.search(
   query="caméra vidéo de surveillance",
   fond="CNIL",
   field_type="ALL",
   date_start="2020-01-01", 
   date_end="2022-01-01", 
   page_size=2,
   page_number=1,
   sort="DATE_DESC"
)

result

# %%
# Testing all date facets with all fonds
fonds = ["ALL", "JORF", "LODA_DATE", "LODA_ETAT", "JURI", "CETAT", "JUFI", "CONSTIT", "KALI", "CIRC", "ACCO", "CNIL", "CODE_DATE","CODE_ETAT"]
facets = ["DATE_SIGNATURE", "DATE_PUBLICATION", "DATE_PARUTION", "LODA_DATE", "LODA_ETAT", "DATE_DECISION", "DATE_ARRET", "DATE_EFFET", "DATE_CREATION", "DATE_EXPORT", "DATE_DEPOT", "DATE_DELIBERATION"]

