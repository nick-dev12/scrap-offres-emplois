FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    python3-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Configuration des variables d'environnement pour mysqlclient
ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mysql"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient"

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copie du reste du code de l'application
COPY . .

# Exposition du port
EXPOSE 8000

# Définir le répertoire de travail sur le répertoire du projet
WORKDIR /app/projet

# Commande par défaut pour démarrer l'application en mode développement
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 