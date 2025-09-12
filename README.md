---
title: ObesiTrack - Prédiction d'Obésité par IA
emoji: 🏥
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# 🏥 ObesiTrack - Application de Prédiction d'Obésité

**ObesiTrack** est une application complète de prédiction d'obésité basée sur l'intelligence artificielle. Elle utilise des modèles de machine learning avancés pour prédire les catégories d'obésité et fournir des recommandations personnalisées.

## ✨ Fonctionnalités

- 🤖 **Prédiction d'obésité** avec 7 catégories différentes
- 🔐 **Authentification sécurisée** avec JWT
- 📊 **Dashboard interactif** avec statistiques
- 🎯 **Recommandations personnalisées** basées sur les résultats
- 📱 **Interface responsive** adaptée à tous les écrans

## 🚀 Utilisation

1. **Accédez à l'interface** via l'URL du Space
2. **Créez un compte** ou connectez-vous
3. **Remplissez le formulaire** avec vos informations
4. **Consultez votre prédiction** et les recommandations

## 📊 Catégories d'Obésité

| Catégorie | Description | Niveau de risque |
|-----------|-------------|------------------|
| Insufficient_Weight | Poids insuffisant | Faible |
| Normal_Weight | Poids normal | Très faible |
| Overweight_Level_I | Surpoids niveau I | Modéré |
| Overweight_Level_II | Surpoids niveau II | Élevé |
| Obesity_Type_I | Obésité type I | Très élevé |
| Obesity_Type_II | Obésité type II | Critique |
| Obesity_Type_III | Obésité type III | Critique |

## 🛠️ Technologies

- **Backend**: FastAPI, Python 3.11
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **Base de données**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Déploiement**: Docker, Hugging Face Spaces

## 📈 API Endpoints

- `GET /` - Page d'accueil
- `POST /signup` - Inscription
- `POST /login` - Connexion
- `POST /predict` - Créer une prédiction
- `GET /dashboard` - Dashboard utilisateur
- `GET /docs` - Documentation API

## 🔒 Sécurité

- Authentification JWT
- Hachage des mots de passe avec bcrypt
- Validation des données avec Pydantic
- Protection CORS

## 👨‍💻 Développeur

**Said Ouchrif** - [GitHub](https://github.com/Saidouchrif)

## 📞 Support

- **Email**: saidouchrif16@gmail.com
- **GitHub**: [ObesiTrack-App](https://github.com/Saidouchrif/ObesiTrack-App)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**⭐ Si ce projet vous aide, n'hésitez pas à lui donner une étoile !**