#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Serveur MCP de requête aux API publics LégiFrance et JudiLibre

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

import logging
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from __version__ import __author__, __description__, __version__
from api_judilibre import JudiLibreAPI
from api_legifrance import LegiFranceAPI

# ============================================================================
# CONFIGURATION ET INITIALISATION
# ============================================================================

# Configuration du logging pour debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Envoi vers stderr pour MCP
        # logging.FileHandler('droit_francais_mcp.log')  # Fichier de log
    ],
)
logger = logging.getLogger(__name__)

# Initialisation de FastMCP
try:
    mcp = FastMCP(f"FR Légifrance et JudiLibre MCP Server v{__version__} - Droit Français Officiel")
    logger.debug(f"ÉTAPE 1: Serveur MCP v{__version__} initialisé avec succès")
    logger.info(f"Version: {__version__} | Auteur: {__author__}")
except Exception as e:
    logger.error(f"ERREUR ÉTAPE 1: Échec de l'initialisation du serveur MCP: {e}")
    raise

# Initialisation de l'API LegiFrance
try:
    legifranceapi = LegiFranceAPI(sandbox=False)
    logger.info("LégiFrance API initialisée avec succès (mode sandbox)")
    logger.debug("ÉTAPE 2: API LegiFrance initialisée avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de l'API LegiFrance: {e}")
    logger.warning(f"ÉTAPE 2: API LegiFrance en échec: {e}")
    legifranceapi = None

# Initialisation de l'API JudiLibre
try:
    judilibreapi = JudiLibreAPI(sandbox=False)
    logger.info("JudiLibre API initialisée avec succès (mode sandbox)")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de l'API JudiLibre: {e}")
    logger.warning(f"API JudiLibre en échec: {e}")
    judilibreapi = None


# ============================================================================
# OUTILS LEGIFRANCE - RECHERCHE DES TEXTES DE DROIT FRANÇAIS
# ============================================================================


@mcp.tool
def rechercher_droit_francais(
    query: str,
    fond: str = "CODE_ETAT",
    type_champ: str = "ALL",
    type_recherche: str = "UN_DES_MOTS",
    code_name: Optional[str] = None,
    filtres_valeurs: Optional[Dict[str, List[str]]] = None,
    filtres_dates: Optional[Dict[str, Dict[str, str]]] = None,
    page_number: int = 1,
    page_size: int = 10,
    sort: Optional[str] = None,
    operateur: str = "ET",
) -> List[Dict[str, Any]]:
    """
    🇫🇷 RECHERCHE AVANCÉE OFFICIELLE dans la base juridique française Légifrance.

    ⚠️ UTILISEZ CET OUTIL POUR TOUTE RECHERCHE AVANCÉE SUR LE DROIT FRANÇAIS ⚠️

    Args:
        query (str): Terme(s) de recherche textuelle. OBLIGATOIRE.
            Exemples: "mariage", "responsabilité civile", "divorce"

        fond (str): Fonds de recherche. Défaut: "CODE_ETAT"
            VALEURS POSSIBLES:
            - "CODE_ETAT": Codes consolidés par état juridique [PAR DÉFAUT - RECOMMANDÉ POUR LES CODES]
            - "CODE_DATE": Codes consolidés par date
            - "LODA_ETAT": Lois, Ordonnances, Décrets, Arrêtés (par état)
            - "LODA_DATE": Lois, Ordonnances, Décrets, Arrêtés (par date)
            - "JORF": Journal Officiel de la République Française
            - "JURI": Jurisprudence judiciaire (Cour de cassation, cours d'appel)
            - "CETAT": Conseil d'État et juridictions administratives
            - "JUFI": Jurisprudence financière (Cour des comptes)
            - "CONSTIT": Conseil Constitutionnel
            - "KALI": Conventions collectives
            - "CIRC": Circulaires et instructions ministérielles
            - "ACCO": Accords d'entreprise
            - "CNIL": Commission Nationale de l'Informatique et des Libertés
            - "ALL": Tous les fonds (recherche transversale)

        type_champ (str): Type de champ où rechercher. Défaut: "ALL"
            VALEURS POSSIBLES:
            - "ALL": Tous les champs [PAR DÉFAUT]
            - "TITLE": Titre du texte
            - "ARTICLE": Contenu des articles
            - "NUM_ARTICLE": Numéro d'article (ex: "Article 1240")
            - "NOR": Numéro d'ordre réglementaire
            - "NUM": Numéro du texte (ex: "Loi n°2018-287")
            - "TEXTE": Contenu textuel complet
            - "RESUMES": Résumés (pour jurisprudence)
            - "MINISTERE": Ministère émetteur
            - "IDCC": Identifiant de convention collective
            - "MOTS_CLES": Mots-clés thématiques

        type_recherche (str): Type de recherche. Défaut: "UN_DES_MOTS"
            VALEURS POSSIBLES:
            - "UN_DES_MOTS": Au moins un des mots [PAR DÉFAUT]
            - "EXACTE": Expression exacte
            - "TOUS_LES_MOTS_DANS_UN_CHAMP": Tous les mots présents
            - "AUCUN_DES_MOTS": Aucun des mots (exclusion)
            - "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION": Expression absente (exclusion)

        code_name (str, optional): Nom du code à rechercher (uniquement pour fonds CODE_DATE/CODE_ETAT).
            EXEMPLES: "Code civil", "Code pénal", "Code du travail", "Code de commerce"

        filtres_valeurs (Dict[str, List[str]], optional): Filtres par valeurs textuelles.
            Format: {"facette": ["valeur1", "valeur2"]}
            EXEMPLES COURANTS:
            - {"NATURE": ["LOI", "ORDONNANCE", "DECRET"]}
            - {"ETAT_JURIDIQUE": ["VIGUEUR"]}
            - {"JURIDICTION_NATURE": ["COUR_CASSATION", "TRIBUNAL_ADMINISTRATIF"]}
            - {"IDCC": ["1880", "2120"]}
            - {"MINISTERE": ["Ministère de la Justice"]}

        filtres_dates (Dict[str, Dict[str, str]], optional): Filtres par périodes de dates.
            Format: {"facette": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}
            EXEMPLES:
            - {"DATE_SIGNATURE": {"start": "2020-01-01", "end": "2023-12-31"}}
            - {"DATE_PUBLICATION": {"start": "2022-01-01", "end": "2022-12-31"}}
            - {"DATE_DECISION": {"start": "2021-01-01", "end": "2024-12-31"}}

        page_number (int): Numéro de la page. Défaut: 1

        page_size (int): Nombre de résultats par page (max 100). Défaut: 10

        sort (str, optional): Ordre de tri des résultats.
            VALEURS POSSIBLES:
            - "PERTINENCE": Tri par pertinence [RECOMMANDÉ]
            - "SIGNATURE_DATE_DESC": Date de signature décroissante
            - "SIGNATURE_DATE_ASC": Date de signature croissante
            - "DATE_PUBLI_DESC": Date de publication décroissante
            - "DATE_PUBLI_ASC": Date de publication croissante

        operateur (str): Opérateur entre les champs. Défaut: "ET"
            VALEURS POSSIBLES:
            - "ET": Tous les critères doivent correspondre [PAR DÉFAUT]
            - "OU": Au moins un critère doit correspondre

    Returns:
        Liste des résultats avec métadonnées

    Répondre factuellement en faisant un résumé des résultats trouvés et en indiquant les IDs des articles pertinents et en affichant le titre et le lien direct vers Légifrance.
    ⚠️ ÉTAPE SUIVANTE OBLIGATOIRE: Utilisez obtenir_article(article_id) pour le contenu complet!

    Examples:
        # Recherche simple dans le Code civil
        rechercher_droit_francais_etendue(
            query="mariage",
            fond="CODE_ETAT",
            code_name="Code civil",
            page_size=20
        )

        # Recherche de lois sur le divorce depuis 2020
        rechercher_droit_francais_etendue(
            query="divorce",
            fond="LODA_ETAT",
            type_recherche="EXACTE",
            filtres_valeurs={"NATURE": ["LOI"]},
            filtres_dates={"DATE_SIGNATURE": {"start": "2020-01-01", "end": "2024-12-31"}},
            sort="SIGNATURE_DATE_DESC"
        )

        # Recherche dans les articles du Code pénal
        rechercher_droit_francais_etendue(
            query="vol",
            fond="CODE_ETAT",
            code_name="Code pénal",
            type_champ="ARTICLE",
            type_recherche="UN_DES_MOTS"
        )

        # Recherche jurisprudentielle à la Cour de cassation
        rechercher_droit_francais_etendue(
            query="responsabilité médicale",
            fond="JURI",
            type_champ="RESUMES",
            filtres_valeurs={"JURIDICTION_NATURE": ["COUR_CASSATION"]},
            page_size=30
        )

        # Recherche dans les conventions collectives
        rechercher_droit_francais_etendue(
            query="télétravail",
            fond="KALI",
            filtres_valeurs={"IDCC": ["1880"]},
            page_size=15
        )
    """
    logger.debug(f"APPEL: rechercher_droit_francais_etendue(query='{query}', fond='{fond}')")

    try:
        # Validation des paramètres
        if not query or not query.strip():
            logger.error("Requête de recherche vide")
            return []

        if page_size < 1 or page_size > 100:
            logger.error(f"Taille du nombre de résultats de recherche invalide: {page_size}")
            return []

        # Vérification de l'initialisation de l'API
        if legifranceapi is None:
            logger.error("API LégiFrance non initialisée")
            return []

        logger.info(f"Recherche: '{query}' dans {fond} (page_size: {page_size})")
        search_results = legifranceapi.search(
            query=query,
            fond=fond,
            type_champ=type_champ,
            type_recherche=type_recherche,
            code_name=code_name,
            filtres_valeurs=filtres_valeurs,
            filtres_dates=filtres_dates,
            page_number=page_number,
            page_size=page_size,
            sort=sort,
            operateur=operateur,
        )

        total_results = len(search_results)
        logger.info(f"Résultats trouvés: {total_results}")

        return search_results or []

    except Exception as e:
        logger.error(f"Erreur lors de la recherche '{query}': {e}")
        return []


@mcp.tool
def obtenir_article(article_id: str) -> Dict[str, Any]:
    """
    🇫🇷 RÉCUPÉRATION OFFICIELLE du texte intégral d'un article juridique français depuis Légifrance.

    ⚠️ OUTIL OFFICIEL pour obtenir le contenu COMPLET des articles de droit français ⚠️

    🔹 Cette fonction est LA DEUXIÈME ÉTAPE OBLIGATOIRE après TOUS les outils de recherche.

    Args:
        article_id (str): Identifiant de l'article obtenu depuis les résultats de recherche. OBLIGATOIRE.

            FORMAT DES IDENTIFIANTS (détection automatique):
            - "LEGIARTI..." : Articles de loi (Code civil, Code pénal, etc.)
            - "LEGITEXT..." : Textes légaux consolidés complets
            - "JURITEXT..." : Décisions de jurisprudence
            - "CNILTEXT..." : Décisions CNIL
            - "KALITEXT..." : Conventions collectives (textes)
            - "KALIARTI..." : Conventions collectives (articles)
            - "ACCOTEXT..." : Accords d'entreprise
            - Autre format : Journal Officiel (par défaut)

            💡 CONSEIL: Utilisez l'ID retourné dans le champ 'id' des résultats de recherche

    Returns:
        Dict contenant le contenu juridique complet avec cette STRUCTURE DÉTAILLÉE:

        📋 MÉTADONNÉES PRINCIPALES:
        - **id**: Identifiant unique de l'article (LEGIARTI..., LEGITEXT..., etc.)
        - **title** / **titre**: Titre de l'article ou du texte
        - **nature**: Nature juridique (CODE, LOI, DECRET, ARRETE, etc.)
        - **etat**: État juridique (VIGUEUR, ABROGE, MODIFIE, etc.)
        - **dateDebut** / **dateVersion**: Date d'entrée en vigueur
        - **dateFin**: Date d'abrogation (si applicable)

        📄 CONTENU TEXTUEL:
        - **texte** / **content** / **texteHtml**: Texte intégral de l'article
        - **articles**: Liste des articles (pour les textes consolidés)
        - **sections**: Structure hiérarchique par sections
        - **nota**: Notes explicatives et observations
        - **commentaire**: Commentaires juridiques

        🔗 LIENS ET RÉFÉRENCES (TRÈS UTILES pour navigation):
        - **liens**:
          * **CITATION**: Articles cités dans ce texte
          * **CONCORDANCE**: Articles en concordance
          * **MODIFICATION**: Articles modifiés par ce texte
          * **TXT_ASSOCIE**: Textes associés
          → Chaque lien contient: id, titre, nature pour navigation facile

        - **sommaire**: Structure hiérarchique du texte (permet navigation)
        - **articleVersions**: Versions antérieures de l'article (historique)

        📊 INFORMATIONS JURIDIQUES AVANCÉES:
        - **num**: Numéro de l'article dans le texte
        - **cid**: Identifiant CID (Container ID)
        - **nor**: Numéro NOR (identification administrative)
        - **dateSignature**: Date de signature du texte
        - **datePubli**: Date de publication au JO
        - **ministere**: Ministère émetteur
        - **autorite**: Autorité signataire

        🏛️ CONTEXTE HIÉRARCHIQUE:
        - **path** / **context**: Chemin complet dans le code
          Exemple: "Code civil > Livre I > Titre V > Chapitre I"
        - **parent**: Information sur le conteneur parent
        - **codeName** / **nomCode**: Nom du code concerné

        💡 COMMENT UTILISER CES MÉTADONNÉES:

        1. **Navigation intelligente**:
           - Utiliser `liens.CITATION` pour explorer les articles référencés
           - Utiliser `sommaire` pour comprendre la structure du texte
           - Utiliser `articleVersions` pour voir l'évolution historique

        2. **Validation juridique**:
           - Vérifier `etat` pour confirmer la validité actuelle
           - Vérifier `dateDebut` et `dateFin` pour la période d'application
           - Vérifier `nota` pour les observations importantes

        3. **Enrichissement de la réponse**:
           - Utiliser `path`/`context` pour situer l'article dans son code
           - Utiliser `liens.TXT_ASSOCIE` pour des textes complémentaires
           - Utiliser `nature` pour qualifier le type de texte

        4. **Citations et références**:
           - Utiliser `nor` pour les références administratives
           - Utiliser `dateSignature` et `datePubli` pour dater précisément
           - Utiliser `ministere`/`autorite` pour identifier l'émetteur

    Répondre factuellement en fournissant le titre et le lien direct vers Légifrance.
    Ajouter le contenu principal et l'intérêt juridique de l'article si pertinent.

    ⚠️ EXPLOITER LES LIENS: Si pertinent, mentionner les articles liés (liens.CITATION)
    pour permettre à l'utilisateur d'approfondir sa recherche.

    WORKFLOW TYPIQUE:
        1. Rechercher avec UN outil de recherche:
           - rechercher_droit_francais_etendue() [recherche avancée]
           - rechercher_droit_francais() [recherche rapide]
           - consulter_code_francais() [codes spécifiques]
           - jurisprudence_francaise() [jurisprudence]

        2. Analyser les résultats et sélectionner les plus pertinents

        3. Extraire l'ID de chaque résultat pertinent (champ 'id')

        4. Appeler obtenir_article(id) pour obtenir le contenu complet

        5. Analyser le contenu détaillé pour répondre à la question juridique

    Examples:
        # Exemple 1: Recherche dans le Code civil puis récupération
        results = consulter_code_francais("Code civil", "mariage")
        for result in results.get('results', []):
            article_id = result.get('id')
            if article_id:
                full_content = obtenir_article(article_id)
                # Analyser full_content...

        # Exemple 2: Recherche jurisprudentielle puis récupération
        results = jurisprudence_francaise("responsabilité médicale")
        if results.get('results'):
            premier_resultat_id = results['results'][0]['id']
            decision_complete = obtenir_article(premier_resultat_id)

        # Exemple 3: Recherche avancée puis récupération
        results = rechercher_droit_francais_etendue(
            query="télétravail",
            fond="KALI",
            page_size=5
        )
        for result in results.get('results', [])[:3]:  # 3 premiers résultats
            convention = obtenir_article(result['id'])

        # Exemple 4: Récupération directe si vous avez déjà l'ID
        article = obtenir_article("LEGIARTI000006419316")  # Article 1240 du Code civil
    """
    logger.debug(f"APPEL: obtenir_article(article_id='{article_id}')")
    try:
        # Validation des paramètres
        if not article_id or not article_id.strip():
            logger.error("ID article vide")
            return {"erreur": "L'ID de l'article ne peut pas être vide"}

        # Vérification de l'initialisation de l'API
        if legifranceapi is None:
            logger.error("API LegiFrance non initialisée")
            return {"erreur": "L'API LegiFrance n'est pas initialisée"}

        logger.info(f"Récupération de l'article: {article_id}")
        article = legifranceapi.article(article_id)
        logger.info(f"Article récupéré avec succès: {article_id}")
        return article

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'article '{article_id}': {e}")
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
) -> List | Dict[str, Any]:
    """
    📚 TAXONOMIE JUDILIBRE - Récupère les listes des termes pour construire des recherches.

    Permet de récupérer les valeurs valides pour les filtres de recherche JudiLibre.

    🎯 UTILISATIONS PRINCIPALES :

    1. **Lister toutes les taxonomies disponibles** :
       - Appeler sans paramètre : obtenir_taxonomie_judilibre()

    2. **Obtenir toutes les valeurs d'une taxonomie** :
       - obtenir_taxonomie_judilibre(taxonomy_id="jurisdiction") → toutes les juridictions
       - obtenir_taxonomie_judilibre(taxonomy_id="chamber") → toutes les chambres
       - obtenir_taxonomie_judilibre(taxonomy_id="type") → tous les types de décisions

    3. **Obtenir l'intitulé d'une clé** :
       - obtenir_taxonomie_judilibre(taxonomy_id="jurisdiction", key="cc") → "Cour de cassation"

    4. **Obtenir la clé d'un intitulé** :
       - obtenir_taxonomie_judilibre(taxonomy_id="jurisdiction", value="cour de cassation") → "cc"

    5. **Taxonomies contextuelles** :
       - obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc") → chambres de la Cour de cassation
       - obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="tj") → tribunaux judiciaires

    📋 TAXONOMIES DISPONIBLES :

    **✅ VALEURS COURANTES (utilisables directement sans taxonomie) :**

    - **jurisdiction** : Juridictions
      Valeurs : cc (Cour de cassation), ca (Cour d'appel), tj (Tribunal judiciaire), tcom (Tribunal de commerce)

    - **type** : Types de décision
      Valeurs : arret, ordonnance, qpc, saisie

    - **solution** : Solutions
      Valeurs : cassation, cassation_partielle, rejet, annulation, irrecevabilite,
                desistement, non-lieu, qpc

    - **publication** : Niveaux de publication
      Valeurs : b (Bulletin), r (Rapport), l (Lettre), c (Communiqué)

    **📚 VALEURS NÉCESSITANT LA TAXONOMIE (nombreuses valeurs) :**

    - **chamber** : Chambres (nécessite context_value: cc ou ca ou tj ou tcom)
      Utilisez : obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc")

    - **formation** : Formations des juridictions
      Utilisez : obtenir_taxonomie_judilibre(taxonomy_id="formation")

    - **theme** : Matières (nomenclature Cour de cassation)
      Utilisez : obtenir_taxonomie_judilibre(taxonomy_id="theme")

    - **field** : Champs de contenu (expose, moyens, motivations, dispositif, etc.)
      Utilisez : obtenir_taxonomie_judilibre(taxonomy_id="field")

    - **location** : Codes et noms des sièges (nécessite context_value: ca ou tj ou tcom)
      Utilisez : obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca")
                ou obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="tj")
                ou obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="tcom")

    - **filetype** : Types de documents associés
      Utilisez : obtenir_taxonomie_judilibre(taxonomy_id="filetype")

    Args:
        taxonomy_id: Identifiant de la taxonomie (type, jurisdiction, chamber, etc.)
        key: Clé pour récupérer l'intitulé complet
        value: Intitulé pour récupérer la clé
        context_value: Contexte pour certaines taxonomies (cc, ca, tj)

    Returns:
        Dictionnaire contenant les données de taxonomie

    Examples:
        # Lister toutes les juridictions
        obtenir_taxonomie_judilibre(taxonomy_id="jurisdiction")

        # Obtenir les chambres de la Cour de cassation
        obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc")

        # Convertir une clé en nom
        obtenir_taxonomie_judilibre(taxonomy_id="jurisdiction", key="cc")
    """
    logger.debug(
        f"APPEL: obtenir_taxonomie_judilibre(taxonomy_id='{taxonomy_id}', key='{key}', value='{value}', context_value='{context_value}')"
    )

    try:
        if judilibreapi is None:
            logger.error("API JudiLibre non initialisée")
            return {"erreur": "L'API JudiLibre n'est pas initialisée"}

        result = judilibreapi.taxonomy(
            taxonomy_id=taxonomy_id, key=key, value=value, context_value=context_value
        )

        logger.info(f"Taxonomie récupérée: {taxonomy_id or 'all'}")
        return result

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la taxonomie: {e}")
        return {"erreur": f"Erreur taxonomie: {str(e)}"}


@mcp.tool
def rechercher_jurisprudence_judilibre(
    query: Optional[str] = None,
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
    nombre_resultats: int = 10,
    page: int = 0,
) -> List[Dict[str, Any]]:
    """
    ⚖️ RECHERCHE DE JURISPRUDENCE dans la base JudiLibre (décisions de justice françaises).

    🔍 OUTIL PRINCIPAL pour rechercher des décisions de justice de toutes les juridictions françaises.

    📋 JURIDICTIONS DISPONIBLES (paramètre juridiction) :
    Utilisez directement ces codes :
    - **"cc"** : Cour de cassation (défaut)
    - **"ca"** : Cours d'appel
    - **"tj"** : Tribunaux judiciaires (ex-TGI/TI)
    - **"ta"** : Tribunaux administratifs
    - **"caa"** : Cours administratives d'appel
    - **"ce"** : Conseil d'État
    - **"tc"** : Tribunaux de commerce
    - **"crc"** : Chambres régionales des comptes

    ⚖️ CHAMBRES DE LA COUR DE CASSATION (paramètre chambre) :
    ⚠️ IMPORTANT: Utilisez uniquement les CLÉS suivantes (pas les noms complets):

    CLÉS À UTILISER POUR CHAMBER :
    - **"pl"**     : Assemblée plénière
    - **"mi"**     : Chambre mixte
    - **"civ1"**   : Première chambre civile
    - **"civ2"**   : Deuxième chambre civile
    - **"civ3"**   : Troisième chambre civile
    - **"comm"**   : Chambre commerciale financière et économique
    - **"soc"**    : Chambre sociale
    - **"cr"**     : Chambre criminelle
    - **"creun"**  : Chambres réunies
    - **"ordo"**   : Première présidence (Ordonnance)
    - **"allciv"** : Toutes les chambres civiles
    - **"other"**  : Autre

    Exemple correct: chambre="civ1" (PAS "Première chambre civile")

    📍 LOCALISATION PAR SIÈGE DE JURIDICTION (paramètre localisation) :
    Permet de filtrer les décisions par le code du siège de juridiction ayant émis les décisions.

    **Pour les Cours d'appel** (utilisez obtenir_taxonomie_judilibre pour la liste complète) :
       Exemples : "ca_paris", "ca_lyon", "ca_versailles", "ca_aix-en-provence", "ca_bordeaux",
                  "ca_toulouse", "ca_rennes", "ca_nimes", "ca_orleans", "ca_grenoble"

    **Pour les Tribunaux judiciaires** (utilisez obtenir_taxonomie_judilibre pour la liste complète) :
       Exemples : "tj06088" (Nice), "tj69123" (Lyon), "tj75101" (Paris), "tj13055" (Marseille)
       Format : tj + code INSEE département + code tribunal

    📂 TYPES DE DÉCISION (paramètre type_decision) :
    Utilisez directement ces codes :
    - **"arret"** : Arrêt
    - **"ordonnance"** : Ordonnance
    - **"qpc"** : Question prioritaire de constitutionnalité
    - **"saisie"** : Saisie

    🎯 SOLUTIONS (paramètre solution) :
    Utilisez directement ces codes :
    - **"cassation"** : Cassation de la décision
    - **"cassation_partielle"** : Cassation partielle
    - **"rejet"** : Rejet du pourvoi
    - **"annulation"** : Annulation
    - **"irrecevabilite"** : Irrecevabilité
    - **"desistement"** : Désistement
    - **"non-lieu"** : Non-lieu à statuer
    - **"qpc"** : Question prioritaire de constitutionnalité

    📰 NIVEAUX DE PUBLICATION (paramètre publication - filtrage automatique) :
    - **"b"** : Bulletin (décisions les plus importantes)
    - **"r"** : Rapport annuel
    - **"l"** : Lettre de chambre
    - **"c"** : Communiqué

    💡 Pour les paramètres avec beaucoup de valeurs, utilisez la taxonomie :
       obtenir_taxonomie_judilibre(taxonomy_id="chamber", context_value="cc") pour les chambres
       obtenir_taxonomie_judilibre(taxonomy_id="theme") pour les thèmes/matières
       obtenir_taxonomie_judilibre(taxonomy_id="formation") pour les formations
       obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca") pour toutes les cours d'appel
       obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="tj") pour tous les tribunaux

    📊 TRI DES RÉSULTATS (paramètre tri) :
    Utilisez directement ces codes :
    - **"scorepub"** (défaut) : Pertinence + niveau de publication (recommandé)
    - **"score"** : Pertinence uniquement
    - **"date"** : Date de la décision

    📐 ORDRE DU TRI (paramètre ordre) :
    - **"desc"** (défaut) : Décroissant (du plus récent/pertinent au moins)
    - **"asc"** : Croissant (du plus ancien/moins pertinent au plus)

    Répondre factuellement en faisant un résumé des résultats trouvés et en indiquant les IDs des articles pertinents et en affichant le titre et le lien direct vers Légifrance.

    ⚠️ ÉTAPE SUIVANTE OBLIGATOIRE :
    Les résultats contiennent uniquement des APERÇUS. Pour obtenir le TEXTE COMPLET
    d'une décision pertinente, vous DEVEZ utiliser :
    → obtenir_decision_judilibre(decision_id)

    L'ID de chaque décision se trouve dans le champ 'id' des résultats.

    Args:
        query: Texte de recherche (optionnel - si vide, retourne résultats vides)
        juridiction: Code de juridiction (cc, ca, tj, ta, caa, ce, tc, crc)
        localisation: Code du siège de juridiction (ex: "tj06088" pour Nice, "ca_lyon" pour Lyon)
                     Utilisez obtenir_taxonomie_judilibre(taxonomy_id="location", context_value="ca" ou "tj")
        chambre: ⚠️ Code de chambre - UTILISEZ LES CLÉS: "pl", "mi", "civ1", "civ2", "civ3",
                 "comm", "soc", "cr", "creun", "ordo", "allciv", "other"
                 Exemple: "civ1" pour Première chambre civile, "soc" pour Chambre sociale
        type_decision: Type (arret, ordonnance, qpc, etc.)
        theme: Matière juridique (obtenir via taxonomie)
        solution: Type de solution (rejet, cassation, annulation, etc.)
        date_debut: Date de début au format ISO (ex: 2023-01-15 ou 2023-01-15T00:00:00Z)
        date_fin: Date de fin au format ISO
        tri: Mode de tri (scorepub, score, date)
        ordre: Ordre du tri (desc ou asc)
        nombre_resultats: Nombre de résultats par page (max 50, défaut 10)
        page: Numéro de page (commence à 0)

    Returns:
        Liste des décisions avec :
          * id: Identifiant unique (REQUIS pour obtenir_decision_judilibre)
          * number: Numéro de la décision
          * date: Date de la décision
          * jurisdiction: Juridiction
          * chamber: Chambre
          * solution: ⭐ TYPE DE SOLUTION (rejet, cassation, etc.) ⭐
          * score: Score de pertinence
          * publication: Niveau de publication

    Examples:
        # Recherche simple à la Cour de cassation
        rechercher_jurisprudence_judilibre(
            query="responsabilité médicale",
            juridiction="cc"
        )

        # Recherche dans la Chambre sociale (utiliser la CLÉ "soc")
        rechercher_jurisprudence_judilibre(
            query="licenciement abusif",
            juridiction="cc",
            chambre="soc",
            date_debut="2023-01-01",
            date_fin="2024-12-31"
        )

        # Recherche dans la Première chambre civile (utiliser la CLÉ "civ1")
        rechercher_jurisprudence_judilibre(
            query="responsabilité contractuelle",
            juridiction="cc",
            chambre="civ1",
            solution="cassation"
        )

        # Recherche au Tribunal judiciaire de Nice
        rechercher_jurisprudence_judilibre(
            query="bail commercial",
            juridiction="tj",
            localisation="tj06088",
            tri="date",
            ordre="desc"
        )

        # Recherche à la Cour d'appel de Lyon
        rechercher_jurisprudence_judilibre(
            query="responsabilité contractuelle",
            juridiction="ca",
            localisation="ca_lyon",
            date_debut="2023-01-01"
        )
    """
    logger.debug(
        f"APPEL: rechercher_jurisprudence_judilibre(query='{query}', juridiction='{juridiction}')"
    )

    try:
        if judilibreapi is None:
            logger.error("API JudiLibre non initialisée")
            return [{"erreur": "L'API JudiLibre n'est pas initialisée"}]

        # Conversion des paramètres en listes si fournis
        jurisdiction_list = [juridiction] if juridiction else None
        location_list = [localisation] if localisation else None
        chamber_list = [chambre] if chambre else None
        type_list = [type_decision] if type_decision else None
        theme_list = [theme] if theme else None
        solution_list = [solution] if solution else None

        logger.info(
            f"Recherche JudiLibre: '{query}' - Juridiction: {juridiction or 'toutes'} - Localisation: {localisation or 'toutes'}"
        )

        results = judilibreapi.search(
            query=query,
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

        logger.info(f"Résultats trouvés: {len(results)}")

        return results

    except Exception as e:
        logger.error(f"Erreur lors de la recherche JudiLibre: {e}")
        return [{"erreur": f"Erreur recherche: {str(e)}"}]


@mcp.tool
def obtenir_decision_judilibre(decision_id: str) -> Dict[str, Any]:
    """
    📄 RÉCUPÉRATION COMPLÈTE d'une décision de justice depuis JudiLibre.

    ⚠️ OUTIL OBLIGATOIRE après rechercher_jurisprudence_judilibre() ⚠️

    Récupère le contenu intégral et structuré d'une décision de justice identifiée
    par son ID unique.

    📋 CONTENU COMPLET RETOURNÉ :

    **MÉTADONNÉES** :
    - Identifiant de la juridiction
    - Identifiant de la chambre
    - Formation
    - Numéro de pourvoi
    - ECLI (European Case Law Identifier)
    - Code NAC
    - Niveau de publication
    - ⭐ Solution (REJET, CASSATION, etc.) ⭐
    - Date de la décision

    **TEXTE INTÉGRAL** :
    - Texte complet de la décision
    - Délimitations des zones :
      * Introduction
      * Exposé du litige
      * Moyens
      * Motivations
      * Dispositif
      * Moyens annexés

    **ÉLÉMENTS ANNEXES** :
    - Éléments de titrage
    - Sommaire
    - Documents associés (rapport, avis avocat général, communiqué, etc.)
    - Textes appliqués
    - Rapprochements de jurisprudence

    Args:
        decision_id: Identifiant unique de la décision obtenu depuis
                    rechercher_jurisprudence_judilibre() (champ 'id')

    Returns:
        Dict contenant la décision complète avec cette STRUCTURE DÉTAILLÉE:

        📋 IDENTIFICATION DE LA DÉCISION:
        - **id**: Identifiant unique (ex: "60794cff9ba5988459c47bf2")
        - **number** / **numbers**: Numéro(s) de pourvoi (ex: ["00-15.781"])
        - **jurisdiction**: Juridiction (cc, ca, tj, etc.)
        - **chamber**: Chambre (civ1, civ2, soc, cr, comm, etc.)
        - **type**: Type de décision (arret, ordonnance, qpc, etc.)
        - **decision_date**: Date de la décision (ex: "2003-01-21")

        📄 TEXTE INTÉGRAL STRUCTURÉ:
        - **text**: Texte complet de la décision (délimité par zones)
        - **zones**: Délimitation précise des parties (TRÈS UTILE):
          * **moyens**: Position des moyens invoqués [{'start': 106, 'end': 160}]
          * **motivations**: Position des motivations [{'start': 160, 'end': 1226}]
          * **dispositif**: Position du dispositif [{'start': 4294, 'end': 4792}]
          → Permet d'extraire facilement chaque partie du texte

        ⚖️ SOLUTION ET PUBLICATION:
        - **solution**: ⭐ TYPE DE DÉCISION (rejet, cassation, annulation, etc.) ⭐
        - **publication**: Niveau de publication ["b" = Bulletin, "r" = Rapport, etc.]
        - **particularInterest**: Décision d'intérêt particulier (true/false)

        🏛️ CONTEXTE JURIDIQUE:
        - **summary**: Résumé officiel de la décision (TRÈS IMPORTANT)
        - **themes**: Liste des thèmes juridiques abordés
          Exemple: ["chose jugée", "responsabilité contractuelle", "subrogation", ...]
        - **nac**: Code NAC (nomenclature)
        - **portalis**: Numéro Portalis

        📚 RÉFÉRENCES ET RAPPROCHEMENTS:
        - **visa**: Textes visés/appliqués
          Exemple: [{"title": "Code des assurances L121-12"}]
        - **rapprochements**: Jurisprudence citée ou similaire
          Exemple: [{"title": "Chambre commerciale, 1991-06-04..."}]

        📂 DOCUMENTS ASSOCIÉS:
        - **files**: Documents joints (rapport, avis, communiqué, etc.)
        - **titlesAndSummaries**: Autres titrages et sommaires

        🔗 DÉCISION CONTESTÉE ET HISTORIQUE:
        - **contested**: Décision attaquée
          * **id**, **date**, **title**, **number**
          Exemple: {"date": "2000-03-23", "title": "Cour d'appel de Limoges"}
        - **forward**: Décision postérieure (si applicable)
        - **timeline**: Historique de la procédure

        🔍 DONNÉES TECHNIQUES:
        - **source**: Source des données (ex: "dila")
        - **update_date**: Date de mise à jour
        - **partial**: Décision partielle (true/false)
        - **legacy**: Données historiques

        💡 COMMENT UTILISER CES MÉTADONNÉES:

        1. **Analyse rapide**:
           - Utiliser `summary` pour comprendre rapidement l'enjeu
           - Vérifier `solution` pour connaître le résultat
           - Consulter `themes` pour identifier les domaines juridiques

        2. **Extraction du texte par zones**:
           ```python
           # Extraire les motivations
           text = decision['text']
           motivations_zones = decision['zones']['motivations']
           for zone in motivations_zones:
               motivations_text = text[zone['start']:zone['end']]
           ```

        3. **Navigation juridique**:
           - Utiliser `visa` pour identifier les textes appliqués
           - Utiliser `rapprochements` pour jurisprudence similaire
           - Utiliser `contested` pour remonter la chaîne de décisions

        4. **Qualification de la décision**:
           - `publication = ["b"]` → Décision publiée au Bulletin (importante)
           - `particularInterest = true` → Décision remarquable
           - `chamber` + `jurisdiction` → Préciser l'autorité

        5. **Enrichissement de la réponse**:
           - Citer les thèmes juridiques (`themes`)
           - Mentionner la décision contestée (`contested`)
           - Indiquer les textes appliqués (`visa`)

    Répondre factuellement en fournissant:
    - Le numéro de la décision et la juridiction
    - La solution (REJET, CASSATION, etc.)
    - Le résumé officiel (summary)
    - Les principaux thèmes juridiques
    - Les zones pertinentes du texte (moyens, motivations, dispositif)

    ⚠️ EXPLOITER LES ZONES: Utiliser `zones` pour extraire précisément
    les parties pertinentes (motivations pour l'analyse, dispositif pour la solution).

    ⚠️ MENTIONNER LES RÉFÉRENCES: Si pertinent, citer les textes appliqués (visa)
    et les rapprochements de jurisprudence pour approfondir.

    WORKFLOW TYPIQUE :
        1. Rechercher : rechercher_jurisprudence_judilibre("responsabilité")
        2. Analyser les résultats et identifier les décisions pertinentes
        3. Extraire l'ID : decision_id = results['results'][0]['id']
        4. Récupérer le texte complet : obtenir_decision_judilibre(decision_id)
        5. Analyser le contenu détaillé pour la réponse juridique

    Examples:
        # Recherche puis récupération complète
        results = rechercher_jurisprudence_judilibre(
            query="responsabilité médicale",
            juridiction="cc"
        )

        # Identifier une décision pertinente
        for decision in results['results']:
            if decision['⭐ SOLUTION ⭐'] == 'CASSATION':
                decision_id = decision['id']

                # Récupérer le texte complet
                decision_complete = obtenir_decision_judilibre(decision_id)

                # Analyser le texte intégral
                texte = decision_complete.get('text')
                motivations = decision_complete.get('zones', {}).get('motivations')
    """
    logger.debug(f"APPEL: obtenir_decision_judilibre(decision_id='{decision_id}')")

    try:
        if not decision_id or not decision_id.strip():
            logger.error("ID décision vide")
            return {"erreur": "L'ID de la décision ne peut pas être vide"}

        if judilibreapi is None:
            logger.error("API JudiLibre non initialisée")
            return {"erreur": "L'API JudiLibre n'est pas initialisée"}

        logger.info(f"Récupération de la décision: {decision_id}")

        decision = judilibreapi.decision(
            decision_id=decision_id, resolve_references=True  # Obtenir les intitulés complets
        )

        # Mise en évidence de la solution dans le résultat
        if decision and "solution" in decision:
            decision["⭐ SOLUTION ⭐"] = decision["solution"].upper()

        logger.info(f"Décision récupérée avec succès: {decision_id}")
        return decision

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la décision '{decision_id}': {e}")
        return {"erreur": f"Erreur récupération décision: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
