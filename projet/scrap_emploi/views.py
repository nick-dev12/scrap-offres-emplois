from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.core.paginator import Paginator
from .models.emploisenegalModel import EmploiSenegal
from .models.emploidakarModel import EmploiDakar
from .controllers.emploidakarController import scrape_emplois_dakar
from .controllers.emploisenegalController import scrape_emplois
from .controllers.senjobController import scrape_senjob
from .models.senjobModel import SenjobModel
from .controllers.offreEmploiSNController import scrape_offre_emploi_sn
from .models.offreEmploiSNModel import OffreEmploiSN


def home(request):
    return render(request, 'scrap_emploi/home.html')


def emplois_senegal_list(request):
    scrape_emplois()
    
    emplois_senegal = EmploiSenegal.objects.all()
    paginator = Paginator(emplois_senegal, 20)  # 20 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'scrap_emploi/emplois_senegal_list.html', context)


def emploi_senegal_detail(request, emploi_id):
    emploi = get_object_or_404(EmploiSenegal, id=emploi_id)
    context = {
        'emploi': emploi
    }
    return render(request, 'scrap_emploi/emploi_senegal_detail.html', context)


def emplois_dakar_list(request):
    scrape_emplois_dakar()
   
    emplois_dakar = EmploiDakar.objects.all()
    paginator = Paginator(emplois_dakar, 20)  # 20 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'scrap_emploi/emplois_dakar_list.html', context)


def emploi_dakar_detail(request, emploi_id):
    emploi = get_object_or_404(EmploiDakar, id=emploi_id)
    context = {
        'emploi': emploi
    }
    return render(request, 'scrap_emploi/emploi_dakar_detail.html', context)


def senjob_list(request):
    scrape_senjob()
    offres_list = SenjobModel.objects.all().order_by('-date_publication')
    paginator = Paginator(offres_list, 10)  # 10 offres par page
    
    page = request.GET.get('page')
    offres = paginator.get_page(page)
    
    return render(request, 'scrap_emploi/senjob_list.html', {'offres': offres})


def senjob_detail(request, offre_id):
    offre = get_object_or_404(SenjobModel, id=offre_id)
    return render(request, 'scrap_emploi/senjob_detail.html', {'offre': offre})


def offre_emploi_sn_list(request):
    scrape_offre_emploi_sn()
    offres_list = OffreEmploiSN.objects.all().order_by('-date_publication')
    paginator = Paginator(offres_list, 10)  # 10 offres par page
    
    page = request.GET.get('page')
    offres = paginator.get_page(page)
    
    return render(request, 'scrap_emploi/offre_emploi_sn_list.html', {'offres': offres})


def offre_emploi_sn_detail(request, offre_id):
    offre = get_object_or_404(OffreEmploiSN, id=offre_id)
    return render(request, 'scrap_emploi/offre_emploi_sn_detail.html', {'offre': offre})





