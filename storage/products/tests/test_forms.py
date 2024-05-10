from django.test import TestCase
from products.forms import AddProductForm


class TestAddProductForm(TestCase):
    def setUp(self) -> None:
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

    def test_labels(self):
        form = AddProductForm()
        self.assertEquals(form.fields['fish'].label, 'Название рыбы')
        self.assertEqual(form.fields['cutting'].label, 'Разделка')
        self.assertEqual(form.fields['size'].label, 'Размер')
        self.assertEqual(form.fields['producer'].label, 'Производитель')
        self.assertEqual(form.fields['package'].label, 'Упаковка')
        self.assertEqual(form.fields['note'].label, 'Заметки')

    def test_constraints(self):
        form = AddProductForm()
        self.assertEquals(form.fields['fish'].max_length, 50)
        self.assertEqual(form.fields['cutting'].max_length, 15)
        self.assertEqual(form.fields['size'].max_length, 15)
        self.assertEqual(form.fields['producer'].max_length, 50)
        self.assertEqual(form.fields['package'].max_length, 15)
        self.assertEqual(form.fields['note'].max_length, None)

        self.assertTrue(form.fields['fish'].required)
        self.assertFalse(form.fields['cutting'].required)
        self.assertFalse(form.fields['size'].required)
        self.assertFalse(form.fields['producer'].required)
        self.assertFalse(form.fields['package'].required)
        self.assertFalse(form.fields['note'].required)

    def test_help_text(self):
        form = AddProductForm()
        self.assertEquals(form.fields['fish'].help_text, '')
        self.assertEqual(form.fields['cutting'].help_text, '')
        self.assertEqual(form.fields['size'].help_text, '')
        self.assertEqual(form.fields['producer'].help_text, '')
        self.assertEqual(form.fields['package'].help_text, '')
        self.assertEqual(form.fields['note'].help_text, '')

    # def test_widgets(self):
    #     form = AddProductForm()
    #     print(form.fields['fish'].widget.__dict__)

    def test_valid_data(self):
        form_minimail = AddProductForm(data=self.minimal_data)
        form_full = AddProductForm(data=self.full_data)
        form_max_size = AddProductForm(data=self.max_size_data)
        self.assertTrue(form_minimail.is_valid())
        self.assertTrue(form_full.is_valid())
        self.assertTrue(form_max_size.is_valid())

    def test_invalid_data(self):
        form_no_data = AddProductForm(data=self.no_data)
        form_overflow = AddProductForm(data=self.overflow_data)
        self.assertFalse(form_no_data.is_valid())
        self.assertFalse(form_overflow.is_valid())

    def test_helper(self):
        form_full = AddProductForm(data=self.full_data)
        # print(form_full.helper.inputs.__dict__)




# fields = ['fish', 'cutting', 'size', 'producer', 'package', 'note']
# Валидацию данных:
# Убедиться, что форма правильно валидирует входные данные пользователя.
# Проверить, что неверные данные приводят к соответствующим сообщениям об ошибках.
# Отображение формы:
# Проверить, что форма правильно отображается на веб-странице.
# Убедиться, что все поля отображаются корректно и в правильном порядке.
# Обработку данных:
# Проверить, что данные, введенные пользователем, правильно обрабатываются формой.
# Убедиться, что данные корректно сохраняются или обрабатываются в соответствии с ожиданиями.
# Обработку различных состояний:
# Проверить поведение формы при различных сценариях, таких как отправка пустой формы, формы с недопустимыми данными и т.д.
# Интеграцию с моделями:
# Убедиться, что форма корректно взаимодействует с соответствующей моделью Django.
# Проверить, что данные, введенные в форму, корректно сохраняются в базе данных.
# Обработку запросов POST и GET:
# Проверить, что обработчики формы правильно реагируют на методы запросов POST и GET.
# Обработку файлов:
# Если форма включает загрузку файлов, необходимо убедиться, что они корректно обрабатываются и сохраняются.
# Защиту от мошеннических запросов:
# Проверить, что применены соответствующие меры защиты от CSRF (межсайтовая подделка запроса).
# Отображение ошибок:
# Проверить, что ошибки валидации данных отображаются пользователю в понятной и информативной форме.
# Работу с AJAX:
# Если форма используется в AJAX-запросах, убедиться, что взаимодействие с формой через AJAX происходит корректно.

