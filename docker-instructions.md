# 🐳 Instructions Docker pour ObesiTrack

## 🚀 Démarrage rapide

### 1. Construction et démarrage
```bash
# Construire et démarrer tous les services
docker-compose up --build

# Ou en arrière-plan
docker-compose up --build -d
```

### 2. Accès aux services
- **Application principale**: http://localhost:7777
- **API ML**: http://localhost:8000
- **Documentation API**: http://localhost:7777/docs
- **MongoDB Express**: http://localhost:8081 (admin/admin123)

### 3. Arrêt des services
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

## 🔧 Commandes utiles

### Logs
```bash
# Voir les logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f obesitrack
docker-compose logs -f mongo
```

### Accès aux conteneurs
```bash
# Accéder au conteneur principal
docker exec -it obesitrack-app bash

# Accéder à MongoDB
docker exec -it obesitrack-mongo mongosh
```

### Redémarrage
```bash
# Redémarrer un service spécifique
docker-compose restart obesitrack

# Redémarrer tous les services
docker-compose restart
```

## 🗄️ Base de données

### Utilisateur admin par défaut
- **Email**: admin@obesitrack.com
- **Mot de passe**: motdepasse123
- **Rôle**: admin

### Connexion MongoDB
- **Host**: localhost
- **Port**: 27017
- **Database**: obesitrack

## 🐛 Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Vérifier les ports utilisés
   netstat -tulpn | grep :7777
   netstat -tulpn | grep :8000
   ```

2. **Problème de permissions**
   ```bash
   # Donner les permissions au script de démarrage
   chmod +x start.sh
   ```

3. **Erreur de connexion MongoDB**
   ```bash
   # Vérifier que MongoDB est démarré
   docker-compose logs mongo
   ```

### Nettoyage complet
```bash
# Supprimer tout (conteneurs, images, volumes)
docker-compose down -v --rmi all
docker system prune -a
```

## 📊 Monitoring

### Vérification de l'état
```bash
# État des services
docker-compose ps

# Utilisation des ressources
docker stats
```

### Health checks
Les services incluent des health checks automatiques pour vérifier leur état.

## 🔒 Sécurité

### Variables d'environnement
Modifiez les variables sensibles dans `docker-compose.yml`:
- `SECRET_KEY`
- `ME_CONFIG_BASICAUTH_PASSWORD`

### Production
Pour la production, utilisez des secrets Docker et des certificats SSL.
