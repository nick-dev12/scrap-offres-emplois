from django.db import models

class SenjobModel(models.Model):
    titre = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255, null=True, blank=True)
    localisation = models.CharField(max_length=100)
    type_contrat = models.CharField(max_length=100, null=True, blank=True)
    date_publication = models.DateField()
    date_expiration = models.DateField()
    lien_offre = models.URLField(max_length=500)
    description_poste = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'senjob'
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre 