import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
import re
import json
from django.utils import timezone
from ..models.offreEmploiSNModel import OffreEmploiSN
from django.db import transaction

logger = logging.getLogger(__name__)

def scrape_offre_emploi_sn():
    """
    Fonction principale pour scraper les offres d'emploi du site offre-emploi.sn
    en utilisant le système de navigation par onglets avec attributs data-page
    qui charge les offres dans un même conteneur sans changer d'URL
    """
    logger.info("Démarrage du scraping OffreEmploiSN")
    
    # Récupérer les offres existantes pour éviter les doublons
    existing_links = set(OffreEmploiSN.objects.values_list('lien_offre', flat=True))
    existing_titles = set(OffreEmploiSN.objects.values_list('titre', flat=True))
    
    logger.info(f"Nombre d'offres déjà en base: {len(existing_links)}")
    
    base_url = "https://offre-emploi.sn/offre-emploi-au-senegal/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'X-Requested-With': 'XMLHttpRequest'  # Important pour les requêtes AJAX
    }
    
    new_offers_count = 0
    existing_offers_count = 0
    consecutive_existing_count = 0
    max_consecutive_existing = 15  # Arrêter après 15 offres consécutives déjà existantes
    
    try:
        # Première étape: récupérer la page principale pour obtenir la structure de pagination
        logger.info(f"Récupération de la page principale: {base_url}")
        response = requests.get(base_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Erreur lors de la récupération de la page principale: {response.status_code}")
            return 0
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Déterminer le nombre total de pages à partir de la pagination
        pagination = soup.select_one('nav.job-manager-pagination')
        if not pagination:
            logger.warning("Pas de pagination trouvée, traitement de la page unique")
            page_numbers = [1]
        else:
            # Trouver tous les liens de pagination avec data-page
            page_links = pagination.select('li a[data-page]')
            page_numbers = []
            
            for link in page_links:
                data_page = link.get('data-page')
                if data_page and data_page.isdigit():
                    page_numbers.append(int(data_page))
            
            if not page_numbers:
                logger.warning("Pas de numéros de page trouvés, traitement de la page unique")
                page_numbers = [1]
        
        # Trier et dédupliquer les numéros de page
        page_numbers = sorted(set(page_numbers))
        max_page = max(page_numbers)
        
        logger.info(f"Pages détectées: {page_numbers}, max: {max_page}")
        
        # Traitement de la première page (déjà chargée)
        job_listings = soup.select('ul.job_listings li')
        logger.info(f"Nombre d'offres trouvées sur la page 1: {len(job_listings)}")
        
        if job_listings:
            processed_result = process_job_listings(job_listings, existing_links, existing_titles)
            new_offers_count += processed_result['new']
            existing_offers_count += processed_result['existing']
            
            # Mise à jour du compteur d'offres consécutives existantes
            if processed_result['new'] > 0:
                consecutive_existing_count = 0
            else:
                consecutive_existing_count += processed_result['existing']
        
        # Pour les pages suivantes, utiliser des requêtes AJAX directement vers le gestionnaire d'onglets
        for page in range(2, max_page + 1):
            # Si trop d'offres consécutives déjà existantes, on arrête
            if consecutive_existing_count >= max_consecutive_existing:
                logger.info(f"Arrêt du scraping après {consecutive_existing_count} offres consécutives déjà existantes")
                break
                
            logger.info(f"Traitement de l'onglet {page}")
            time.sleep(3)  # Pause entre les requêtes
            
            # Construction de la requête AJAX pour récupérer les offres de l'onglet
            ajax_url = "https://offre-emploi.sn/jm-ajax/get_listings/"
            
            # Paramètres pour la requête AJAX - simulation du clic sur l'onglet avec data-page
            form_data = {
                'page': str(page),
                'per_page': '10',
                'orderby': 'featured',
                'order': 'DESC',
                'show_pagination': 'true'
            }
            
            try:
                # Envoi de la requête POST pour simuler le clic sur l'onglet
                ajax_response = requests.post(ajax_url, headers=headers, data=form_data, timeout=30)
                
                if ajax_response.status_code != 200:
                    logger.error(f"Erreur lors de la requête AJAX pour l'onglet {page}: {ajax_response.status_code}")
                    continue
                
                # Analyser la réponse JSON
                try:
                    ajax_data = ajax_response.json()
                    
                    # Vérifier si la réponse contient du HTML
                    if not ajax_data.get('html'):
                        logger.warning(f"Pas de contenu HTML dans la réponse AJAX pour l'onglet {page}")
                        continue
                    
                    # Parser le HTML des offres
                    job_soup = BeautifulSoup(ajax_data['html'], 'html.parser')
                    job_listings = job_soup.select('li')
                    
                    logger.info(f"Nombre d'offres trouvées dans l'onglet {page}: {len(job_listings)}")
                    
                    if job_listings:
                        processed_result = process_job_listings(job_listings, existing_links, existing_titles)
                        new_offers_count += processed_result['new']
                        existing_offers_count += processed_result['existing']
                        
                        # Mise à jour du compteur d'offres consécutives existantes
                        if processed_result['new'] > 0:
                            consecutive_existing_count = 0
                        else:
                            consecutive_existing_count += processed_result['existing']
                    
                except json.JSONDecodeError:
                    logger.error(f"Erreur de décodage JSON pour l'onglet {page}")
                    
                    # Méthode alternative: essayer de récupérer directement le HTML
                    try:
                        # Construire l'URL avec le paramètre de page
                        alt_url = f"{base_url}?pg={page}"
                        alt_response = requests.get(alt_url, headers=headers, timeout=30)
                        
                        if alt_response.status_code == 200:
                            alt_soup = BeautifulSoup(alt_response.content, 'html.parser')
                            job_listings = alt_soup.select('ul.job_listings li')
                            
                            if job_listings:
                                logger.info(f"Méthode alternative: {len(job_listings)} offres trouvées dans l'onglet {page}")
                                processed_result = process_job_listings(job_listings, existing_links, existing_titles)
                                new_offers_count += processed_result['new']
                                existing_offers_count += processed_result['existing']
                                
                                if processed_result['new'] > 0:
                                    consecutive_existing_count = 0
                                else:
                                    consecutive_existing_count += processed_result['existing']
                    except Exception as e:
                        logger.error(f"Échec de la méthode alternative pour l'onglet {page}: {str(e)}")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'onglet {page}: {str(e)}")
                continue
        
        logger.info(f"Scraping terminé. {new_offers_count} nouvelles offres ajoutées. {existing_offers_count} offres déjà existantes ignorées.")
        return new_offers_count
        
    except Exception as e:
        logger.error(f"Erreur générale lors du scraping: {str(e)}")
        return 0

def process_job_listings(job_listings, existing_links, existing_titles):
    """
    Traite une liste d'offres d'emploi et les ajoute à la base de données si elles n'existent pas déjà
    
    Args:
        job_listings: Liste des éléments HTML représentant les offres
        existing_links: Ensemble des liens d'offres existantes
        existing_titles: Ensemble des titres d'offres existantes
        
    Returns:
        dict: Dictionnaire contenant le nombre de nouvelles offres et d'offres existantes traitées
    """
    new_count = 0
    existing_count = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    for job in job_listings:
        try:
            # Extraction des informations de base
            titre = job.get('data-title', '').strip()
            entreprise = job.get('data-company', '').strip()
            lieu = job.get('data-address', '').strip()
            lien_image = job.get('data-image', '')
            
            # Si pas de titre, essayer d'extraire depuis le HTML
            if not titre:
                titre_elem = job.select_one('h4')
                if titre_elem:
                    titre = titre_elem.get_text(strip=True).split('\n')[0]
            
            if not titre:
                logger.warning("Offre sans titre détectée, ignorée")
                continue
            
            # Extraction du lien de l'offre
            lien_elem = job.select_one('a')
            if not lien_elem or 'href' not in lien_elem.attrs:
                logger.warning(f"Pas de lien trouvé pour l'offre: {titre}")
                continue
                
            lien_offre = lien_elem['href']
            
            # Extraction du type de contrat
            type_contrat_elem = job.get('data-job_type', '')
            type_contrat = ''
            if type_contrat_elem:
                # Utilisation d'une expression régulière pour extraire le texte entre les balises <span>
                match = re.search(r'>(.*?)<', type_contrat_elem)
                if match:
                    type_contrat = match.group(1)
            
            # Si pas de type de contrat via data-attribute, essayer via le HTML
            if not type_contrat:
                type_elem = job.select_one('.job-type')
                if type_elem:
                    type_contrat = type_elem.get_text(strip=True)
            
            # Vérifier si l'offre existe déjà
            if lien_offre in existing_links or titre.lower() in [t.lower() for t in existing_titles]:
                logger.debug(f"Offre déjà existante: {titre} ({lien_offre})")
                existing_count += 1
                continue
            
            # Extraction de la description courte
            description_elem = job.select_one('.listing-desc p')
            description_courte = description_elem.text.strip() if description_elem else ""
            
            # Extraction de la date de publication
            date_elem = job.select_one('.listing-date time') or job.select_one('.listing-date')
            date_publication = timezone.now()  # Par défaut, date actuelle
            
            if date_elem:
                date_text = date_elem.get_text(strip=True).lower()
                
                if 'nouveau' in date_text:
                    date_publication = timezone.now()
                elif 'publié il y a' in date_text:
                    try:
                        # Extraire le nombre de jours/semaines/mois
                        parts = date_text.replace('publié il y a', '').strip().split()
                        if len(parts) >= 2:
                            number = int(parts[0])
                            period = parts[1]
                            
                            if 'jour' in period:
                                date_publication = timezone.now() - timezone.timedelta(days=number)
                            elif 'semaine' in period:
                                date_publication = timezone.now() - timezone.timedelta(weeks=number)
                            elif 'mois' in period:
                                date_publication = timezone.now() - timezone.timedelta(days=number*30)
                    except Exception as e:
                        logger.error(f"Erreur lors du parsing de la date: {str(e)}")
            
            logger.info(f"Récupération des détails pour l'offre: {titre}")
            
            # Récupérer les détails complets de l'offre
            time.sleep(2)  # Attente entre les requêtes
            
            details_response = requests.get(lien_offre, headers=headers, timeout=30)
            if details_response.status_code != 200:
                logger.error(f"Erreur lors de la récupération des détails: {details_response.status_code}")
                description_complete = ""
                closing_date = None
            else:
                details_soup = BeautifulSoup(details_response.content, 'html.parser')
                
                # Extraction de la description complète avec conservation des balises HTML
                description_complete = ""
                job_description = details_soup.select_one('.job_description')
                
                if job_description:
                    # Récupérer le contenu HTML de la description
                    description_complete = str(job_description)
                else:
                    # Fallback: essayer d'autres sélecteurs courants
                    content_selectors = [
                        'article.single_job_listing .job_description',
                        '.job-overview .job-description',
                        '.single-job-content',
                        '.job-details'
                    ]
                    
                    for selector in content_selectors:
                        content_elem = details_soup.select_one(selector)
                        if content_elem:
                            description_complete = str(content_elem)
                            break
                    
                    # Si toujours rien, prendre tout le contenu HTML de l'article
                    if not description_complete:
                        article_content = details_soup.select_one('article.single_job_listing')
                        if article_content:
                            description_complete = str(article_content)
                
                # Extraction de la date de clôture (si disponible)
                closing_date = None
                closing_date_elem = details_soup.select_one('.job-overview .date-expiration')
                if closing_date_elem:
                    try:
                        closing_date_text = closing_date_elem.text.strip()
                        if "Closing date:" in closing_date_text:
                            date_str = closing_date_text.replace("Closing date:", "").strip()
                            closing_date = datetime.strptime(date_str, '%d %b %Y').date()
                    except Exception as e:
                        logger.error(f"Erreur lors du parsing de la date de clôture: {str(e)}")
                
                # Chercher dans la description complète
                if not closing_date and description_complete and "Closing date:" in description_complete:
                    try:
                        match = re.search(r'Closing date:\s*(\d{1,2}\s+\w+\s+\d{4})', description_complete)
                        if match:
                            date_str = match.group(1)
                            closing_date = datetime.strptime(date_str, '%d %b %Y').date()
                    except Exception as e:
                        logger.error(f"Erreur lors du parsing de la date de clôture dans la description: {str(e)}")
                        
            # Créer l'offre dans la base de données
            with transaction.atomic():
                offre = OffreEmploiSN(
                    titre=titre,
                    entreprise=entreprise,
                    lieu=lieu,
                    type_contrat=type_contrat,
                    date_publication=date_publication,
                    lien_offre=lien_offre,
                    lien_image=lien_image,
                    description_courte=description_courte,
                    description_complete=description_complete,
                    date_cloture=closing_date
                )
                offre.save()
                
                # Ajouter aux ensembles pour éviter les doublons dans la même session
                existing_links.add(lien_offre)
                existing_titles.add(titre)
                
                new_count += 1
                logger.info(f"Nouvelle offre ajoutée: {titre}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'offre: {str(e)}")
            continue
    
    return {'new': new_count, 'existing': existing_count}