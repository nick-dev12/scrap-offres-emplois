from datetime import datetime, timedelta
import logging
from ..models.senjobModel import SenjobModel
import requests
from bs4 import BeautifulSoup
from django.db import transaction
import time

logger = logging.getLogger(__name__)

def scrape_senjob():
    logger.info("Démarrage du scraping Senjob")
    
    # Récupérer tous les liens et titres d'offres existants une seule fois au début
    existing_links = set(SenjobModel.objects.values_list('lien_offre', flat=True))
    existing_titles = set(SenjobModel.objects.values_list('titre', flat=True))
    
    logger.info(f"Nombre d'offres déjà en base: {len(existing_links)}")
    
    total_offres = 0
    existing_offres_count = 0
    consecutive_existing_offres = 0
    max_consecutive_existing = 15  # Arrêter après 15 offres consécutives déjà existantes
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    page_number = 1
    has_next_page = True
    
    while has_next_page:
        try:
            # Construction de l'URL
            page_url = f"https://senjob.com/sn/offres-d-emploi.php{'?page=' + str(page_number) if page_number > 1 else ''}"
            logger.info(f"Analyse de la page {page_number} : {page_url}")
            
            # Attente entre les requêtes
            time.sleep(2)
            
            # Récupération de la page
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Recherche des offres
            offres = soup.select('tr[style*="height:70px"]')
            if not offres:
                logger.info("Aucune offre trouvée sur cette page")
                break
                
            logger.info(f"Nombre d'offres trouvées sur la page {page_number} : {len(offres)}")
            
            page_has_new_offres = False
            
            # Traitement de chaque offre
            for offre in offres:
                try:
                    logger.info("Début du traitement d'une nouvelle offre")
                    
                    # Extraction du lien et du titre
                    lien_element = offre.select_one('a[href*="jobseekers"]')
                    if not lien_element:
                        logger.warning("Pas de lien trouvé pour cette offre")
                        continue
                        
                    lien_offre = lien_element.get('href', '')
                    if not lien_offre.startswith('http'):
                        lien_offre = 'https://senjob.com/sn/' + lien_offre.lstrip('/')
                    titre = lien_element.get_text(strip=True)
                    
                    # Vérification si l'offre existe déjà (par lien ou titre)
                    if lien_offre in existing_links or titre.lower() in [t.lower() for t in existing_titles]:
                        logger.info(f"L'offre {titre} existe déjà")
                        existing_offres_count += 1
                        consecutive_existing_offres += 1
                        continue
                    else:
                        # Réinitialiser le compteur d'offres consécutives existantes
                        consecutive_existing_offres = 0
                        page_has_new_offres = True
                        
                    # Extraction de la localisation
                    localisation = offre.select_one('td[style*="font-size:14px"] span.green_text_normal')
                    localisation = localisation.get_text(strip=True) if localisation else "Non spécifié"
                    
                    # Extraction des dates
                    date_cells = offre.select('td')
                    date_publication = None
                    date_expiration = None
                    
                    for cell in date_cells:
                        hidden_span = cell.select_one('span[style="display:none"]')
                        if hidden_span:
                            date_text = hidden_span.get_text(strip=True)
                            if not date_publication:
                                date_publication = date_text
                            else:
                                date_expiration = date_text
                                break
                    
                    # Conversion des dates
                    try:
                        date_pub = datetime.strptime(date_publication, '%Y-%m-%d').date() if date_publication else None
                        date_exp = datetime.strptime(date_expiration, '%Y-%m-%d').date() if date_expiration else None
                        
                        if date_pub and not date_exp:
                            date_exp = date_pub + timedelta(days=30)
                        elif not date_pub and not date_exp:
                            date_pub = datetime.now().date()
                            date_exp = date_pub + timedelta(days=30)
                    except ValueError as e:
                        logger.error(f"Erreur lors du parsing des dates: {str(e)}")
                        date_pub = datetime.now().date()
                        date_exp = date_pub + timedelta(days=30)
                    
                    # Récupération des détails de l'offre
                    logger.info(f"Récupération des détails depuis {lien_offre}")
                    time.sleep(2)
                    details_response = requests.get(lien_offre, headers=headers)
                    details_response.raise_for_status()
                    details_soup = BeautifulSoup(details_response.text, 'html.parser')
                        
                    # Extraction des détails
                    view_div = details_soup.select_one('div.view')
                    if not view_div:
                        logger.warning(f"Pas de contenu trouvé pour {lien_offre}")
                        continue
                        
                    # Extraction du contenu HTML de la div avec la classe "view"
                    description = str(view_div)
                    
                    # Extraction des informations complémentaires
                    entreprise = "Non spécifié"
                    type_contrat = "Non spécifié"
                    
                    info_divs = view_div.select('div')
                    for div in info_divs:
                        text = div.get_text(strip=True)
                        if "A PROPOS DE" in text.upper():
                            entreprise = text.split(":")[-1].strip()
                        elif "TYPE DE CONTRAT" in text.upper():
                            type_contrat = text.split(":")[-1].strip()
                    
                    # Sauvegarde de l'offre
                    logger.info(f"Tentative de sauvegarde de l'offre : {titre}")
                    with transaction.atomic():
                        offre_obj = SenjobModel(
                            titre=titre,
                            entreprise=entreprise,
                            localisation=localisation,
                            type_contrat=type_contrat,
                            date_publication=date_pub,
                            date_expiration=date_exp,
                            description_poste=description,
                            lien_offre=lien_offre
                        )
                        offre_obj.save()
                        
                        # Ajouter aux ensembles pour éviter les doublons dans la même session
                        existing_links.add(lien_offre)
                        existing_titles.add(titre)
                        
                        total_offres += 1
                        logger.info(f"Offre sauvegardée avec succès : {titre}")

                except Exception as e:
                    logger.error(f"Erreur lors du traitement de l'offre : {str(e)}")
                    logger.exception(e)
                    continue
            
            # Arrêter si on a trouvé trop d'offres consécutives déjà existantes
            if consecutive_existing_offres >= max_consecutive_existing:
                logger.info(f"Arrêt du scraping après {consecutive_existing_offres} offres consécutives déjà existantes")
                break
                
            # Si la page ne contient que des offres déjà existantes, on continue quand même à la page suivante
            if not page_has_new_offres and existing_offres_count > 0:
                logger.info("Page ne contenant que des offres déjà existantes, passage à la page suivante")
            
            # Analyse de la structure de pagination
            logger.info("Analyse de la structure de pagination...")
            pagination_td = soup.find('td', recursive=True)
            if pagination_td:
                logger.info("TD de pagination trouvé")
                pagination_divs = pagination_td.find_all('div', class_='resultsOffre')
                logger.info(f"Nombre de divs de pagination trouvés : {len(pagination_divs)}")
                
                # Recherche le dernier numéro de page
                last_page = 1
                for div in pagination_divs:
                    link = div.find('a')
                    if link:
                        try:
                            text = link.text.strip()
                            if text.isdigit():
                                page_num = int(text)
                                if page_num > last_page:
                                    last_page = page_num
                        except ValueError:
                            continue
                
                logger.info(f"Dernier numéro de page trouvé : {last_page}")
                
                # Si nous ne sommes pas à la dernière page
                current_page = int(page_url.split('page=')[-1]) if 'page=' in page_url else 1
                logger.info(f"Page courante : {current_page}")
                
                if current_page < last_page:
                    page_number += 1
                    has_next_page = True
                    logger.info(f"Passage à la page suivante : {page_number}")
                else:
                    logger.info("Plus de pages à analyser")
                    has_next_page = False
            else:
                logger.info("Aucun TD de pagination trouvé")
                has_next_page = False
            
        except Exception as e:
            logger.error(f"Erreur lors du scraping de la page {page_number}: {str(e)}")
            logger.exception(e)
            break
    
    logger.info(f"Scraping terminé. Total des nouvelles offres ajoutées : {total_offres}. Offres déjà existantes ignorées : {existing_offres_count}")
    return total_offres