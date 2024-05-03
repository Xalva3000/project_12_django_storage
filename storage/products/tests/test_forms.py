from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


from products.models import Product


class RegisterUserTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.product_list_url = reverse("products:products")
        self.queryset = Product.objects.all().order_by('-pk')
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    def test_form_registration_get(self):
        path = reverse('products:add_product')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'products/add_product.html')


