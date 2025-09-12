# Dockerfile pour Hugging Face Spaces
# Documentation: https://huggingface.co/docs/hub/spaces-sdks-docker

FROM python:3.11

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Définir le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copier tout le code de l'application
COPY --chown=user . /app

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs

# Exposer le port 7860 (requis par Hugging Face Spaces)
EXPOSE 7860

# Variables d'environnement
ENV PYTHONPATH=/app
ENV API_HOST=0.0.0.0
ENV API_PORT=7860
ENV ML_API_PORT=8000

# Commande par défaut
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]