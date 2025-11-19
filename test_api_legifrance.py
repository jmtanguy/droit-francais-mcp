#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests simples pour l'API Légifrance.
Ces tests utilisent l'API sandbox et nécessitent des credentials valides dans .env

Pour exécuter les tests:
    pytest test_api_legifrance.py -v
    pytest test_api_legifrance.py -v -m integration  # Seulement les tests d'intégration
    pytest test_api_legifrance.py -v -k "test_search"  # Seulement les tests de recherche
"""

import pytest

from api_legifrance import LegifranceAPI

# Marquer tous les tests comme tests d'intégration car ils appellent l'API réelle
pytestmark = pytest.mark.integration


# Fixture pour partager une instance de l'API entre tous les tests
@pytest.fixture(scope="module")
def api():
    """
    Fixture qui crée une instance unique de JudiLibreAPI pour tous les tests.
    L'instance est créée une seule fois au début et réutilisée pour tous les tests.
    """
    return LegifranceAPI(sandbox=True)


def test_init_sandbox(api):
    """Test l'initialisation du client en mode sandbox"""

    assert api.client_id is not None, "Le client_id doit être défini"
    assert api.client_secret is not None, "Le client_secret doit être défini"
    assert "sandbox" in api.base_url, "L'URL de base doit contenir 'sandbox'"
    assert api.access_token is None, "Le token doit être None avant authentification"


def test_get_access_token(api):
    """Test l'obtention du token d'accès OAuth"""
    token = api.get_access_token()

    assert token is not None, "Le token ne doit pas être None"
    assert isinstance(token, str), "Le token doit être une chaîne"
    assert len(token) > 0, "Le token ne doit pas être vide"
    assert api.access_token == token, "Le token doit être stocké dans l'instance"
    assert api.token_expires_at is not None, "La date d'expiration doit être définie"


def test_token_caching(api):
    """Test que le token est mis en cache et réutilisé"""
    token1 = api.get_access_token()
    token2 = api.get_access_token()

    assert token1 == token2, "Le même token doit être réutilisé"


def test_search_simple(api):
    """Test une recherche simple dans le Code civil"""

    results = api.search(query="mariage", fond="CODE_ETAT", code="Code civil", page_size=5)

    assert results is not None, "Les résultats ne doivent pas être None"
    assert len(results) > 0, "La liste de résultats ne doit pas être vide"


def test_search_with_filters(api):
    """Test une recherche avec filtres par valeurs"""
    results = api.search(
        query="travail",
        fond="JORF",
        search_type="UN_DES_MOTS",
        filters={"NATURE": ["LOI"]},
        page_size=3,
    )
    assert results is not None


def test_search_with_date_filters(api):
    """Test une recherche avec filtres par dates"""
    results = api.search(
        query="environnement",
        fond="JORF",
        date_start="2020-01-01",
        page_size=5,
    )

    assert results is not None


def test_search_pagination(api):
    """Test la pagination des résultats"""

    # Première page
    results_page1 = api.search(query="contrat", fond="CODE_ETAT", page_number=1, page_size=3)

    # Deuxième page
    results_page2 = api.search(query="contrat", fond="CODE_ETAT", page_number=2, page_size=3)

    assert results_page1 is not None
    assert results_page2 is not None

    # Vérifier que les résultats sont différents
    if len(results_page1) > 0 and len(results_page2) > 0:
        id_page1 = results_page1["results"][0]["titles"][0]["id"]
        id_page2 = results_page2["results"][0]["titles"][0]["id"]
        assert id_page1 != id_page2, "Les résultats des deux pages doivent être différents"


def test_search_exact_match(api):
    """Test la recherche exacte"""

    results = api.search(query="Code civil", fond="CODE_ETAT", search_type="EXACTE", page_size=5)

    assert results is not None


def test_search_in_title(api):
    """Test la recherche dans les titres uniquement"""

    results = api.search(query="pénal", fond="CODE_ETAT", field_type="TITLE", page_size=5)

    assert results is not None

def test_search_with_date(api):
    """Test la recherche avec filtre de dates - utilise JORF car CODE_ETAT ne supporte pas les filtres de dates"""

    results = api.search(query="environnement", fond="JORF", page_size=5, date_end="2022-01-01" )

    assert results is not None

def test_article_legiarti(api):
    """Test la récupération d'un article de loi (LEGIARTI)"""

    # D'abord faire une recherche pour obtenir un ID valide
    search_results = api.search(
        query="mariage", fond="CODE_ETAT", code="Code civil", page_size=1
    )

    # Si on a des résultats, essayer de récupérer plus de détails
    # Note: cet exemple peut nécessiter d'ajuster selon la structure réelle des résultats
    assert search_results is not None


def test_article_legitext(api):
    """Test la récupération d'un texte légal (LEGITEXT)"""
    result = api.consult("LEGITEXT000006070721")
    assert result is not None
        
def test_article_legiarticle(api):
    result = api.consult("LEGIARTI000006307920")
    assert result is not None 

def test_article_juritext(api):
    result = api.consult("JURITEXT000037999394")
    assert result is not None  

def test_article_CNILTEXT(api):
    result = api.consult("CNILTEXT000017652361")
    assert result is not None  

def test_article_KALITEXT(api):
    result = api.consult("KALITEXT000005677408")
    assert result is not None  

def test_article_KALIARTI(api):
    result = api.consult("KALIARTI000005833238")
    assert result is not None  

def test_article_ACCOTEXT(api):
    result = api.consult("ACCOTEXT000037731479")
    assert result is not None  

def test_article_JORF(api):
    result = api.consult("JORFTEXT000033736934")
    assert result is not None  


def test_search_invalid_fond(api):
    """Test qu'une erreur est levée pour un fond invalide"""

    with pytest.raises(ValueError, match="Fond invalide"):
        api.search(query="test", fond="INVALID_FOND")


def test_search_invalid_search_type(api):
    """Test qu'une erreur est levée pour un type de recherche invalide"""

    with pytest.raises(ValueError, match="Type de recherche invalide"):
        api.search(query="test", search_type="INVALID_TYPE")


def test_search_invalid_field_type(api):
    """Test qu'une erreur est levée pour un type de champ invalide"""

    with pytest.raises(ValueError, match="Type de champ invalide"):
        api.search(query="test", field_type="INVALID_CHAMP")


def test_search_no_query(api):
    """Test qu'une erreur est levée si aucune query n'est fournie"""

    with pytest.raises(ValueError, match="Le paramètre 'recherche' doit être fourni"):
        api.search()


def test_search_invalid_operator(api):
    """Test qu'une erreur est levée pour un opérateur invalide"""

    with pytest.raises(ValueError, match="L'opérateur doit être"):
        api.search(query="test", operator="INVALID")


def test_search_with_sort(api):
    """Test la recherche avec tri personnalisé"""

    results = api.search(query="loi", fond="JORF", sort="SIGNATURE_DATE_DESC", page_size=5)

    assert results is not None


def test_search_kali_conventions(api):
    """Test la recherche dans les conventions collectives"""

    results = api.search(query="télétravail", fond="KALI", page_size=3)

    assert results is not None


def test_search_jurisprudence(api):
    """Test la recherche dans la jurisprudence"""

    results = api.search(query="responsabilité", fond="JURI", page_size=3)

    assert results is not None


if __name__ == "__main__":
    # Permet d'exécuter directement le fichier pour des tests rapides
    print("Exécution des tests...")
    api_instance = LegifranceAPI(sandbox=True)
    print("\nTest 1: Initialisation")
    test_init_sandbox(api_instance)
    print("✓ Réussi")

    print("\nTest 2: Obtention du token")
    test_get_access_token(api_instance)
    print("✓ Réussi")

    print("\nTest 3: Recherche simple")
    test_search_simple(api_instance)
    print("✓ Réussi")

    print("\nTest 4: Recherche avec filtres")
    test_search_with_filters(api_instance)
    print("✓ Réussi")

    print("\n✓ Tous les tests de base sont réussis!")
    print("\nPour exécuter tous les tests avec pytest:")
    print("  pytest test_api_legifrance.py -v")
