"""
URL configuration for projet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scrap_emploi import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    path('emplois-senegal/', views.emplois_senegal_list, name='emplois_senegal_list'),
    path('emplois-senegal/<int:emploi_id>/', views.emploi_senegal_detail, name='emploi_senegal_detail'),
    
    path('emplois-dakar/', views.emplois_dakar_list, name='emplois_dakar_list'),
    path('emplois-dakar/<int:emploi_id>/', views.emploi_dakar_detail, name='emploi_dakar_detail'),
    
    path('senjob/', views.senjob_list, name='senjob_list'),
    path('senjob/<int:offre_id>/', views.senjob_detail, name='senjob_detail'),
]
