#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests simples pour l'API JudiLibre.
Ces tests utilisent l'API sandbox et nécessitent des credentials valides dans .env

NOUVELLES FONCTIONNALITÉS:
    L'API JudiLibre dispose maintenant de méthodes helper pour gérer facilement les taxonomies:
    - get_taxonomy_keys(): Récupère uniquement les clés disponibles
    - get_taxonomy_values(): Récupère les paires clé/valeur

    Exemple d'utilisation:

        # Récupérer les chambres disponibles
        chambers = api.get_taxonomy_values("chamber")
        for chamber in chambers:
            print(f"{chamber['key']}: {chamber['value']}")

        # Utiliser une chambre dans une recherche
        if chambers:
            results = api.search(
                query="contrat",
                chamber=[chambers[0]['key']],
                page_size=10
            )

Pour exécuter les tests:
    pytest test_api_judilibre.py -v
    pytest test_api_judilibre.py -v -m integration  # Seulement les tests d'intégration
    pytest test_api_judilibre.py -v -k "test_search"  # Seulement les tests de recherche
    pytest test_api_judilibre.py -v -k "taxonomy"  # Seulement les tests de taxonomie
"""

import pytest

from api_judilibre import JudiLibreAPI

# Marquer tous les tests comme tests d'intégration car ils appellent l'API réelle
pytestmark = pytest.mark.integration


# Fixture pour partager une instance de l'API entre tous les tests
@pytest.fixture(scope="module")
def api():
    """
    Fixture qui crée une instance unique de JudiLibreAPI pour tous les tests.
    L'instance est créée une seule fois au début et réutilisée pour tous les tests.
    """
    return JudiLibreAPI(sandbox=True)


def test_init_sandbox(api):
    """Test l'initialisation du client en mode sandbox"""

    assert api.client_id is not None, "Le client_id doit être défini"
    assert api.client_secret is not None, "Le client_secret doit être défini"
    assert "sandbox" in api.base_url, "L'URL de base doit contenir 'sandbox'"


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
    """Test une recherche simple"""

    results = api.search(query="responsabilité", page_size=5)

    assert results is not None, "Les résultats ne doivent pas être None"


def test_search_with_field_filter(api):
    """Test une recherche sur des champs spécifiques"""

    results = api.search(query="dommages", field=["motivations", "dispositif"], page_size=3)

    assert results is not None


def test_search_with_operator_and(api):
    """Test une recherche avec l'opérateur AND"""

    results = api.search(query="responsabilité contractuelle", operator="and", page_size=5)

    assert results is not None


def test_search_with_operator_exact(api):
    """Test une recherche exacte"""

    results = api.search(query="Cour de cassation", operator="exact", page_size=5)

    assert results is not None


def test_search_with_date_range(api):
    """Test une recherche avec intervalle de dates"""

    results = api.search(
        query="divorce", date_start="2020-01-01", date_end="2023-12-31", page_size=5
    )

    assert results is not None


def test_search_with_type_filter(api):
    """Test une recherche filtrée par type de décision"""

    results = api.search(query="contrat", type=["arret"], page_size=5)

    assert results is not None


def test_search_with_chamber_civ1(api):
    """Test une recherche dans la première chambre civile avec la clé correcte"""

    results = api.search(
        query="responsabilité contractuelle",
        chamber=["civ1"],  # Utilisation de la CLÉ correcte
        page_size=5,
    )

    assert results is not None


def test_search_with_chamber_soc(api):
    """Test une recherche dans la chambre sociale avec la clé correcte"""

    results = api.search(
        query="licenciement", chamber=["soc"], page_size=5  # Utilisation de la CLÉ correcte
    )

    assert results is not None


def test_search_with_jurisdiction_filter(api):
    """Test une recherche filtrée par juridiction"""

    results = api.search(query="prescription", jurisdiction=["cc"], page_size=5)

    assert results is not None


def test_search_with_publication_filter(api):
    """Test une recherche filtrée par niveau de publication"""

    results = api.search(query="cassation", publication=["b"], page_size=3)  # Bulletin

    assert results is not None


def test_search_with_solution_filter(api):
    """Test une recherche filtrée par solution"""

    results = api.search(query="recours", solution=["rejet"], page_size=5)

    assert results is not None


def test_search_with_sort_date(api):
    """Test une recherche triée par date"""

    results = api.search(query="propriété", sort="date", order="desc", page_size=5)

    assert results is not None


def test_search_with_sort_score(api):
    """Test une recherche triée par pertinence"""

    results = api.search(query="préjudice", sort="score", order="desc", page_size=5)

    assert results is not None


def test_search_pagination(api):
    """Test la pagination des résultats"""

    # Première page
    results_page1 = api.search(query="contrat", page=0, page_size=3)

    # Deuxième page
    results_page2 = api.search(query="contrat", page=1, page_size=3)

    assert results_page1 is not None
    assert results_page2 is not None

    # Vérifier que les résultats sont différents (si disponibles)
    if len(results_page1) > 0 and len(results_page2) > 0:
        id_page1 = results_page1[0].get("id")
        id_page2 = results_page2[0].get("id")
        if id_page1 and id_page2:
            assert id_page1 != id_page2, "Les résultats des deux pages doivent être différents"


def test_search_with_resolve_references(api):
    """Test une recherche avec résolution des références"""

    results = api.search(query="divorce", resolve_references=True, page_size=3)

    assert results is not None


def test_search_particular_interest(api):
    """Test une recherche filtrée par intérêt particulier"""

    results = api.search(query="jurisprudence", particularInterest=True, page_size=5)

    assert results is not None


def test_search_with_multiple_filters(api):
    """Test une recherche avec plusieurs filtres combinés"""

    results = api.search(
        query="responsabilité",
        type=["arret"],
        chamber=["allciv"],
        date_start="2020-01-01",
        date_end="2023-12-31",
        sort="date",
        order="desc",
        page_size=5,
    )

    assert results is not None


def test_search_empty_query(api):
    """Test une recherche sans query (devrait retourner résultats vides selon spec)"""

    results = api.search(page_size=5)

    assert results is not None
    # Selon la spec, une recherche sans query retourne un résultat vide
    # Mais l'API peut quand même retourner une structure de données


def test_search_invalid_page_size(api):
    """Test qu'une erreur est levée pour page_size > 50"""

    with pytest.raises(ValueError, match="page_size ne peut pas dépasser 50"):
        api.search(query="test", page_size=100)


def test_search_invalid_operator(api):
    """Test qu'une erreur est levée pour un opérateur invalide"""

    with pytest.raises(ValueError, match="operator doit être"):
        api.search(query="test", operator="invalid")


def test_search_invalid_sort(api):
    """Test qu'une erreur est levée pour un tri invalide"""

    with pytest.raises(ValueError, match="sort doit être"):
        api.search(query="test", sort="invalid")


def test_search_invalid_order(api):
    """Test qu'une erreur est levée pour un ordre invalide"""

    with pytest.raises(ValueError, match="order doit être"):
        api.search(query="test", order="invalid")


def test_decision_with_resolve_references(api):
    """Test la récupération d'une décision avec références résolues"""

    # Obtenir un ID valide
    search_results = api.search(query="contrat", page_size=1)

    if search_results and "results" in search_results and len(search_results["results"]) > 0:
        decision_id = search_results["results"][0].get("id")
        if decision_id:
            decision = api.decision(decision_id, resolve_references=True)
            assert decision is not None


def test_decision_with_query_highlight(api):
    """Test la récupération d'une décision avec surlignage de termes"""

    # Obtenir un ID valide
    search_results = api.search(query="divorce", page_size=1)

    if search_results and "results" in search_results and len(search_results["results"]) > 0:
        decision_id = search_results["results"][0].get("id")
        if decision_id:
            decision = api.decision(decision_id, query="divorce", operator="or")
            assert decision is not None


def test_decision_empty_id(api):
    """Test qu'une erreur est levée si l'ID est vide"""

    with pytest.raises(ValueError, match="L'identifiant de la décision est obligatoire"):
        api.decision("")


def test_decision_invalid_operator(api):
    """Test qu'une erreur est levée pour un opérateur invalide dans decision()"""

    with pytest.raises(ValueError, match="operator doit être"):
        api.decision("test_id", query="test", operator="invalid")


def test_taxonomy_jurisdiction(api):
    """Test la récupération de la taxonomie des juridictions"""

    jurisdictions = api.taxonomy("jurisdiction")

    assert jurisdictions is not None
    assert isinstance(jurisdictions, (dict, list))


def test_taxonomy_chamber(api):
    """Test la récupération de la taxonomie des chambres"""

    chambers = api.taxonomy("chamber")

    assert chambers is not None


def test_taxonomy_type(api):
    """Test la récupération de la taxonomie des types de décision"""

    types = api.taxonomy("type")

    assert types is not None


def test_taxonomy_publication(api):
    """Test la récupération de la taxonomie des niveaux de publication"""

    publications = api.taxonomy("publication")

    assert publications is not None


def test_taxonomy_solution(api):
    """Test la récupération de la taxonomie des solutions"""

    solutions = api.taxonomy("solution")

    assert solutions is not None


def test_taxonomy_field(api):
    """Test la récupération de la taxonomie des champs"""

    fields = api.taxonomy("field")

    assert fields is not None


def test_taxonomy_with_key(api):
    """Test la récupération d'un intitulé par clé"""

    result = api.taxonomy("jurisdiction", key="cc")

    assert result is not None
    # Devrait retourner quelque chose comme {"key": "cc", "value": "Cour de cassation"}


def test_taxonomy_with_value(api):
    """Test la récupération d'une clé par intitulé"""

    result = api.taxonomy("jurisdiction", value="cour de cassation")

    assert result is not None


def test_taxonomy_with_context(api):
    """Test la récupération d'une taxonomie avec contexte"""

    chambers_cc = api.taxonomy("chamber", context_value="cc")

    assert chambers_cc is not None


def test_taxonomy_key_and_value_mutually_exclusive(api):
    """Test que key et value sont mutuellement exclusifs"""

    with pytest.raises(ValueError, match="mutuellement exclusifs"):
        api.taxonomy("jurisdiction", key="cc", value="cour de cassation")


def test_taxonomy_key_requires_id(api):
    """Test que key nécessite taxonomy_id"""

    with pytest.raises(ValueError, match="taxonomy_id' est requis"):
        api.taxonomy(key="cc")


def test_taxonomy_value_requires_id(api):
    """Test que value nécessite taxonomy_id"""

    with pytest.raises(ValueError, match="taxonomy_id' est requis"):
        api.taxonomy(value="cour de cassation")


if __name__ == "__main__":
    # Permet d'exécuter directement le fichier pour des tests rapides
    print("Exécution des tests JudiLibre...")

    # Créer une instance unique de l'API pour tous les tests
    api_instance = JudiLibreAPI(sandbox=True)

    print("\nTest 1: Initialisation")
    test_init_sandbox(api_instance)
    print("✓ Réussi")

    print("\nTest 2: Obtention du token")
    test_get_access_token(api_instance)
    print("✓ Réussi")

    print("\nTest 3: Recherche simple")
    test_search_simple(api_instance)
    print("✓ Réussi")

    print("\nTest 4: Recherche avec filtres de date")
    test_search_with_date_range(api_instance)
    print("✓ Réussi")

    print("\n✓ Tous les tests de base sont réussis!")
    print("\nPour exécuter tous les tests avec pytest:")
    print("  pytest test_api_judilibre.py -v")
