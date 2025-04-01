from django.urls import path
from . import api

urlpatterns = [
    path('tipos-bolso/<int:pk>/', api.tipo_bolso_detail_api, name='tipo_bolso_detail_api'),
]
