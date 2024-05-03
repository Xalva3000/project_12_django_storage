from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
import json

from products.utils import tools

from products.models import Product


# urlpatterns = [
#     path('', LoginUser.as_view(), name='home'),
#     path("products/", views.ProductsList.as_view(), name='products'),
#     path("products/<int:pk>/", views.ShowProduct.as_view(), name='product'),
#     path("products/add_product/", views.AddProduct.as_view(), name='add_product'),
#     path("products/update/<int:pk>", views.UpdateProduct.as_view(), name='update_product'),
#     path("about/", views.about, name="about"),
# ]

class TestViews(TestCase):
    fixtures = ['products_product.json']

    def setUp(self) -> None:
        # products.count = 22
        self.client = Client()
        self.product_list_url = reverse("products:products")
        self.queryset = Product.objects.all().order_by('-pk')
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    def test_products_list_GET_login(self):
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "products/products.html")
        self.assertEqual(response.context_data["title"], "Продукты")
        self.assertEqual(response.context_data["tools"], tools["products"])
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(response.context_data["products"].count(), 20)
        self.assertEqual(self.queryset.count(), 22)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["products"][:20], self.queryset[:20])

    def test_products_list_GET_login_page_2(self):
        page = 2
        paginate_by = 20
        response = self.client.get(self.product_list_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertQuerySetEqual(response.context_data["products"], self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_products_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.product_list_url
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)

    def product_detail(self):
        pk = 1
        p1 = Product.objects.get(pk=pk)
        path = reverse('products:product', args=[pk])
        response = self.client.get(path)
        self.assertEqual(p1.fish, response.context_data['product'].fish)


    # def test_redirect_add_product(self):
    #     path = reverse("add_product")
    #     redirect_url = reverse_lazy('products:products')


# class ProductsList(DataMixin, ListView):
#     template_name = 'products/products.html'
#     context_object_name = 'products'
#     title_page = 'Продукты'
#     category_page = 'products'
#     paginate_by = 20
#
#     def get_queryset(self):
#         return Product.objects.all()