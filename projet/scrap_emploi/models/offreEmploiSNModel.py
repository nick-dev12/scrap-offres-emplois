from django.db import models
from django.utils.text import slugify

class OffreEmploiSN(models.Model):
    titre = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255)
    lieu = models.CharField(max_length=255, null=True, blank=True)
    type_contrat = models.CharField(max_length=50, null=True, blank=True)
    date_publication = models.DateTimeField()
    lien_offre = models.URLField(unique=True)
    lien_image = models.URLField(null=True, blank=True)
    description_courte = models.TextField(null=True, blank=True)
    description_complete = models.TextField(null=True, blank=True)
    date_cloture = models.DateField(null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    date_scraping = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Offre Emploi SN"
        verbose_name_plural = "Offres Emploi SN"
        ordering = ['-date_publication']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.titre}-{self.entreprise}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.titre} - {self.entreprise}" 