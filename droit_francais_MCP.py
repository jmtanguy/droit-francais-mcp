#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Serveur MCP de requête aux API publiques Légifrance et Judilibre

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

import logging
import sys
from typing import Any, Dict, List, Optional, Union
from fastmcp import FastMCP

from __version__ import __author__, __description__, __version__
from api_judilibre import JudilibreAPI
from api_legifrance import LegifranceAPI

# ============================================================================
# CONFIGURATION ET INITIALISATION
# ============================================================================

# Configuration du logging pour debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Envoi vers stderr pour MCP
    ],
)
logger = logging.getLogger(__name__)

# Initialisation de FastMCP
try:
    mcp = FastMCP(f"FR Légifrance et Judilibre MCP Server v{__version__} - Droit Français Officiel")
except Exception as e:
    logger.error(f"ERREUR ÉTAPE 1: Échec de l'initialisation du serveur MCP: {e}")
    raise

# Initialisation de l'API LegiFrance
try:
    legifranceapi = LegifranceAPI(sandbox=False)
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de l'API LegiFrance: {e}")
    legifranceapi = None

# Initialisation de l'API Judilibre
try:
    judilibreapi = JudilibreAPI(sandbox=False)
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de l'API Judilibre: {e}")
    judilibreapi = None


# ============================================================================
# RESOURCES - DOCUMENTATION DÉTAILLÉE
# ============================================================================


@mcp.resource("legifrance://documentation/fonds")
def documentation_fonds_legifrance() -> str:
    """Fonds de recherche Légifrance disponibles."""
    return """
# FONDS LÉGIFRANCE

**ALL** (défaut): Tous les fonds | **CODE_ETAT/CODE_DATE**: Codes consolidés | **LODA_ETAT/LODA_DATE**: Lois, Ordonnances, Décrets, Arrêtés | **JORF**: Journal Officiel | **JURI**: Jurisprudence judiciaire | **CETAT**: Conseil d'État | **JUFI**: Cour des comptes | **CONSTIT**: Conseil Constitutionnel | **KALI**: Conventions collectives | **ACCO**: Accords d'entreprise | **CIRC**: Circulaires | **CNIL**: CNIL
"""


@mcp.resource("legifrance://documentation/champs")
def documentation_champs_legifrance() -> str:
    """Types de champs de recherche Légifrance."""
    return """
# CHAMPS DE RECHERCHE

**ALL** (défaut): Tous les champs | **TITLE**: Titre | **ARTICLE**: Contenu articles | **TEXTE**: Texte complet | **NUM_ARTICLE**: N° article | **NOR**: N° ordre réglementaire | **NUM**: N° texte | **RESUMES**: Résumés jurisprudence | **MINISTERE**: Ministère | **IDCC**: Convention collective | **MOTS_CLES**: Mots-clés
"""


@mcp.resource("legifrance://documentation/types-recherche")
def documentation_types_recherche_legifrance() -> str:
    """Types de recherche Légifrance."""
    return """
# TYPES DE RECHERCHE

**EXACTE** (défaut, recommandé): Expression exacte | **TOUS_LES_MOTS_DANS_UN_CHAMP**: Tous les mots présents (ET) | **UN_DES_MOTS**: Au moins un mot (OU) | **AUCUN_DES_MOTS**: Exclusion de mots | **AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION**: Exclusion expression exacte
"""


@mcp.resource("legifrance://documentation/options-tri")
def documentation_options_tri_legifrance() -> str:
    """Options de tri Légifrance."""
    return """
# TRI DES RÉSULTATS

**PERTINENCE** (recommandé): Score de pertinence | **SIGNATURE_DATE_DESC**: Date signature récente→ancienne | **SIGNATURE_DATE_ASC**: Date signature ancienne→récente | **DATE_PUBLI_DESC**: Date publication récente→ancienne | **DATE_PUBLI_ASC**: Date publication ancienne→récente
"""



@mcp.resource("legifrance://documentation/filtres-dates")
def documentation_filtres_dates_legifrance() -> str:
    """Filtres de dates Légifrance."""
    return """
# FILTRES DE DATES

Format: YYYY-MM-DD (date_debut obligatoire, date_fin optionnel)

⚠️ **FONDS COMPATIBLES**: JORF, LODA_DATE, LODA_ETAT (DATE_PUBLICATION) | JURI, CETAT, JUFI, CONSTIT (DATE_DECISION) | KALI, CIRC, ACCO (DATE_SIGNATURE)

❌ **INCOMPATIBLES**: ALL, CODE_DATE, CODE_ETAT, CNIL (filtres ignorés avec avertissement)

Note: DATE_PUBLICATION ≠ DATE_DECISION ≠ DATE_SIGNATURE. Pour jurisprudence: date de décision, pas de mise en ligne.
"""



@mcp.resource("judilibre://documentation/juridictions")
def documentation_juridictions_judilibre() -> str:
    """Juridictions Judilibre."""
    return """
# JURIDICTIONS

**cc**: Cour de cassation | **ca**: Cours d'appel | **tj**: Tribunaux judiciaires | **tcom**: Tribunaux de commerce 
"""


@mcp.resource("judilibre://documentation/chambres")
def documentation_chambres_judilibre() -> str:
    """Chambres Cour de cassation."""
    return """
# CHAMBRES (Cour de cassation)

**pl**: Assemblée plénière | **mi**: Chambre mixte | **civ1**: 1ère civ. | **civ2**: 2e civ. | **civ3**: 3e civ. | **comm**: Commerciale | **soc**: Sociale | **cr**: Criminelle | **creun**: Chambres réunies | **ordo**: Ordonnance | **allciv**: Toutes civ. | **other**: Autre

Note: Claude convertit automatiquement les noms complets en codes.
"""


@mcp.resource("judilibre://documentation/solutions")
def documentation_solutions_judilibre() -> str:
    """Solutions des décisions."""
    return """
# SOLUTIONS

**cassation**: Cassation | **cassation_partielle**: Cassation partielle | **rejet**: Rejet | **annulation**: Annulation | **irrecevabilite**: Irrecevabilité | **desistement**: Désistement | **non-lieu**: Non-lieu | **qpc**: QPC
"""


@mcp.resource("judilibre://documentation/localisations")
def documentation_localisations_judilibre() -> str:
    """Localisations (sièges de juridictions)."""
    return """
# LOCALISATIONS

**Cours d'appel**: ca_<ville> (ex: ca_paris, ca_lyon) | **Tribunaux judiciaires**: tj<INSEE> (ex: tj75101=Paris, tj69123=Lyon) | **Tribunaux commerce**: tcom<INSEE>

Utiliser `obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca|tj|tcom")` pour liste complète. Claude convertit automatiquement les noms de villes.
"""


@mcp.resource("judilibre://documentation/types-decision")
def documentation_types_decision_judilibre() -> str:
    """Types de décision."""
    return """
# TYPES DE DÉCISION

**arret**: Juridictions collégiales (cc, ca, ce, caa, crc) | **ordonnance**: Juge unique, référés, toutes juridictions | **qpc**: QPC (cc, ce uniquement) | **saisie**: Saisies (tj uniquement)
"""


@mcp.resource("judilibre://documentation/themes")
def documentation_themes_judilibre() -> str:
    """Thèmes juridiques."""
    return """
# THÈMES (Matières juridiques)

Liste longue (centaines). Catégories: **Civil** (responsabilité, contrats, famille, successions) | **Commercial** (sociétés, concurrence, PI, proc. collectives) | **Travail** (licenciement, salaires, sécurité sociale) | **Pénal** (infractions, procédure, peines) | **Admin** (fonction publique, urbanisme) | **Fiscal** (IR, TVA, IS)

Utiliser `obtenir_taxonomie_judilibre(taxonomy_id="theme")` pour codes exacts. Explorer sans filtre puis affiner.
"""


@mcp.resource("judilibre://documentation/options-tri")
def documentation_options_tri_judilibre() -> str:
    """Options de tri Judilibre."""
    return """
# TRI

**scorepub** (défaut, recommandé): Pertinence + publication (Bulletin>Rapport>Lettre>Communiqué>Non publié) | **score**: Pertinence seule | **date**: Date décision

**Ordre**: desc (défaut, récent→ancien) | asc (ancien→récent)
"""



# ============================================================================
# OUTILS LEGIFRANCE - RECHERCHE DES TEXTES DE DROIT FRANÇAIS
# ============================================================================


@mcp.tool
def rechercher_legifrance(
    recherche: str,
    fond: str = "ALL",
    type_champ: str = "ALL",
    type_recherche: str = "TOUS_LES_MOTS_DANS_UN_CHAMP",
    code: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    page: int = 0,
    page_taille: int = 20,
    tri: Optional[str] = "PERTINENCE",
    operateur: str = "ET",
) -> Any:
    """
    Recherche avancée dans la base juridique Légifrance (codes, lois, jurisprudence, conventions).

    Args:
        recherche: Terme(s) de recherche. Ex: "mariage", "responsabilité civile"
        fond: Fonds (ALL, CODE_ETAT, LODA_ETAT, JORF, JURI, KALI, etc.). Défaut: "ALL"
        type_champ: Champ de recherche (ALL, TITLE, ARTICLE, etc.). Défaut: "ALL"
        type_recherche: Type de recherche : EXACTE, TOUS_LES_MOTS_DANS_UN_CHAMP, UN_DES_MOTS, AUCUN_DES_MOTS. Défaut: "TOUS_LES_MOTS_DANS_UN_CHAMP"
        code: Nom du code (ex: "Code civil") pour fonds CODE_ETAT/CODE_DATE. Défaut : None
        date_debut: Date de début pour filtres dates (YYYY-MM-DD) avec les fonds: JORF, LODA_DATE, LODA_ETAT, JURI, CETAT, JUFI, CONSTIT, KALI, CIRC, ACCO. Défaut : None
        date_fin: Date de fin pour filtres dates (YYYY-MM-DD) avec les fonds: JORF, LODA_DATE, LODA_ETAT, JURI, CETAT, JUFI, CONSTIT, KALI, CIRC, ACCO : Défaut : None
        page: Numéro de page. Défaut: 0
        page_taille: Résultats par page (max 50). Défaut: 20
        tri: Ordre de tri avec PERTINENCE, SIGNATURE_DATE_DESC, SIGNATURE_DATE_ASC, DATE_PUBLI_DESC, DATE_PUBLI_ASC Défaut: PERTINENCE
        operateur: Opérateur entre champs (ET, OU). Défaut: "ET"

    Returns:
        Liste de résultats avec métadonnées. Utiliser l'outil consult_legifrance(id) pour le contenu complet.

    Ressources utiles:
        - legifrance://documentation/fonds - Liste des fonds disponibles
        - legifrance://documentation/champs - Types de champs de recherche
        - legifrance://documentation/types-recherche - Valeurs pour type_recherche
        - legifrance://documentation/filtres-dates - Guide sur les filtres de dates
        - legifrance://documentation/options-tri - Valeurs pour sort
    """

    try:
        # Validation des paramètres
        if not recherche or not recherche.strip():
            logger.error("Requête de recherche vide")
            return []

        # Vérification de l'initialisation de l'API
        if legifranceapi is None:
            logger.error("API Légifrance non initialisée")
            return []

        # Validation des filtres de dates selon le fond
        FONDS_WITH_DATE_FILTERS = ["JORF", "LODA_DATE", "LODA_ETAT", "JURI", "CETAT", "JUFI", "CONSTIT", "KALI", "CIRC", "ACCO"]

        if (date_debut or date_fin) and fond not in FONDS_WITH_DATE_FILTERS:
            warning = [
                f"⚠️ ATTENTION: Les filtres de dates (date_debut/date_fin) sont ignorés pour le fond '{fond}'. "
                f"Les filtres de dates ne fonctionnent que pour les fonds: {', '.join(FONDS_WITH_DATE_FILTERS)}"
            ]
            # Effacer les filtres de dates pour éviter toute confusion
            date_debut = None
            date_fin = None
        else:
            warning = None

        search_results = legifranceapi.search(
            query=recherche,
            fond=fond,
            field_type=type_champ,
            search_type=type_recherche,
            code=code,
            date_start=date_debut,
            date_end=date_fin,
            page_number=page,
            page_size=page_taille,
            sort=tri,
            operator=operateur,
        )

        search_results = search_results or []
        if warning:
            search_results = {"warning": warning, "results": search_results}

        return search_results

    except Exception as e:
        logger.error(f"Erreur lors de la recherche '{recherche}': {e}")
        return "Erreur lors de la recherche"


@mcp.tool
def consulter_legifrance(id: str) -> Any:
    """
    Récupère le texte intégral d'un article juridique depuis Légifrance.

    Cette fonction est la DEUXIÈME ÉTAPE après toute recherche pour obtenir le contenu complet.

    Args:
        id: ID de l'article (LEGIARTI..., LEGITEXT..., JURITEXT..., etc.)
                   Obtenu depuis les résultats de recherche (metadata 'id')

    Returns:
        Le contenu juridique 
    """

    try:
        # Validation des paramètres
        if not id or not id.strip():
            logger.error("ID article vide")
            return {"erreur": "L'ID de l'article ne peut pas être vide"}

        # Vérification de l'initialisation de l'API
        if legifranceapi is None:
            logger.error("API Légifrance non initialisée")
            return {"erreur": "L'API Légifrance n'est pas initialisée"}

        article = legifranceapi.consult(id)
        return article

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'article '{id}': {e}")
        return {"erreur": f"Erreur de récupération d'article: {str(e)}"}


# ============================================================================
# OUTILS JUDILIBRE - RECHERCHE DE JURISPRUDENCE
# ============================================================================


@mcp.tool
def obtenir_taxonomie_judilibre(
    taxonomy_id: Optional[str] = None,
    key: Optional[str] = None,
    value: Optional[str] = None,
    context_value: Optional[str] = None,
) -> Any:
    """
    Récupère les valeurs valides pour les filtres de recherche Judilibre (juridictions, chambres, solutions, etc.).
    Utiliser les ressources en priorité pour connaître les valeurs possibles avant d'utiliser cette fonction.
    
    Args:
        taxonomy_id: Type de taxonomie (jurisdiction, chamber, solution, theme, location, etc.)
        key: Clé pour obtenir l'intitulé complet
        value: Intitulé pour obtenir la clé
        context_value: Contexte pour certaines taxonomies (cc, ca, tj)

    Returns:
        Données de taxonomie (liste ou dict selon les paramètres)

    Exemples d'usage:
        - obtenir_taxonomie_judilibre() → toutes les taxonomies
        - obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc") → chambres Cour de cassation
        - obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca") → cours d'appel

    Ressources utiles:
        - judilibre://documentation/juridictions - Juridictions disponibles
        - judilibre://documentation/chambres - Chambres de la Cour de cassation
        - judilibre://documentation/solutions - Types de solutions
    """
    logger.debug(
        f"APPEL: obtenir_taxonomie_judilibre(taxonomy_id='{taxonomy_id}', key='{key}', value='{value}', context_value='{context_value}')"
    )

    try:
        if judilibreapi is None:
            logger.error("API Judilibre non initialisée")
            return {"erreur": "L'API Judilibre n'est pas initialisée"}

        result = judilibreapi.taxonomy(
            taxonomy_id=taxonomy_id, key=key, value=value, context_value=context_value
        )

        return result

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la taxonomie: {e}")
        return {"erreur": f"Erreur taxonomie: {str(e)}"}


@mcp.tool
def rechercher_jurisprudence_judilibre(
    recherche: Optional[str] = None,
    juridiction: Optional[str] = None,
    localisation: Optional[str] = None,
    chambre: Optional[str] = None,
    type_decision: Optional[str] = None,
    theme: Optional[str] = None,
    solution: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    tri: str = "scorepub",
    ordre: str = "desc",
    nombre_resultats: int = 20,
    page: int = 0,
) -> Any:
    """
    Recherche de jurisprudence dans la base Judilibre (décisions de toutes les juridictions françaises).
    À utiliser en priorité pour la recherche jurisprudentielle.

    Args:
        recherche: Texte de recherche
        juridiction: Code juridiction (cc, ca, tj, tcom). Defaut : None (recherche dans toutes les juridictions)
        localisation: Code siège. Format varie selon juridiction (très nombreux, donc à utiliser que si nécessaire). Défaut : None
            Exemples: "ca_paris", "tj06088" (Nice), "ca_lyon"
            Utiliser obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca" ou "tj")
        chambre: Code chambre - CLÉS: "pl", "mi", "civ1", "civ2", "civ3", "comm", "soc", "cr" Défaut : None
            ⚠️ Utiliser les CLÉS, pas les noms complets
        type_decision: Type de décision. Valeurs: arret, ordonnance, qpc, saisie. Défaut : None
        theme: Code matière juridique (très nombreux, donc à utiliser que si nécessaire). Défaut : None
            Utiliser obtenir_taxonomie_judilibre(taxonomy_id="theme") pour la liste
        solution: Solution (cassation, rejet, annulation, etc.). Défaut : None
        date_debut: Date début ISO (ex: 2023-01-15). Défaut : None
        date_fin: Date fin ISO (ex: 2023-12-15). Défaut : None
        tri: Ordre de tri. Valeurs: scorepub, score, date. Défaut: "scorepub"
        ordre: Sens du tri (desc, asc). Défaut: "desc"
        nombre_resultats: Résultats par page (max 50). Défaut: 20
        page: Numéro de page (commence à 0). Défaut : 0

    Returns:
        Liste de décisions incluant les id.
        Utiliser obtenir_decision_judilibre(id) pour le texte complet.

    Ressources utiles:
        - judilibre://documentation/juridictions - Codes de juridictions
        - judilibre://documentation/chambres - Codes de chambres
        - judilibre://documentation/localisations - Codes de localisations (sièges)
        - judilibre://documentation/types-decision - Types de décision
        - judilibre://documentation/themes - Thèmes (matières juridiques)
        - judilibre://documentation/solutions - Types de solutions
        - judilibre://documentation/options-tri - Options de tri (tri + ordre)
   """

    try:
        if judilibreapi is None:
            logger.error("API Judilibre non initialisée")
            return [{"erreur": "L'API Judilibre n'est pas initialisée"}]

        # Conversion des paramètres en listes si fournis
        jurisdiction_list = [juridiction] if juridiction else ["cc", "ca", "tj", "tcom"] # Par défaut toutes les juridictions
        location_list = [localisation] if localisation else None
        chamber_list = [chambre] if chambre else None
        type_list = [type_decision] if type_decision else None
        theme_list = [theme] if theme else None
        solution_list = [solution] if solution else None

        results = judilibreapi.search(
            query=recherche,
            jurisdiction=jurisdiction_list,
            location=location_list,
            chamber=chamber_list,
            type=type_list,
            theme=theme_list,
            solution=solution_list,
            date_start=date_debut,
            date_end=date_fin,
            sort=tri,
            order=ordre,
            page_size=nombre_resultats,
            page=page,
            resolve_references=True,  # Obtenir les intitulés complets
        )

        return results

    except Exception as e:
        logger.error(f"Erreur lors de la recherche Judilibre: {e}")
        return "Erreur lors de la recherche Judilibre"


@mcp.tool
def consulter_decision_judilibre(decision_id: str) -> Any:
    """
    Récupère le contenu d'une décision de justice depuis Judilibre.

    Cette fonction est la DEUXIÈME ÉTAPE après rechercher_jurisprudence_judilibre() pour obtenir le texte complet.

    Args:
        decision_id: ID unique de la décision (champ 'id' des résultats de recherche)

    Returns:
        La décision complète.

    """
    logger.debug(f"APPEL: obtenir_decision_judilibre(decision_id='{decision_id}')")

    try:
        if not decision_id or not decision_id.strip():
            logger.error("ID décision vide")
            return {"erreur": "L'ID de la décision ne peut pas être vide"}

        if judilibreapi is None:
            logger.error("API Judilibre non initialisée")
            return {"erreur": "L'API Judilibre n'est pas initialisée"}

        decision = judilibreapi.consult(decision_id=decision_id)
        return decision

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la décision '{decision_id}': {e}")
        return {"erreur": f"Erreur récupération décision: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
