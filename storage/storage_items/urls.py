from django.urls import path
from . import views

urlpatterns = [
    path('not_zero/', views.StorageItemsList.as_view(), name='not_zero'),
    path('available/', views.StorageItemsAvailableList.as_view(), name='available'),
]