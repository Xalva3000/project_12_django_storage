from random import randint

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from contractors import views


class TestUrls(SimpleTestCase):
    def setUp(self) -> None:
        self.pk = randint(1, 1000)

    def test_list_url_is_resolved(self):
        #     path("", views.ContractorsList.as_view(), name='contractors'),
        url = reverse('contractors:contractors')
        self.assertEquals(resolve(url).func.view_class, views.ContractorsList)

    def test_show_url_is_resolved(self):
        #     path("<int:pk>/", views.ShowContractor.as_view(), name='contractor'),
        url = reverse('contractors:contractor', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func.view_class, views.ShowContractor)

    def test_add_url_is_resolved(self):
        #     path("add_contractor/", views.AddContractor.as_view(), name='add_contractor'),
        url = reverse('contractors:add_contractor')
        self.assertEquals(resolve(url).func.view_class, views.AddContractor)

    def test_update_url_is_resolved(self):
        #     path("update/<int:pk>/", views.UpdateContractor.as_view(), name='update_contractor'),
        url = reverse('contractors:update_contractor', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func.view_class, views.UpdateContractor)
