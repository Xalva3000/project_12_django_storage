from django.urls import path

from . import views

urlpatterns = [
    path("", views.ContractorsList.as_view(), name='contractors'),
    path("<int:pk>/", views.ShowContractor.as_view(), name='contractor'),
    path("add_contractor/", views.AddContractor.as_view(), name='add_contractor'),
    path("update/<int:pk>/", views.UpdateContractor.as_view(), name='update_contractor'),
]