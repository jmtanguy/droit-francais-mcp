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
import requests
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from api_legifrance_query_builder import LegifranceQueryBuilder

class LegifranceAPI:
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
        fond: Optional[str] = "ALL",
        field_type: str = "ALL",
        search_type: str = "TOUS_LES_MOTS_DANS_UN_CHAMP",
        code: Optional[str] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        page_number: int = 0,
        page_size: int = 10,
        sort: Optional[str] = None,
        operator: str = "ET",
        advanced_search: bool = False,
        clean: bool = True
        ) -> Any:
        """
        Effectue une recherche dans l'API Légifrance.

        Args:
            query (str, optional): Terme(s) de recherche textuelle.
                Si None et search_input est None, lève une ValueError.

            fond (str, optional): Fonds de recherche.
                Valeurs possibles (voir LegiFranceSearchInput.FONDS):
                - ALL : Tous les fonds [DÉFAUT]
                - JORF : Journal Officiel de la République Française
                - CNIL : Commission Nationale de l'Informatique et des Libertés
                - CETAT : Conseil d'État
                - JURI : Jurisprudence judiciaire
                - JUFI : Jurisprudence financière
                - CONSTIT : Conseil Constitutionnel
                - KALI : Conventions collectives
                - CODE_DATE : Codes consolidés (par date)
                - CODE_ETAT : Codes consolidés (par état juridique) 
                - LODA_DATE : Lois, Ordonnances, Décrets, Arrêtés (par date)
                - LODA_ETAT : Lois, Ordonnances, Décrets, Arrêtés (par état)
                - CIRC : Circulaires et instructions
                - ACCO : Accords d'entreprise
                Défaut: "ALL"

            field_type: (str, optional): Type de champ dans lequel rechercher.
                Valeurs possibles (voir LegiFranceSearchInput.TYPE_CHAMP):
                - ALL : Tous les champs [DÉFAUT]
                - TITLE : Titre du texte
                - ARTICLE : Contenu des articles
                - NOR : Numéro d'ordre réglementaire
                - NUM : Numéro du texte
                - MINISTERE : Ministère émetteur
                - ... (voir docstring de LegiFranceSearchInput.add_champ pour la liste complète)
                Défaut: "ALL"

            search_type: (str, optional): Type de recherche effectuée.
                Valeurs possibles (voir LegiFranceSearchInput.TYPE_RECHERCHE):
                - EXACTE : Expression exacte [DÉFAUT]
                - UN_DES_MOTS : Au moins un des mots
                - TOUS_LES_MOTS_DANS_UN_CHAMP : Tous les mots présents
                - AUCUN_DES_MOTS : Aucun des mots (exclusion)
                - AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION : Expression absente (exclusion)
                Défaut: "EXACTE"

            code (str, optional): Nom du code à rechercher (uniquement pour fonds CODE_DATE/CODE_ETAT).
                Exemples: "Code civil", "Code pénal", "Code du travail", etc.
                Défaut: None (tous les codes)

            filters (Dict[str, List[str]], optional): Filtres par valeurs textuelles.
                Format: {"facette": ["valeur1", "valeur2", ...]}
                Exemples:
                    - {"NATURE": ["LOI", "ORDONNANCE"]}
                    - {"JURIDICTION_NATURE": ["TRIBUNAL_ADMINISTRATIF"]}
                    - {"ETAT_JURIDIQUE": ["VIGUEUR"]}
                Voir docstring de LegiFranceSearchInput.add_filtre_valeurs pour toutes les facettes.
                Défaut: None (pas de filtres)


            date_start (str, optional): Date de début/référence pour le filtre (format "YYYY-MM-DD").
                Utilisé seul ou combiné avec date_end.
                Seulement pour les fonds JORF,LODA_DATE,LODA_ETAT,JURI,CETAT,JUFI,CONSTIT,KALI,CIRC,ACCO.
                Défaut: None

            date_end (str, optional): Date de fin pour créer un intervalle (format "YYYY-MM-DD").
                Nécessite date_start.
                Défaut: None (date unique)
            
            page_number (int, optional): Numéro de la page à récupérer.
                Appliqué même si search_input est fourni (écrase la pagination de search_input).
                Défaut: 1

            page_size (int, optional): Nombre de résultats par page.
                Maximum: 50 (la valeur sera automatiquement limitée).
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

            operator (str, optional): Opérateur entre les champs de recherche.
                Valeurs possibles:
                - ET : Tous les champs doivent correspondre (AND) [DÉFAUT]
                - OU : Au moins un champ doit correspondre (OR)
                Défaut: "ET"

            advanced_search (bool, optional): Active le mode recherche avancée.
                Défaut: False

        Returns:
            Liste des résultats


        Raises:
            Exception: Si la requête échoue ou si les paramètres sont invalides

        """
        endpoint = f"{self.api_url}/search"

        # Mode simple : construire la requête à partir des paramètres
        if query is None:
            raise ValueError("Le paramètre 'recherche' doit être fourni")

        queryBuilder = LegifranceQueryBuilder()

        # Définir le fonds (avec valeur par défaut)
        fond = fond or "ALL"
        if fond not in queryBuilder.FONDS.values():
            raise ValueError(
                f"Fond invalide. Utilisez une des valeurs: {list(queryBuilder.FONDS.values())}"
            )
        queryBuilder.set_fond(fond)

        # Valider et créer le critère de recherche
        if search_type not in queryBuilder.TYPE_RECHERCHE.values():
            raise ValueError(
                f"Type de recherche invalide. Utilisez une des valeurs: {list(queryBuilder.TYPE_RECHERCHE.values())}"
            )

        if field_type not in queryBuilder.TYPE_CHAMP.values():
            raise ValueError(
                f"Type de champ invalide. Utilisez une des valeurs: {list(queryBuilder.TYPE_CHAMP.values())}"
            )

        critere = queryBuilder.create_criteria(query, search_type)
        queryBuilder.add_field(field_type, [critere])

        # Ajouter le filtre pour le nom du code si applicable
        if (fond in ["CODE_ETAT", "CODE_DATE"]) and code:
            queryBuilder.add_filtre("TEXT_NOM_CODE", [code])

        # Ajouter les filtres par valeurs
        if filters:
            for facette, valeurs in filters.items():
                queryBuilder.add_filtre(facette, valeurs)

        # Ajouter les filtres par dates
        if date_start:
            queryBuilder.add_dates( date_start, date_end)


        # Configurer l'opérateur global
        if operator not in ["ET", "OU"]:
            raise ValueError("L'opérateur doit être 'ET' ou 'OU'")
        queryBuilder.set_operator(operator)

        # Configurer la recherche avancée
        if advanced_search:
            queryBuilder.set_advanced_search(True)

        # Appliquer la pagination (écrase celle de search_input si fourni)
        queryBuilder.set_pagination(page_number, page_size)

        # Appliquer le tri si fourni (écrase celui de search_input si fourni)
        if sort:
            queryBuilder.set_sort(sort)

        # force la recherche sur des documents en vigueur
        if fond in ["JORF","CODE_ETAT","CODE_DATE","LODA_DATE","LODA_ETAT"]:
            queryBuilder.add_filtre("ARTICLE_LEGAL_STATUS", ["VIGUEUR"])

        # Construire le payload final
        payload = queryBuilder.build()

        try:
            response = requests.post(endpoint, headers=self._get_api_headers(), json=payload)
            response.raise_for_status()
            json = response.json()
            summary = self.clean(json) if clean else json
            return summary if summary else "Aucun résultat"

        except requests.exceptions.HTTPError as e:
            # Améliorer le message d'erreur avec les détails de la réponse
            error_msg = f"Erreur HTTP {e.response.status_code}: {e}"

            # Ajouter les en-têtes de réponse pour le débogage
            if e.response.status_code == 403:
                error_msg += "\n\n⚠️ Erreur 403 Forbidden - Causes possibles:"
                error_msg += "\n1. Votre compte n'est pas abonné à l'API Légifrance"
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

    def consult(self, id_: str, clean: bool = True) -> Any:
        """
        Récupère un article spécifique.
        Voir la documentation pour les types d'identifiants supportés.

        Args:
            article_id: Identifiant de l'article

        Returns:
            Données de l'article
        """
        # Gérer les identifiants avec date (ex: LEGITEXT000006069565_31-12-2006)
        if "_" in id_:
            id_ = id_.split('_')[0]

        # Sélectionner l'endpoint en fonction du type d'identifiant
        if id_.startswith("LEGIARTI") or id_.startswith("LEGISCTA"):
            # Articles de loi
            endpoint = f"{self.api_url}/consult/getArticle"
            params = {"id": id_}

        elif id_.startswith("LEGITEXT"):
            # Textes légaux consolidés
            endpoint = f"{self.api_url}/consult/legiPart"
            params = {"textId": id_,"date":date.today().isoformat()}  # Utiliser une date future pour obtenir la version la plus récente

        elif id_.startswith("JURITEXT"):
            # Jurisprudence
            endpoint = f"{self.api_url}/consult/juri"
            params = {"textId": id_}

        elif id_.startswith("CNILTEXT"):
            # CNIL
            endpoint = f"{self.api_url}/consult/cnil"
            params = {"textId": id_}

        elif id_.startswith("KALITEXT"):
            # Conventions collectives
            endpoint = f"{self.api_url}/consult/kaliText"
            params = {"id": id_}

        elif id_.startswith("KALIARTI"):
            # Conventions collectives
            endpoint = f"{self.api_url}/consult/kaliArticle"
            params = {"id": id_}

        elif id_.startswith("ACCOTEXT"):
            # Accords d'entreprise
            endpoint = f"{self.api_url}/consult/acco"
            params = {"id": id_}

        else:
            # Journal officiel par defaut
            endpoint = f"{self.api_url}/consult/jorf"
            params = {"textCid": id_}

        try:
            response = requests.post(endpoint, headers=self._get_api_headers(), json=params)
            response.raise_for_status()
            api_response = self.clean( response.json() ) if clean else response.json()
            return api_response

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la récupération de l'article")



    def clean(self, x, depth=0, max_depth=8):
        """
        Nettoie un dictionnaire ou une liste en ne conservant que les clés autorisées à tous les niveaux
        de la hiérarchie et en supprimant les valeurs None ou vides.
        La descente dans la hiérarchie est limitée à max_depth niveaux (par défaut 4).

        Clés conservées: id, title, text, values, datePublication, startDate, origine, nature,
        natureJuridiction, solution, numeroAffaire, president, avocats, titre, texte, juridiction

        Args:
            x (dict or list): Dictionnaire ou liste à nettoyer.
            depth (int): Niveau actuel de profondeur (usage interne).
            max_depth (int): Profondeur maximale de descente (par défaut 4).

        Returns:
            dict or list: Structure nettoyée avec uniquement les clés autorisées à tous les niveaux.
        """
        # Liste des clés à conserver à tous les niveaux de la hiérarchie
        allowed_keys = {
            "id", "title", "text", "values", "datePublication", "startDate",
            "origine", "nature", "natureJuridiction", "solution", "numeroAffaire",
            "president", "avocats", "titre", "texte", "juridiction", "content"
        }

        # Arrêter la descente si on a atteint la profondeur maximale
        if depth >= max_depth:
            return None

        if isinstance(x, dict):
            cleaned = {}
            for k, v in x.items():
                if v:  # Ignorer les valeurs vides
                    if k in allowed_keys and not isinstance(v, (dict, list)):
                        # Clé autorisée : conserver la valeur
                        cleaned[k] = v
                    elif isinstance(v, (dict, list)):
                        # Valeur est dict/list : descendre dans la hiérarchie
                        cleaned_value = self.clean(v, depth + 1, max_depth)
                        if cleaned_value:  # Ne garder que si le résultat n'est pas vide
                            cleaned[k] = cleaned_value
            return cleaned if cleaned else None

        if isinstance(x, list):
            # Si la liste contient uniquement des chaînes de caractères, la garder intacte
            if x and all(isinstance(item, str) for item in x):
                return x
            # Sinon, traiter récursivement
            l = [cleaned_v for v in x if v and (cleaned_v := self.clean(v, depth + 1, max_depth)) is not None]
            return l if l else None

        return x
    

