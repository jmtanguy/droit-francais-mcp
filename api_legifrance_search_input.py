#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de requêtes pour l'API Légifrance
Basé sur SearchRequestDTO de la documentation Swagger

Copyright (c) 2025 Jean-Michel Tanguy
Licensed under the MIT License (see LICENSE file)

Remarques :
   Certaines parties de ce code ont été développées avec l’aide de Vibe Coding
   et d’outils d’intelligence artificielle.
"""

import json
from typing import Any, Dict, List, Optional


class LegiFranceSearchInput:
    """Générateur de requêtes pour l'API Légifrance"""

    # Constantes pour les types de recherche
    TYPE_RECHERCHE = {
        "UN_DES_MOTS": "UN_DES_MOTS",
        "EXACTE": "EXACTE",
        "TOUS_LES_MOTS_DANS_UN_CHAMP": "TOUS_LES_MOTS_DANS_UN_CHAMP",
        "AUCUN_DES_MOTS": "AUCUN_DES_MOTS",
        "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION": "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION",
    }

    # Constantes pour les types de champs avec descriptions et usage
    TYPE_CHAMP = {
        "ALL": "ALL",  # Recherche dans tous les champs
        "TITLE": "TITLE",  # Titre du texte
        "TABLE": "TABLE",  # Table des matières
        "NOR": "NOR",  # Numéro d'ordre réglementaire
        "NUM": "NUM",  # Numéro du texte
        "ADVANCED_TEXTE_ID": "ADVANCED_TEXTE_ID",  # Identifiant technique du texte
        "NUM_DELIB": "NUM_DELIB",  # Numéro de délibération
        "NUM_DEC": "NUM_DEC",  # Numéro de décision
        "NUM_ARTICLE": "NUM_ARTICLE",  # Numéro d'article
        "ARTICLE": "ARTICLE",  # Contenu des articles
        "MINISTERE": "MINISTERE",  # Ministère émetteur
        "VISA": "VISA",  # Visas du texte
        "NOTICE": "NOTICE",  # Notice du texte
        "VISA_NOTICE": "VISA_NOTICE",  # Visas et notice combinés
        "TRAVAUX_PREP": "TRAVAUX_PREP",  # Travaux préparatoires
        "SIGNATURE": "SIGNATURE",  # Signataires
        "NOTA": "NOTA",  # Nota du texte
        "NUM_AFFAIRE": "NUM_AFFAIRE",  # Numéro d'affaire (jurisprudence)
        "ABSTRATS": "ABSTRATS",  # Résumés/abstracts
        "RESUMES": "RESUMES",  # Résumés
        "TEXTE": "TEXTE",  # Contenu textuel complet
        "ECLI": "ECLI",  # Identifiant ECLI (jurisprudence européenne)
        "NUM_LOI_DEF": "NUM_LOI_DEF",  # Numéro de loi déférée
        "TYPE_DECISION": "TYPE_DECISION",  # Type de décision
        "NUMERO_INTERNE": "NUMERO_INTERNE",  # Numéro interne
        "REF_PUBLI": "REF_PUBLI",  # Référence de publication
        "RESUME_CIRC": "RESUME_CIRC",  # Résumé de circulaire
        "TEXTE_REF": "TEXTE_REF",  # Texte de référence
        "TITRE_LOI_DEF": "TITRE_LOI_DEF",  # Titre de loi déférée
        "RAISON_SOCIALE": "RAISON_SOCIALE",  # Raison sociale (accords d'entreprise)
        "MOTS_CLES": "MOTS_CLES",  # Mots-clés
        "IDCC": "IDCC",  # Identifiant de convention collective
    }

    # Descriptions détaillées des types de champs
    TYPE_CHAMP_DESCRIPTIONS = {
        "ALL": {
            "nom": "Tous les champs",
            "description": "Recherche dans l'ensemble des champs disponibles du document",
            "usage": "Recherche générale quand on ne sait pas dans quel champ chercher",
            "exemple": 'Rechercher "mariage" dans tout le document',
        },
        "TITLE": {
            "nom": "Titre",
            "description": "Titre officiel du texte juridique",
            "usage": "Rechercher des textes par leur intitulé exact ou partiel",
            "exemple": 'Rechercher "Code civil" ou "loi sur le mariage"',
        },
        "TABLE": {
            "nom": "Table des matières",
            "description": "Structure et organisation du texte (parties, livres, titres, chapitres)",
            "usage": "Naviguer dans l'organisation du texte, chercher des sections",
            "exemple": 'Rechercher "Livre premier" ou "Titre II"',
        },
        "NOR": {
            "nom": "Numéro NOR",
            "description": "Numéro d'ordre réglementaire unique attribué aux textes",
            "usage": "Recherche précise d'un texte par son identifiant officiel",
            "exemple": "JUSC1732516D pour un décret spécifique",
        },
        "NUM": {
            "nom": "Numéro du texte",
            "description": "Numéro officiel du texte (loi n°, décret n°, etc.)",
            "usage": "Rechercher un texte par son numéro de publication",
            "exemple": "Loi n°2018-287 ou Décret n°2019-123",
        },
        "ADVANCED_TEXTE_ID": {
            "nom": "Identifiant technique",
            "description": "Identifiant technique interne du système Légifrance",
            "usage": "Recherche technique par ID système (usage avancé)",
            "exemple": "LEGITEXT000006070721",
        },
        "NUM_DELIB": {
            "nom": "Numéro de délibération",
            "description": "Numéro de délibération pour les textes délibératifs",
            "usage": "Rechercher des délibérations spécifiques (CNIL, collectivités)",
            "exemple": "Délibération n°2019-001",
        },
        "NUM_DEC": {
            "nom": "Numéro de décision",
            "description": "Numéro de décision pour la jurisprudence",
            "usage": "Rechercher des décisions de justice par leur numéro",
            "exemple": "Arrêt n°19-12345",
        },
        "NUM_ARTICLE": {
            "nom": "Numéro d'article",
            "description": "Numéro ou référence d'un article spécifique",
            "usage": "Rechercher des articles précis dans les codes ou lois",
            "exemple": "Article 1134 ou Article L123-1",
        },
        "ARTICLE": {
            "nom": "Contenu des articles",
            "description": "Texte intégral du contenu des articles",
            "usage": "Rechercher dans le contenu même des articles",
            "exemple": 'Rechercher "responsabilité" dans les articles',
        },
        "MINISTERE": {
            "nom": "Ministère",
            "description": "Ministère ou autorité émettrice du texte",
            "usage": "Filtrer les textes par ministère d'origine",
            "exemple": "Ministère de la Justice, Ministère de l'Intérieur",
        },
        "VISA": {
            "nom": "Visas",
            "description": "Références aux textes sur lesquels s'appuie la décision",
            "usage": "Rechercher les fondements juridiques cités",
            "exemple": "Vu le Code civil, vu la loi du...",
        },
        "NOTICE": {
            "nom": "Notice",
            "description": "Notice explicative ou informative du texte",
            "usage": "Rechercher des explications ou contexte du texte",
            "exemple": "Informations sur l'application du texte",
        },
        "VISA_NOTICE": {
            "nom": "Visas et notice",
            "description": "Recherche combinée dans les visas et la notice",
            "usage": "Rechercher à la fois dans les références et explications",
            "exemple": "Contexte juridique complet du texte",
        },
        "TRAVAUX_PREP": {
            "nom": "Travaux préparatoires",
            "description": "Documents préparatoires (rapports, débats parlementaires)",
            "usage": "Comprendre l'intention du législateur",
            "exemple": "Rapport de la commission, exposé des motifs",
        },
        "SIGNATURE": {
            "nom": "Signataires",
            "description": "Autorités ayant signé ou approuvé le texte",
            "usage": "Rechercher par autorité signataire",
            "exemple": "Ministre, Président de la République",
        },
        "NOTA": {
            "nom": "Nota",
            "description": "Notes explicatives ou d'application du texte",
            "usage": "Trouver des précisions sur l'application",
            "exemple": "Conditions d'entrée en vigueur, exceptions",
        },
        "NUM_AFFAIRE": {
            "nom": "Numéro d'affaire",
            "description": "Numéro d'affaire judiciaire ou administrative",
            "usage": "Rechercher une affaire judiciaire précise",
            "exemple": "19-12.345 pour une affaire en cours d'appel",
        },
        "ABSTRATS": {
            "nom": "Abstracts",
            "description": "Résumés courts du contenu principal",
            "usage": "Recherche dans les résumés pour avoir un aperçu",
            "exemple": "Mots-clés du résumé exécutif",
        },
        "RESUMES": {
            "nom": "Résumés",
            "description": "Résumés détaillés du texte",
            "usage": "Rechercher dans les synthèses du contenu",
            "exemple": "Points principaux du texte",
        },
        "TEXTE": {
            "nom": "Texte intégral",
            "description": "Contenu textuel complet du document",
            "usage": "Recherche exhaustive dans tout le contenu",
            "exemple": "Rechercher n'importe quel terme dans le texte",
        },
        "ECLI": {
            "nom": "Identifiant ECLI",
            "description": "European Case Law Identifier - Identifiant européen de jurisprudence",
            "usage": "Recherche de jurisprudence avec référence européenne",
            "exemple": "ECLI:FR:CCASS:2019:C100123",
        },
        "NUM_LOI_DEF": {
            "nom": "Numéro de loi déférée",
            "description": "Numéro de la loi contestée devant le Conseil constitutionnel",
            "usage": "Rechercher les décisions constitutionnelles par loi contestée",
            "exemple": "Loi n°2018-123 déférée au Conseil constitutionnel",
        },
        "TYPE_DECISION": {
            "nom": "Type de décision",
            "description": "Catégorie de la décision de justice",
            "usage": "Filtrer par type de décision judiciaire",
            "exemple": "Arrêt, ordonnance, jugement",
        },
        "NUMERO_INTERNE": {
            "nom": "Numéro interne",
            "description": "Numéro de référence interne à l'administration",
            "usage": "Recherche par référence administrative interne",
            "exemple": "Numéro de dossier administratif",
        },
        "REF_PUBLI": {
            "nom": "Référence de publication",
            "description": "Référence de publication dans les bulletins officiels",
            "usage": "Rechercher par référence de publication officielle",
            "exemple": "JORF n°123 du 15/06/2019",
        },
        "RESUME_CIRC": {
            "nom": "Résumé de circulaire",
            "description": "Résumé spécifique aux circulaires ministérielles",
            "usage": "Rechercher dans les résumés de circulaires",
            "exemple": "Objectifs et portée de la circulaire",
        },
        "TEXTE_REF": {
            "nom": "Texte de référence",
            "description": "Références aux textes cités ou modifiés",
            "usage": "Trouver les textes qui citent ou modifient d'autres textes",
            "exemple": "Références aux codes modifiés",
        },
        "TITRE_LOI_DEF": {
            "nom": "Titre de loi déférée",
            "description": "Titre de la loi contestée devant le Conseil constitutionnel",
            "usage": "Rechercher les décisions constitutionnelles par titre de loi",
            "exemple": "Loi de finances pour 2019",
        },
        "RAISON_SOCIALE": {
            "nom": "Raison sociale",
            "description": "Nom de l'entreprise pour les accords d'entreprise",
            "usage": "Rechercher les accords par nom d'entreprise",
            "exemple": "SNCF, Renault, Total",
        },
        "MOTS_CLES": {
            "nom": "Mots-clés",
            "description": "Mots-clés thématiques associés au texte",
            "usage": "Rechercher par thématique ou domaine juridique",
            "exemple": "Droit du travail, fiscalité, urbanisme",
        },
        "IDCC": {
            "nom": "IDCC",
            "description": "Identifiant de Convention Collective",
            "usage": "Rechercher une convention collective par son numéro IDCC",
            "exemple": "IDCC 1596 pour la métallurgie",
        },
    }

    # Constantes pour les fonds avec descriptions
    FONDS = {
        "JORF": "JORF",  # Journal Officiel de la République Française - Textes publiés au JO
        "CNIL": "CNIL",  # Commission Nationale de l'Informatique et des Libertés - Décisions et délibérations
        "CETAT": "CETAT",  # Conseil d'État - Jurisprudence administrative
        "JURI": "JURI",  # Jurisprudence judiciaire - Décisions de justice
        "JUFI": "JUFI",  # Jurisprudence financière - Décisions des juridictions financières
        "CONSTIT": "CONSTIT",  # Conseil Constitutionnel - Décisions constitutionnelles
        "KALI": "KALI",  # Conventions collectives - Accords collectifs de travail
        "CODE_DATE": "CODE_DATE",  # Codes consolidés - Recherche par date de version
        "CODE_ETAT": "CODE_ETAT",  # Codes consolidés - Recherche par état juridique
        "LODA_DATE": "LODA_DATE",  # Lois, Ordonnances, Décrets, Arrêtés - Recherche par date de version
        "LODA_ETAT": "LODA_ETAT",  # Lois, Ordonnances, Décrets, Arrêtés - Recherche par état juridique
        "ALL": "ALL",  # Tous les fonds - Recherche transversale
        "CIRC": "CIRC",  # Circulaires et instructions - Textes d'application
        "ACCO": "ACCO",  # Accords d'entreprise - Accords collectifs d'entreprise
    }

    # Descriptions détaillées des fonds
    FONDS_DESCRIPTIONS = {
        "JORF": {
            "nom": "Journal Officiel de la République Française",
            "description": "Textes publiés au Journal Officiel : lois, décrets, arrêtés, avis, annonces...",
            "contenu": "Publications officielles, textes réglementaires, nominations, marchés publics",
        },
        "CNIL": {
            "nom": "Commission Nationale de l'Informatique et des Libertés",
            "description": "Décisions, délibérations et avis de la CNIL en matière de protection des données",
            "contenu": "Autorisations, sanctions, recommandations, délibérations",
        },
        "CETAT": {
            "nom": "Conseil d'État",
            "description": "Jurisprudence administrative du Conseil d'État et des juridictions administratives",
            "contenu": "Arrêts, ordonnances, avis du Conseil d'État et des cours administratives d'appel",
        },
        "JURI": {
            "nom": "Jurisprudence judiciaire",
            "description": "Décisions des juridictions de l'ordre judiciaire",
            "contenu": "Arrêts de la Cour de cassation, cours d'appel, tribunaux",
        },
        "JUFI": {
            "nom": "Jurisprudence financière",
            "description": "Décisions des juridictions financières (Cour des comptes, CRC)",
            "contenu": "Arrêts de la Cour des comptes et des chambres régionales des comptes",
        },
        "CONSTIT": {
            "nom": "Conseil Constitutionnel",
            "description": "Décisions du Conseil constitutionnel",
            "contenu": "Décisions sur la constitutionnalité des lois, QPC, contrôle des élections",
        },
        "KALI": {
            "nom": "Conventions collectives",
            "description": "Conventions et accords collectifs de travail étendus",
            "contenu": "Conventions collectives nationales, accords de branche, avenants",
        },
        "CODE_DATE": {
            "nom": "Codes consolidés (par date)",
            "description": "Codes en vigueur recherchés par date de version",
            "contenu": "Tous les codes français consolidés avec historique des versions",
        },
        "CODE_ETAT": {
            "nom": "Codes consolidés (par état juridique)",
            "description": "Codes en vigueur recherchés par état juridique",
            "contenu": "Codes français avec statut juridique (en vigueur, abrogé, etc.)",
        },
        "LODA_DATE": {
            "nom": "LODA (par date)",
            "description": "Lois, Ordonnances, Décrets, Arrêtés recherchés par date de version",
            "contenu": "Textes législatifs et réglementaires consolidés avec historique",
        },
        "LODA_ETAT": {
            "nom": "LODA (par état juridique)",
            "description": "Lois, Ordonnances, Décrets, Arrêtés recherchés par état juridique",
            "contenu": "Textes législatifs et réglementaires avec statut juridique",
        },
        "ALL": {
            "nom": "Tous les fonds",
            "description": "Recherche transversale dans tous les fonds disponibles",
            "contenu": "Ensemble de la base juridique Légifrance",
        },
        "CIRC": {
            "nom": "Circulaires et instructions",
            "description": "Circulaires et instructions ministérielles",
            "contenu": "Textes d'application, instructions, notes de service",
        },
        "ACCO": {
            "nom": "Accords d'entreprise",
            "description": "Accords collectifs d'entreprise déposés",
            "contenu": "Accords d'entreprise, protocoles d'accord, avenants d'entreprise",
        },
    }

    def __init__(self):
        self.query = {
            "fond": "",
            "recherche": {
                "champs": [],
                "filtres": [],
                "pageNumber": 1,
                "pageSize": 50,
                "operateur": "ET",
                "sort": "PERTINENCE",
                "secondSort": "DATE_DESC",
                "typePagination": "DEFAUT",
            },
        }

    def set_fond(self, fond: str) -> "LegiFranceSearchInput":
        """
        Définit le fonds de recherche.

        Args:
            fond (str): Fonds sur lequel appliquer la recherche.
                Pour rechercher dans tous les fonds, utiliser 'ALL'.
                Pour les fonds LODA et CODE, deux types de recherche existent :
                - _DATE : recherche par date de version (CODE_DATE, LODA_DATE)
                - _ETAT : recherche par état juridique (CODE_ETAT, LODA_ETAT)

                Valeurs possibles:
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
                - ALL : Tous les fonds
                - CIRC : Circulaires et instructions
                - ACCO : Accords d'entreprise

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Raises:
            ValueError: Si le fonds spécifié n'est pas valide

        Example:
            >>> search = LegiFranceSearchInput()
            >>> search.set_fond("LODA_DATE")
        """
        if fond not in self.FONDS.values():
            raise ValueError(
                f"Fonds invalide. Utilisez une des valeurs: {list(self.FONDS.values())}"
            )
        self.query["fond"] = fond
        return self

    def add_champ(
        self, type_champ: str, criteres: List[Dict], operateur: str = "ET"
    ) -> "LegiFranceSearchInput":
        """
        Ajoute un champ de recherche (objet ChampDTO dans l'API Légifrance).

        Cette méthode permet de définir dans quel champ de document effectuer la recherche
        et quels critères de recherche y appliquer.

        Args:
            type_champ (str): Type de champ dans lequel rechercher.
                Il est possible d'utiliser 'ALL' pour rechercher dans tous les champs.

                Valeurs possibles (selon ChampDTO de l'API):
                - ALL : Tous les champs
                - TITLE : Titre du texte
                - TABLE : Table des matières
                - NOR : Numéro d'ordre réglementaire
                - NUM : Numéro du texte
                - ADVANCED_TEXTE_ID : Identifiant technique du texte
                - NUM_DELIB : Numéro de délibération
                - NUM_DEC : Numéro de décision
                - NUM_ARTICLE : Numéro d'article
                - ARTICLE : Contenu des articles
                - MINISTERE : Ministère émetteur
                - VISA : Visas du texte
                - NOTICE : Notice du texte
                - VISA_NOTICE : Visas et notice combinés
                - TRAVAUX_PREP : Travaux préparatoires
                - SIGNATURE : Signataires
                - NOTA : Nota du texte
                - NUM_AFFAIRE : Numéro d'affaire (jurisprudence)
                - ABSTRATS : Résumés/abstracts
                - RESUMES : Résumés
                - TEXTE : Contenu textuel complet
                - ECLI : Identifiant ECLI (jurisprudence européenne)
                - NUM_LOI_DEF : Numéro de loi déférée
                - TYPE_DECISION : Type de décision
                - NUMERO_INTERNE : Numéro interne
                - REF_PUBLI : Référence de publication
                - RESUME_CIRC : Résumé de circulaire
                - TEXTE_REF : Texte de référence
                - TITRE_LOI_DEF : Titre de loi déférée
                - RAISON_SOCIALE : Raison sociale (accords d'entreprise)
                - MOTS_CLES : Mots-clés
                - IDCC : Identifiant de convention collective

            criteres (List[Dict]): Liste des critères/groupes de critères de recherche pour ce champ.
                Chaque critère doit être créé avec la méthode create_critere().
                Les critères définissent les mots ou expressions à rechercher dans le champ.

            operateur (str, optional): Opérateur entre les critères de recherche.
                Défaut: "ET"
                Valeurs possibles:
                - "ET" : Tous les critères doivent être satisfaits (AND logique)
                - "OU" : Au moins un critère doit être satisfait (OR logique)

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Raises:
            ValueError: Si le type de champ spécifié n'est pas valide

        Example:
            >>> search = LegiFranceSearchInput()
            >>> critere1 = search.create_critere("mariage", "EXACTE")
            >>> critere2 = search.create_critere("divorce", "UN_DES_MOTS")
            >>> search.add_champ("TITLE", [critere1, critere2], "OU")
        """
        if type_champ not in self.TYPE_CHAMP.values():
            raise ValueError(
                f"Type de champ invalide. Utilisez une des valeurs: {list(self.TYPE_CHAMP.values())}"
            )

        champ = {"typeChamp": type_champ, "criteres": criteres, "operateur": operateur}
        self.query["recherche"]["champs"].append(champ)
        return self

    def create_critere(
        self,
        valeur: str,
        type_recherche: str = "UN_DES_MOTS",
        operateur: str = "ET",
        proximite: Optional[int] = None,
        criteres: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Crée un critère de recherche (objet CritereDTO dans l'API Légifrance).

        Un critère définit ce qui doit être recherché dans un champ spécifique.
        Les critères peuvent être imbriqués pour créer des groupes de critères complexes.

        Args:
            valeur (str): Mot(s) ou expression recherchés.
                Exemples: "dispositions", "mariage pour tous", "Code civil"

            type_recherche (str, optional): Type de recherche effectuée.
                Défaut: "UN_DES_MOTS"

                Valeurs possibles (selon CritereDTO de l'API):
                - "UN_DES_MOTS" : Au moins un des mots doit être présent
                - "EXACTE" : L'expression exacte doit être présente
                - "TOUS_LES_MOTS_DANS_UN_CHAMP" : Tous les mots doivent être présents dans le champ
                - "AUCUN_DES_MOTS" : Aucun des mots ne doit être présent (exclusion)
                - "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION" : L'expression ne doit pas être présente (exclusion)

            operateur (str, optional): Opérateur entre les sous-critères (si criteres est défini).
                Défaut: "ET"
                Valeurs possibles:
                - "ET" : Tous les sous-critères doivent être satisfaits (AND logique)
                - "OU" : Au moins un sous-critère doit être satisfait (OR logique)

            proximite (int, optional): Proximité maximum entre les mots du champ valeur.
                La proximité représente la distance maximale, en mots, entre deux termes recherchés.
                Par exemple, proximite=2 signifie qu'au maximum 2 mots peuvent séparer les termes recherchés.
                Défaut: None (pas de contrainte de proximité)

                Exemple:
                    Avec valeur="fonction publique" et proximite=3, les expressions suivantes seront trouvées:
                    - "fonction publique" (0 mots entre)
                    - "fonction de la publique" (2 mots entre)
                    - "fonction territoriale ou publique" (2 mots entre)
                    Mais pas: "fonction de la République publique" (3 mots entre, dépasse la limite)

            criteres (List[Dict], optional): Sous-critère/Sous-groupe de critères.
                Permet de créer des requêtes imbriquées complexes.
                Chaque élément doit être un dictionnaire créé avec create_critere().
                Défaut: None (pas de sous-critères)

                Exemple de structure imbriquée:
                    critere_parent avec sous-critères:
                    - critere_enfant_1: "soins" ET
                    - critere_enfant_2: "fonction publique" (avec proximité)

        Returns:
            Dict: Dictionnaire représentant le critère, conforme au format CritereDTO de l'API

        Raises:
            ValueError: Si le type de recherche spécifié n'est pas valide

        Examples:
            >>> # Recherche simple d'un mot
            >>> search = LegiFranceSearchInput()
            >>> critere = search.create_critere("mariage", "EXACTE")

            >>> # Recherche avec proximité
            >>> critere = search.create_critere("fonction publique", "TOUS_LES_MOTS_DANS_UN_CHAMP", proximite=3)

            >>> # Recherche avec sous-critères imbriqués
            >>> sous_critere1 = search.create_critere("soins", "UN_DES_MOTS")
            >>> sous_critere2 = search.create_critere("fonction publique", "TOUS_LES_MOTS_DANS_UN_CHAMP", proximite=3)
            >>> critere_parent = search.create_critere(
            ...     "dispositions",
            ...     "UN_DES_MOTS",
            ...     operateur="ET",
            ...     proximite=2,
            ...     criteres=[sous_critere1, sous_critere2]
            ... )
        """
        if type_recherche not in self.TYPE_RECHERCHE.values():
            raise ValueError(
                f"Type de recherche invalide. Utilisez une des valeurs: {list(self.TYPE_RECHERCHE.values())}"
            )

        critere: Dict[str, Any] = {
            "valeur": valeur,
            "typeRecherche": type_recherche,
            "operateur": operateur,
        }

        if proximite is not None:
            critere["proximite"] = proximite

        if criteres is not None:
            critere["criteres"] = criteres

        return critere

    def add_filtre_valeurs(self, facette: str, valeurs: List[str]) -> "LegiFranceSearchInput":
        """
        Ajoute un filtre par valeurs (objet FiltreDTO dans l'API Légifrance).

        Les filtres permettent de restreindre les résultats selon des critères spécifiques
        comme la nature du texte, la juridiction, etc. La requête est effectuée automatiquement
        avec un opérateur ET entre les filtres listés.

        Args:
            facette (str): Nom de la facette => nom du filtre.
                Les facettes disponibles dépendent du fonds recherché et sont retournées
                dynamiquement dans les réponses de l'API (SearchResponseDTO.facets).

                **FACETTES COMMUNES À PLUSIEURS FONDS:**

                - **NATURE** : Nature du texte
                  Valeurs possibles: LOI, ORDONNANCE, ARRETE, DECRET, CODE, CIRCULAIRE,
                                    CONSTITUTION, TRAITE, ACCORD, CONVENTION, REGLEMENT, etc.

                - **ETAT_JURIDIQUE** (ou legalStatus) : État juridique du texte
                  Valeurs possibles: VIGUEUR, ABROGE, ABROGE_DIFF, VIGUEUR_DIFF,
                                    VIGUEUR_ETEN, VIGUEUR_NON_ETEN, PERIME, ANNULE,
                                    MODIFIE, DISJOINT, SUBSTITUE, TRANSFERE, INITIALE,
                                    MODIFIE_MORT_NE, SANS_ETAT, DENONCE, REMPLACE

                **FACETTES SPÉCIFIQUES AUX FONDS JURIDICTIONNELS (CETAT, JURI, JUFI, CONSTIT):**

                - **JURIDICTION** : Juridiction émettrice
                  Valeurs possibles: Conseil d'État, Cour de cassation, Cour des comptes,
                                    Conseil constitutionnel, Tribunal administratif,
                                    Cour d'appel, etc.

                - **JURIDICTION_NATURE** : Nature de la juridiction
                  Valeurs possibles: TRIBUNAL_ADMINISTRATIF, COURS_APPEL, COURS_COMPTES,
                                    CONSEIL_ETAT, COUR_CASSATION, TRIBUNAL_CONFLITS,
                                    COUR_JUSTICE_REPUBLIQUE, etc.

                - **TYPE_DECISION** : Type de décision
                  Valeurs possibles: ARRET, ORDONNANCE, AVIS, DECISION, JUGEMENT, etc.

                - **CHAMBRE** : Chambre de la juridiction
                  Valeurs possibles: Première chambre civile, Chambre criminelle,
                                    Chambre sociale, Chambre commerciale, etc.

                - **FORMATION** : Formation de jugement
                  Valeurs possibles: Plénière, Section, Assemblée, etc.

                **FACETTES SPÉCIFIQUES AU FONDS JORF (Journal Officiel):**

                - **MINISTERE** : Ministère émetteur
                  Valeurs possibles: Ministère de la Justice, Ministère de l'Intérieur,
                                    Ministère des Finances, Ministère de la Santé, etc.

                - **NUM_PARUTION** : Numéro de parution du JO

                **FACETTES SPÉCIFIQUES AU FONDS KALI (Conventions collectives):**

                - **IDCC** : Identifiant de Convention Collective
                  Valeurs possibles: Numéros IDCC (ex: "1880", "2120", etc.)

                - **MOTS_CLES** : Mots-clés thématiques
                  Valeurs possibles: ABATTOIRS, CHAUX HYDRAULIQUES, ENSEIGNEMENT,
                                    TRANSPORT, COMMERCE, etc.

                - **TYPE_TEXTE** : Type de texte conventionnel
                  Valeurs possibles: TEXTE_BASE, TEXTE_ATTACHE, TEXTE_ETENDU, etc.

                **FACETTES SPÉCIFIQUES AU FONDS CIRC (Circulaires):**

                - **MINISTERE_DEPOSANT** : Ministère déposant la circulaire

                - **ETAT_CIRCULAIRE** : État de la circulaire
                  Valeurs possibles: VIGUEUR (V), ABROGE (A), etc.

                **FACETTES SPÉCIFIQUES AU FONDS ACCO (Accords d'entreprise):**

                - **RAISON_SOCIALE** : Raison sociale de l'entreprise

                - **THEME** : Thème de l'accord
                  Valeurs possibles: Salaires, Temps de travail, Formation, etc.

                **FACETTES SPÉCIFIQUES AUX DÉBATS ET QUESTIONS PARLEMENTAIRES:**

                - **TYPE_PARLEMENT** : Type de parlement
                  Valeurs possibles: AN (Assemblée Nationale), SENAT (Sénat)

                - **LEGISLATURE** : Législature
                  Valeurs possibles: 14, 15, 16, etc.

                **AUTRES FACETTES:**

                - **ANNEE** (years) : Année de publication/signature

                - **CODE_NAME** : Nom du code (pour le fonds CODE)
                  Valeurs possibles: Code civil, Code pénal, Code du travail, etc.

            valeurs (List[str]): Liste des valeurs du filtre dans le cas d'un filtre textuel.
                Les valeurs exactes dépendent de la facette choisie.
                Utilisez les valeurs retournées par l'API dans les facettes de réponse.

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Note:
            - Plusieurs filtres peuvent être ajoutés. Ils seront combinés avec un opérateur ET.
            - Les facettes disponibles varient selon le fonds recherché.
            - Consultez d'abord les résultats d'une recherche pour voir les facettes disponibles
              et leurs valeurs possibles dans le contexte de votre fonds.

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Filtrer par nature de texte (JORF, LODA)
            >>> search.add_filtre_valeurs("NATURE", ["LOI", "ORDONNANCE", "ARRETE"])
            >>>
            >>> # Filtrer par juridiction (CETAT, JURI)
            >>> search.add_filtre_valeurs("JURIDICTION_NATURE", ["TRIBUNAL_ADMINISTRATIF", "COURS_APPEL"])
            >>>
            >>> # Filtrer par état juridique
            >>> search.add_filtre_valeurs("ETAT_JURIDIQUE", ["VIGUEUR", "VIGUEUR_DIFF"])
            >>>
            >>> # Filtrer par IDCC pour conventions collectives (KALI)
            >>> search.add_filtre_valeurs("IDCC", ["1880", "2120"])
            >>>
            >>> # Filtrer par ministère (JORF)
            >>> search.add_filtre_valeurs("MINISTERE", ["Ministère de la Justice"])
        """
        filtre = {"facette": facette, "valeurs": valeurs}
        self.query["recherche"]["filtres"].append(filtre)
        return self

    def add_filtre_dates(
        self, facette: str, start_date: str, end_date: str
    ) -> "LegiFranceSearchInput":
        """
        Ajoute un filtre par période de dates (objet FiltreDTO avec DatePeriod dans l'API Légifrance).

        Permet de filtrer les résultats sur une plage de dates définie.

        Args:
            facette (str): Nom de la facette de date => nom du filtre.

                **FACETTES DE DATES PRINCIPALES:**

                - **DATE_SIGNATURE** : Date de signature du texte
                  Applicable aux fonds: JORF, LODA, CODE, CIRC

                - **DATE_PUBLICATION** (ou DATE_PUBLI) : Date de publication officielle
                  Applicable aux fonds: JORF, LODA, CODE, CIRC, KALI

                - **DATE_VERSION** : Date de version du texte consolidé
                  Applicable aux fonds: CODE, LODA (recherche par date)

                - **DATE_PARUTION** : Date de parution au Journal Officiel
                  Applicable au fonds: JORF

                - **DATE_DECISION** : Date de la décision judiciaire
                  Applicable aux fonds: CETAT, JURI, JUFI, CONSTIT

                - **DATE_ARRET** : Date de l'arrêt
                  Applicable aux fonds: JURI, CETAT

                - **DATE_CREATION** : Date de création du document
                  Applicable aux fonds: ACCO, CIRC

                - **DATE_MODIFICATION** (ou DATE_UPDATE, lastUpdate) : Date de dernière modification
                  Applicable à plusieurs fonds pour le suivi des mises à jour

                - **DATE_EFFET** : Date d'entrée en vigueur/effet
                  Applicable aux fonds: ACCO, KALI

                - **DATE_ABROGATION** : Date d'abrogation du texte
                  Applicable aux fonds: LODA, CODE

                - **DATE_DEPOT** : Date de dépôt (pour accords d'entreprise)
                  Applicable au fonds: ACCO

                - **DATE_EXPORT** : Date d'export du document
                  Applicable au fonds: CIRC

                - **DATE_OPPOSABILITE** : Date de déclaration d'opposabilité
                  Applicable au fonds: CIRC

                - **DATE_DELIBERATION** : Date de délibération
                  Applicable au fonds: CNIL

            start_date (str): Date de début de la période.
                Format: "YYYY-MM-DD" (ex: "2015-01-01")
                Le format ISO 8601 est requis.

            end_date (str): Date de fin de la période.
                Format: "YYYY-MM-DD" (ex: "2018-01-31")
                Le format ISO 8601 est requis.

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Filtrer les textes signés entre le 1er janvier 2015 et le 31 janvier 2018
            >>> search.add_filtre_dates("DATE_SIGNATURE", "2015-01-01", "2018-01-31")
            >>> # Filtrer les textes publiés en 2020
            >>> search.add_filtre_dates("DATE_PUBLICATION", "2020-01-01", "2020-12-31")
        """
        filtre = {"facette": facette, "dates": {"start": start_date, "end": end_date}}
        self.query["recherche"]["filtres"].append(filtre)
        return self

    def add_filtre_date_unique(self, facette: str, date: str) -> "LegiFranceSearchInput":
        """
        Ajoute un filtre par date unique (objet FiltreDTO dans l'API Légifrance).

        Permet de filtrer les résultats sur une date précise.

        Args:
            facette (str): Nom de la facette de date => nom du filtre.

                **FACETTES DE DATES PRINCIPALES:**

                - **DATE_SIGNATURE** : Date de signature du texte
                  Applicable aux fonds: JORF, LODA, CODE, CIRC

                - **DATE_PUBLICATION** (ou DATE_PUBLI) : Date de publication officielle
                  Applicable aux fonds: JORF, LODA, CODE, CIRC, KALI

                - **DATE_VERSION** : Date de version du texte consolidé
                  Applicable aux fonds: CODE, LODA (recherche par date)

                - **DATE_PARUTION** : Date de parution au Journal Officiel
                  Applicable au fonds: JORF

                - **DATE_DECISION** : Date de la décision judiciaire
                  Applicable aux fonds: CETAT, JURI, JUFI, CONSTIT

                - **DATE_ARRET** : Date de l'arrêt
                  Applicable aux fonds: JURI, CETAT

                - **DATE_CREATION** : Date de création du document
                  Applicable aux fonds: ACCO, CIRC

                - **DATE_MODIFICATION** (ou DATE_UPDATE, lastUpdate) : Date de dernière modification
                  Applicable à plusieurs fonds pour le suivi des mises à jour

                - **DATE_EFFET** : Date d'entrée en vigueur/effet
                  Applicable aux fonds: ACCO, KALI

                - **DATE_ABROGATION** : Date d'abrogation du texte
                  Applicable aux fonds: LODA, CODE

                - **DATE_DEPOT** : Date de dépôt (pour accords d'entreprise)
                  Applicable au fonds: ACCO

                - **DATE_EXPORT** : Date d'export du document
                  Applicable au fonds: CIRC

                - **DATE_OPPOSABILITE** : Date de déclaration d'opposabilité
                  Applicable au fonds: CIRC

                - **DATE_DELIBERATION** : Date de délibération
                  Applicable au fonds: CNIL

            date (str): Date unique pour le filtre.
                Format: "YYYY-MM-DD" (ex: "2016-01-01")
                Le format ISO 8601 est requis.
                Le format datetime complet ISO 8601 est également accepté (ex: "2016-01-01T00:00:00").

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Filtrer les textes signés le 1er janvier 2016
            >>> search.add_filtre_date_unique("DATE_SIGNATURE", "2016-01-01")
        """
        filtre = {"facette": facette, "singleDate": date}
        self.query["recherche"]["filtres"].append(filtre)
        return self

    def set_pagination(
        self, page_number: int = 1, page_size: int = 10, type_pagination: str = "DEFAUT"
    ) -> "LegiFranceSearchInput":
        """
        Configure la pagination des résultats (selon RechercheSpecifiqueDTO de l'API Légifrance).

        Args:
            page_number (int, optional): Numéro de la page à consulter.
                Défaut: 1 (première page)
                La numérotation commence à 1.

            page_size (int, optional): Nombre d'éléments par page.
                Défaut: 10
                Maximum: 100 (la valeur sera automatiquement limitée à 100 si dépassée)

            type_pagination (str, optional): Type de pagination.
                Défaut: "DEFAUT"

                Valeurs possibles:
                - "DEFAUT" : Pagination standard (DEFAULT dans l'API)
                - "ARTICLE" : Pagination spécifique pour les recherches dans les articles d'un texte

                Note: Dans la plupart des cas, utiliser "DEFAUT".
                Lors de la navigation dans plusieurs pages, il est nécessaire de passer
                la valeur reçue dans la réponse précédente.

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Pagination standard : 50 résultats par page, page 1
            >>> search.set_pagination(page_number=1, page_size=50)
            >>> # Aller à la page 3 avec 25 résultats par page
            >>> search.set_pagination(page_number=3, page_size=25)
        """
        self.query["recherche"]["pageNumber"] = page_number
        self.query["recherche"]["pageSize"] = min(page_size, 100)  # Max 100
        self.query["recherche"]["typePagination"] = type_pagination
        return self

    def set_operateur_global(self, operateur: str) -> "LegiFranceSearchInput":
        """
        Définit l'opérateur global entre les champs de recherche (selon RechercheSpecifiqueDTO de l'API).

        Cet opérateur détermine comment les différents champs de recherche sont combinés.

        Args:
            operateur (str): Opérateur entre les champs de recherche.

                Valeurs possibles:
                - "ET" : Tous les champs doivent correspondre (AND logique)
                         Exemple: Si vous recherchez "mariage" dans TITLE ET "divorce" dans ARTICLE,
                         seuls les documents contenant les deux seront retournés.

                - "OU" : Au moins un champ doit correspondre (OR logique)
                         Exemple: Si vous recherchez "mariage" dans TITLE OU "divorce" dans ARTICLE,
                         les documents contenant l'un ou l'autre (ou les deux) seront retournés.

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Raises:
            ValueError: Si l'opérateur n'est pas "ET" ou "OU"

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Les documents doivent correspondre à TOUS les champs
            >>> search.set_operateur_global("ET")
            >>> # Les documents doivent correspondre à AU MOINS UN champ
            >>> search.set_operateur_global("OU")
        """
        if operateur not in ["ET", "OU"]:
            raise ValueError("L'opérateur doit être 'ET' ou 'OU'")
        self.query["recherche"]["operateur"] = operateur
        return self

    def set_sort(self, sort: str, second_sort: Optional[str] = None) -> "LegiFranceSearchInput":
        """
        Configure le tri des résultats (selon RechercheSpecifiqueDTO de l'API Légifrance).

        Les tris possibles dépendent du fonds recherché.

        Args:
            sort (str): Tri principal des éléments trouvés.

                Exemples de valeurs courantes (selon le fonds):
                - "PERTINENCE" : Tri par pertinence (défaut recommandé)
                - "SIGNATURE_DATE_DESC" : Date de signature décroissante (plus récent en premier)
                - "SIGNATURE_DATE_ASC" : Date de signature croissante
                - "DATE_PUBLI_DESC" : Date de publication décroissante
                - "DATE_PUBLI_ASC" : Date de publication croissante
                - "DATE_VERSION_DESC" : Date de version décroissante
                - "DATE_VERSION_ASC" : Date de version croissante
                - "ID_DESC" : Identifiant décroissant
                - "ID_ASC" : Identifiant croissant
                - "DATE_UPDATE" : Date de mise à jour

                Note: Les options de tri disponibles varient selon le fonds (JORF, LODA, CODE, etc.)

            second_sort (str, optional): Tri secondaire des éléments trouvés.
                Appliqué lorsque le tri principal donne des résultats identiques.
                Accepte les mêmes valeurs que le paramètre 'sort'.
                Défaut: None (pas de tri secondaire)

                Exemples:
                - "ID" : Par identifiant
                - "DATE_DESC" : Par date décroissante
                - "DATE_ASC" : Par date croissante

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Tri par pertinence uniquement
            >>> search.set_sort("PERTINENCE")
            >>> # Tri par date de signature décroissante, puis par ID
            >>> search.set_sort("SIGNATURE_DATE_DESC", "ID")
            >>> # Tri par date de publication, puis par date de signature
            >>> search.set_sort("DATE_PUBLI_DESC", "SIGNATURE_DATE_DESC")
        """
        self.query["recherche"]["sort"] = sort
        if second_sort:
            self.query["recherche"]["secondSort"] = second_sort
        return self

    def set_advanced_search(self, advanced: bool = True) -> "LegiFranceSearchInput":
        """
        Active ou désactive le mode de recherche avancée (selon RechercheSpecifiqueDTO de l'API).

        Ce paramètre permet d'indiquer s'il s'agit d'une recherche avancée ou simple.

        Args:
            advanced (bool, optional): Déterminer s'il s'agit d'une recherche avancée.
                Défaut: True

                Valeurs:
                - True : Mode recherche avancée activé
                - False : Mode recherche simple

        Returns:
            LegiFranceSearchInput: Instance pour chaînage des méthodes

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> # Activer la recherche avancée
            >>> search.set_advanced_search(True)
            >>> # Désactiver la recherche avancée (recherche simple)
            >>> search.set_advanced_search(False)
        """
        self.query["recherche"]["fromAdvancedRecherche"] = advanced
        return self

    def build(self) -> Dict:
        """
        Construit et retourne la requête finale au format SearchRequestDTO de l'API Légifrance.

        Valide que tous les paramètres requis sont définis et retourne un dictionnaire
        représentant la requête complète prête à être envoyée à l'API.

        Returns:
            Dict: Dictionnaire représentant la requête de recherche complète,
                  conforme au format SearchRequestDTO de l'API Légifrance.

                  Structure retournée:
                  {
                      "fond": "LODA_DATE",  # Fonds de recherche
                      "recherche": {         # Objet RechercheSpecifiqueDTO
                          "champs": [...],   # Liste des champs de recherche (ChampDTO)
                          "filtres": [...],  # Liste des filtres (FiltreDTO)
                          "pageNumber": 1,   # Numéro de page
                          "pageSize": 50,    # Taille de page
                          "operateur": "ET", # Opérateur global
                          "sort": "PERTINENCE",  # Tri principal
                          "secondSort": "DATE_DESC",  # Tri secondaire (optionnel)
                          "typePagination": "DEFAUT",  # Type de pagination
                          "fromAdvancedRecherche": false  # Mode recherche avancée (optionnel)
                      }
                  }

        Raises:
            ValueError: Si le fonds n'a pas été défini avec set_fond()

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> search.set_fond("LODA_DATE")
            >>> critere = search.create_critere("mariage", "EXACTE")
            >>> search.add_champ("TITLE", [critere])
            >>> query = search.build()
            >>> print(query)
            {'fond': 'LODA_DATE', 'recherche': {...}}
        """
        if not self.query["fond"]:
            raise ValueError("Le fonds doit être défini")
        return self.query.copy()

    def to_json(self, indent: int = 2) -> str:
        """
        Retourne la requête au format JSON.

        Construit la requête avec build() et la sérialise en JSON.

        Args:
            indent (int, optional): Nombre d'espaces pour l'indentation du JSON.
                Défaut: 2
                Utilisez None pour obtenir un JSON compact sans indentation.

        Returns:
            str: Chaîne JSON représentant la requête de recherche,
                 prête à être envoyée à l'endpoint /search de l'API Légifrance.

        Raises:
            ValueError: Si le fonds n'a pas été défini (propagé depuis build())

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> search.set_fond("LODA_DATE")
            >>> critere = search.create_critere("mariage", "EXACTE")
            >>> search.add_champ("TITLE", [critere])
            >>> json_str = search.to_json()
            >>> print(json_str)
            {
              "fond": "LODA_DATE",
              "recherche": {
                "champs": [...]
              }
            }
        """
        return json.dumps(self.build(), indent=indent, ensure_ascii=False)

    def reset(self) -> "LegiFranceSearchInput":
        """
        Remet à zéro le générateur de requêtes.

        Réinitialise toutes les configurations à leurs valeurs par défaut.
        Utile pour réutiliser le même objet pour construire une nouvelle requête.

        Returns:
            LegiFranceSearchInput: Instance réinitialisée pour chaînage des méthodes

        Examples:
            >>> search = LegiFranceSearchInput()
            >>> search.set_fond("LODA_DATE")
            >>> # ... construire une requête ...
            >>> search.reset()  # Réinitialise tout
            >>> search.set_fond("JORF")  # Commence une nouvelle requête
        """
        self.__init__()
        return self
