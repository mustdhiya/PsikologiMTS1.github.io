from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),                 # Halaman utama dashboard
    path('scoring/', views.scoring, name='scoring'),         # Halaman scoring/nilai
    path('sertifikat/1/', views.certif1, name='certif1'),    # Sertifikat 1
    path('sertifikat/2/', views.certif2, name='certif2'),    # Sertifikat 2
    path('sertifikat/3/', views.certif3, name='certif3'),    # Sertifikat 3
    path('sertifikat/4/', views.certif4, name='certif4'),    # Sertifikat 4
]
