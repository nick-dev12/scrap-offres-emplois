# Guide de déploiement d'une application Django avec Gunicorn et Nginx

Ce guide détaille les étapes pour déployer une application Django sur un serveur VPS en utilisant Gunicorn comme serveur d'application et Nginx comme serveur proxy inverse, avec configuration d'un domaine ou sous-domaine.

## Table des matières

1. [Prérequis](#prérequis)
2. [Étape 1 : Préparation du serveur](#étape-1--préparation-du-serveur)
3. [Étape 2 : Configuration de la base de données](#étape-2--configuration-de-la-base-de-données)
4. [Étape 3 : Déploiement de l&#39;application Django](#étape-3--déploiement-de-lapplication-django)
5. [Étape 4 : Configuration de Gunicorn](#étape-4--configuration-de-gunicorn) b
6. [Étape 5 : Configuration de Nginx](#étape-5--configuration-de-nginx)
7. [Étape 6 : Configuration du domaine](#étape-6--configuration-du-domaine)
8. [Étape 7 : Sécurisation avec SSL/TLS](#étape-7--sécurisation-avec-ssltls)
9. [Dépannage](#dépannage)
10. [Maintenance](#maintenance)

## Prérequis

- Un serveur VPS avec Ubuntu 20.04/22.04 ou une distribution Linux similaire
- Un nom de domaine ou sous-domaine pointant vers l'adresse IP de votre serveur
- Accès SSH au serveur avec privilèges sudo
- Application Django fonctionnelle en local

## Étape 1 : Préparation du serveur

### 1.1 Mise à jour du système

```bash
# Se connecter au serveur
ssh utilisateur@adresse_ip_du_serveur

# Mettre à jour la liste des paquets et le système
sudo apt update
sudo apt upgrade -y

# Installer les dépendances nécessaires
sudo apt install -y python3 python3-pip python3-dev python3-venv build-essential libpq-dev nginx git
```

### 1.2 Création d'un utilisateur dédié (optionnel mais recommandé)

```bash
# Créer un nouvel utilisateur
sudo adduser django_user

# Ajouter l'utilisateur au groupe sudo
sudo usermod -aG sudo django_user

# Changer pour le nouvel utilisateur
su - django_user
```

### 1.3 Configuration du pare-feu

```bash
# Installer et configurer UFW
sudo apt install -y ufw

# Autoriser SSH, HTTP et HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Activer le pare-feu
sudo ufw enable

# Vérifier le statut
sudo ufw status
```

## Étape 2 : Configuration de la base de données

### 2.1 Installation de PostgreSQL

```bash
# Installer PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Vérifier le statut du service
sudo systemctl status postgresql
```

### 2.2 Création de la base de données et de l'utilisateur

```bash
# Se connecter à PostgreSQL en tant qu'utilisateur postgres
sudo -u postgres psql

# Créer un utilisateur pour l'application Django
CREATE USER mon_utilisateur WITH PASSWORD 'mon_mot_de_passe';

# Créer une base de données
CREATE DATABASE ma_base_de_donnees;

# Accorder les privilèges à l'utilisateur
GRANT ALL PRIVILEGES ON DATABASE ma_base_de_donnees TO mon_utilisateur;

# Modifier les paramètres de l'utilisateur pour Django
ALTER ROLE mon_utilisateur SET client_encoding TO 'utf8';
ALTER ROLE mon_utilisateur SET default_transaction_isolation TO 'read committed';
ALTER ROLE mon_utilisateur SET timezone TO 'UTC';

# Quitter PostgreSQL
\q
```

### 2.3 Vérification de la connexion

```bash
# Tester la connexion à la base de données
psql -h localhost -U mon_utilisateur -d ma_base_de_donnees
# Entrez le mot de passe quand demandé

# Quitter PostgreSQL
\q
```

## Étape 3 : Déploiement de l'application Django

### 3.1 Clonage du dépôt Git

```bash
# Créer un répertoire pour l'application
mkdir -p /home/django_user/apps
cd /home/django_user/apps

# Cloner le dépôt Git
git clone https://github.com/votre-compte/votre-projet.git
cd votre-projet
```

### 3.2 Configuration de l'environnement virtuel

```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Installer Gunicorn
pip install gunicorn psycopg2-binary
```

### 3.3 Configuration des paramètres Django

```bash
# Créer un fichier .env pour les variables d'environnement
nano .env
```

Contenu du fichier .env :

```
DEBUG=False
SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,adresse_ip_du_serveur
DATABASE_URL=postgres://mon_utilisateur:mon_mot_de_passe@localhost:5432/ma_base_de_donnees
```

Modifier settings.py pour utiliser ces variables :

```bash
nano votre_projet/settings.py
```

Exemple de configuration dans settings.py :

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ...

DEBUG = os.getenv('DEBUG', 'False') == 'True'

SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ma_base_de_donnees'),
        'USER': os.getenv('DB_USER', 'mon_utilisateur'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'mon_mot_de_passe'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Configuration des fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 3.4 Migrations et fichiers statiques

```bash
# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Créer un superutilisateur (facultatif)
python manage.py createsuperuser
```

### 3.5 Test du serveur de développement

```bash
# Tester l'application avec le serveur de développement
python manage.py runserver 0.0.0.0:8000
```

Vérifiez que l'application fonctionne en accédant à `http://adresse_ip_du_serveur:8000` dans votre navigateur.

## Étape 4 : Configuration de Gunicorn

### 4.1 Test de Gunicorn

```bash
# Arrêter le serveur de développement (Ctrl+C)
# Tester Gunicorn
cd /home/django_user/apps/votre-projet
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 votre_projet.wsgi:application
```

Vérifiez que l'application fonctionne avec Gunicorn en accédant à `http://adresse_ip_du_serveur:8000`.

### 4.2 Création d'un fichier de service systemd pour Gunicorn

```bash
# Arrêter Gunicorn (Ctrl+C)
# Créer le fichier de service
sudo nano /etc/systemd/system/gunicorn.service
```

Contenu du fichier gunicorn.service :

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=django_user
Group=www-data
WorkingDirectory=/home/django_user/apps/votre-projet
ExecStart=/home/django_user/apps/votre-projet/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/django_user/apps/votre-projet/gunicorn.sock \
          votre_projet.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4.3 Activation du service Gunicorn

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Démarrer Gunicorn
sudo systemctl start gunicorn

# Activer le démarrage automatique
sudo systemctl enable gunicorn

# Vérifier le statut
sudo systemctl status gunicorn
```

### 4.4 Vérification du socket Gunicorn

```bash
# Vérifier que le socket a été créé
ls -la /home/django_user/apps/votre-projet/gunicorn.sock
```

## Étape 5 : Configuration de Nginx

### 5.1 Création de la configuration Nginx

```bash
# Créer le fichier de configuration
sudo nano /etc/nginx/sites-available/votre-projet
```

Contenu du fichier de configuration :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location = /favicon.ico { access_log off; log_not_found off; }
  
    location /static/ {
        root /home/django_user/apps/votre-projet;
    }
  
    location /media/ {
        root /home/django_user/apps/votre-projet;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django_user/apps/votre-projet/gunicorn.sock;
    }
}
```

### 5.2 Activation de la configuration

```bash
# Créer un lien symbolique
sudo ln -s /etc/nginx/sites-available/votre-projet /etc/nginx/sites-enabled/

# Vérifier la syntaxe de la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### 5.3 Vérification des permissions

```bash
# S'assurer que Nginx peut accéder aux fichiers
sudo usermod -a -G django_user www-data
sudo chmod 710 /home/django_user
sudo chmod 750 /home/django_user/apps
sudo chmod -R 750 /home/django_user/apps/votre-projet

# Vérifier les permissions des fichiers statiques
sudo chmod -R 755 /home/django_user/apps/votre-projet/staticfiles
sudo chmod -R 755 /home/django_user/apps/votre-projet/media
```

## Étape 6 : Configuration du domaine

### 6.1 Configuration DNS

Accédez au panneau de gestion DNS de votre registrar et créez les enregistrements suivants :

1. Enregistrement A pour le domaine principal :

   - Type: A
   - Nom: @ ou votre-domaine.com
   - Valeur: adresse_ip_du_serveur
2. Enregistrement A pour le sous-domaine www :

   - Type: A
   - Nom: www
   - Valeur: adresse_ip_du_serveur

### 6.2 Vérification de la propagation DNS

```bash
# Vérifier la propagation DNS
dig votre-domaine.com
dig www.votre-domaine.com

# Ou utiliser nslookup
nslookup votre-domaine.com
nslookup www.votre-domaine.com
```

La propagation DNS peut prendre jusqu'à 48 heures, mais généralement quelques heures suffisent.

## Étape 7 : Sécurisation avec SSL/TLS

### 7.1 Installation de Certbot

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Suivre les instructions à l'écran
```

### 7.2 Vérification du renouvellement automatique

```bash
# Tester le renouvellement automatique
sudo certbot renew --dry-run
```

### 7.3 Vérification de la configuration HTTPS

Accédez à `https://votre-domaine.com` dans votre navigateur et vérifiez que le site est sécurisé.

## Dépannage

### Vérification des journaux

```bash
# Journaux Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Journaux Gunicorn
sudo journalctl -u gunicorn

# Journaux Django (si configuré)
tail -f /home/django_user/apps/votre-projet/logs/django.log
```

### Problèmes courants et solutions

#### 1. Erreur 502 Bad Gateway

Vérifiez que :

- Le socket Gunicorn existe et a les bonnes permissions
- Le service Gunicorn est en cours d'exécution
- Les chemins dans la configuration Nginx sont corrects

```bash
# Redémarrer Gunicorn et Nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

#### 2. Fichiers statiques non chargés

Vérifiez que :

- Les chemins STATIC_ROOT et MEDIA_ROOT sont correctement définis
- Les permissions des répertoires sont correctes
- La configuration Nginx pour les fichiers statiques est correcte

```bash
# Vérifier les permissions
sudo chmod -R 755 /home/django_user/apps/votre-projet/staticfiles
```

#### 3. Problèmes de base de données

Vérifiez que :

- PostgreSQL est en cours d'exécution
- Les informations de connexion sont correctes
- L'utilisateur a les permissions nécessaires

```bash
# Vérifier le statut de PostgreSQL
sudo systemctl status postgresql

# Tester la connexion
psql -h localhost -U mon_utilisateur -d ma_base_de_donnees
```

#### 4. Erreur "Access denied for user" (MySQL/MariaDB)

Si vous utilisez MySQL ou MariaDB et rencontrez une erreur d'accès refusé comme:

```
Access denied for user 'utilisateur'@'adresse_ip' (using password: YES)
```

Voici comment résoudre ce problème:

```bash
# Se connecter à MySQL en tant qu'administrateur
sudo mysql -u root -p

# Créer l'utilisateur avec les permissions d'accès depuis n'importe quelle adresse IP
CREATE USER 'utilisateur'@'%' IDENTIFIED BY 'mot_de_passe';
GRANT ALL PRIVILEGES ON nom_base.* TO 'utilisateur'@'%';

# Ou permettre l'accès depuis une adresse IP spécifique
CREATE USER 'utilisateur'@'adresse_ip' IDENTIFIED BY 'mot_de_passe';
GRANT ALL PRIVILEGES ON nom_base.* TO 'utilisateur'@'adresse_ip';

# Appliquer les changements
FLUSH PRIVILEGES;

# Quitter MySQL
EXIT;
```

Vérifiez également que le fichier de configuration MySQL autorise les connexions distantes:

```bash
# Éditer le fichier de configuration MySQL
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Modifier la ligne bind-address de 127.0.0.1 à 0.0.0.0
# ou la commenter avec un #

# Redémarrer MySQL
sudo systemctl restart mysql
```

## Maintenance

### Mise à jour de l'application

```bash
# Se connecter au serveur
ssh django_user@adresse_ip_du_serveur

# Aller dans le répertoire du projet
cd /home/django_user/apps/votre-projet

# Activer l'environnement virtuel
source venv/bin/activate

# Tirer les dernières modifications
git pull

# Installer les nouvelles dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Redémarrer Gunicorn
sudo systemctl restart gunicorn
```

### Sauvegarde de la base de données

```bash
# Créer un répertoire pour les sauvegardes
mkdir -p /home/django_user/backups

# Sauvegarde PostgreSQL
pg_dump -U mon_utilisateur ma_base_de_donnees > /home/django_user/backups/backup_$(date +%Y%m%d).sql

# Sauvegarde MySQL
mysqldump -u mon_utilisateur -p ma_base_de_donnees > /home/django_user/backups/backup_$(date +%Y%m%d).sql

# Automatiser avec cron
echo "0 2 * * * pg_dump -U mon_utilisateur ma_base_de_donnees > /home/django_user/backups/backup_\$(date +\%Y\%m\%d).sql" | sudo tee -a /etc/cron.d/db_backup
```

### Surveillance du serveur

```bash
# Installer des outils de surveillance
sudo apt install -y htop

# Surveiller l'utilisation des ressources
htop

# Surveiller l'espace disque
df -h

# Surveiller les journaux système
sudo tail -f /var/log/syslog
```

---

Ce guide couvre les étapes essentielles pour déployer une application Django avec Gunicorn et Nginx sur un VPS. Adaptez les commandes et configurations selon vos besoins spécifiques et la structure de votre projet.
