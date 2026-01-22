from django.urls import path
from .views import AuditoriaAPIView

urlpatterns = [
    path('auditoria/', AuditoriaAPIView.as_view(), name='auditoria_list_create'),
]
