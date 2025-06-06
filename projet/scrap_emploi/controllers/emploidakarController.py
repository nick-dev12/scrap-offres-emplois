import requests
from bs4 import BeautifulSoup
from ..models.emploidakarModel import EmploiDakar
import json
import logging
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
import time

logger = logging.getLogger(__name__)

def scrape_emplois_dakar():
    # Headers pour simuler un navigateur réel
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # URL de l'API AJAX de WP Job Manager
    api_url = "https://www.emploidakar.com/jm-ajax/get_listings/"
    page = 1
    new_offers_count = 0
    existing_offers_count = 0
    consecutive_existing_offers = 0
    max_consecutive_existing = 40  # Arrêter après 15 offres consécutives déjà existantes
    
    # Récupérer tous les liens d'offres et titres existants une seule fois au début
    existing_offers = set(EmploiDakar.objects.values_list('lien_offre', flat=True))
    existing_references = set(EmploiDakar.objects.values_list('reference', flat=True))
    existing_titles = set(EmploiDakar.objects.values_list('titre', flat=True))
    
    logger.info("Démarrage du scraping EmploiDakar...")
    logger.info(f"Nombre d'offres déjà en base: {len(existing_offers)}")
    
    while True:
        logger.info(f"Traitement de la page {page}")
        
        # Paramètres de la requête AJAX
        data = {
            'page': page,
            'per_page': 25,
            'orderby': 'date',
            'order': 'DESC',
            'featured': None,
            'filled': None,
            'job_types': [],
            'search_categories': [],
            'search_keywords': '',
            'search_location': ''
        }
        
        try:
            # Faire la requête HTTP avec un délai
            time.sleep(2)  # Attendre 2 secondes entre chaque requête
            response = requests.post(api_url, headers=headers, data=data, timeout=30)
            logger.info(f"Statut de la réponse API: {response.status_code}")
            
            if response.status_code != 200:
                logger.error("Échec de la récupération des offres depuis l'API")
                break
            
            try:
                # Parser la réponse JSON
                json_data = response.json()
                
                if not json_data.get('html'):
                    logger.info("Aucun contenu HTML trouvé dans la réponse JSON")
                    break
                
                # Parser le HTML contenu dans la réponse JSON
                soup = BeautifulSoup(json_data['html'], 'html.parser')
                job_listings = soup.select('li.job_listing')
                logger.info(f"Nombre d'offres trouvées sur la page {page}: {len(job_listings)}")
                
                if not job_listings:
                    logger.info("Aucune offre trouvée sur cette page")
                    break
                
                page_has_new_offers = False
                
                # Extraire les détails de chaque offre
                for job in job_listings:
                    try:
                        # Extraire d'abord le titre pour vérification
                        titre_elem = job.select_one('.position h3')
                        titre = titre_elem.text.strip() if titre_elem else "Sans titre"
                        
                        lien_elem = job.select_one('a')
                        if not lien_elem or 'href' not in lien_elem.attrs:
                            continue
                            
                        lien_offre = lien_elem['href']
                        reference = lien_offre.split('/')[-2]
                        
                        # Vérification rapide par référence, lien et titre
                        if (reference in existing_references or 
                            lien_offre in existing_offers or 
                            titre.lower() in [t.lower() for t in existing_titles]):
                            
                            logger.debug(f"Offre déjà existante: {titre} ({lien_offre})")
                            existing_offers_count += 1
                            consecutive_existing_offers += 1
                            continue
                        else:
                            # Réinitialiser le compteur d'offres consécutives existantes
                            consecutive_existing_offers = 0
                            page_has_new_offers = True
                            
                        # Extraire les autres informations seulement si c'est une nouvelle offre
                        entreprise_elem = job.select_one('.company strong')
                        entreprise = entreprise_elem.text.strip() if entreprise_elem else "Entreprise non spécifiée"
                        
                        localisation_elem = job.select_one('.location')
                        localisation = localisation_elem.text.strip() if localisation_elem else "Lieu non spécifié"
                        
                        type_contrat_elem = job.select_one('.meta .job-type')
                        type_contrat = type_contrat_elem.text.strip() if type_contrat_elem else "Type non spécifié"
                        
                        date_elem = job.select_one('.meta time')
                        if date_elem and 'datetime' in date_elem.attrs:
                            date_publication = datetime.fromisoformat(date_elem['datetime'])
                            date_publication = timezone.make_aware(date_publication)
                        else:
                            date_publication = timezone.now()
                        
                        # Extraire la description détaillée de l'offre
                        time.sleep(1)  # Attendre 1 seconde avant de récupérer les détails
                        job_detail_response = requests.get(lien_offre, headers=headers)
                        if job_detail_response.status_code == 200:
                            job_detail_soup = BeautifulSoup(job_detail_response.content, 'html.parser')
                            job_description_elem = job_detail_soup.select_one('.job_description')
                            if job_description_elem:
                                # Conserver la structure HTML
                                job_description = str(job_description_elem)
                                logger.info(f"Description extraite pour l'offre {titre} ({len(job_description)} caractères)")
                            else:
                                job_description = ""
                                logger.warning(f"Pas de description trouvée pour l'offre {titre}")
                        else:
                            job_description = ""
                            logger.error(f"Impossible d'accéder aux détails de l'offre {titre}")
                        
                        # Créer la nouvelle offre
                        nouvelle_offre = EmploiDakar.objects.create(
                            titre=titre,
                            description_poste=job_description,
                            entreprise=entreprise,
                            localisation=localisation,
                            type_contrat=type_contrat,
                            date_publication=date_publication,
                            lien_offre=lien_offre,
                            reference=reference
                        )
                        
                        # Ajouter aux ensembles d'offres existantes pour éviter les doublons dans la même session
                        existing_offers.add(lien_offre)
                        existing_references.add(reference)
                        existing_titles.add(titre)
                        
                        new_offers_count += 1
                        logger.info(f"Nouvelle offre ajoutée: {titre}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement d'une offre: {str(e)}")
                        continue
                
                # Arrêter si on a trouvé trop d'offres consécutives déjà existantes
                if consecutive_existing_offers >= max_consecutive_existing:
                    logger.info(f"Arrêt du scraping après {consecutive_existing_offers} offres consécutives déjà existantes")
                    break
                
                # Si la page ne contient que des offres déjà existantes, on peut considérer 
                # qu'on a probablement déjà tout ce qui est récent
                if not page_has_new_offers and existing_offers_count > 0:
                    logger.info("Page ne contenant que des offres déjà existantes, passage à la page suivante")
                
                # Vérifier s'il y a une page suivante
                if page >= int(json_data.get('max_num_pages', 1)):
                    logger.info("Plus de pages à scraper")
                    break
                
                page += 1
                
            except json.JSONDecodeError:
                logger.error("Échec du parsing de la réponse JSON")
                break
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau: {str(e)}")
            break
    
    logger.info(f"Scraping terminé. {new_offers_count} nouvelles offres ajoutées. {existing_offers_count} offres déjà existantes ignorées.")
    return new_offers_count


    