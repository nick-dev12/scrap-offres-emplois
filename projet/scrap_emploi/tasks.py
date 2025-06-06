from celery import shared_task
from .controllers.emploidakarController import scrape_emplois_dakar
from .controllers.emploisenegalController import scrape_emplois
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