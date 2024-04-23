from random import randint

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from contracts import views, execution


class TestUrls(SimpleTestCase):
    def setUp(self) -> None:
        self.pk = randint(1, 1000)

    def test_list_url_is_resolved(self):
        # path("", views.ContractsMinimalList.as_view(), name='contracts'),
        url = reverse('contracts:contracts')
        self.assertEquals(resolve(url).func.view_class, views.ContractsMinimalList)

    def test_extended_list_url_is_resolved(self):
        # path("plus/", views.ContractsPlusList.as_view(), name='contracts_plus'),
        url = reverse('contracts:contracts_plus')
        self.assertEquals(resolve(url).func.view_class, views.ContractsPlusList)

    def test_deleted_list_url_is_resolved(self):
        # path("deleted/", views.DeletedContractsMinimalList.as_view(), name='contracts_deleted'),
        url = reverse('contracts:contracts_deleted')
        self.assertEquals(resolve(url).func.view_class, views.DeletedContractsMinimalList)

    def test_show_url_is_resolved(self):
        # path("<int:pk>/", views.ShowContract.as_view(), name='contract'),
        url = reverse('contracts:contract', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func.view_class, views.ShowContract)

    def test_add_url_is_resolved(self):
        # path("add_contract/", views.AddContract.as_view(), name='add_contract'),
        url = reverse('contracts:add_contract')
        self.assertEquals(resolve(url).func.view_class, views.AddContract)

    def test_update_url_is_resolved(self):
        # path("<int:pk>/update/", views.UpdateContract.as_view(), name='contract_update'),
        url = reverse('contracts:contract_update', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func.view_class, views.UpdateContract)

    def test_add_specifications_url_is_resolved(self):
        # path('<int:pk>/add_specifications/',  views.add_specifications, name='add_specifications'),
        url = reverse('contracts:add_specifications', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, views.add_specifications)

    def test_switch_reserve_url_is_resolved(self):
        # path('<int:pk>/reserve/', execution.switch_reserve_by_contract_id, name='contract_reserve'),
        url = reverse('contracts:contract_reserve', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.switch_reserve_by_contract_id)


    def test_switch_payment_url_is_resolved(self):
        # path('<int:pk>/payment/', execution.switch_payment_by_contract_id, name='contract_payment'),
        url = reverse('contracts:contract_payment', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.switch_payment_by_contract_id)

    def test_switch_execution_url_is_resolved(self):
        # path('<int:pk>/execute/', execution.switch_execution_by_contract_id, name='contract_execution'),
        url = reverse('contracts:contract_execution', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.switch_execution_by_contract_id)

    def test_delete_url_is_resolved(self):
        # path('<int:pk>/delete/', execution.delete_contract, name='contract_delete'),
        url = reverse('contracts:contract_delete', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.delete_contract)

    def test_change_manager_share_is_resolved(self):
        # path('<int:pk>/change_manager_share/', execution.change_manager_share, name='change_manager_share'),
        url = reverse('contracts:change_manager_share', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.change_manager_share)

    def test_change_note_is_resolved(self):
        # path('<int:pk>/change_note/', execution.change_note, name='change_note'),
        url = reverse('contracts:change_note', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.change_note)

    def test_add_payment_is_resolved(self):
        # path('<int:pk>/add_payment/', execution.add_payment, name='add_payment'),
        url = reverse('contracts:add_payment', kwargs={'pk': self.pk})
        self.assertEquals(resolve(url).func, execution.add_payment)
