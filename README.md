# 🏛️ Serveur MCP Droit Français

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/jmtanguy/DroitFrancaisMCP/releases)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io/)

Ce projet a pour objectif d’explorer l’intégration d’outils dans **Claude Desktop** via le protocole **Model Context Protocol (MCP)**.

Il s’inscrit dans une démarche d’expérimentation et de validation visant à comprendre comment l’orchestration d’outils peut améliorer la fiabilité, la pertinence et l’efficacité des modèles de langage (LLM) lorsqu’ils traitent des données techniques.

Dans ce cadre, l’accent est mis sur l’accès à des données juridiques fiables issues de sources officielles.

Le serveur MCP développé ici fournit une interface unifiée pour interroger les API publiques du droit français, notamment :

- Légifrance – pour la législation, les codes, les lois et les décrets
- JudiLibre – pour la jurisprudence et les décisions judiciaires

Grâce à ce serveur, il devient possible de rechercher et de consulter :

- 📖 Les codes juridiques français (Code civil, Code pénal, Code du travail, etc.)
- 📜 Les lois, ordonnances, décrets et arrêtés
- ⚖️ La jurisprudence de toutes les juridictions françaises
- 📰 Le Journal Officiel de la République Française (JORF)
- 🤝 Les conventions collectives
- 🏛️ Les décisions du Conseil d'État, de la Cour de cassation et des tribunaux

---

## 📋 Table des matières

- [Prérequis](#-prérequis)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Outils disponibles](#outils-disponibles)
- [Architecture](#architecture)
- [Tests](#-tests)
- [Licence](#-licence)

---

## 🔑 Prérequis

### 1. Accès à l'API PISTE

**IMPORTANT** : Pour utiliser ce serveur, vous devez obligatoirement obtenir des accès aux API publiques via le site officiel **[PISTE](https://piste.gouv.fr/)**.

Afin de valider l'accès aux API, vous devez également valider les conditions d'utilisations pour les API Légifrance et Judilibre.

#### Comment obtenir vos accès

1. **Créer un compte** sur [piste.gouv.fr](https://piste.gouv.fr/)
2. **Demander l'accès** aux API suivantes :
   - **API Légifrance** : Recherche et consultation des textes juridiques
   - **API JudiLibre** : Recherche et consultation des décisions de justice
3. **Récupérer vos identifiants** :
   - `CLIENT_ID` : Identifiant client unique
   - `CLIENT_SECRET` : Clé secrète d'authentification

> 💡 **Note** : Les API PISTE sont gratuites mais nécessitent une inscription préalable. Comptez quelques jours pour l'activation de votre compte.

### 2. Système

- **Python 3.8+** (version recommandée : 3.10+)
- **pip** pour la gestion des paquets
- **Git** pour cloner le dépôt
- **Claude Desktop** ou **Cursor** (pour l'intégration MCP)

---

## ✨ Fonctionnalités

### 🔍 Recherche Légifrance

- **Recherche avancée** dans tous les fonds juridiques français
- **Filtres puissants** : par nature, date, juridiction, ministère, etc.
- **Consultation d'articles** : texte intégral avec métadonnées complètes
- **Multi-fonds** : codes, lois, JORF, jurisprudence, conventions collectives

### ⚖️ Recherche JudiLibre

- **Recherche de jurisprudence** dans toutes les juridictions françaises
- **Filtres contextuels** : juridiction, chambre, localisation, solution, thème
- **Texte intégral** des décisions avec zones structurées
- **Taxonomie complète** : accès aux listes de valeurs valides (chambres, formations, thèmes)

### 🛠️ Fonctionnalités techniques

- **Authentification OAuth 2.0** sécurisée
- **Gestion automatique des tokens**
- **Logging détaillé** pour le débogage
- **Mode Sandbox et Production**
- **Validation des paramètres**
- **Gestion d'erreurs**

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/jmtanguy/DroitFrancaisMCP.git
cd DroitFrancaisMCP
```

Ou télécharger le ZIP de ce projet.

### 2. Installation

Exécuter le script d’installation correspondant à votre système d’exploitation :

- Windows : install.ps1
- macOS / Linux : install.sh

Ces scripts effectuent automatiquement les opérations suivantes :

- 📦 Création d’un environnement virtuel Python
- 🔽 Installation de l’ensemble des dépendances nécessaires
- ⚙️ Configuration du client Claude Desktop pour qu’il utilise ce serveur MCP

---

## ⚙️ Configuration {#configuration}

### 1. Créer le fichier d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env
```

### 2. Remplir vos identifiants PISTE

Éditez le fichier `.env` avec vos vraies valeurs :

```bash
# Identifiants API PISTE Production
PISTE_CLIENT_ID=votre_client_id_production_ici
PISTE_CLIENT_SECRET=votre_client_secret_production_ici

# Identifiants API PISTE Sandbox (optionnel pour les tests)
PISTE_SANDBOX_CLIENT_ID=votre_client_id_sandbox_ici
PISTE_SANDBOX_CLIENT_SECRET=votre_client_secret_sandbox_ici
```

> ⚠️ **SÉCURITÉ** : Le fichier `.env` contient vos secrets et ne doit **JAMAIS** être commité dans Git !

### 3. Configuration des clients MCP

#### Configuration Claude Desktop

Pour utiliser le serveur avec Claude Desktop, vérifier cette configuration dans :

**macOS/Linux** : `~/.config/claude-desktop/claude_desktop_config.json`
**Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "/chemin/absolu/vers/DroitFrancaisMCP/.venv/bin/python3",
      "args": ["/chemin/absolu/vers/DroitFrancaisMCP/droit_francais_MCP.py"]
    }
  }
}
```

> 💡 **Conseil** : Remplacez `/chemin/absolu/vers/` par le chemin complet vers votre répertoire.

#### Configuration Cursor

Pour utiliser le serveur avec Cursor, ajoutez cette configuration dans votre fichier de configuration MCP (généralement `~/.cursor/mcp.json` ou dans les paramètres de Cursor) :

```json
{
  "mcpServers": {
    "DroitFrancaisMCP": {
      "command": "<PATH_TO_DroitFrancaisMCP>/.venv/bin/python3",
      "args": [
        "-u",
        "<PATH_TO_DroitFrancaisMCP>/droit_francais_MCP.py"
      ],
      "cwd": "<PATH_TO_DroitFrancaisMCP>",
      "env": {
        "PYTHONPATH": "<PATH_TO_DroitFrancaisMCP>",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      },
      "envFile": "<PATH_TO_ENV_FILE>",
      "description": "MCP server for French legal research (Légifrance, JudiLibre)",
      "enabled": true
    }
  }
}
```

> 💡 **Remplacez** :
>
> - `<PATH_TO_DroitFrancaisMCP>` par le chemin complet vers votre répertoire DroitFrancaisMCP
> - `<PATH_TO_ENV_FILE>` par le chemin complet vers votre fichier `.env` contenant les identifiants PISTE

---

## 📖 Utilisation {#utilisation}

### Démarrage du serveur

#### Avec Claude Desktop

1. Redémarrez Claude Desktop
2. Le serveur devrait apparaître dans la liste des serveurs MCP disponibles
3. Vous pouvez maintenant utiliser les outils directement dans Claude

#### Avec Cursor

1. Redémarrez Cursor
2. Le serveur devrait apparaître dans la liste des serveurs MCP disponibles
3. Vous pouvez maintenant utiliser les outils directement dans Cursor via le protocole MCP

## Exemples

Dans Claude Desktop ou Cursor, essayez :

```text
Recherche-moi les articles sur le mariage dans le Code civil
```

```text
Quels sont les arrêts récents de la Cour de cassation concernant le licenciement pour faute grave ?
````

```text
Donne-moi le texte complet de la loi n° 2021-1109 du 24 août 2021 sur le respect des principes de la République
```

Claude ou Cursor identifiera automatiquement les outils MCP adaptés pour interroger les sources officielles et vous présentera les résultats correspondants.

---

## 🛠️ Outils disponibles {#outils-disponibles}

### Légifrance

| Outil | Description |
|-------|-------------|
| `rechercher_droit_francais()` | Recherche avancée multi-critères dans tous les fonds juridiques |
| `obtenir_article()` | Récupération du texte intégral d'un article avec métadonnées |

### JudiLibre

| Outil | Description |
|-------|-------------|
| `rechercher_jurisprudence_judilibre()` | Recherche de décisions de justice avec filtres avancés |
| `obtenir_decision_judilibre()` | Récupération du texte intégral d'une décision |
| `obtenir_taxonomie_judilibre()` | Accès aux listes de valeurs valides (chambres, juridictions, etc.) |

---

## 🏗️ Architecture {#architecture}

```text
DroitFrancaisMCP/
├── droit_francais_MCP.py          # Serveur MCP principal
├── api_legifrance.py              # Client API Légifrance
├── api_legifrance_search_input.py # Modèles de requête Légifrance
├── api_legifrance_search_output.py# Modèles de réponse Légifrance
├── api_judilibre.py               # Client API JudiLibre
├── test_api_legifrance.py         # Tests Légifrance
├── test_api_judilibre.py          # Tests JudiLibre
├── requirements.txt               # Dépendances Python
├── .env.example                   # Template de configuration
└── README.md                      # Documentation
```

### Composants principaux

- **`droit_francais_MCP.py`** : Serveur MCP qui expose les outils via FastMCP
- **`api_legifrance.py`** : Client pour l'API Légifrance avec authentification OAuth
- **`api_judilibre.py`** : Client pour l'API JudiLibre avec gestion des tokens
- **Tests** : Scripts de validation des fonctionnalités

---

## 🧪 Tests

### Tester l'API Légifrance

```bash
python3 test_api_legifrance.py
```

### Tester l'API JudiLibre

```bash
python3 test_api_judilibre.py
```

### Avec pytest

```bash
pytest test_api_legifrance.py -v
pytest test_api_judilibre.py -v
```

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🔗 Liens utiles

- [Site officiel PISTE](https://piste.gouv.fr/) - Demande d'accès aux API
- [Model Context Protocol](https://modelcontextprotocol.io/) - Spécification MCP
- [Claude Desktop](https://claude.ai/download) - Application Claude
- [Cursor](https://cursor.sh/) - Éditeur de code avec support MCP

---

## 🤖 Développement avec IA

Ce projet a été développé avec l'assistance d'outils d'intelligence artificielle :

- **Claude** (Anthropic) - Assistant de développement et génération de code
- **GitHub Copilot** - Autocomplétion de code

L'utilisation de ces outils a permis d'accélérer le développement tout en maintenant une qualité de code élevée et une documentation complète. Tous les éléments générés ont été revus, validés et adaptés aux besoins spécifiques du projet.

> 💡 **Transparence** : Cette mention permet aux contributeurs et utilisateurs de comprendre le contexte de création du projet.

---

## 👤 Auteur

Jean-Michel Tanguy
