# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs

# Exposer les ports
EXPOSE 7777 8000

# Script de démarrage pour gérer les deux services
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Commande par défaut
CMD ["/app/start.sh"]