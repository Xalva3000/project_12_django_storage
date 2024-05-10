from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from faker import Faker
from products.utils import menu, tools

from contractors.models import Contractor

fake = Faker(['ru_RU'])
Faker.seed(1)

data_dct = {
    'minimal_data': {
        'name': 'ООО Алаид',
    },
    'full_data': {
        'name': 'ООО Камчатка Харвест',
        'address': 'г.Петропавловск-Камчатский',
        'email': 'charvest@mail.ru',
        'contact_data': '+6851651',
    },
    'empty_data': {
        'name': '',
        'address': '',
        'email': '',
        'contact_data': '',
    },
    'no_data': {},
    'max_size_data': {
        'name': '1' * 100,
        'address': '1' * 200,
        'email': '1' * 42 + '@mail.ru',
        'contact_data': '1' * 1000,
    },
    'overflow_data': {
        'name': '1' * 101,
        'address': '1' * 201,
        'email': '1' * 43 + '@mail.ru',
        'contact_data': '1' * 1000,
    },
}


class TestContractorsView(TestCase):
    # fixtures = ['contractors_contractor.json']

    # class ContractorsList(LoginRequiredMixin, DataMixin, ListView):
    #     template_name = 'contractors/contractors.html'
    #     context_object_name = 'contractors'
    #     title_page = 'Контрагенты'
    #     category_page = 'contractors'
    #     paginate_by = 20
    #
    #     def get_queryset(self):
    #         return Contractor.objects.all()

    def setUp(self) -> None:
        [Contractor.objects.create(name=fake.company(),
                                   address=fake.address(),
                                   email=fake.ascii_company_email()) for _ in range(22)]
        self.client = Client()
        self.contractors_url = reverse("contractors:contractors")
        self.queryset = Contractor.objects.all().order_by('-pk')

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    def test_contractors_list_GET_login(self):
        response = self.client.get(self.contractors_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "contractors/contractors.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Контрагенты')
        self.assertEqual(response.context_data["tools"], tools["contractors"])
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(response.context_data["contractors"].count(), 20)
        self.assertEqual(self.queryset.count(), 22)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["contractors"][:20], self.queryset[:20])

    def test_contractors_list_GET_login_page_2(self):
        page = 2
        paginate_by = 20
        response = self.client.get(self.contractors_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertQuerySetEqual(response.context_data["contractors"], self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_contractors_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.contractors_url
        response = self.client.get(self.contractors_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)


class TestShowContractorView(TestCase):
    # fixtures = ['products_product.json']

    # class ShowContractor(LoginRequiredMixin, DataMixin, DetailView):
    #     model = Contractor
    #     template_name = 'contractors/contractor.html'
    #     context_object_name = 'contractor'
    #     category_page = 'contractors'
    #     pk_url_kwarg = 'pk'
    #     title_page = 'Детали контрагента'
    #
    #     def get_object(self, queryset=None):
    #         return get_object_or_404(Contractor.objects, pk=self.kwargs[self.pk_url_kwarg])

    def setUp(self) -> None:
        [Contractor.objects.create(name=fake.company(),
                                   address=fake.address(),
                                   email=fake.ascii_company_email()) for _ in range(22)]
        self.client = Client()

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.existing_pk = 1
        self.not_existing_pk = 100

    def test_view_parameters(self):
        c1 = Contractor.objects.get(pk=self.existing_pk)
        path = reverse('contractors:contractor', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contractors/contractor.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(c1.name, response.context_data['contractor'].name)
        self.assertEqual(response.context_data["title"], 'Детали контрагента')
        self.assertEqual(response.context_data["tools"], tools["contractors"])
        self.assertIn('contractor', response.context_data)
        self.assertEquals(response.context_data['contractor'], c1)

    def test_existing_object(self):
        c1 = Contractor.objects.get(pk=self.existing_pk)
        path = reverse('contractors:contractor', args=[self.existing_pk])
        response = self.client.get(path)

        self.assertEqual(response.context_data['contractor'], c1)
        self.assertEqual(response.context_data['contractor'].id, c1.pk)
        self.assertEqual(response.context_data['contractor'].name, c1.name)
        self.assertEqual(response.context_data['contractor'].address, c1.address)
        self.assertEqual(response.context_data['contractor'].email, c1.email)
        self.assertEqual(response.context_data['contractor'].contact_data, c1.contact_data)

    def test_not_existing_object(self):
        path = reverse('contractors:contractor', args=[self.not_existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)

    def test_redirect(self):
        path = reverse('contractors:contractor', args=[self.existing_pk])
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + path

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)


class TestAddContractorView(TestCase):

    def setUp(self) -> None:
        self.path = reverse('contractors:add_contractor')
        self.client = Client()

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    # class AddContractor(LoginRequiredMixin, DataMixin, CreateView):
    #     form_class = AddContractorForm
    #     template_name = 'contractors/add_contractor.html'
    #     title_page = 'Добавление контрагента'
    #     category_page = 'contractors'
    #
    #     def form_valid(self, form):
    #         w = form.save(commit=False)
    #         w.author = self.request.user
    #         return super().form_valid(form)
    def test_view_parameters(self):

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contractors/add_contractor.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Добавление контрагента')
        self.assertEqual(response.context_data["tools"], tools["contractors"])

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
        response = self.client.post(self.path, data=data_dct['minimal_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(Contractor.objects.count(), 0)

    def test_valid_minimal_object_creation(self):
        response = self.client.post(self.path, data=data_dct['minimal_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contractors:contractor', args=[1]))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 1)

    def test_empty_object_creation(self):
        response = self.client.post(self.path, data=data_dct['empty_data'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contractors/add_contractor.html")
        self.assertEqual(Contractor.objects.count(), 0)

    def test_overflow_object_creation(self):
        response = self.client.post(self.path, data=data_dct['overflow_data'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contractors/add_contractor.html")
        self.assertEqual(Contractor.objects.count(), 0)

    def test_full_object_creation(self):
        response = self.client.post(self.path, data=data_dct['full_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contractors:contractor', args=[1]))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 1)

    def test_max_size_object_creation(self):
        response = self.client.post(self.path, data=data_dct['max_size_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contractors:contractor', args=[1]))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 1)


class TestUpdateContractorView(TestCase):
    # fixtures = ['products_product.json']
    def setUp(self) -> None:
        [Contractor.objects.create(name=fake.company(),
                                   address=fake.address(),
                                   email=fake.ascii_company_email()) for _ in range(22)]
        self.client = Client()

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.existing_pk = 1
        self.not_existing_pk = 100

    # class UpdateContractor(LoginRequiredMixin, DataMixin, UpdateView):
    #     model = Contractor
    #     form_class = AddContractorForm
    #     template_name = 'contractors/add_contractor.html'
    #     title_page = 'Редактирование контрагента'
    #     category_page = 'contractors'
    #
    #     def get_success_url(self):
    #         pk = self.kwargs[self.pk_url_kwarg]
    #         return reverse('contractors:contractor', kwargs={"pk": pk})

    def test_view_parameters(self):
        c1 = Contractor.objects.get(pk=self.existing_pk)
        path = reverse('contractors:update_contractor', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "contractors/add_contractor.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(c1.name, response.context_data['contractor'].name)
        self.assertEqual(response.context_data["title"], 'Редактирование контрагента')
        self.assertEqual(response.context_data["tools"], tools["contractors"])
        self.assertIn('contractor', response.context_data)
        self.assertEquals(response.context_data['contractor'], c1)

    def test_no_login_redirection(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        redirect_uri = reverse('users:login') + '?next=' + path

        self.client.logout()
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)

    def test_no_login_object_update(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        redirect_uri = reverse('users:login') + '?next=' + path
        self.client.logout()
        response = self.client.post(path, data=data_dct['minimal_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(Contractor.objects.count(), 22)
        c1 = Contractor.objects.get(pk=self.existing_pk)
        self.assertNotEquals(c1.name, data_dct['minimal_data']['name'])

    def test_valid_minimal_object_update(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        response = self.client.post(path, data=data_dct['minimal_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contractors:contractor', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 22)
        c1 = Contractor.objects.get(pk=self.existing_pk)
        self.assertEquals(c1.name, data_dct['minimal_data']['name'])
        self.assertEquals(c1.address, '')
        self.assertEquals(c1.email, '')
        self.assertEquals(c1.contact_data, '')

    def test_empty_object_update(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        response = self.client.post(path, data=data_dct['empty_data'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contractors/add_contractor.html")
        self.assertEqual(Contractor.objects.count(), 22)
        c1 = Contractor.objects.get(pk=self.existing_pk)
        self.assertNotEquals(c1.name, '')

    def test_overflow_object_update(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        response = self.client.post(path, data=data_dct['overflow_data'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "contractors/add_contractor.html")
        self.assertEqual(Contractor.objects.count(), 22)
        c1 = Contractor.objects.get(pk=self.existing_pk)
        self.assertNotEquals(c1.name, data_dct['overflow_data']['name'])

    def test_full_object_update(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        response = self.client.post(path, data=data_dct['full_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contractors:contractor', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 22)
        c1 = Contractor.objects.get(pk=self.existing_pk)
        self.assertEquals(c1.name, data_dct['full_data']['name'])
        self.assertEquals(c1.address, data_dct['full_data']['address'])
        self.assertEquals(c1.email, data_dct['full_data']['email'])
        self.assertEquals(c1.contact_data, data_dct['full_data']['contact_data'])

    def test_max_size_object_update(self):
        path = reverse('contractors:update_contractor', args=[self.existing_pk])
        response = self.client.post(path, data=data_dct['max_size_data'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('contractors:contractor', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Contractor.objects.count(), 22)
        c1 = Contractor.objects.get(pk=self.existing_pk)
        self.assertEquals(c1.name, data_dct['max_size_data']['name'])
        self.assertEquals(c1.address, data_dct['max_size_data']['address'])
        self.assertEquals(c1.email, data_dct['max_size_data']['email'])
        self.assertEquals(c1.contact_data, data_dct['max_size_data']['contact_data'])
