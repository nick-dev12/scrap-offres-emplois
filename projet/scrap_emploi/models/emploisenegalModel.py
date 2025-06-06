from django.db import models

class EmploiSenegal(models.Model):
    titre = models.CharField(max_length=200)
    description_poste = models.TextField()
    profil_recherche = models.TextField(default='')
    entreprise = models.CharField(max_length=100)
    localisation = models.CharField(max_length=100)
    lien_offre = models.URLField()
    source = models.CharField(max_length=100, default='emploisenegal.com')
    date_publication = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    niveau_etude = models.CharField(max_length=100, blank=True, null=True)
    niveau_experience = models.CharField(max_length=100, blank=True)
    type_contrat = models.CharField(max_length=100, blank=True)
    competences = models.CharField(max_length=200, blank=True)
    secteur_activite = models.CharField(max_length=200, blank=True, null=True)
    site_internet = models.URLField(blank=True, null=True)
    description_entreprise = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titre} - {self.entreprise}"

    class Meta:
        ordering = ['-date_publication']