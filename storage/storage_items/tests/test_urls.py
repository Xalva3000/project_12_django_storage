from random import randint

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from storage_items import views


class TestUrls(SimpleTestCase):

    def setUp(self) -> None:
        self.pk = randint(1, 1000)

    def test_list_url_is_resolved(self):
        # path('storage_items/', views.StorageItemsList.as_view(), name='storage_items'),
        url = reverse('storage_items:storage_items')
        self.assertEquals(resolve(url).func.view_class, views.StorageItemsList)
