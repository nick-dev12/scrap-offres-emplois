from django.db import models

class EmploiDakar(models.Model):
    titre = models.CharField(max_length=200)
    description_poste = models.TextField(null=True, blank=True)
    profil_recherche = models.TextField(null=True, blank=True)
    entreprise = models.CharField(max_length=200)
    localisation = models.CharField(max_length=200)
    type_contrat = models.CharField(max_length=50)
    date_publication = models.DateTimeField(null=True, blank=True)
    lien_offre = models.URLField(max_length=255)
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.titre} - {self.entreprise}"

    class Meta:
        ordering = ['-date_publication'] 