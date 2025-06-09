from celery import shared_task
from .controllers.emploidakarController import scrape_emplois_dakar
from .controllers.emploisenegalController import scrape_emplois
from .controllers.senjobController import scrape_senjob
from .controllers.offreEmploiSNController import scrape_offre_emploi_sn
import logging

logger = logging.getLogger(__name__)

@shared_task
def scrape_emploidakar_periodic():
    """
    Tâche périodique pour scraper les offres d'EmploiDakar
    """
    try:
        logger.info("Démarrage du scraping périodique EmploiDakar")
        new_offers = scrape_emplois_dakar()
        logger.info(f"Scraping EmploiDakar terminé. {new_offers} nouvelles offres ajoutées.")
        return new_offers
    except Exception as e:
        logger.error(f"Erreur lors du scraping EmploiDakar: {str(e)}")
        raise

@shared_task
def scrape_emploisenegal_periodic():
    """
    Tâche périodique pour scraper les offres d'EmploiSenegal
    """
    try:
        logger.info("Démarrage du scraping périodique EmploiSenegal")
        new_offers = scrape_emplois()
        logger.info(f"Scraping EmploiSenegal terminé. {new_offers} nouvelles offres ajoutées.")
        return new_offers
    except Exception as e:
        logger.error(f"Erreur lors du scraping EmploiSenegal: {str(e)}")
        raise

@shared_task
def scrape_senjob_periodic():
    """
    Tâche périodique pour scraper les offres de Senjob
    """
    try:
        logger.info("Démarrage du scraping périodique Senjob")
        new_offers = scrape_senjob()
        logger.info(f"Scraping Senjob terminé. {new_offers} nouvelles offres ajoutées.")
        return new_offers
    except Exception as e:
        logger.error(f"Erreur lors du scraping Senjob: {str(e)}")
        raise

@shared_task
def scrape_offre_emploi_sn_periodic():
    """
    Tâche périodique pour scraper les offres d'OffreEmploiSN
    """
    try:
        logger.info("Démarrage du scraping périodique OffreEmploiSN")
        new_offers = scrape_offre_emploi_sn()
        logger.info(f"Scraping OffreEmploiSN terminé. {new_offers} nouvelles offres ajoutées.")
        return new_offers
    except Exception as e:
        logger.error(f"Erreur lors du scraping OffreEmploiSN: {str(e)}")
        raise 