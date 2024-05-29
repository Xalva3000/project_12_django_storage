from datetime import date
from http import HTTPStatus
from pprint import pprint

from random import seed, choice

from django.contrib.auth.models import User
from django.db.models import Q

from django.test import TestCase, Client
from django.urls import reverse
from faker import Faker

from products.models import Product
from contractors.models import Contractor
from contracts.models import Contract, Specification

from products.utils import tools, menu

from contracts.filters import ContractFilter


#
# class ContractsMinimalList(LoginRequiredMixin, DataMixin, ListView):
#     model = Contract
#     template_name = "contracts/contracts_minimal.html"
#     context_object_name = "contracts"
#     title_page = "Контракты"
#     category_page = "contracts"
#     paginate_by = 50
#     # queryset = Contract.objects.filter(date_delete__isnull=True).order_by('-date_plan', '-pk')
#
#     queryset = Contract.objects.filter(
#         date_delete__isnull=True
#     ).annotate(
#         total_weight=SubquerySum(F('specifications__variable_weight') * F('specifications__quantity')),
#         total_sum=SubquerySum(F('specifications__variable_weight') * F('specifications__quantity') * F('specifications__price')),
#         total_payments=SubquerySum(F('payments__amount'))).order_by('-date_plan', '-pk')
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         self.filterset = ContractFilter(self.request.GET, queryset=queryset)
#         return self.filterset.qs.distinct()
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = self.filterset.form
#         context['query_length'] = self.get_queryset().count()
#         context['income_stats'] = self.get_stats(self.get_queryset(), Contract.ContractType.INCOME)
#         context['outcome_stats'] = self.get_stats(self.get_queryset(), Contract.ContractType.OUTCOME)
#         return context
#
#     @staticmethod
#     def get_stats(queryset, contract_type=Contract.ContractType.INCOME):
#         qs = queryset.filter(contract_type=contract_type)
#         result = {}
#         weight = qs.aggregate(w=Sum(F('total_weight')))
#         result['weight'] = weight['w']
#         cost = qs.aggregate(s=Sum(F('total_sum')))
#         result['cost'] = cost['s']
#         payments = qs.aggregate(p=Sum(F('total_payments')))
#         result['payments'] = payments['p']
#
#         bonuses_qs = qs.values('id', 'manager__username', 'manager_share')
#         lst = []
#         bonuses = {}
#         for dct in bonuses_qs:
#             if dct['id'] not in lst and dct['manager_share']:
#                 lst.append(dct['id'])
#                 bonuses[dct['manager__username']] = bonuses.get(dct['manager__username'], 0) + dct['manager_share']
#
#         result['bonuses'] = bonuses
#
#         if contract_type == Contract.ContractType.OUTCOME:
#             expenses = [c.specifications.aggregate(cost=Sum(F('quantity') * F('variable_weight') * F('storage_item__price'))) for c in qs if c.specifications.all()]
#             result['expenses'] = sum([dct['cost'] for dct in expenses])
#             if result['expenses']:
#                 result['expected'] = result['cost'] - result['expenses']
#         return result
#


class TestContractsTodayListView(TestCase):

    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')
        self.today_list_url = reverse('contracts:contracts_today')
        self.queryset = Contract.objects.filter(Q(date_delete__isnull=True), Q(date_plan=date.today())).order_by('-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME) for _ in range(22)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]

    # class ContractsTodayList(LoginRequiredMixin, DataMixin, ListView):
    #     model = Contract
    #     template_name = "contracts/contracts_today.html"
    #     context_object_name = "contracts"
    #     title_page = "Отгрузки сегодня"
    #     category_page = "contracts"
    #     paginate_by = 20
    #
    def test_GET_login(self):
        response = self.client.get(self.today_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "contracts/contracts_today.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Отгрузки сегодня')
        self.assertEqual(response.context_data["tools"], tools["contracts"])
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(response.context_data["contracts"].count(), 20)
        self.assertEqual(self.queryset.count(), 22)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["contracts"][:20], self.queryset[:20])

    def test_contractors_list_GET_login_page_2(self):
        page = 2
        paginate_by = 20
        response = self.client.get(self.today_list_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertQuerySetEqual(response.context_data["contracts"],
                                 self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_contractors_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.today_list_url
        response = self.client.get(self.today_list_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)


class TestPlusListView(TestCase):
    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')
        self.today_list_url = reverse('contracts:contracts_plus')
        self.queryset = Contract.objects.filter(Q(date_delete__isnull=True), Q(date_plan=date.today())).order_by('-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME) for _ in range(22)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]

    # class ContractsPlusList(LoginRequiredMixin, DataMixin, ListView):
    #     model = Contract
    #     template_name = "contracts/contracts_plus.html"
    #     context_object_name = "contracts"
    #     title_page = "Контракты+"
    #     category_page = "contracts"
    #     paginate_by = 10
    #     queryset = Contract.objects.filter(date_delete__isnull=True).order_by('-date_plan', '-pk')

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     self.filterset = ContractFilter(self.request.GET, queryset=queryset)
    #     return self.filterset.qs.distinct()
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = self.filterset.form
    #     context['mod'] = 'plus'
    #     return context
    def test_GET_login(self):
        response = self.client.get(self.today_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "contracts/contracts_plus.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Контракты+')
        self.assertEqual(response.context_data["tools"], tools["contracts"])
        self.assertEqual(response.context_data["paginator"].per_page, 10)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(response.context_data["contracts"].count(), 10)
        self.assertEqual(self.queryset.count(), 22)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["contracts"][:10], self.queryset[:10])

    def test_contractors_list_GET_login_page_2(self):
        page = 2
        paginate_by = 10
        response = self.client.get(self.today_list_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, paginate_by)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertQuerySetEqual(response.context_data["contracts"],
                                 self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_contractors_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.today_list_url
        response = self.client.get(self.today_list_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)


class TestDeletedListView(TestCase):

    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')
        self.today_list_url = reverse('contracts:contracts_deleted')
        self.queryset = Contract.objects.filter(date_delete__isnull=False).order_by('-date_plan', '-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME,
                                                  date_delete=date.today()) for _ in range(52)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]

    def test_GET_login(self):
        response = self.client.get(self.today_list_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "contracts/contracts_deleted.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Удаленные контракты')
        self.assertEqual(response.context_data["tools"], tools["contracts"])
        self.assertEqual(response.context_data["paginator"].per_page, 50)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(response.context_data["contracts"].count(), 50)
        self.assertEqual(response.context_data["mod"], 'deleted')

        self.assertEqual(self.queryset.count(), 52)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["contracts"][:50], self.queryset[:50])
        # request = QueryDict({'contract_type': ['income'], 'contractor__name': [''], 'date_plan_min': [''], 'date_plan_max': [''], 'specifications__product__fish': [''], 'specifications__storage_item__product__fish': [''], 'reserved': ['unknown'], 'paid': ['unknown'], 'executed': ['unknown'], 'note': [''], 'date_delete': [''], 'manager__username': ['']})

        # self.assertEquals(type(response.context_data['form']), type(ContractFilter().form))

    # class DeletedContractsMinimalList(LoginRequiredMixin, DataMixin, ListView):
    #     model = Contract
    #     template_name = "contracts/contracts_deleted.html"
    #     context_object_name = "contracts"
    #     title_page = "Удаленные контракты"
    #     category_page = "contracts"
    #     paginate_by = 50
    #     queryset = Contract.objects.filter(date_delete__isnull=False).order_by('-date_plan', '-pk')
    #
    #     def get_queryset(self):
    #         queryset = super().get_queryset()
    #         self.filterset = ContractFilter(self.request.GET, queryset=queryset)
    #         return self.filterset.qs.distinct()
    #
    #     def get_context_data(self, **kwargs):
    #         context = super().get_context_data(**kwargs)
    #         context['form'] = self.filterset.form
    #         context['mod'] = 'deleted'
    #         return context

    def test_contractors_list_GET_login_page_2(self):
        page = 2
        paginate_by = 50
        response = self.client.get(self.today_list_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, paginate_by)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertQuerySetEqual(response.context_data["contracts"],
                                 self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_contractors_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.today_list_url
        response = self.client.get(self.today_list_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)


class TestShowContractView(TestCase):
    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.queryset = Contract.objects.filter(date_delete__isnull=False).order_by('-date_plan', '-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME,
                                                  date_delete=date.today()) for _ in range(10)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]
        self.existing_pk = 1
        self.not_existing_pk = 100

    # class ShowContract(LoginRequiredMixin, DataMixin, DetailView):
    #     model = Contract
    #     template_name = 'contracts/contract.html'
    #     context_object_name = 'contract'
    #     pk_url_kwarg = 'pk'
    #     title_page = 'Детали контракта'
    #     category_page = 'contracts'
    #
    #     def get_object(self, queryset=None):
    #         return get_object_or_404(Contract.objects, pk=self.kwargs[self.pk_url_kwarg])
    #
    #     def get_context_data(self, **kwargs):
    #         context = super().get_context_data(**kwargs)
    #         contract = Contract.objects.get(pk=self.kwargs[self.pk_url_kwarg])
    #         if contract.specifications.all():
    #             tonnage = contract.specifications.aggregate(ton=Sum(F('quantity') * F('variable_weight')))
    #             context['tonnage'] = tonnage['ton']
    #             total = contract.specifications.aggregate(summa=Sum(F('quantity') * F('variable_weight') * F('price')))
    #             context['total'] = total['summa']
    #             if contract.contract_type == Contract.ContractType.OUTCOME:
    #                 purchase = contract.specifications.aggregate(summa=Sum(F('quantity') * F('variable_weight') * F('storage_item__price')))
    #                 context['purchase'] = purchase['summa']
    #                 context['profit'] = total['summa'] - purchase['summa']
    #
    #         payments = contract.payments.all()
    #         if payments:
    #             context['payments'] = payments
    #             payments_sum = contract.payments.aggregate(summa=Sum('amount'))
    #             context['payments_sum'] = payments_sum['summa']
    #             context['balance'] = total['summa'] - payments_sum['summa']
    #
    #         return context

    def test_view_parameters(self):
        c1 = Contract.objects.get(pk=self.existing_pk)
        path = reverse('contracts:contract', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contracts/contract.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(c1.contractor, response.context_data['contract'].contractor)
        self.assertEqual(response.context_data["title"], 'Детали контракта')
        self.assertEqual(response.context_data["tools"], tools["contracts"])
        self.assertIn('contract', response.context_data)
        self.assertEquals(response.context_data['contract'], c1)
        # self.assertEquals(response.context_data['pk_url_kwarg'], 'pk')

    def test_existing_object(self):
        c1 = Contract.objects.get(pk=self.existing_pk)
        path = reverse('contracts:contract', args=[self.existing_pk])
        response = self.client.get(path)

        self.assertEqual(response.context_data['contract'], c1)
        self.assertEqual(response.context_data['contract'].id, c1.pk)
        self.assertEqual(response.context_data['contract'].contractor, c1.contractor)
        self.assertEqual(response.context_data['contract'].date_plan, c1.date_plan)
        self.assertEqual(response.context_data['contract'].contract_type, c1.contract_type)
        self.assertEqual(response.context_data['contract'].reserved, c1.reserved)
        self.assertEqual(response.context_data['contract'].paid, c1.paid)
        self.assertEqual(response.context_data['contract'].executed, c1.executed)
        self.assertEqual(response.context_data['contract'].note, c1.note)
        self.assertEqual(response.context_data['contract'].date_create, c1.date_create)
        self.assertEqual(response.context_data['contract'].date_delete, c1.date_delete)
        self.assertEqual(response.context_data['contract'].date_execution, c1.date_execution)
        self.assertEqual(response.context_data['contract'].manager_share, c1.manager_share)
        self.assertEqual(response.context_data['contract'].manager, c1.manager)

    def test_not_existing_object(self):
        path = reverse('contracts:contract', args=[self.not_existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)

    def test_redirect(self):
        path = reverse('contracts:contract', args=[self.existing_pk])
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + path

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)


class TestAddContractView(TestCase):
    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.path = reverse('contracts:add_contract')
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')
        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]

        self.existing_pk = 1
        self.not_existing_pk = 100

        self.data = {
            'empty': {},
            'minimal': {
                'contractor': 1,
                'date_plan': date.today(),
                'contract_type': Contract.ContractType.INCOME,
            },
            'full': {
                'contractor': 1,
                'date_plan': date.today(),
                'contract_type': Contract.ContractType.INCOME,
                'note': 'авто ГАЗель 251'
            },
        }

    # class AddContract(LoginRequiredMixin, DataMixin, CreateView):
    #     form_class = AddContractForm
    #     template_name = 'contracts/add_contract.html'
    #     title_page = 'Добавление контракта'
    #     category_page = 'contracts'
    #
    #     def get_success_url(self):
    #         insert_action_notification(contract=self.object.id, action='created', extra_info=self.request.user)
    #         return reverse("contracts:contract", args=[self.object.id,])
    #
    #     def form_valid(self, form):
    #         contract = form.save(commit=False)
    #         contract.manager = self.request.user
    #         return super().form_valid(form)

    def test_view_parameters(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contracts/add_contract.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Добавление контракта')
        self.assertEqual(response.context_data["tools"], tools["contracts"])

    def test_no_login_redirection(self):
        redirect_uri = reverse('users:login') + '?next=' + self.path

        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)

    def test_no_login_object_creation(self):
        redirect_uri = reverse('users:login') + '?next=' + self.path
        self.client.logout()
        response = self.client.post(self.path, data=self.data['minimal'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(Contract.objects.count(), 0)

    def test_valid_minimal_object_creation(self):
        response = self.client.post(self.path, data=self.data['minimal'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contracts:contract', args=[1]))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contract.objects.count(), 1)

    def test_empty_object_creation(self):
        response = self.client.post(self.path, data=self.data['empty'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contracts/add_contract.html")
        self.assertEqual(Contract.objects.count(), 0)

    def test_full_object_creation(self):
        response = self.client.post(self.path, data=self.data['full'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contracts:contract', args=[1]))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contract.objects.count(), 1)


class TestUpdateContractView(TestCase):

    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.queryset = Contract.objects.filter(date_delete__isnull=False).order_by('-date_plan', '-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME,
                                                  date_delete=date.today()) for _ in range(10)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]

        self.existing_pk = 1
        self.not_existing_pk = 100

        self.data = {
            'empty': {
                'contractor': '',
                'date_plan': '',
                'contract_type': '',
            },
            'minimal': {
                'contractor': 1,
                'date_plan': date.today(),
                'contract_type': Contract.ContractType.INCOME,
            },
            'full': {
                'contractor': 2,
                'date_plan': date.today(),
                'contract_type': Contract.ContractType.INCOME,
                'note': 'авто ГАЗель 251'
            },
        }

    # class UpdateContract(LoginRequiredMixin, DataMixin, UpdateView):
    #     model = Contract
    #     form_class = UpdateContractForm
    #     template_name = 'contracts/add_contract.html'
    #     title_page = 'Редактирование контракта'
    #     category_page = 'contracts'
    #
    #     def get_success_url(self):
    #         pk = self.kwargs["pk"]
    #         return reverse('contracts:contract', kwargs={"pk": pk})

    def test_view_parameters(self):
        c1 = Contract.objects.get(pk=self.existing_pk)
        path = reverse('contracts:contract_update', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contracts/add_contract.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(c1.pk, response.context_data['contract'].id)
        self.assertEqual(c1.contractor, response.context_data['contract'].contractor)
        self.assertEqual(response.context_data["title"], 'Редактирование контракта')
        self.assertEqual(response.context_data["tools"], tools["contracts"])
        self.assertIn('contract', response.context_data)
        self.assertEquals(response.context_data['contract'], c1)

    def test_no_login_redirection(self):
        path = reverse('contracts:contract_update', args=[self.existing_pk])
        redirect_uri = reverse('users:login') + '?next=' + path

        self.client.logout()
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)

    #
    def test_no_login_object_update(self):
        path = reverse('contracts:contract_update', args=[self.existing_pk])
        redirect_uri = reverse('users:login') + '?next=' + path
        self.client.logout()
        response = self.client.post(path, data=self.data['minimal'].update({'date_plan': date(2020, 2, 2)}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(Contract.objects.count(), 10)
        c1 = Contract.objects.get(pk=self.existing_pk)
        self.assertNotEquals(c1.date_plan, date(2020, 2, 2))

    def test_valid_minimal_object_update(self):
        path = reverse('contracts:contract_update', args=[self.existing_pk])
        data = {
            'contractor': 1,
            'date_plan': date(2020, 2, 2),
            'contract_type': Contract.ContractType.INCOME,
        }
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contracts:contract', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 10)
        c1 = Contract.objects.get(pk=self.existing_pk)
        self.assertEquals(c1.date_plan, date(2020, 2, 2))
        self.assertEquals(c1.note, '')

    def test_empty_object_update(self):
        path = reverse('contracts:contract_update', args=[self.existing_pk])
        response = self.client.post(path, data=self.data['empty'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contracts/add_contract.html")
        self.assertEqual(Contractor.objects.count(), 10)
        c1 = Contract.objects.get(pk=self.existing_pk)
        self.assertNotEquals(c1.contractor, '')

    def test_full_object_update(self):
        data = {
            'contractor': 2,
            'date_plan': date(2020, 2, 2),
            'contract_type': Contract.ContractType.INCOME,
            'note': 'авто ГАЗель 251'
        }

        path = reverse('contracts:contract_update', args=[self.existing_pk])
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contracts:contract', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 10)
        c1 = Contract.objects.get(pk=self.existing_pk)
        self.assertEquals(c1.contractor, Contractor.objects.get(pk=data['contractor']))
        self.assertEquals(c1.date_plan, data['date_plan'])
        self.assertEquals(c1.contract_type, data['contract_type'])
        self.assertEquals(c1.note, data['note'])


class TestAddSpecificationsView(TestCase):
    def setUp(self) -> None:
        fake = Faker(['ru_RU'])
        Faker.seed(1)
        seed(1)
        self.client = Client()
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.queryset = Contract.objects.filter(date_delete__isnull=False).order_by('-date_plan', '-pk')

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.contractors = [Contractor.objects.create(name=fake.company()) for _ in range(10)]
        self.contracts = [Contract.objects.create(contractor=choice(self.contractors),
                                                  contract_type=Contract.ContractType.INCOME,
                                                  date_delete=date.today()) for _ in range(10)]
        self.specifications = [Specification.objects.create(product=choice(self.products),
                                                            contract=choice(self.contracts))]

        self.existing_pk = 1
        self.not_existing_pk = 100

        self.data = {
            'empty': {
                'contractor': '',
                'date_plan': '',
                'contract_type': '',
            },
            'minimal': {
                'contractor': 1,
                'date_plan': date.today(),
                'contract_type': Contract.ContractType.INCOME,
            },
            'full': {
                'contractor': 2,
                'date_plan': date.today(),
                'contract_type': Contract.ContractType.INCOME,
                'note': 'авто ГАЗель 251'
            },
        }

        self.formset_data_new_spec = {
            # 'csrfmiddlewaretoken': ['B0XQhqzD9dXC91nxF9GVeYJGFN2lNAbjWubWyHGuRPdZgvMZSehYyEUBeC6ATRQT'],
            'specifications-TOTAL_FORMS': ['1'],
            'specifications-INITIAL_FORMS': ['0'],
            'specifications-MIN_NUM_FORMS': ['0'],
            'specifications-MAX_NUM_FORMS': ['1000'],
            'specifications-0-product': ['1'],
            'specifications-0-variable_weight': ['1'],
            'specifications-0-quantity': ['70000'],
            'specifications-0-price': ['120'],
            'specifications-0-contract': ['1'],
            'specifications-0-id': ['']}

        self.formset_data = {
            # 'csrfmiddlewaretoken': ['U2dnGRfMy4NCuw9uRPYeJ3YrJE3TvD7VfwrtX8mDgG3ZB0yW4Uzh3J9mit78BUMv'],
            'specifications-TOTAL_FORMS': ['2'],
            'specifications-INITIAL_FORMS': ['2'],
            'specifications-MIN_NUM_FORMS': ['0'],
            'specifications-MAX_NUM_FORMS': ['1000'],
            'specifications-0-storage_item': ['20'],
            'specifications-0-variable_weight': ['1.00'],
            'specifications-0-quantity': ['2400.00'],
            'specifications-0-price': ['950.00'],
            'specifications-0-contract': ['36'],
            'specifications-0-id': ['53'],
            'specifications-1-storage_item': ['19'],
            'specifications-1-variable_weight': ['1.00'],
            'specifications-1-quantity': ['2400.00'],
            'specifications-1-price': ['1050.00'],
            'specifications-1-contract': ['36'],
            'specifications-1-id': ['54']}

    # @login_required
    # def add_specifications(request, pk):
    #     # формирование группы форм
    #     spec_amount = int(request.POST.get('spec_amount', 3))
    #     contract = get_object_or_404(Contract, pk=pk)
    #     if contract.contract_type == Contract.ContractType.INCOME:
    #         fields = ['product', 'variable_weight', 'quantity', 'price', 'contract']
    #     else:
    #         fields = ['storage_item', 'variable_weight', 'quantity', 'price', 'contract']
    #
    #     SpecificationFormSet = inlineformset_factory(
    #         Contract, Specification,
    #         fields=fields,
    #         extra=spec_amount)
    #     formset = SpecificationFormSet(instance=contract)
    #
    #     # сохранение данных группы форм
    #     if request.method == 'POST' and 'spec_amount' not in request.POST.keys():
    #         formset = SpecificationFormSet(request.POST, instance=contract)
    #         if formset.is_valid():
    #             formset.save()
    #             insert_action_notification(contract=contract, action='new_change')  # сообщение об изменении
    #             uri = reverse('contracts:contract', kwargs={'pk': pk})
    #             return redirect(uri)
    #     context = {'formset': formset, 'contract': contract, 'tools': tools['contracts'], 'menu': menu}
    #     return render(request, 'contracts/add_specifications.html', context)

    def test_view_parameters_get_default(self):
        c1 = Contract.objects.get(pk=self.existing_pk)
        path = reverse('contracts:add_specifications', args=[self.existing_pk])

        response = self.client.get(path)
        # pprint(response.__dict__)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contracts/add_specifications.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(c1.pk, response.context['contract'].id)
        self.assertEqual(c1.contractor, response.context['contract'].contractor)
        self.assertEqual(response.context["tools"], tools["contracts"])
        self.assertIn('contract', response.context)
        self.assertEquals(response.context['contract'], c1)
        self.assertEqual(len(response.context['formset']), 3)
        self.assertEqual(response.context['formset'].instance, c1)

    def test_view_parameters_post_two_new_specs(self):
        c1 = Contract.objects.get(pk=self.existing_pk)
        path = reverse('contracts:add_specifications', args=[self.existing_pk])

        response = self.client.post(path, data={'spec_amount': 2})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contracts/add_specifications.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(c1.pk, response.context['contract'].id)
        self.assertEqual(c1.contractor, response.context['contract'].contractor)
        self.assertEqual(response.context["tools"], tools["contracts"])
        self.assertIn('contract', response.context)
        self.assertEquals(response.context['contract'], c1)
        self.assertEqual(len(response.context['formset']), 2)
        self.assertEqual(response.context['formset'].instance, c1)

    def test_view_parameters_post_new_spec_data(self):
        c1 = Contract.objects.get(pk=self.existing_pk)
        path = reverse('contracts:add_specifications', args=[self.existing_pk])
        redirect_uri = reverse('contracts:contract', args=[c1.pk])

        response = self.client.post(path, data=self.formset_data_new_spec)
        # pprint(response.__dict__)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateNotUsed(response)
        self.assertIsNone(response.context)
        self.assertRedirects(response, redirect_uri)


    def test_no_login_redirection(self):
        path = reverse('contracts:add_specifications', args=[self.existing_pk])
        redirect_uri = reverse('users:login') + '?next=' + path

        self.client.logout()
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)

# <QueryDict: {'csrfmiddlewaretoken': ['At7jk3cCiPddRGj5sItZ4NQsAKu9piqFVXlpBkjt0rtAYaIxFN42ot1n9zyovz5f'], 'specifications-TOTAL_FORMS': ['2'], 'specifications-INITIAL_FO
# RMS': ['2'], 'specifications-MIN_NUM_FORMS': ['0'], 'specifications-MAX_NUM_FORMS': ['1000'], 'specifications-0-product': ['17'], 'specifications-0-variable_weight': ['1
# .00'], 'specifications-0-quantity': ['7000.00'], 'specifications-0-price': ['800.00'], 'specifications-0-contract': ['33'], 'specifications-0-id': ['45'], 'specification
# s-1-product': ['18'], 'specifications-1-variable_weight': ['1.00'], 'specifications-1-quantity': ['7000.00'], 'specifications-1-price': ['700.00'], 'specifications-1-con
# tract': ['33'], 'specifications-1-id': ['46']}>


# Обработка POST-запросов: Удостовериться, что view корректно обрабатывает POST-запросы,
# правильно извлекает данные из форм, и сохраняет данные при условии их валидности.
# Это включает тестирование процесса сохранения данных формы.
#
# Типы Контрактов: Проверить работу view с разными типами контрактов (INCOME и другими).
# Убедиться, что view выбирает правильные поля для формирования группы форм в зависимости от типа контракта.
#
# Создание и Рендеринг Форм: Проверить создание формы с помощью inlineformset_factory и
# убедиться, что формы корректно отображаются на странице. Проверить рендер шаблона
# с корректно переданными контекстами.
#
# Уведомления и Перенаправления: Проверить, что уведомления успешно создаются и
# правильно отображаются, а также что перенаправление пользователя происходит
# на ожидаемую страницу после сохранения данных формы.
#
# Обработка Некорректных Данных: Убедиться, что view правильно обрабатывает
# некорректные данные в формах, выводит соответствующие сообщения об ошибках,
# и не сохраняет невалидные данные.
# Количество Форм: Проверить формирование необходимого количества форм
# в зависимости от выбранного spec_amount и правильность передачи данных в формы.
