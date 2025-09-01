# -----------------------------
# Étape 1 : Base Python
# -----------------------------
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer dépendances système (Postgres client, build tools si besoin)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Étape 2 : Dépendances Python
# -----------------------------
# Copier requirements en premier pour profiter du cache Docker
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Étape 3 : Copier le code
# -----------------------------
COPY . .

# -----------------------------
# Étape 4 : Lancer l’application
# -----------------------------
EXPOSE 8000

# Commande de démarrage avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
