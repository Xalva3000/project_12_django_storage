from django.urls import path

from products import views
from users.views import LoginUser

urlpatterns = [
    path('', LoginUser.as_view(), name='home'),
    path("products/", views.ProductsList.as_view(), name='products'),
    path("products/<int:pk>/", views.ShowProduct.as_view(), name='product'),
    path("products/add_product/", views.AddProduct.as_view(), name='add_product'),
    path("products/update/<int:pk>", views.UpdateProduct.as_view(), name='update_product'),
    path("about/", views.about, name="about"),
]