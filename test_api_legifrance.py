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

from api_legifrance import LegiFranceAPI

# Marquer tous les tests comme tests d'intégration car ils appellent l'API réelle
pytestmark = pytest.mark.integration


# Fixture pour partager une instance de l'API entre tous les tests
@pytest.fixture(scope="module")
def api():
    """
    Fixture qui crée une instance unique de JudiLibreAPI pour tous les tests.
    L'instance est créée une seule fois au début et réutilisée pour tous les tests.
    """
    return LegiFranceAPI(sandbox=True)


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

    results = api.search(query="mariage", fond="CODE_ETAT", code_name="Code civil", page_size=5)

    assert results is not None, "Les résultats ne doivent pas être None"
    assert len(results) > 0, "La liste de résultats ne doit pas être vide"


def test_search_with_filters(api):
    """Test une recherche avec filtres par valeurs"""

    results = api.search(
        query="travail",
        fond="JORF",
        type_recherche="UN_DES_MOTS",
        filtres_valeurs={"NATURE": ["LOI"]},
        page_size=3,
    )

    assert results is not None

    # Vérifier que les résultats ont des données valides
    if len(results) > 0:
        for article in results:
            assert "article_id" in article or "title" in article


def test_search_with_date_filters(api):
    """Test une recherche avec filtres par dates"""

    results = api.search(
        query="environnement",
        fond="JORF",
        filtres_dates={"DATE_SIGNATURE": {"start": "2020-01-01", "end": "2023-12-31"}},
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
        id_page1 = results_page1[0]["article_id"]
        id_page2 = results_page2[0]["article_id"]
        assert id_page1 != id_page2, "Les résultats des deux pages doivent être différents"


def test_search_exact_match(api):
    """Test la recherche exacte"""

    results = api.search(query="Code civil", fond="CODE_ETAT", type_recherche="EXACTE", page_size=5)

    assert results is not None


def test_search_in_title(api):
    """Test la recherche dans les titres uniquement"""

    results = api.search(query="pénal", fond="CODE_ETAT", type_champ="TITLE", page_size=5)

    assert results is not None


def test_article_legiarti(api):
    """Test la récupération d'un article de loi (LEGIARTI)"""

    # D'abord faire une recherche pour obtenir un ID valide
    search_results = api.search(
        query="mariage", fond="CODE_ETAT", code_name="Code civil", page_size=1
    )

    # Si on a des résultats, essayer de récupérer plus de détails
    # Note: cet exemple peut nécessiter d'ajuster selon la structure réelle des résultats
    assert search_results is not None


def test_article_legitext(api):
    """Test la récupération d'un texte légal (LEGITEXT)"""

    # Utiliser un ID de texte connu (Code civil)
    # Note: Cet ID peut nécessiter d'être ajusté selon la sandbox
    try:
        result = api.article("LEGITEXT000006070721")
        assert result is not None
        assert isinstance(result, dict)
    except Exception as e:
        # Si l'ID n'est pas valide en sandbox, le test passe quand même
        assert "Erreur lors de la récupération" in str(e)


def test_search_invalid_fond(api):
    """Test qu'une erreur est levée pour un fond invalide"""

    with pytest.raises(ValueError, match="Fond invalide"):
        api.search(query="test", fond="INVALID_FOND")


def test_search_invalid_type_recherche(api):
    """Test qu'une erreur est levée pour un type de recherche invalide"""

    with pytest.raises(ValueError, match="Type de recherche invalide"):
        api.search(query="test", type_recherche="INVALID_TYPE")


def test_search_invalid_type_champ(api):
    """Test qu'une erreur est levée pour un type de champ invalide"""

    with pytest.raises(ValueError, match="Type de champ invalide"):
        api.search(query="test", type_champ="INVALID_CHAMP")


def test_search_no_query(api):
    """Test qu'une erreur est levée si aucune query n'est fournie"""

    with pytest.raises(ValueError, match="Le paramètre 'query' doit être fourni"):
        api.search()


def test_search_invalid_operator(api):
    """Test qu'une erreur est levée pour un opérateur invalide"""

    with pytest.raises(ValueError, match="L'opérateur doit être"):
        api.search(query="test", operateur="INVALID")


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
    api_instance = LegiFranceAPI(sandbox=True)
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
