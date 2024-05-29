from http import HTTPStatus
from pprint import pprint
from random import choice, seed

from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.test import TestCase, Client
from django.urls import reverse
from faker import Faker

from storage_items.models import StorageItem
from products.utils import menu, tools

from products.models import Product


# fake = Faker(['ru_RU'])
# Faker.seed(1)


class TestStorageItemsView(TestCase):
    # fixtures = ['storage_item_contractor.json']

    # class StorageItemsList(LoginRequiredMixin, DataMixin, ListView):
    #     template_name = 'storage_items/storage_items.html'
    #     context_object_name = 'storage_items'
    #     # allow_empty = False
    #     title_page = 'Склад'
    #     category_page = 'storage_items'
    #     paginate_by = 100
    #
    #     def get_queryset(self):
    #         return StorageItem.not_zero.annotate(weight_available=Sum(F('weight') * F('available')),
    #                                              weight_stored=Sum(F('weight') * F('stored'))).order_by('product__fish', 'price')

    def setUp(self) -> None:
        seed(1)
        self.products = [Product.objects.create(fish=num) for num in range(1, 100)]
        self.weights = (1,15,18,20,22,25)
        self.prices = range(300, 800, 100)
        [StorageItem.objects.get_or_create(
            product=choice(self.products),
            weight=choice(self.weights),
            price=choice(self.prices),
            available=100) for _ in range(1000)]
        self.client = Client()
        self.storage_item_url = reverse("storage_items:not_zero")
        self.queryset = StorageItem.not_zero.annotate(weight_available=Sum(F('weight') * F('available')),
                                                      weight_stored=Sum(F('weight') * F('stored'))).order_by('product__fish', 'price')

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    def test_storage_item_list_GET_login(self):
        response = self.client.get(self.storage_item_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "storage_items/storage_items.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Склад')
        self.assertEqual(response.context_data["tools"], tools["storage_items"])
        self.assertEqual(response.context_data["paginator"].per_page, 100)
        self.assertTrue(response.context_data["is_paginated"])
        self.assertEqual(response.context_data["storage_items"].count(), 100)
        self.assertEqual(self.queryset.count(), 834)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["storage_items"][:100], self.queryset[:100])

    def test_storage_item_list_GET_login_page_2(self):
        page = 2
        paginate_by = 100
        response = self.client.get(self.storage_item_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, 100)
        self.assertTrue(response.context_data["is_paginated"])
        self.assertQuerySetEqual(response.context_data["storage_items"], self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_storage_item_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.storage_item_url
        response = self.client.get(self.storage_item_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)


class TestStorageItemsAvailableView(TestCase):
    # fixtures = ['storage_item_contractor.json']

    # class StorageItemsAvailableList(LoginRequiredMixin, DataMixin, ListView):
    #     template_name = 'storage_items/storage_items.html'
    #     context_object_name = 'storage_items'
    #     title_page = 'Склад'
    #     category_page = 'storage_items'
    #     paginate_by = 100
    #
    #     def get_queryset(self):
    #         return StorageItem.sellable.annotate(weight_available=Sum(F('weight') * F('available')),
    #                                              weight_stored=Sum(F('weight') * F('stored'))).order_by('product__fish', 'price')

    def setUp(self) -> None:
        seed(1)
        self.products = [Product.objects.create(fish=num) for num in range(1, 100)]
        self.weights = (1, 15, 18, 20, 22, 25)
        self.prices = range(300, 800, 100)
        [StorageItem.objects.get_or_create(
            product=choice(self.products),
            weight=choice(self.weights),
            price=choice(self.prices),
            available=100) for _ in range(1000)]
        self.client = Client()
        self.storage_item_url = reverse("storage_items:available")
        self.queryset = StorageItem.sellable.annotate(weight_available=Sum(F('weight') * F('available')),
                                                      weight_stored=Sum(F('weight') * F('stored'))).order_by('product__fish', 'price')

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    def test_storage_item_list_GET_login(self):
        paginate_by = 100
        response = self.client.get(self.storage_item_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "storage_items/storage_items.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Склад')
        self.assertEqual(response.context_data["tools"], tools["storage_items"])
        self.assertEqual(response.context_data["paginator"].per_page, paginate_by)
        self.assertTrue(response.context_data["is_paginated"])
        self.assertEqual(response.context_data["storage_items"].count(), paginate_by)
        self.assertEqual(self.queryset.count(), 834)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["storage_items"][:paginate_by], self.queryset[:paginate_by])

    def test_storage_item_list_GET_login_page_2(self):
        page = 2
        paginate_by = 100
        response = self.client.get(self.storage_item_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, paginate_by)
        self.assertTrue(response.context_data["is_paginated"])
        self.assertQuerySetEqual(response.context_data["storage_items"], self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_storage_item_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.storage_item_url
        response = self.client.get(self.storage_item_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)

