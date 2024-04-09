from django.urls import path
from . import views

urlpatterns = [
    path('storage_items/', views.StorageItemsList.as_view(), name='storage_items'),
]