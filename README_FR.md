*Ce projet a été réalisé dans le cadre du cursus 42 par mbichet.*

# Call Me Maybe

## Description

Ce projet traite de l'appel de fonctions à partir de prompts en langage naturel en utilisant un modèle de langage. L'objectif est de générer des sorties structurées de type appel de fonction à partir de questions textuelles, en appliquant un décodage contraint pour limiter le modèle aux tokens attendus.

Le dépôt charge des données de prompts et des définitions de fonctions depuis des fichiers JSON, exécute un processus de décodage contrôlé pour générer le nom de la fonction et ses paramètres, puis écrit les résultats dans un fichier JSON de sortie.

## Instructions

### Prérequis

- Python 3.10 ou plus récent
- Dépendances listées dans `pyproject.toml` :
  - `pydantic`
  - `numpy`
  - `transformers`
  - `huggingface_hub`
  - `torch`

### Installation

```bash
python -m pip install pydantic numpy transformers huggingface_hub
```

### Exécution

Lancer le programme avec les fichiers d'entrée par défaut :

```bash
python -m src
```

Lancer avec des chemins JSON explicites :

```bash
python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json
```

## Ressources

- Documentation OpenAI Function Calling
- Documentation Hugging Face Transformers
- Documentation NumPy
- Documentation Pydantic
- Articles et tutoriels sur le décodage contraint et la génération guidée

### Utilisation de l'IA

L'IA a été utilisée pour aider à rédiger ce README et clarifier les choix de conception. Le code principal et la logique métier restent basés sur le dépôt et les décisions du projet.

## Explication de l'algorithme

L'approche de décodage contraint fonctionne de la manière suivante :

1. Charger les fichiers JSON de prompts et de définitions de fonctions.
2. Construire des ensembles de tokens autorisés pour les valeurs numériques et textuelles.
3. Encoder le prompt et les informations de fonction en séquences de tokens d'entrée.
4. Calculer les logits du modèle et n'autoriser que des tokens spécifiques à chaque étape de génération.
5. Identifier le nom de la fonction en comparant la sortie encodée avec les séquences de fonction attendues.
6. Une fois le nom de fonction déterminé, passer à l'extraction des paramètres et décoder les valeurs en respectant les masques autorisés.
7. Convertir la sortie finale en dictionnaire structuré contenant le nom de la fonction et les paramètres.

Cette méthode limite les sorties libres du modèle et augmente la probabilité d'obtenir un format structuré valide.

## Choix de conception

- `src/__main__.py` orchestre le flux principal et l'usage du modèle.
- `src/parsing.py` gère la lecture des arguments de la ligne de commande et l'ouverture des fichiers JSON.
- `src/output.py` parse les réponses du modèle et écrit le résultat final en JSON.
- Pydantic est utilisé pour encadrer les données du modèle et garantir la structure des objets.
- Le décodage contraint est appliqué au niveau des tokens pour forcer des sorties conformes.
- Des chemins JSON par défaut sont fournis, tout en permettant des chemins personnalisés via les arguments.

## Analyse de performance

- **Précision** : le décodage contraint augmente les chances d'une sortie au format correct, mais dépend du modèle et de la qualité des prompts.
- **Vitesse** : cette méthode est itérative et token par token, elle est donc plus lente qu'une génération en une seule passe.
- **Fiabilité** : la solution est plus fiable pour des sorties structurées lorsque les masques et le vocabulaire sont bien alignés, mais des cas limites restent possibles.

## Difficultés rencontrées

- Extraire de manière fiable le nom de la fonction et les paramètres depuis la sortie du modèle.
- Gérer les ensembles de tokens autorisés pour différentes catégories de valeurs.
- Définir un format de prompt clair pour contraindre le modèle à répondre sous forme d'appel de fonction.
- Maintenir une bonne compatibilité avec les typages Python et les règles de linting.

## Stratégie de tests

- Validation manuelle avec les fichiers JSON fournis dans `data/input`.
- Exécution du module avec les chemins par défaut et des chemins personnalisés.
- Vérifications statiques par compilation Python et validation de type.
- Contrôle du fichier de sortie `data/output/function_calling_results.json` produit.

## Exemple d'utilisation

Exécution par défaut :

```bash
python -m src
```

Exécution avec chemins explicites :

```bash
python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json
```

Le résultat attendu est un fichier JSON dans `data/output` contenant le prompt, le nom de la fonction et les paramètres extraits.

---

## Remarques

- Si le chemin de sortie ne se termine pas par `.json`, le programme renvoie une erreur de parsing.
- Le projet suppose que le modèle renvoie une réponse de type fonction incluant les sections `function:` et `parameters:`.
