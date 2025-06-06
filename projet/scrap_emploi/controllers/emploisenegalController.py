import requests
from bs4 import BeautifulSoup
from ..models.emploisenegalModel import EmploiSenegal
from datetime import datetime
import logging
import random
from django.utils import timezone

logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'
]

def scrape_emplois():
    logger.info("Début du scraping EmploiSenegal")
    
    # Récupérer les offres existantes pour éviter les doublons
    existing_links = set(EmploiSenegal.objects.values_list('lien_offre', flat=True))
    existing_titles = set(EmploiSenegal.objects.values_list('titre', flat=True))
    
    logger.info(f"Nombre d'offres déjà en base: {len(existing_links)}")
    
    base_url = "https://www.emploisenegal.com/recherche-jobs-senegal"
    page = 0
    new_offers_count = 0
    existing_offers_count = 0
    consecutive_existing_offers = 0
    max_consecutive_existing = 40  # Arrêter après 40 offres consécutives déjà existantes
    
    while True:
        url = f"{base_url}?page={page}"
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        logger.info(f"Requête vers {url}")
        try:
            response = requests.get(url, headers=headers, timeout=30)
            logger.info(f"Statut de la réponse: {response.status_code}")
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            offres = soup.find_all('div', class_='card card-job')
            logger.info(f"{len(offres)} offres trouvées sur la page {page}")
            
            if not offres:
                logger.info(f"Fin du scraping à la page {page}. Aucune offre trouvée.")
                break
            
            page_has_new_offers = False
            
            for offre in offres:
                try:
                    # Extraction du titre et du lien en premier pour vérification
                    titre_element = offre.find('h3').find('a')
                    titre = titre_element.get_text(strip=True)
                    lien_offre = "https://www.emploisenegal.com" + titre_element['href']
                    
                    # Vérifier si l'offre existe déjà
                    if lien_offre in existing_links or titre.lower() in [t.lower() for t in existing_titles]:
                        logger.debug(f"Offre déjà existante: {titre} ({lien_offre})")
                        existing_offers_count += 1
                        consecutive_existing_offers += 1
                        continue
                    else:
                        # Réinitialiser le compteur d'offres consécutives existantes
                        consecutive_existing_offers = 0
                        page_has_new_offers = True
                    
                    logger.info(f"Traitement de la nouvelle offre: {titre}")
                    
                    # Extraction de l'entreprise
                    entreprise_element = offre.find('a', class_='card-job-company company-name')
                    entreprise = entreprise_element.get_text(strip=True) if entreprise_element else "Non spécifié"
                    
                    # Extraction de la description
                    description_element = offre.find('div', class_='card-job-description')
                    description = description_element.find('p').get_text(strip=True) if description_element else ""
                    
                    # Extraction des informations complémentaires
                    infos = offre.find_all('li')
                    localisation = "Non spécifié" 
                    niveau_etude = "Non spécifié"
                    niveau_experience = "Non spécifié"
                    type_contrat = "Non spécifié"
                    competences = "Non spécifié"
                    
                    for info in infos:
                        info_text = info.get_text()
                        if "Région de" in info_text or "Localisation" in info_text:
                            localisation = info.get_text(strip=True)
                            localisation = localisation.replace("Localisation:", "").strip()
                        elif "Niveau d'études requis" in info_text:
                            niveau_etude = info.get_text(strip=True) if "Niveau d'études requis" in info_text else None
                            niveau_etude = niveau_etude.replace("Niveau d'études requis :", "").strip() if niveau_etude else None
                        elif "Niveau d'expérience" in info_text:
                            niveau_experience = info.get_text(strip=True)
                            niveau_experience = niveau_experience.replace("Niveau d'expérience :", "").strip()
                        elif "Contrat proposé" in info_text:
                            type_contrat = info.get_text(strip=True)
                            type_contrat = type_contrat.replace("Contrat proposé :", "").strip()
                        elif "Compétences clés" in info_text:
                            competences = info.get_text(strip=True)
                            competences = competences.replace("Compétences clés :", "").strip()
                    
                    # Extraction de la date
                    date_element = offre.find('time')
                    try:
                        date_str = date_element.get_text(strip=True)
                        date_publication = datetime.strptime(date_str, '%d.%m.%Y').date()
                        # Rendre la date aware
                        date_publication = timezone.make_aware(datetime.combine(date_publication, datetime.min.time()))
                    except (ValueError, AttributeError):
                        date_publication = timezone.now()

                    try:
                        # Récupérer le contenu HTML de la page de détails
                        details_response = requests.get(lien_offre, headers=headers, timeout=30)
                        details_soup = BeautifulSoup(details_response.content, 'html.parser')
                        
                        # Extraire la description du poste
                        description_poste_element = details_soup.find('div', class_='job-description')
                        description_poste = str(description_poste_element) if description_poste_element else ""
                        
                        # Extraire les détails du profil recherché
                        profil_recherche_element = details_soup.find('div', class_='job-qualifications')
                        profil_recherche = str(profil_recherche_element) if profil_recherche_element else ""
                        
                        skills_elements = details_soup.select('.skills li')
                        competences = ', '.join([li.get_text(strip=True) for li in skills_elements]) if skills_elements else ""
                        
                        entreprise_element = details_soup.find('div', class_='card-block-company')
                        if entreprise_element:
                            secteur_activite_element = entreprise_element.find('div', class_='field-item even')
                            secteur_activite = secteur_activite_element.get_text(strip=True) if secteur_activite_element else ""
                        else:
                            secteur_activite = ""
                        
                        site_internet_element = entreprise_element.find('a', rel='nofollow') if entreprise_element else None
                        site_internet = site_internet_element['href'] if site_internet_element else ""
                        
                        description_entreprise_element = entreprise_element.find('p', class_='truncated-text') if entreprise_element else None
                        description_entreprise = description_entreprise_element.get_text(strip=True) if description_entreprise_element else ""
                    except Exception as e:
                        logger.error(f"Erreur lors de la récupération des détails pour {titre}: {str(e)}")
                        # Valeurs par défaut en cas d'erreur
                        description_poste = description
                        profil_recherche = ""
                        secteur_activite = ""
                        site_internet = ""
                        description_entreprise = ""
                    
                    # Créer une nouvelle offre
                    nouvelle_offre = EmploiSenegal.objects.create(
                        titre=titre,
                        description_poste=description_poste,
                        profil_recherche=profil_recherche,
                        entreprise=entreprise,
                        localisation=localisation,
                        niveau_etude=niveau_etude,
                        niveau_experience=niveau_experience, 
                        type_contrat=type_contrat,
                        competences=competences,
                        date_publication=date_publication,
                        secteur_activite=secteur_activite,
                        site_internet=site_internet,
                        description_entreprise=description_entreprise,
                        lien_offre=lien_offre
                    )
                    
                    # Ajouter aux ensembles pour éviter les doublons dans la même session
                    existing_links.add(lien_offre)
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
            
            # Si la page ne contient que des offres déjà existantes, on continue quand même à la page suivante
            if not page_has_new_offers and existing_offers_count > 0:
                logger.info("Page ne contenant que des offres déjà existantes, passage à la page suivante")
            
            # Passer à la page suivante
            page += 1
                
        except Exception as e:
            logger.error(f"Erreur lors du scraping de la page {page}: {str(e)}")
            break

    logger.info(f"Fin du scraping EmploiSenegal. {new_offers_count} nouvelles offres ajoutées. {existing_offers_count} offres déjà existantes ignorées.")
    return new_offers_count

def scrape_emplois_new():
    # Cette fonction n'est plus utilisée mais conservée pour référence
    url = "https://emploisenegal.com/recherche-jobs-senegal"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    emplois = []
    articles = soup.find_all('article', class_='js_result_row')

    for article in articles:
        titre = article.find('h2', class_='js_result_title').text.strip()
        lien_offre = article.find('a', class_='js_result_link')['href']
        entreprise = article.find('div', class_='js_result_recruiter').text.strip()
        localisation = article.find('div', class_='js_result_location').text.strip()
        date_publication_str = article.find('div', class_='js_result_date').text.strip()
        date_publication = datetime.strptime(date_publication_str, '%d/%m/%Y').date()

        # Récupérer les détails de l'offre
        details_response = requests.get(lien_offre)
        details_soup = BeautifulSoup(details_response.content, 'html.parser')

        description_poste = str(details_soup.find('div', class_='job-description'))
        profil_recherche = str(details_soup.find('div', class_='job-qualifications'))

        emploi = EmploiSenegal(
            titre=titre,
            description_poste=description_poste,
            profil_recherche=profil_recherche,
            entreprise=entreprise,
            localisation=localisation,
            lien_offre=lien_offre,
            date_publication=date_publication
        )
        emplois.append(emploi)

    EmploiSenegal.objects.bulk_create(emplois, ignore_conflicts=True)

 