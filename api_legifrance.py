#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client pour l'API Légifrance via PISTE.
Documentation de l'API Légifrance : https://piste.gouv.fr/api-dila-legifrance/

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from api_legifrance_search_input import LegiFranceSearchInput
from api_legifrance_search_output import LegiFranceSearchOutput


class LegiFranceAPI:
    """
    Client pour l'API Légifrance
    """

    def __init__(self, sandbox: bool = True):
        """
        Initialise le client

        Args:
            sandbox: Utiliser l'environnement sandbox (True) ou production (False) de l 'API PISTE
        """
        load_dotenv(verbose=False)  # Charger les variables d'environnement depuis le fichier .env
        if sandbox:
            self.client_id = os.getenv("PISTE_SANDBOX_CLIENT_ID")
            self.client_secret = os.getenv("PISTE_SANDBOX_CLIENT_SECRET")
            self.token_url = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
            self.base_url = "https://sandbox-api.piste.gouv.fr"
            if not self.client_id or not self.client_secret:
                raise ValueError(
                    "Les identifiants PISTE Sandbox sont manquants. "
                    "Veuillez définir PISTE_SANDBOX_CLIENT_ID et PISTE_SANDBOX_CLIENT_SECRET "
                    "dans votre fichier .env. "
                    "Consultez .env.example pour un exemple de configuration."
                )
        else:
            self.client_id = os.getenv("PISTE_CLIENT_ID")
            self.client_secret = os.getenv("PISTE_CLIENT_SECRET")
            self.token_url = "https://oauth.piste.gouv.fr/api/oauth/token"
            self.base_url = "https://api.piste.gouv.fr"
            if not self.client_id or not self.client_secret:
                raise ValueError(
                    "Les identifiants PISTE Production sont manquants. "
                    "Veuillez définir PISTE_CLIENT_ID et PISTE_CLIENT_SECRET "
                    "dans votre fichier .env. "
                    "Consultez .env.example pour un exemple de configuration."
                )

        self.api_url = f"{self.base_url}/dila/legifrance/lf-engine-app"

        # Stockage du token
        self.access_token = None
        self.token_expires_at = None

    def get_access_token(self) -> str:
        """
        Obtient un token d'accès via OAuth 2.0 Client Credentials

        Returns:
            Token d'accès
        """
        # Vérifier si le token existant est encore valide
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Headers pour la requête OAuth
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Données de la requête OAuth 2.0 Client Credentials
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid",
        }

        try:
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]

            # Calculer l'expiration du token (avec marge de sécurité)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return self.access_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'obtention du token: {e}")

    def _get_api_headers(self) -> Dict[str, str]:
        """
        Génère les en-têtes pour les appels API
        """
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        return headers

    def test_connection(self) -> Dict[str, Any]:
        """
        Teste la connexion à l'API en vérifiant que le token est valide.
        Cette méthode peut être utilisée pour diagnostiquer les problèmes d'authentification.

        Returns:
            Dict contenant les informations de connexion et le statut

        Raises:
            Exception: Si la connexion échoue
        """
        try:
            token = self.get_access_token()
            token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"

            result = {
                "status": "success",
                "base_url": self.base_url,
                "api_url": self.api_url,
                "token_obtained": True,
                "token_preview": token_preview,
                "token_expires_at": (
                    self.token_expires_at.isoformat() if self.token_expires_at else None
                ),
                "message": "Token obtenu avec succès. Vérifiez votre abonnement à l'API Légifrance sur https://piste.gouv.fr/ si vous obtenez des erreurs 403.",
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Échec de l'obtention du token. Vérifiez vos identifiants dans le fichier .env",
            }

    def ping(self) -> str:
        """
        Teste la connexion à l'endpoint de recherche avec un simple ping.
        Retourne "pong" si la connexion fonctionne.

        Returns:
            "pong" si la connexion réussit

        Raises:
            Exception: Si le ping échoue
        """
        endpoint = f"{self.api_url}/search/ping"

        try:
            response = requests.get(endpoint, headers=self._get_api_headers())
            response.raise_for_status()
            return response.text.strip()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erreur HTTP {e.response.status_code} lors du ping"
            if e.response.status_code == 403:
                error_msg += "\n⚠️ Erreur 403: Votre compte n'est probablement pas abonné à l'API Légifrance sur https://piste.gouv.fr/"
            try:
                error_details = e.response.text[:200]
                error_msg += f"\nRéponse: {error_details}"
            except:
                pass
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors du ping: {e}")

    def search(
        self,
        query: Optional[str] = None,
        fond: Optional[str] = None,
        type_champ: str = "ALL",
        type_recherche: str = "UN_DES_MOTS",
        code_name: Optional[str] = None,
        filtres_valeurs: Optional[Dict[str, List[str]]] = None,
        filtres_dates: Optional[Dict[str, Dict[str, str]]] = None,
        page_number: int = 1,
        page_size: int = 10,
        sort: Optional[str] = None,
        operateur: str = "ET",
        advanced_search: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Effectue une recherche dans l'API Légifrance avec support complet de toutes les fonctionnalités.

        Args:
            query (str, optional): Terme(s) de recherche textuelle.
                Ignoré si search_input est fourni.
                Si None et search_input est None, lève une ValueError.

            fond (str, optional): Fonds de recherche.
                Ignoré si search_input est fourni.
                Valeurs possibles (voir LegiFranceSearchInput.FONDS):
                - JORF : Journal Officiel de la République Française
                - CNIL : Commission Nationale de l'Informatique et des Libertés
                - CETAT : Conseil d'État
                - JURI : Jurisprudence judiciaire
                - JUFI : Jurisprudence financière
                - CONSTIT : Conseil Constitutionnel
                - KALI : Conventions collectives
                - CODE_DATE : Codes consolidés (par date)
                - CODE_ETAT : Codes consolidés (par état juridique) [DÉFAUT]
                - LODA_DATE : Lois, Ordonnances, Décrets, Arrêtés (par date)
                - LODA_ETAT : Lois, Ordonnances, Décrets, Arrêtés (par état)
                - ALL : Tous les fonds
                - CIRC : Circulaires et instructions
                - ACCO : Accords d'entreprise
                Défaut: "CODE_ETAT"

            type_champ (str, optional): Type de champ dans lequel rechercher.
                Ignoré si search_input est fourni.
                Valeurs possibles (voir LegiFranceSearchInput.TYPE_CHAMP):
                - ALL : Tous les champs [DÉFAUT]
                - TITLE : Titre du texte
                - ARTICLE : Contenu des articles
                - NOR : Numéro d'ordre réglementaire
                - NUM : Numéro du texte
                - MINISTERE : Ministère émetteur
                - ... (voir docstring de LegiFranceSearchInput.add_champ pour la liste complète)
                Défaut: "ALL"

            type_recherche (str, optional): Type de recherche effectuée.
                Ignoré si search_input est fourni.
                Valeurs possibles (voir LegiFranceSearchInput.TYPE_RECHERCHE):
                - UN_DES_MOTS : Au moins un des mots [DÉFAUT]
                - EXACTE : Expression exacte
                - TOUS_LES_MOTS_DANS_UN_CHAMP : Tous les mots présents
                - AUCUN_DES_MOTS : Aucun des mots (exclusion)
                - AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION : Expression absente (exclusion)
                Défaut: "UN_DES_MOTS"

            code_name (str, optional): Nom du code à rechercher (uniquement pour fonds CODE_DATE/CODE_ETAT).
                Ignoré si search_input est fourni.
                Exemples: "Code civil", "Code pénal", "Code du travail", etc.
                Défaut: None (tous les codes)

            filtres_valeurs (Dict[str, List[str]], optional): Filtres par valeurs textuelles.
                Ignoré si search_input est fourni.
                Format: {"facette": ["valeur1", "valeur2", ...]}
                Exemples:
                    - {"NATURE": ["LOI", "ORDONNANCE"]}
                    - {"JURIDICTION_NATURE": ["TRIBUNAL_ADMINISTRATIF"]}
                    - {"ETAT_JURIDIQUE": ["VIGUEUR"]}
                Voir docstring de LegiFranceSearchInput.add_filtre_valeurs pour toutes les facettes.
                Défaut: None (pas de filtres)

            filtres_dates (Dict[str, Dict[str, str]], optional): Filtres par périodes de dates.
                Ignoré si search_input est fourni.
                Format: {"facette": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}
                Exemples:
                    - {"DATE_SIGNATURE": {"start": "2020-01-01", "end": "2023-12-31"}}
                    - {"DATE_PUBLICATION": {"start": "2022-01-01", "end": "2022-12-31"}}
                Voir docstring de LegiFranceSearchInput.add_filtre_dates pour toutes les facettes.
                Défaut: None (pas de filtres de dates)

            page_number (int, optional): Numéro de la page à récupérer.
                Appliqué même si search_input est fourni (écrase la pagination de search_input).
                Défaut: 1

            page_size (int, optional): Nombre de résultats par page.
                Maximum: 100 (la valeur sera automatiquement limitée).
                Appliqué même si search_input est fourni (écrase la pagination de search_input).
                Défaut: 10

            sort (str, optional): Ordre de tri des résultats.
                Appliqué même si search_input est fourni (écrase le tri de search_input).
                Valeurs courantes:
                - PERTINENCE : Tri par pertinence
                - SIGNATURE_DATE_DESC : Date de signature décroissante
                - SIGNATURE_DATE_ASC : Date de signature croissante
                - DATE_PUBLI_DESC : Date de publication décroissante
                - DATE_PUBLI_ASC : Date de publication croissante
                - ID_DESC : Identifiant décroissant
                - ID_ASC : Identifiant croissant
                Défaut: None (tri par défaut de l'API - généralement PERTINENCE)

            operateur (str, optional): Opérateur entre les champs de recherche.
                Ignoré si search_input est fourni.
                Valeurs possibles:
                - ET : Tous les champs doivent correspondre (AND) [DÉFAUT]
                - OU : Au moins un champ doit correspondre (OR)
                Défaut: "ET"

            advanced_search (bool, optional): Active le mode recherche avancée.
                Ignoré si search_input est fourni.
                Défaut: False

        Returns:
            Liste des résultats: [
                        {
                            "id": str,
                            "title": str,
                            "nature": str,
                            "legalStatus": str,
                            "dateDebut": str,
                            "dateFin": str,
                            "extracts": [...],
                            ...
                        },
                        ...
                    ]


        Raises:
            ValueError: Si ni query ni search_input n'est fourni
            ValueError: Si le fond, type_champ, type_recherche ou operateur est invalide
            Exception: Si l'appel à l'API échoue

        Examples:
            >>> api = LegiFranceAPI()

            >>> # Exemple 1 : Recherche simple
            >>> results = api.search(
            ...     query="mariage",
            ...     fond="CODE_ETAT",
            ...     code_name="Code civil",
            ...     page_size=20
            ... )

            >>> # Exemple 2 : Recherche avec filtres
            >>> results = api.search(
            ...     query="divorce",
            ...     fond="JORF",
            ...     type_recherche="EXACTE",
            ...     filtres_valeurs={"NATURE": ["LOI", "ORDONNANCE"]},
            ...     filtres_dates={"DATE_SIGNATURE": {"start": "2020-01-01", "end": "2023-12-31"}},
            ...     sort="SIGNATURE_DATE_DESC"
            ... )

            >>> # Exemple 3 : Recherche avancée avec critères complexes
            >>> builder = LegiFranceSearchInput()
            >>> builder.set_fond("LODA_DATE")
            >>>
            >>> # Critère principal dans le titre
            >>> critere_titre = builder.create_critere("fonction publique", "TOUS_LES_MOTS_DANS_UN_CHAMP", proximite=2)
            >>> builder.add_champ("TITLE", [critere_titre])
            >>>
            >>> # Critère dans les articles
            >>> critere_article = builder.create_critere("rémunération", "UN_DES_MOTS")
            >>> builder.add_champ("ARTICLE", [critere_article], operateur="OU")
            >>>
            >>> # Filtres
            >>> builder.add_filtre_valeurs("NATURE", ["LOI", "DECRET"])
            >>> builder.add_filtre_dates("DATE_SIGNATURE", "2020-01-01", "2023-12-31")
            >>> builder.set_operateur_global("ET")
            >>> builder.set_advanced_search(True)
            >>>
            >>> results = api.search(search_input=builder, page_size=50)

            >>> # Exemple 4 : Recherche dans les conventions collectives
            >>> results = api.search(
            ...     query="télétravail",
            ...     fond="KALI",
            ...     filtres_valeurs={"IDCC": ["1880", "2120"]},
            ...     page_size=30
            ... )

            >>> # Exemple 5 : Recherche jurisprudentielle
            >>> results = api.search(
            ...     query="responsabilité médicale",
            ...     fond="JURI",
            ...     type_champ="RESUMES",
            ...     filtres_valeurs={"JURIDICTION_NATURE": ["COUR_CASSATION"]},
            ...     sort="DATE_DECISION_DESC"
            ... )
        """
        endpoint = f"{self.api_url}/search"

        # Mode simple : construire la requête à partir des paramètres
        if query is None:
            raise ValueError("Le paramètre 'query' doit être fourni")

        queryBuilder = LegiFranceSearchInput()

        # Définir le fonds (avec valeur par défaut)
        fond = fond or "CODE_ETAT"
        if fond not in queryBuilder.FONDS.values():
            raise ValueError(
                f"Fond invalide. Utilisez une des valeurs: {list(queryBuilder.FONDS.values())}"
            )
        queryBuilder.set_fond(fond)

        # Valider et créer le critère de recherche
        if type_recherche not in queryBuilder.TYPE_RECHERCHE.values():
            raise ValueError(
                f"Type de recherche invalide. Utilisez une des valeurs: {list(queryBuilder.TYPE_RECHERCHE.values())}"
            )

        if type_champ not in queryBuilder.TYPE_CHAMP.values():
            raise ValueError(
                f"Type de champ invalide. Utilisez une des valeurs: {list(queryBuilder.TYPE_CHAMP.values())}"
            )

        critere = queryBuilder.create_critere(query, type_recherche)
        queryBuilder.add_champ(type_champ, [critere])

        # Ajouter le filtre pour le nom du code si applicable
        if (fond in ["CODE_ETAT", "CODE_DATE"]) and code_name:
            queryBuilder.add_filtre_valeurs("TEXT_NOM_CODE", [code_name])

        # Ajouter les filtres par valeurs
        if filtres_valeurs:
            for facette, valeurs in filtres_valeurs.items():
                queryBuilder.add_filtre_valeurs(facette, valeurs)

        # Ajouter les filtres par dates
        if filtres_dates:
            for facette, dates in filtres_dates.items():
                if "start" in dates and "end" in dates:
                    queryBuilder.add_filtre_dates(facette, dates["start"], dates["end"])
                elif "date" in dates:
                    queryBuilder.add_filtre_date_unique(facette, dates["date"])

        # Configurer l'opérateur global
        if operateur not in ["ET", "OU"]:
            raise ValueError("L'opérateur doit être 'ET' ou 'OU'")
        queryBuilder.set_operateur_global(operateur)

        # Configurer la recherche avancée
        if advanced_search:
            queryBuilder.set_advanced_search(True)

        # Appliquer la pagination (écrase celle de search_input si fourni)
        queryBuilder.set_pagination(page_number, page_size)

        # Appliquer le tri si fourni (écrase celui de search_input si fourni)
        if sort:
            queryBuilder.set_sort(sort)

        # Construire le payload final
        payload = queryBuilder.build()

        try:
            response = requests.post(endpoint, headers=self._get_api_headers(), json=payload)
            response.raise_for_status()

            searchExtractor = LegiFranceSearchOutput()
            json = response.json()
            summary = searchExtractor.extract_full_summary(json)
            return summary

        except requests.exceptions.HTTPError as e:
            # Améliorer le message d'erreur avec les détails de la réponse
            error_msg = f"Erreur HTTP {e.response.status_code}: {e}"

            # Ajouter les en-têtes de réponse pour le débogage
            if e.response.status_code == 403:
                error_msg += "\n\n⚠️ Erreur 403 Forbidden - Causes possibles:"
                error_msg += "\n1. Votre compte sandbox n'est pas abonné à l'API Légifrance"
                error_msg += "\n2. Les permissions nécessaires ne sont pas activées"
                error_msg += "\n3. Vérifiez votre abonnement sur https://piste.gouv.fr/"

            try:
                error_details = e.response.json()
                if isinstance(error_details, dict):
                    error_msg += f"\n\nDétails de la réponse API: {error_details}"
                    # Si l'API retourne un message d'erreur spécifique
                    if "message" in error_details:
                        error_msg += f"\nMessage: {error_details['message']}"
                    if "error" in error_details:
                        error_msg += f"\nErreur: {error_details['error']}"
            except:
                error_msg += f"\n\nRéponse brute: {e.response.text[:500]}"

            # Ajouter les en-têtes de réponse pour le débogage
            error_msg += f"\n\nEn-têtes de réponse: {dict(e.response.headers)}"

            raise Exception(f"Erreur lors de la recherche: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la recherche: {e}")

    def article(self, article_id: str) -> Dict[str, Any]:
        """
        Récupère un article spécifique.
        Voir la documentation pour les types d'identifiants supportés.

        Args:
            article_id: Identifiant de l'article

        Returns:
            Données de l'article
        """
        # Sélectionner l'endpoint en fonction du type d'identifiant

        if article_id.startswith("LEGIARTI"):
            # Articles de loi
            endpoint = f"{self.api_url}/consult/getArticle"
            params = {"id": article_id}

        elif article_id.startswith("LEGITEXT"):
            # Textes légaux consolidés
            endpoint = f"{self.api_url}/consult/legiPart"
            params = {"textId": article_id}

        elif article_id.startswith("JURITEXT"):
            # Jurisprudence
            endpoint = f"{self.api_url}/consult/juri"
            params = {"textId": article_id}

        elif article_id.startswith("CNILTEXT"):
            endpoint = f"{self.api_url}/consult/cnil"
            params = {"textId": article_id}

        elif article_id.startswith("KALITEXT"):
            # Conventions collectives
            endpoint = f"{self.api_url}/consult/kaliText"
            params = {"id": article_id}

        elif article_id.startswith("KALIARTI"):
            # Conventions collectives
            endpoint = f"{self.api_url}/consult/kaliArticle"
            params = {"id": article_id}

        elif article_id.startswith("ACCOTEXT"):
            endpoint = f"{self.api_url}/consult/acco"
            params = {"id": article_id}

        else:
            # Journal officiel par defaut
            endpoint = f"{self.api_url}/consult/jorf"
            params = {"textCid": article_id}

        try:
            response = requests.post(endpoint, headers=self._get_api_headers(), json=params)
            response.raise_for_status()
            api_response = response.json()
            return api_response

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la récupération de l'article: {e}")


# La fonction main() a été déplacée vers test_api.py pour éviter les conflits avec FastMCP (pas de print() dans un module importé)
# Utilisez test_api.py pour tester cette classe
