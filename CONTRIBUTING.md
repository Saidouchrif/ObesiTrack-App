# 🤝 Guide de Contribution - ObesiTrack

Merci de votre intérêt à contribuer au projet ObesiTrack ! Ce guide vous aidera à comprendre comment contribuer efficacement.

## 📋 Table des Matières

- [🎯 Comment Contribuer](#-comment-contribuer)
- [🛠️ Configuration de l'Environnement](#️-configuration-de-lenvironnement)
- [📝 Standards de Code](#-standards-de-code)
- [🧪 Tests](#-tests)
- [📚 Documentation](#-documentation)
- [🔄 Processus de Pull Request](#-processus-de-pull-request)
- [🐛 Signaler un Bug](#-signaler-un-bug)
- [✨ Proposer une Fonctionnalité](#-proposer-une-fonctionnalité)

## 🎯 Comment Contribuer

### Types de Contributions

- 🐛 **Correction de bugs**
- ✨ **Nouvelles fonctionnalités**
- 📚 **Amélioration de la documentation**
- 🧪 **Tests**
- 🎨 **Amélioration de l'interface utilisateur**
- ⚡ **Optimisation des performances**

## 🛠️ Configuration de l'Environnement

### Prérequis

- Python 3.11+
- Docker et Docker Compose
- Git
- MongoDB (optionnel, Docker fourni)

### Installation

1. **Fork et Clone**
   ```bash
   git clone https://github.com/Saidouchrif/ObesiTrack-App.git
   cd ObesiTrack-App
   ```

2. **Configuration Python**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configuration Pre-commit**
   ```bash
   pre-commit install
   ```

4. **Démarrage avec Docker**
   ```bash
   docker-compose up --build
   ```

## 📝 Standards de Code

### Python

- **Style**: Black (longueur de ligne: 127 caractères)
- **Imports**: isort
- **Linting**: Flake8
- **Types**: MyPy (optionnel)

### Structure des Fichiers

```
ObesiTrack-App/
├── App/
│   ├── Back-end/          # API FastAPI
│   ├── Front-end/         # Interface utilisateur
│   └── models/           # Modèles de données
├── ModelAi/              # Modèle ML et API
├── tests/                # Tests
├── .github/              # GitHub Actions et templates
└── docs/                 # Documentation
```

### Conventions de Nommage

- **Variables**: `snake_case`
- **Fonctions**: `snake_case`
- **Classes**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Fichiers**: `snake_case.py`

## 🧪 Tests

### Exécution des Tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest App/Back-end/tests/
pytest ModelAi/tests/

# Tests avec couverture
pytest --cov=App --cov=ModelAi

# Tests de performance
pytest tests/performance/ -m performance
```

### Écriture de Tests

- Utilisez des noms descriptifs
- Un test par fonctionnalité
- Tests unitaires et d'intégration
- Mocks pour les dépendances externes

Exemple :
```python
def test_user_authentication_success():
    """Test d'authentification utilisateur réussie"""
    # Arrange
    user_data = {"email": "test@example.com", "password": "password123"}
    
    # Act
    response = client.post("/login", json=user_data)
    
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## 📚 Documentation

### Documentation du Code

- Docstrings pour toutes les fonctions publiques
- Commentaires pour la logique complexe
- Type hints quand possible

Exemple :
```python
def predict_obesity(data: PredictionData) -> PredictionResult:
    """
    Prédit le niveau d'obésité basé sur les données utilisateur.
    
    Args:
        data: Données de prédiction utilisateur
        
    Returns:
        Résultat de la prédiction avec probabilités
        
    Raises:
        ValidationError: Si les données sont invalides
    """
    # Implementation...
```

### Documentation des APIs

- Utilisez les docstrings FastAPI
- Exemples de requêtes/réponses
- Codes d'erreur documentés

## 🔄 Processus de Pull Request

### 1. Créer une Branche

```bash
git checkout -b feature/nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

### 2. Développement

- Faites des commits atomiques
- Messages de commit clairs
- Tests pour les nouvelles fonctionnalités

### 3. Tests Locaux

```bash
# Linting
black --check .
isort --check-only .
flake8 .

# Tests
pytest

# Tests Docker
docker-compose up --build
```

### 4. Pull Request

- Utilisez le template fourni
- Description claire des changements
- Screenshots si applicable
- Tests passants

### 5. Review

- Répondez aux commentaires
- Faites les modifications demandées
- Gardez la PR à jour

## 🐛 Signaler un Bug

Utilisez le template d'issue pour les bugs :

1. Vérifiez que le bug n'existe pas déjà
2. Utilisez le template `bug_report.md`
3. Fournissez des étapes de reproduction
4. Incluez l'environnement et les versions

## ✨ Proposer une Fonctionnalité

Utilisez le template d'issue pour les fonctionnalités :

1. Vérifiez que la fonctionnalité n'existe pas déjà
2. Utilisez le template `feature_request.md`
3. Décrivez le problème et la solution
4. Incluez des maquettes si applicable

## 📋 Checklist de Contribution

Avant de soumettre une PR, vérifiez :

- [ ] Code formaté avec Black
- [ ] Imports organisés avec isort
- [ ] Pas d'erreurs Flake8
- [ ] Tests passants
- [ ] Documentation mise à jour
- [ ] Messages de commit clairs
- [ ] PR basée sur la branche `dev`

## 🏷️ Labels et Milestones

### Labels Utilisés

- `bug`: Correction de bug
- `enhancement`: Nouvelle fonctionnalité
- `documentation`: Documentation
- `tests`: Tests
- `dependencies`: Mise à jour de dépendances
- `good first issue`: Bon pour débuter
- `help wanted`: Aide demandée

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Saidouchrif/ObesiTrack-App/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Saidouchrif/ObesiTrack-App/discussions)
- **Email**: admin@obesitrack.com

## 📄 Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que le projet.

---

**Merci de contribuer à ObesiTrack ! 🎉**

Repository: https://github.com/Saidouchrif/ObesiTrack-App.git
