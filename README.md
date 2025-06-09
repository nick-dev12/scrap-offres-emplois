# Application Django Dockerisée

Ce projet est configuré pour fonctionner avec Docker et Docker Compose.

## Fichiers Docker créés

1. **Dockerfile** - Configure l'environnement Python avec toutes les dépendances nécessaires.
2. **docker-compose.yml** - Définit les services pour l'application complète (web, db, redis, celery, celery-beat).
3. **docker-compose.dev.yml** - Version simplifiée pour le développement (uniquement le service web).
4. **.dockerignore** - Exclut les fichiers inutiles lors de la construction de l'image.
5. **docker-entrypoint.sh** - Script qui attend que la base de données soit prête, exécute les migrations et collecte les fichiers statiques.
6. **requirements-docker.txt** - Dépendances minimales pour l'image Docker.

## Prérequis

- Docker
- Docker Compose

## Instructions d'utilisation

### Option 1: Mode développement simplifié

Pour démarrer uniquement le service web sans dépendances de base de données:

```bash
docker-compose -f docker-compose.dev.yml up
```

### Option 2: Mode complet avec tous les services

Pour démarrer tous les services (web, db, redis, celery):

```bash
docker-compose up
```

### Option 3: Exécuter directement le conteneur

```bash
docker run -p 8000:8000 -v ${PWD}:/app --workdir /app/projet mon-django-app python manage.py runserver 0.0.0.0:8000
```

## Configuration de la base de données

Par défaut, l'application est configurée pour utiliser MySQL:

```
DATABASE_URL=mysql://django:django_password@db/django_db
```

Vous devrez peut-être modifier les paramètres de connexion dans les fichiers de configuration Django.

## Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes:

```
DEBUG=1
SECRET_KEY=votre_cle_secrete
DATABASE_URL=mysql://django:django_password@db/django_db
CELERY_BROKER_URL=redis://redis:6379/0
```

## Commandes utiles

### Construire l'image Docker

```bash
docker build -t mon-django-app .
```

### Exécuter des migrations

```bash
docker-compose exec web python manage.py migrate
```

### Créer un superutilisateur

```bash
docker-compose exec web python manage.py createsuperuser
```

### Accéder au shell Django

```bash
docker-compose exec web python manage.py shell
```

### Voir les logs

```bash
docker-compose logs
```

## Dépannage

Si vous rencontrez des problèmes de connexion réseau lors du téléchargement des images Docker, essayez:

1. Vérifier la connexion Internet
2. Configurer les paramètres de proxy Docker si nécessaire
3. Utiliser l'option `--default-timeout=100` lors de l'installation des packages pip

## Structure des services

- **web**: Application Django principale
- **db**: Base de données MySQL
- **redis**: Broker pour Celery
- **celery**: Worker Celery pour les tâches asynchrones
- **celery-beat**: Planificateur Celery pour les tâches périodiques

## Personnalisation

Vous pouvez modifier les fichiers Docker et docker-compose.yml selon vos besoins spécifiques. 