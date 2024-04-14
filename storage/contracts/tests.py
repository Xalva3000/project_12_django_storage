from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class GetContractPage(TestCase):
    def setUp(self):
        pass

    def test_case_1(self):
        path = reverse('contracts:contracts')
        response = self.client.get(path)
        print(response)

    def test_case_2(self):
        path = reverse('contracts:contracts_plus')
        response = self.client.get(path)
        print(response)

    def test_case_3(self):
        path = reverse('contracts:contracts_deleted')
        response = self.client.get(path)
        print(response)

    def test_case_4(self):
        path = reverse('contracts:contract')
        response = self.client.get(path)
        print(response)

    def test_case_5(self):
        path = reverse('contracts:add_contract')
        response = self.client.get(path)
        print(response)

    def test_case_6(self):
        path = reverse('contracts:add_contract')
        response = self.client.get(path)
        print(response)

    def test_case_7(self):
        path = reverse('contracts:contract_update')
        response = self.client.get(path)
        print(response)

    def test_case_8(self):
        path = reverse('contracts:add_specifications')
        response = self.client.get(path)
        print(response)

    def test_case_9(self):
        path = reverse('contracts:contract_execution')
        response = self.client.get(path)
        print(response)

    def test_case_10(self):
        path = reverse('contracts:contract_delete', args=[1])
        response = self.client.get(path)
        print(response)

    def test_case_11(self):
        path = reverse('contracts:change_manager_share', kwargs={})
        response = self.client.get(path)
        print(response)

    def test_case_12(self):
        path = reverse('contracts:change_note', args=[1])
        response = self.client.get(path)
        print(response)

    def test_case_13(self):
        path = reverse('contracts:add_payment', args=[1])
        response = self.client.get(path)
        print(response)

    def test_case_14(self):
        path = reverse('contracts:contract_reserve', args=[1])
        response = self.client.get(path)
        print(response)

    def test_case_15(self):
        path = reverse('contracts:contract_payment', args=[1])
        response = self.client.get(path)
        print(response)

    def test_case_16(self):
        path = reverse('contracts:contract_execution', args=[1])
        response = self.client.get(path)
        print(response)

    def tearDown(self):
        pass

# class GetPagesTestCase(TestCase):
# 	fixtures = ['women_women.json','women_category.json','women_husband.json','women_tagpost.json', 'auth_user.json']
#
# 	def setUp(self):
# 		pass
#
# 	def test_main_page(self):
# 		# path = reverse('edit_page', args=['sharka-blue'])
# 		# print(path)
# 		# path = reverse('post', args=['sharka-blue'])
# 		path = reverse('home')
# 		response = self.client.get(path)
# 		self.assertEqual(response.status_code, HTTPStatus.OK)
# 		self.assertIn('women/index.html', response.template_name)
# 		self.assertTemplateUsed(response, 'women/index.html')
# 		self.assertEqual(response.context_data['title'], 'Главная страница')
#
# 	def test_redirect_add_page(self):
# 		path = reverse('add_content')
# 		redirect_uri = reverse('users:login') + '?next=' + path
# 		response = self.client.get(path)
# 		self.assertEqual(response.status_code, HTTPStatus.FOUND)
# 		self.assertRedirects(response, redirect_uri)
#
# 	def test_data_mainpage(self):
# 		w = Women.published.all().select_related('cat').order_by('title')
# 		path = reverse('home')
# 		response = self.client.get(path)
# 		self.assertQuerySetEqual(response.context_data['posts'], w)
#
# 	def test_paginate_mainpage(self):
# 		path = reverse('home')
# 		# page = 2
# 		# paginate_by = 5
# 		# response = self.client.get(path + f'?page={page}')
# 		response = self.client.get(path)
# 		w = Women.published.all().select_related('cat').order_by('title')
# 		self.assertQuerySetEqual(response.context_data['posts'][:2], w[:2])
# 		# self.assertEqual(response.context_data['posts'], w[(page - 1) + paginate_by:page * paginate_by])
#
# 	def test_content_post(self):
# 		w = Women.published.get(pk=1)
#
# 		path = reverse('post', args=[w.slug])
# 		response = self.client.get(path)
#
# 		self.assertEqual(w.content, response.context_data['post'].content)
#
# 	def tearDown(self):
# 		pass
