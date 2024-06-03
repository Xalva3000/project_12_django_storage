from datetime import date
from http import HTTPStatus
from pprint import pprint
from random import seed, choice
from time import sleep

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase, Client
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from faker import Faker

from products.utils import contract_re_map, insert_action_notification, menu, tools
from contracts.models import Contract, Payment
from storage_items.models import StorageItem
from products.models import Product
from contractors.models import Contractor
from contracts.models import Specification



class TestReserveSwitch(TestCase):
    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')


        self.queryset = Contract.objects.filter(Q(date_delete__isnull=True), Q(date_plan=date.today())).order_by('-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME) for _ in range(22)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]
        self.existing_pk = 1
        self.not_existing_pk = 100

        # @login_required
        # def switch_reserve_by_contract_id(request, pk):
        #     contract = get_object_or_404(Contract, pk=pk)
        #     if contract.date_delete:
        #         uri = reverse('contracts:contracts_deleted')
        #         return redirect(uri)
        #     notify_tasker({'pk': pk})
        #     re = contract_re_map(contract)
        #     specifications = contract.specifications.all()
        #     operation = False
        #     stage = 'reserve'
        #     if specifications.count() > 0:
        #         if contract.contract_type == Contract.ContractType.INCOME:
        #             if re == '00':
        #                 operation = 'apply'
        #                 switch_income_reserve_stage(contract=contract, operation=operation)
        #             elif re == '10':
        #                 operation = 'cancel'
        #                 switch_income_reserve_stage(contract=contract, operation=operation)
        #         else:
        #             if re == '10':
        #                 operation = 'cancel'
        #                 switch_outcome_stage(contract=contract, stage=stage, operation=operation)
        #                 contract.reserved = False
        #
        #             elif re == '00':
        #                 operation = 'apply'
        #                 switch_outcome_stage(contract=contract, stage=stage, operation=operation)
        #                 contract.reserved = True
        #
        #     if operation:
        #         action = 'reserved' if operation == 'apply' else 'unreserved'
        #         insert_action_notification(contract=contract, action=action)
        #         contract.save()
        #
        #     uri = reverse('contracts:contract', kwargs={'pk': pk})
        #     return redirect(uri)


    def test_switch_reserve_new_si_login(self):
        self.assertFalse(Contract.objects.get(pk=1).reserved)
        path = reverse('contracts:contract_reserve', args=[self.existing_pk])

        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertTrue(Contract.objects.get(pk=1).reserved)

        self.assertEqual(c1.specifications.all().count(), StorageItem.objects.all().count())
        spec = c1.specifications.all()[0]
        si = StorageItem.objects.all()[0]

        self.assertEqual(spec.product, si.product)
        self.assertEqual(spec.quantity, si.available)
        self.assertEqual(spec.price, si.price)
        self.assertEqual(si.stored, 0)

    def test_switch_reserve_two_new_si_login(self):
        contract = Contract.objects.get(pk=1)
        Specification.objects.create(contract=contract, product=self.products[0],
                                     variable_weight=18, price=200, quantity=1000)
        self.assertFalse(contract.reserved)
        path = reverse('contracts:contract_reserve', args=[self.existing_pk])

        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertTrue(Contract.objects.get(pk=1).reserved)

        self.assertEqual(c1.specifications.all().count(), StorageItem.objects.all().count())
        spec1 = c1.specifications.all()[0]
        si1 = StorageItem.objects.all()[0]

        self.assertEqual(spec1.product, si1.product)
        self.assertEqual(spec1.quantity, si1.available)
        self.assertEqual(spec1.price, si1.price)
        self.assertEqual(si1.stored, 0)

        spec2 = c1.specifications.all()[1]
        si2 = StorageItem.objects.all()[1]

        self.assertEqual(spec2.product, si2.product)
        self.assertEqual(spec2.quantity, si2.available)
        self.assertEqual(spec2.price, si2.price)
        self.assertEqual(si2.stored, 0)

    def test_switch_reserve_new_si_plus_old_si_login(self):
        contract = Contract.objects.get(pk=1)
        Specification.objects.create(contract=contract, product=self.products[0],
                                     variable_weight=18, price=200, quantity=1000)
        StorageItem.objects.create(product=self.products[0], weight=18, price=200, available=500, stored=500)
        self.assertFalse(contract.reserved)
        path = reverse('contracts:contract_reserve', args=[self.existing_pk])

        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertTrue(Contract.objects.get(pk=1).reserved)

        # print(c1.specifications.all())
        # print(StorageItem.objects.all())

        self.assertEqual(c1.specifications.all().count(), StorageItem.objects.all().count())
        spec1 = c1.specifications.all()[0]
        si1 = StorageItem.objects.all()[1]

        self.assertEqual(spec1.product, si1.product)
        self.assertEqual(spec1.quantity, si1.available)
        self.assertEqual(spec1.price, si1.price)
        self.assertEqual(si1.stored, 0)

        spec2 = c1.specifications.all()[1]
        si2 = StorageItem.objects.all()[0]

        self.assertEqual(spec2.product, si2.product)
        self.assertEqual(spec2.quantity, si2.available-500)
        self.assertEqual(spec2.price, si2.price)
        self.assertEqual(si2.stored, 500)

    def test_switch_reserve_on_already_reserved_contract(self):
        contract = Contract.objects.get(pk=self.existing_pk)
        self.assertFalse(StorageItem.objects.filter(price=200).exists())
        Specification.objects.create(contract=contract, product=self.products[0],
                                     variable_weight=18, price=200, quantity=1000)
        self.client.get(reverse('contracts:contract_reserve', args=[self.existing_pk]))
        self.assertTrue(Contract.objects.get(pk=self.existing_pk).reserved)

        self.assertTrue(StorageItem.objects.filter(price=200).exists())
        self.assertEqual(StorageItem.objects.filter(price=200)[0].available, 1000)
        path = reverse('contracts:contract_reserve', args=[self.existing_pk])

        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertFalse(Contract.objects.get(pk=1).reserved)
        self.assertEqual(StorageItem.objects.filter(price=200)[0].available, 0)


    def test_switch_login_not_existing_pk(self):
        path = reverse('contracts:contract_reserve', args=[self.not_existing_pk])
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_no_login_redirect(self):
        path = reverse('contracts:contract_reserve', args=[self.existing_pk])
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + path

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)



class TestExecutionSwitch(TestCase):
    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')


        self.queryset = Contract.objects.filter(Q(date_delete__isnull=True), Q(date_plan=date.today())).order_by('-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME) for _ in range(22)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]
        self.existing_pk = 1
        self.not_existing_pk = 100

        # @login_required
        # def switch_execution_by_contract_id(request, pk):
        #     contract = get_object_or_404(Contract, pk=pk)
        #     if contract.date_delete:
        #         uri = reverse('contracts:contracts_deleted')
        #         return redirect(uri)
        #     specifications = contract.specifications.all()
        #     re = contract_re_map(contract)
        #     operation = False
        #     stage = 'execution'
        #     if specifications and re in ('10', '11'):
        #
        #         if contract.contract_type == Contract.ContractType.INCOME:
        #             if re == '10':
        #                 operation = 'apply'
        #                 switch_income_execution_stage(contract=contract, operation=operation)
        #             elif re == '11':
        #                 operation = 'cancel'
        #                 switch_income_execution_stage(contract=contract, operation=operation)
        #         if contract.contract_type == Contract.ContractType.OUTCOME:
        #             if re == '10':
        #                 operation = 'apply'
        #                 switch_outcome_stage(contract=contract, stage=stage, operation=operation)
        #                 # contract.date_plan = datetime.date.today()
        #                 contract.date_execution = datetime.date.today()
        #             elif re == '11':
        #                 operation = 'cancel'
        #                 switch_outcome_stage(contract=contract, stage=stage, operation=operation)
        #                 contract.date_execution = None
        #
        #     if operation:
        #         action = 'executed' if operation == 'apply' else 'unexecuted'
        #         insert_action_notification(contract=contract, action=action)
        #         contract.executed = not contract.executed
        #         contract.save()
        #     uri = reverse('contracts:contract', kwargs={'pk': pk})
        #     return redirect(uri)
    def test_switch_execution_login(self):
        self.assertFalse(Contract.objects.get(pk=1).executed)
        self.client.get(reverse('contracts:contract_reserve', args=[self.existing_pk]))

        path = reverse('contracts:contract_execution', args=[self.existing_pk])
        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertTrue(Contract.objects.get(pk=1).executed)

    def test_switch_login_not_reserved_contract(self):
        path = reverse('contracts:contract_execution', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)

    def test_switch_execution_two_new_si_login(self):
        contract = Contract.objects.get(pk=self.existing_pk)
        Specification.objects.create(contract=contract, product=self.products[0],
                                     variable_weight=18, price=200, quantity=1000)
        self.assertFalse(contract.reserved)

        self.client.get(reverse('contracts:contract_reserve', args=[self.existing_pk]))
        self.assertTrue(Contract.objects.get(pk=self.existing_pk).reserved)

        path = reverse('contracts:contract_execution', args=[self.existing_pk])
        response = self.client.get(path)

        c1 = Contract.objects.get(pk=self.existing_pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)


        self.assertEqual(c1.specifications.all().count(), StorageItem.objects.all().count())
        spec1 = c1.specifications.all()[0]
        si1 = StorageItem.objects.all()[0]

        self.assertEqual(spec1.product, si1.product)
        self.assertEqual(si1.available, spec1.quantity)
        self.assertEqual(spec1.price, si1.price)
        self.assertEqual(si1.stored, spec1.quantity)

        spec2 = c1.specifications.all()[1]
        si2 = StorageItem.objects.all()[1]

        self.assertEqual(spec2.product, si2.product)
        self.assertEqual(si2.available, spec2.quantity)
        self.assertEqual(spec2.price, si2.price)
        self.assertEqual(si2.stored, spec2.quantity)

    def test_switch_reserve_new_si_plus_old_si_login(self):
        contract = Contract.objects.get(pk=1)
        Specification.objects.create(contract=contract, product=self.products[0],
                                     variable_weight=18, price=200, quantity=1000)
        StorageItem.objects.create(product=self.products[0], weight=18, price=200, available=500, stored=500)
        self.assertFalse(contract.reserved)
        self.client.get(reverse('contracts:contract_reserve', args=[self.existing_pk]))
        self.assertTrue(Contract.objects.get(pk=self.existing_pk).reserved)


        path = reverse('contracts:contract_execution', args=[self.existing_pk])

        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertTrue(Contract.objects.get(pk=1).reserved)

        # print(c1.specifications.all())
        # print(StorageItem.objects.all())

        self.assertEqual(c1.specifications.all().count(), StorageItem.objects.all().count())
        spec1 = c1.specifications.all()[0]
        si1 = StorageItem.objects.all()[1]

        self.assertEqual(spec1.product, si1.product)
        self.assertEqual(spec1.quantity, si1.available)
        self.assertEqual(spec1.price, si1.price)
        self.assertEqual(si1.stored, spec1.quantity)

        spec2 = c1.specifications.all()[1]
        si2 = StorageItem.objects.all()[0]

        self.assertEqual(spec2.product, si2.product)
        self.assertEqual(spec2.quantity, si2.available - 500)
        self.assertEqual(spec2.price, si2.price)
        self.assertEqual(spec2.quantity, si2.stored - 500)

    def test_switch_reserve_on_already_executed_contract(self):
        contract = Contract.objects.get(pk=self.existing_pk)
        self.assertFalse(StorageItem.objects.filter(price=200).exists())
        Specification.objects.create(contract=contract, product=self.products[0],
                                     variable_weight=18, price=200, quantity=1000)
        self.client.get(reverse('contracts:contract_reserve', args=[self.existing_pk]))
        self.assertTrue(Contract.objects.get(pk=self.existing_pk).reserved)

        self.assertTrue(StorageItem.objects.filter(price=200).exists())
        self.assertEqual(StorageItem.objects.filter(price=200)[0].available, 1000)
        self.assertEqual(StorageItem.objects.filter(price=200)[0].stored, 0)

        self.client.get(reverse('contracts:contract_execution', args=[self.existing_pk]))
        self.assertTrue(Contract.objects.get(pk=1).reserved)
        self.assertTrue(Contract.objects.get(pk=1).executed)
        self.assertEqual(StorageItem.objects.filter(price=200)[0].available, 1000)
        self.assertEqual(StorageItem.objects.filter(price=200)[0].stored, 1000)

        path = reverse('contracts:contract_execution', args=[self.existing_pk])
        response = self.client.get(path)

        c1 = Contract.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertTrue(Contract.objects.get(pk=1).reserved)
        self.assertFalse(Contract.objects.get(pk=1).executed)
        self.assertEqual(StorageItem.objects.filter(price=200)[0].available, 1000)
        self.assertEqual(StorageItem.objects.filter(price=200)[0].stored, 0)

    def test_switch_login_not_existing_pk(self):
        path = reverse('contracts:contract_execution', args=[self.not_existing_pk])

        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_no_login_redirect(self):
        path = reverse('contracts:contract_execution', args=[self.existing_pk])
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + path

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)





#
# @login_required
# def switch_payment_by_contract_id(request, pk):
#     contract = get_object_or_404(Contract, pk=pk)
#     if contract.date_delete:
#         uri = reverse('contracts:contracts_deleted')
#         return redirect(uri)
#     if contract.specifications.all():
#         action = 'unpaid' if contract.paid else 'paid'
#         contract.paid = not contract.paid
#         contract.save()
#         insert_action_notification(contract=contract, action=action)
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)
#
#

#
#
# @login_required
# def delete_contract(request, pk):
#     contract = Contract.objects.get(pk=pk)
#     re = contract_re_map(contract)
#     action = False
#     if re == '00' and not contract.date_delete:
#         action = 'deleted'
#         contract.date_delete = datetime.date.today()
#     elif re == '00' and contract.date_delete:
#         action = 'undeleted'
#         contract.date_delete = None
#
#     if action:
#         insert_action_notification(contract=contract, action=action)
#         contract.save()
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)
#
#
# def change_manager_share(request, pk):
#     try:
#         new_share = abs(int(request.POST.get('new_share', 0)))
#         contract = Contract.objects.get(pk=pk)
#         contract.manager_share = new_share
#         contract.save()
#     except ValueError:
#         pass
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)
#
#
# def change_note(request, pk):
#     new_note = request.POST.get('new_note', '')
#     contract = Contract.objects.get(pk=pk)
#     contract.note = new_note
#     contract.save()
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)
#
#
# def add_payment(request, pk):
#     try:
#         action = 'new_payment'
#         amount = int(request.POST.get(action, 0))
#         if amount == 0:
#             raise ValueError
#         payment = Payment.objects.create(contract_id=pk, amount=amount)
#         payment.save()
#         insert_action_notification(contract=pk, action=action, extra_info=amount)
#     except ValueError:
#         pass
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)

