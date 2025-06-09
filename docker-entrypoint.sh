#!/bin/bash

# Attendre que la base de données soit prête
echo "Attente de la base de données..."
python -c "
import sys
import time
import MySQLdb

start_time = time.time()
while True:
    try:
        MySQLdb.connect(
            host='db',
            user='django',
            passwd='django_password',
            db='django_db'
        )
        break
    except MySQLdb.OperationalError:
        if time.time() - start_time > 30:
            sys.exit('Échec de connexion à la base de données après 30 secondes')
        time.sleep(1)
    except Exception as e:
        print(f'Erreur de connexion: {e}')
        if time.time() - start_time > 10:
            print('Poursuite sans base de données...')
            break
        time.sleep(1)
"

# Vérifier si manage.py existe
if [ -f "/app/projet/manage.py" ]; then
    cd /app/projet

    # Appliquer les migrations
    echo "Application des migrations..."
    python manage.py migrate --noinput || echo "Échec des migrations, mais on continue..."

    # Collecter les fichiers statiques
    echo "Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput || echo "Échec de la collecte des fichiers statiques, mais on continue..."
else
    echo "manage.py non trouvé dans /app/projet"
    echo "Contenu du répertoire /app:"
    ls -la /app
    echo "Contenu du répertoire /app/projet (s'il existe):"
    ls -la /app/projet || echo "Le répertoire projet n'existe pas"
fi

# Exécuter la commande passée au conteneur
exec "$@" 