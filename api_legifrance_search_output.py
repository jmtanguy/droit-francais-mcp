#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur de données pour l'API Légifrance
Module pour extraire et traiter les données JSON retournées par l'API de recherche

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class LegiFranceSearchOutput:
    """Classe pour extraire les données de l'API juridique"""

    def __init__(self):
        self.facet_title_map = {
            "TEXT_LEGAL_STATUS": "Statut légal des textes",
            "ARTICLE_LEGAL_STATUS": "Statut légal des articles",
            "TEXT_NOM_CODE": "Codes disponibles",
        }

    def extract_full_summary(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait un résumé structuré de toute la réponse

        Args:
            api_response: Réponse complète de l'API

        Returns:
            Résumé structuré avec titles et articles fusionnés par index
        """
        titles = self._extract_titles_info(api_response)
        articles = self._extract_articles_info(api_response)

        # Fusionner les titles et articles par index
        items = []
        results = api_response.get("results", [])
        for result in results:

            # Main text
            if (result.get("titles") is not None) and (len(result.get("titles")) > 0):
                id = result.get("titles")[0].get("id")
                if (id is not None) and (result.get("text") is not None):
                    item = {}
                    item["article_id"] = result.get("titles")[0].get("id")
                    item["title"] = result.get("titles")[0].get("title")
                    item["nature"] = result.get("nature")
                    item["text"] = result.get("text")
                    items.append(item)

            # adding sections
            for section in result.get("sections", []):
                if section.get("extracts") and isinstance(section["extracts"], list):
                    for extract in section["extracts"]:
                        id = extract.get("id")
                        if id is not None:
                            item = {}
                            item["article_id"] = extract.get("id")
                            item["title"] = (
                                f"Article {extract.get('num', 'N/A')} - {extract.get('title', None)}"
                            )
                            item["section_title"] = section.get("title", None)
                            item["content"] = self._clean_article_content(extract.get("values", []))
                            item["date_version"] = extract.get("dateVersion", None)
                            item["date_debut"] = extract.get("dateDebut", None)
                            item["date_fin"] = extract.get("dateFin", None)
                            item = {k: v for k, v in item.items() if v is not None}
                            items.append(item)

        return items

    #        return {
    #            'execution_time': api_response.get('executionTime', 0),
    #            'total_articles': len(items),
    #            'pagination_type': api_response.get('typePagination'),
    #            'articles': items,
    #            'facets': self._extract_facets_info(api_response)
    #        }

    def _extract_titles_info(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait les informations de base des titres (id, title, description)

        Args:
            api_response: Réponse complète de l'API

        Returns:
            Liste des titres avec leurs informations
        """
        if not api_response.get("results") or not isinstance(api_response["results"], list):
            return []

        extracted_titles = []

        for result in api_response["results"]:
            if result.get("titles") and isinstance(result["titles"], list):
                for title in result["titles"]:
                    extracted_titles.append(
                        {
                            "id": title.get("id"),
                            "title": title.get("title", "Titre non disponible"),
                            "description": self._generate_description(title),
                            "legal_status": title.get("legalStatus", "Non spécifié"),
                            "nature": title.get("nature", "Non spécifiée"),
                            "cid": title.get("cid"),
                            "start_date": title.get("startDate"),
                            "end_date": title.get("endDate"),
                        }
                    )

        return extracted_titles

    def _extract_articles_info(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait les informations des articles avec leurs contenus

        Args:
            api_response: Réponse complète de l'API

        Returns:
            Liste des articles avec leurs informations
        """
        if not api_response.get("results") or not isinstance(api_response["results"], list):
            return []

        extracted_articles = []

        for result in api_response["results"]:
            if result.get("sections") and isinstance(result["sections"], list):
                for section in result["sections"]:
                    if section.get("extracts") and isinstance(section["extracts"], list):
                        for extract in section["extracts"]:
                            extracted_articles.append(
                                {
                                    "id": extract.get("id"),
                                    "title": f"Article {extract.get('num', 'N/A')} - {extract.get('title', 'Titre non disponible')}",
                                    "description": self._generate_article_description(
                                        extract, section
                                    ),
                                    "section_title": section.get("title", "Section non nommée"),
                                    "article_number": extract.get("num"),
                                    "legal_status": extract.get("legalStatus", "Non spécifié"),
                                    "content": self._clean_article_content(
                                        extract.get("values", [])
                                    ),
                                    "date_version": extract.get("dateVersion"),
                                    "date_debut": extract.get("dateDebut"),
                                    "date_fin": extract.get("dateFin"),
                                    "type": extract.get("type"),
                                }
                            )

        return extracted_articles

    def _extract_facets_info(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait les informations des facettes

        Args:
            api_response: Réponse complète de l'API

        Returns:
            Informations des facettes
        """
        if not api_response.get("facets") or not isinstance(api_response["facets"], list):
            return []

        facets_info = []
        for facet in api_response["facets"]:
            facets_info.append(
                {
                    "id": facet.get("facetElem", "unknown"),
                    "title": self._format_facet_title(facet.get("facetElem")),
                    "description": f"Facette sur le champ: {facet.get('field', 'non spécifié')}",
                    "field": facet.get("field"),
                    "values": facet.get("values", {}),
                    "total_elements": facet.get("totalElement", 0),
                    "childs": facet.get("childs", {}),
                }
            )

        return facets_info

    def _generate_description(self, title: Dict[str, Any]) -> str:
        """
        Génère une description basée sur les informations disponibles

        Args:
            title: Objet titre

        Returns:
            Description générée
        """
        parts = []

        if title.get("nature"):
            parts.append(f"Nature: {title['nature']}")

        if title.get("legalStatus"):
            parts.append(f"Statut: {title['legalStatus']}")

        if title.get("startDate"):
            try:
                start_date = datetime.fromisoformat(title["startDate"].replace("Z", "+00:00"))
                parts.append(f"En vigueur depuis: {start_date.strftime('%d/%m/%Y')}")
            except (ValueError, AttributeError):
                pass

        if title.get("endDate") and title["endDate"] != "2999-01-01T00:00:00.000+0000":
            try:
                end_date = datetime.fromisoformat(title["endDate"].replace("Z", "+00:00"))
                parts.append(f"Fin de vigueur: {end_date.strftime('%d/%m/%Y')}")
            except (ValueError, AttributeError):
                pass

        return " | ".join(parts) if parts else "Aucune description disponible"

    def _generate_article_description(
        self, extract: Dict[str, Any], section: Dict[str, Any]
    ) -> str:
        """
        Génère une description pour un article

        Args:
            extract: Extrait d'article
            section: Section parent

        Returns:
            Description générée
        """
        parts = []

        if section.get("title"):
            parts.append(f"Section: {section['title']}")

        if extract.get("legalStatus"):
            parts.append(f"Statut: {extract['legalStatus']}")

        if extract.get("dateVersion"):
            try:
                date = datetime.fromisoformat(extract["dateVersion"].replace("Z", "+00:00"))
                parts.append(f"Version du: {date.strftime('%d/%m/%Y')}")
            except (ValueError, AttributeError):
                pass

        if extract.get("values") and isinstance(extract["values"], list) and extract["values"]:
            clean_content = self._clean_article_content(extract["values"])
            preview = clean_content[:150]
            parts.append(f"Aperçu: {preview}{'...' if len(clean_content) > 150 else ''}")

        return " | ".join(parts)

    def _clean_article_content(self, values: List[str]) -> str:
        """
        Nettoie le contenu des articles (supprime les balises HTML et formate)

        Args:
            values: Tableau des valeurs de l'article

        Returns:
            Contenu nettoyé
        """
        if not values or not isinstance(values, list):
            return "Contenu non disponible"

        content = " ".join(values)
        # Supprime les balises HTML
        content = re.sub(r"<mark>", "", content)
        content = re.sub(r"</mark>", "", content)
        content = re.sub(r"\[\.\.\.]*", "...", content)

        return content.strip()

    def _format_facet_title(self, facet_elem: Optional[str]) -> str:
        """
        Formate le titre d'une facette

        Args:
            facet_elem: Élément de facette

        Returns:
            Titre formaté
        """
        key = facet_elem if facet_elem is not None else "Facette inconnue"
        return self.facet_title_map.get(key, key)
