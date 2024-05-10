from random import randint

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from storage_items import views


# urlpatterns = [
#     path('not_zero/', views.StorageItemsList.as_view(), name='not_zero'),
#     path('available/', views.StorageItemsAvailableList.as_view(), name='available'),
# ]

class TestUrls(SimpleTestCase):

    def setUp(self) -> None:
        self.pk = randint(1, 1000)

    def test_list_url_is_resolved(self):
        url = reverse('storage_items:not_zero')
        self.assertEquals(resolve(url).func.view_class, views.StorageItemsList)

    def test_available_list_url_is_resolved(self):
        url = reverse('storage_items:available')
        self.assertEquals(resolve(url).func.view_class, views.StorageItemsAvailableList)
