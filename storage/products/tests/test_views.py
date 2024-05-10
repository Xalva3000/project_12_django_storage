from random import choice

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from products.utils import tools, menu

from products.models import Product




fish_list = ('Tuna', 'Trout', 'Cod', 'Sardine', 'Carp',
             'Mackerel', 'Catfish', 'Tilapia', 'Flounder', 'Halibut',
             'Haddock', 'Perch', 'Swordfish', 'Snapper', 'Herring',
             'Salmon', 'Pickle', 'Лосось', 'Камбала', 'Минтай',
             'Горбуша', 'Кижуч')
cutting_list = ('НР', 'БГ', 'ПБГ', 'филе', '')
size_list = ('S', 'M', 'L', '2L', '')
producer_list = ('Алаид', 'Камчатка Харвест', 'Акрос', 'Скат', '')


#     path('', LoginUser.as_view(), name='home'),
#     path("products/", views.ProductsList.as_view(), name='products'),
#     path("products/<int:pk>/", views.ShowProduct.as_view(), name='product'),
#     path("products/add_product/", views.AddProduct.as_view(), name='add_product'),
#     path("products/update/<int:pk>", views.UpdateProduct.as_view(), name='update_product'),
#     path("about/", views.about, name="about"),

class TestProductsListView(TestCase):
    # fixtures = ['products_product.json']

    # class ProductsList(LoginRequiredMixin, DataMixin, ListView):
    #     template_name = 'products/products.html'
    #     context_object_name = 'products'
    #     title_page = 'Продукты'
    #     category_page = 'products'
    #     paginate_by = 20
    #
    #     def get_queryset(self):
    #         return Product.objects.all().order_by('-pk')

    def setUp(self) -> None:
        # products.count = 22
        [Product.objects.create(fish=fish,
                                cutting=choice(cutting_list),
                                size=choice(size_list)) for fish in fish_list]
        self.client = Client()
        self.product_list_url = reverse("products:products")
        self.queryset = Product.objects.all().order_by('-pk')
        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

    def test_products_list_GET_login(self):
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "products/products.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], "Продукты")
        self.assertEqual(response.context_data["tools"], tools["products"])
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(response.context_data["products"].count(), 20)
        self.assertEqual(self.queryset.count(), 22)
        self.assertIn("custom_url", response.context_data)
        self.assertQuerySetEqual(response.context_data["products"][:20], self.queryset[:20])

    def test_products_list_GET_login_page_2(self):
        page = 2
        paginate_by = 20
        response = self.client.get(self.product_list_url + f"?page={page}")
        self.assertEqual(response.context_data["paginator"].per_page, 20)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertQuerySetEqual(response.context_data["products"],
                                 self.queryset[(page - 1) * paginate_by:page * paginate_by])

    def test_products_list_redirect(self):
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + self.product_list_url
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)


class TestShowProductView(TestCase):
    fixtures = ['products_product.json']

    # class ShowProduct(LoginRequiredMixin, DataMixin, DetailView):
    #     model = Product
    #     template_name = 'products/product.html'
    #     context_object_name = 'product'
    #     pk_url_kwarg = 'pk'
    #     title_page = 'Детали продукта'
    #     category_page = 'products'
    #
    #     def get_object(self, queryset=None):
    #         return get_object_or_404(Product.objects, pk=self.kwargs[self.pk_url_kwarg])

    def setUp(self) -> None:
        self.client = Client()

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.existing_pk = 1
        self.not_existing_pk = 100

    def test_view_parameters(self):
        p1 = Product.objects.get(pk=self.existing_pk)
        path = reverse('products:product', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "products/product.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(p1.fish, response.context_data['product'].fish)
        self.assertEqual(response.context_data["title"], 'Детали продукта')
        self.assertEqual(response.context_data["tools"], tools["products"])
        self.assertIn('product', response.context_data)
        self.assertEquals(response.context_data['product'], p1)

    def test_existing_object(self):
        p1 = Product.objects.get(pk=self.existing_pk)
        path = reverse('products:product', args=[self.existing_pk])
        response = self.client.get(path)

        self.assertEqual(response.context_data['product'], p1)
        self.assertEqual(response.context_data['product'].id, p1.pk)
        self.assertEqual(response.context_data['product'].fish, p1.fish)
        self.assertEqual(response.context_data['product'].cutting, p1.cutting)
        self.assertEqual(response.context_data['product'].size, p1.size)
        self.assertEqual(response.context_data['product'].producer, p1.producer)
        self.assertEqual(response.context_data['product'].package, p1.package)
        self.assertEqual(response.context_data['product'].note, p1.note)
        self.assertEqual(response.context_data['product'].date_create, p1.date_create)
        self.assertEqual(response.context_data['product'].date_update, p1.date_update)

    def test_not_existing_object(self):
        path = reverse('products:product', args=[self.not_existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)

    def test_redirect(self):
        path = reverse('products:product', args=[self.existing_pk])
        self.client.logout()
        redirect_uri = reverse('users:login') + '?next=' + path

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)


class TestAddProductView(TestCase):

    def setUp(self) -> None:
        self.path = reverse('products:add_product')
        self.client = Client()

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.minimal_data = {
            'fish': 'Salmon',
        }
        self.full_data = {
            'fish': 'Лосось',
            'cutting': 'НР',
            'size': '2+кг',
            'producer': 'Производитель',
            'package': 'мешок',
            'note': 'срок хранения 9 мес',
        }
        self.empty_data = {
            'fish': '',
            'cutting': '',
            'size': '',
            'producer': '',
            'package': '',
            'note': '',
        }
        self.no_data = {}
        self.max_size_data = {
            'fish': '1' * 50,
            'cutting': '1' * 15,
            'size': '1' * 15,
            'producer': '1' * 50,
            'package': '1' * 15,
            'note': '1' * 1000,
        }
        self.overflow_data = {
            'fish': '1' * 51,
            'cutting': '1' * 16,
            'size': '1' * 16,
            'producer': '1' * 51,
            'package': '1' * 16,
            'note': '1' * 1000,
        }

    # class AddProduct(LoginRequiredMixin, DataMixin, CreateView):
    #     form_class = AddProductForm
    #     template_name = 'products/add_product.html'
    #     title_page = 'Добавление продукта'
    #     category_page = 'products'
    #     success_url = reverse_lazy('products:products')
    def test_view_parameters(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "products/add_product.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(response.context_data["title"], 'Добавление продукта')
        self.assertEqual(response.context_data["tools"], tools["products"])
        # self.assertIn('product', response.context_data)
        # self.assertEquals(response.context_data['product'], p1)

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
        response = self.client.post(self.path, data=self.minimal_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(Product.objects.count(), 0)

    def test_valid_minimal_object_creation(self):
        response = self.client.post(self.path, data=self.minimal_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('products:products'))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Product.objects.count(), 1)

    def test_empty_object_creation(self):
        response = self.client.post(self.path, data=self.empty_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "products/add_product.html")
        self.assertEqual(Product.objects.count(), 0)

    def test_overflow_object_creation(self):
        response = self.client.post(self.path, data=self.overflow_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "products/add_product.html")
        self.assertEqual(Product.objects.count(), 0)

    def test_full_object_creation(self):
        response = self.client.post(self.path, data=self.full_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('products:products'))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Product.objects.count(), 1)

    def test_max_size_object_creation(self):
        response = self.client.post(self.path, data=self.max_size_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('products:products'))
        self.assertEqual(response.request['PATH_INFO'], self.path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Product.objects.count(), 1)


class TestUpdateProductView(TestCase):
    fixtures = ['products_product.json']

    def setUp(self) -> None:
        self.client = Client()

        User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        self.client.login(username='homer', password='simpson')

        self.existing_pk = 1
        self.not_existing_pk = 100

        self.minimal_data = {
            'fish': 'Salmon',
        }
        self.full_data = {
            'fish': 'Лосось',
            'cutting': 'НР',
            'size': '2+кг',
            'producer': 'Производитель',
            'package': 'мешок',
            'note': 'срок хранения 9 мес',
        }
        self.empty_data = {
            'fish': '',
            'cutting': '',
            'size': '',
            'producer': '',
            'package': '',
            'note': '',
        }
        self.no_data = {}
        self.max_size_data = {
            'fish': '1' * 50,
            'cutting': '1' * 15,
            'size': '1' * 15,
            'producer': '1' * 50,
            'package': '1' * 15,
            'note': '1' * 1000,
        }
        self.overflow_data = {
            'fish': '1' * 51,
            'cutting': '1' * 16,
            'size': '1' * 16,
            'producer': '1' * 51,
            'package': '1' * 16,
            'note': '1' * 1000,
        }

    # class UpdateProduct(LoginRequiredMixin, DataMixin, UpdateView):
    #     model = Product
    #     form_class = AddProductForm
    #     template_name = 'products/add_product.html'
    #     title_page = 'Редактирование продукта'
    #     category_page = 'products'
    #
    #     def get_success_url(self):
    #         pk = self.kwargs["pk"]
    #         return reverse('products:product', kwargs={"pk": pk})

    def test_view_parameters(self):
        p1 = Product.objects.get(pk=self.existing_pk)
        path = reverse('products:update_product', args=[self.existing_pk])

        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        self.assertTemplateUsed(response, "products/add_product.html")
        self.assertEqual(response.context['menu'], menu)
        self.assertEqual(p1.fish, response.context_data['product'].fish)
        self.assertEqual(response.context_data["title"], 'Редактирование продукта')
        self.assertEqual(response.context_data["tools"], tools["products"])
        self.assertIn('product', response.context_data)
        self.assertEquals(response.context_data['product'], p1)

    def test_no_login_redirection(self):
        path = reverse('products:update_product', args=[self.existing_pk])
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
        path = reverse('products:update_product', args=[self.existing_pk])
        redirect_uri = reverse('users:login') + '?next=' + path
        self.client.logout()
        response = self.client.post(path, data=self.minimal_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(Product.objects.count(), 22)
        p1 = Product.objects.get(pk=self.existing_pk)
        self.assertNotEquals(p1.fish, self.minimal_data['fish'])

    def test_valid_minimal_object_update(self):
        path = reverse('products:update_product', args=[self.existing_pk])
        response = self.client.post(path, data=self.minimal_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('products:product', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Product.objects.count(), 22)
        p1 = Product.objects.get(pk=self.existing_pk)
        self.assertEquals(p1.fish, self.minimal_data['fish'])
        self.assertEquals(p1.cutting, '')
        self.assertEquals(p1.size, '')
        self.assertEquals(p1.producer, '')
        self.assertEquals(p1.package, '')
        self.assertEquals(p1.note, '')

    def test_empty_object_update(self):
        path = reverse('products:update_product', args=[self.existing_pk])
        response = self.client.post(path, data=self.empty_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "products/add_product.html")
        self.assertEqual(Product.objects.count(), 22)
        p1 = Product.objects.get(pk=self.existing_pk)
        self.assertNotEquals(p1.fish, '')

    def test_overflow_object_update(self):
        path = reverse('products:update_product', args=[self.existing_pk])
        response = self.client.post(path, data=self.overflow_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertTemplateUsed(response, "products/add_product.html")
        self.assertEqual(Product.objects.count(), 22)
        p1 = Product.objects.get(pk=self.existing_pk)
        self.assertNotEquals(p1.fish, self.overflow_data['fish'])

    def test_full_object_update(self):
        path = reverse('products:update_product', args=[self.existing_pk])
        response = self.client.post(path, data=self.full_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('products:product', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Product.objects.count(), 22)
        p1 = Product.objects.get(pk=self.existing_pk)
        self.assertEquals(p1.fish, self.full_data['fish'])
        self.assertEquals(p1.cutting, self.full_data['cutting'])
        self.assertEquals(p1.size, self.full_data['size'])
        self.assertEquals(p1.producer, self.full_data['producer'])
        self.assertEquals(p1.package, self.full_data['package'])
        self.assertEquals(p1.note, self.full_data['note'])

    def test_max_size_object_creation(self):
        path = reverse('products:update_product', args=[self.existing_pk])
        response = self.client.post(path, data=self.max_size_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('products:product', args=[self.existing_pk]))
        self.assertEqual(response.request['PATH_INFO'], path)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertIsNone(response.context)
        self.assertFalse(response.templates)
        self.assertEqual(Product.objects.count(), 22)
        p1 = Product.objects.get(pk=self.existing_pk)
        self.assertEquals(p1.fish, self.max_size_data['fish'])
        self.assertEquals(p1.cutting, self.max_size_data['cutting'])
        self.assertEquals(p1.size, self.max_size_data['size'])
        self.assertEquals(p1.producer, self.max_size_data['producer'])
        self.assertEquals(p1.package, self.max_size_data['package'])
        self.assertEquals(p1.note, self.max_size_data['note'])

# HTTP запросы и ответы:
# Проверка, что view возвращает корректный HTTP код состояния (например, 200 OK, 404 Not Found и т. д.).
# Убедиться, что view возвращает ожидаемый контент в HTTP ответе.

# Авторизация и доступ:
# Проверка корректной обработки авторизованных и неавторизованных пользователей.
# Убедиться, что view ограничивает доступ к определенным пользователям или группам пользователей, если требуется.

# Взаимодействие с моделями данных:
# Проверка, что view правильно извлекает данные из моделей или других источников.
# Убедиться, что view правильно обрабатывает данные перед их выводом.

# Обработка и валидация данных:
# Проверка корректной обработки данных, вводимых пользователем через формы или запросы.
# Убедиться, что view корректно валидирует и сохраняет данные.

# Обработка исключений и ошибок:
# Проверка обработки исключений и ошибок внутри view.
# Убедиться, что view возвращает правильный HTTP код в случае исключительных ситуаций.

# Работа с различными методами HTTP:
# Проверка, что view корректно обрабатывает различные методы HTTP, такие как GET, POST, PUT, DELETE и т. д.

# Интеграция с другими компонентами:
# Проверка взаимодействия с другими компонентами, такими как middleware, шаблоны, статические файлы и т. д.
