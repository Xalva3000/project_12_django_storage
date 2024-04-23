from random import randint

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from products import views


class TestUrls(SimpleTestCase):

    def setUp(self) -> None:
        self.pk = randint(1, 1000)

    def test_list_url_is_resolved(self):
        url = reverse('products:products')
        self.assertEquals(resolve(url).func.view_class, views.ProductsList)

    def test_show_url_is_resolved(self):
        url = reverse('products:product', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func.view_class, views.ShowProduct)

    def test_add_url_is_resolved(self):
        url = reverse('products:add_product')
        self.assertEquals(resolve(url).func.view_class, views.AddProduct)

    def test_update_url_is_resolved(self):
        url = reverse('products:update_product', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func.view_class, views.UpdateProduct)
