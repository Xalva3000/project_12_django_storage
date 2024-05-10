from django.test import TestCase
from contractors.forms import AddContractorForm

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


class TestAddContractorForm(TestCase):

    def test_labels(self):
        form = AddContractorForm()
        self.assertEquals(form.fields['name'].label, 'Название')
        self.assertEqual(form.fields['address'].label, 'Адрес')
        self.assertEqual(form.fields['email'].label, 'E-mail')
        self.assertEqual(form.fields['contact_data'].label, 'Контакты')

    def test_constraints(self):
        form = AddContractorForm()
        self.assertEquals(form.fields['name'].max_length, 100)
        self.assertEqual(form.fields['address'].max_length, 200)
        self.assertEqual(form.fields['email'].max_length, 50)
        self.assertEqual(form.fields['contact_data'].max_length, None)

        self.assertTrue(form.fields['name'].required)
        self.assertFalse(form.fields['address'].required)
        self.assertFalse(form.fields['email'].required)
        self.assertFalse(form.fields['contact_data'].required)


    def test_help_text(self):
        form = AddContractorForm()
        self.assertEquals(form.fields['name'].help_text, '')
        self.assertEqual(form.fields['address'].help_text, '')
        self.assertEqual(form.fields['email'].help_text, '')
        self.assertEqual(form.fields['contact_data'].help_text, '')


    # def test_widgets(self):
    #     form = AddProductForm()
    #     print(form.fields['fish'].widget.__dict__)

    def test_valid_data(self):
        form_minimail = AddContractorForm(data=data_dct['minimal_data'])
        form_full = AddContractorForm(data=data_dct['full_data'])
        form_max_size = AddContractorForm(data=data_dct['max_size_data'])
        self.assertTrue(form_minimail.is_valid())
        self.assertTrue(form_full.is_valid())
        self.assertTrue(form_max_size.is_valid())

    def test_invalid_data(self):
        form_no_data = AddContractorForm(data=data_dct['no_data'])
        form_overflow = AddContractorForm(data=data_dct['overflow_data'])
        self.assertFalse(form_no_data.is_valid())
        self.assertFalse(form_overflow.is_valid())

    def test_helper(self):
        form_full = AddContractorForm(data=data_dct['full_data'])
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

