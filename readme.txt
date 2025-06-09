==================================================================
COMMANDES LINUX UTILES POUR GÉRER VOTRE VPS
==================================================================

------------------------------------------------------------------
NAVIGATION ET EXPLORATION
------------------------------------------------------------------

# Afficher le répertoire de travail actuel
pwd

# Lister les fichiers et dossiers
ls                  # Liste simple
ls -l               # Liste détaillée (permissions, taille, date)
ls -la              # Liste détaillée incluant les fichiers cachés
ls -lh              # Liste détaillée avec tailles lisibles (Ko, Mo, Go)

# Se déplacer dans les répertoires
cd /chemin/vers/dossier    # Aller vers un dossier spécifique
cd ..                      # Remonter d'un niveau
cd ~                       # Aller dans votre répertoire personnel
cd /                       # Aller à la racine du système

# Rechercher des fichiers
find /chemin -name "nom_fichier"    # Rechercher un fichier par son nom
find /chemin -type f -size +100M    # Trouver les fichiers de plus de 100 Mo
grep -r "texte" /chemin             # Rechercher du texte dans les fichiers

------------------------------------------------------------------
GESTION DES FICHIERS ET DOSSIERS
------------------------------------------------------------------

# Créer des dossiers
mkdir nom_dossier                   # Créer un dossier
mkdir -p dossier1/dossier2/dossier3 # Créer une structure de dossiers

# Créer des fichiers
touch nom_fichier.txt               # Créer un fichier vide
echo "contenu" > nom_fichier.txt    # Créer un fichier avec du contenu
echo "plus de contenu" >> nom_fichier.txt  # Ajouter du contenu à un fichier

# Copier des fichiers et dossiers
cp fichier.txt destination/         # Copier un fichier
cp -r dossier/ destination/         # Copier un dossier et son contenu

# Déplacer/renommer des fichiers et dossiers
mv fichier.txt nouveau_nom.txt      # Renommer un fichier
mv fichier.txt /nouveau/chemin/     # Déplacer un fichier
mv dossier/ /nouveau/chemin/        # Déplacer un dossier

# Supprimer des fichiers et dossiers
rm fichier.txt                      # Supprimer un fichier
rm -f fichier.txt                   # Forcer la suppression sans confirmation
rm -r dossier/                      # Supprimer un dossier et son contenu
rm -rf dossier/                     # Forcer la suppression d'un dossier (ATTENTION!)

------------------------------------------------------------------
AFFICHAGE ET ÉDITION DE FICHIERS
------------------------------------------------------------------

# Afficher le contenu des fichiers
cat fichier.txt                     # Afficher tout le contenu
less fichier.txt                    # Afficher page par page (q pour quitter)
head -n 20 fichier.txt              # Afficher les 20 premières lignes
tail -n 20 fichier.txt              # Afficher les 20 dernières lignes
tail -f fichier.log                 # Suivre les ajouts à un fichier en temps réel

# Éditer des fichiers
nano fichier.txt                    # Éditeur simple (idéal pour débutants)
vim fichier.txt                     # Éditeur avancé (i pour insérer, :wq pour sauvegarder et quitter)
vi fichier.txt                      # Similaire à vim
pico fichier.txt                    # Alternative à nano

------------------------------------------------------------------
GESTION DES DROITS ET PERMISSIONS
------------------------------------------------------------------

# Changer le propriétaire
chown utilisateur:groupe fichier.txt    # Changer le propriétaire et le groupe
chown -R utilisateur:groupe dossier/    # Changer récursivement pour un dossier

# Changer les permissions
chmod 755 fichier.txt                   # Définir permissions (rwx r-x r-x)
chmod +x fichier.sh                     # Rendre un fichier exécutable
chmod -R 755 dossier/                   # Changer récursivement pour un dossier

------------------------------------------------------------------
COMPRESSION ET DÉCOMPRESSION
------------------------------------------------------------------

# Créer des archives
tar -czvf archive.tar.gz dossier/       # Créer une archive compressée
zip -r archive.zip dossier/             # Créer une archive ZIP

# Extraire des archives
tar -xzvf archive.tar.gz                # Extraire une archive tar.gz
unzip archive.zip                       # Extraire une archive ZIP

------------------------------------------------------------------
GESTION DES PROCESSUS
------------------------------------------------------------------

# Afficher les processus
ps aux                                  # Afficher tous les processus
top                                     # Afficher les processus en temps réel
htop                                    # Version améliorée de top (à installer)

# Gérer les processus
kill PID                                # Arrêter un processus par son ID
killall nom_processus                   # Arrêter tous les processus du même nom
nohup commande &                        # Exécuter une commande qui continue après déconnexion
screen                                  # Gestionnaire de sessions (Ctrl+a d pour détacher)

------------------------------------------------------------------
RÉSEAU
------------------------------------------------------------------

# Informations réseau
ifconfig                                # Afficher les interfaces réseau
ip addr show                            # Alternative moderne à ifconfig
netstat -tulpn                          # Afficher les connexions et ports ouverts
ss -tulpn                               # Alternative moderne à netstat

# Tests réseau
ping domaine.com                        # Tester la connectivité
curl -I domaine.com                     # Vérifier les en-têtes HTTP
wget http://domaine.com/fichier         # Télécharger un fichier

------------------------------------------------------------------
GESTION DU SYSTÈME
------------------------------------------------------------------

# Informations système
df -h                                   # Espace disque disponible
du -sh /chemin                          # Taille d'un dossier
free -m                                 # Mémoire disponible
uname -a                                # Informations sur le système

# Gestion des utilisateurs
adduser nom_utilisateur                 # Ajouter un utilisateur
usermod -aG groupe utilisateur          # Ajouter un utilisateur à un groupe
passwd utilisateur                      # Changer le mot de passe

# Mises à jour (Debian/Ubuntu)
apt update                              # Mettre à jour la liste des paquets
apt upgrade                             # Mettre à jour les paquets installés
apt install nom_paquet                  # Installer un paquet

# Mises à jour (CentOS/RHEL)
yum update                              # Mettre à jour les paquets
yum install nom_paquet                  # Installer un paquet

------------------------------------------------------------------
DOCKER (si installé)
------------------------------------------------------------------

# Commandes Docker de base
docker ps                               # Lister les conteneurs en cours d'exécution
docker ps -a                            # Lister tous les conteneurs
docker images                           # Lister les images
docker-compose up -d                    # Démarrer les services en arrière-plan
docker-compose down                     # Arrêter les services
docker logs nom_conteneur               # Voir les logs d'un conteneur

------------------------------------------------------------------
ASTUCES
------------------------------------------------------------------

# Historique des commandes
history                                 # Afficher l'historique des commandes
!123                                    # Exécuter la commande n°123 de l'historique

# Combinaisons de touches utiles
Ctrl+C                                  # Arrêter une commande en cours
Ctrl+Z                                  # Suspendre une commande
Ctrl+D                                  # Se déconnecter (équivalent à exit)
Ctrl+L                                  # Effacer l'écran (équivalent à clear)
Ctrl+R                                  # Rechercher dans l'historique des commandes

# Alias (raccourcis de commandes)
alias ll='ls -la'                       # Créer un alias temporaire
# Pour un alias permanent, ajoutez-le à ~/.bashrc

# Aide
man commande                            # Afficher le manuel d'une commande
commande --help                         # Afficher l'aide d'une commande 