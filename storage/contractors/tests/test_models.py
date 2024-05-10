from datetime import date
from pprint import pprint

from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.test import TestCase

from products.models import Product
from contracts.models import Contract, Payment
from contractors.models import Contractor
from contracts.models import Specification
from storage_items.models import StorageItem


class TestModels(TestCase):
    def setUp(self) -> None:

        self.min = Contractor.objects.create(name='ООО Алаид')
        self.two_fields = Contractor.objects.create(name='ООО Камчатка Харвест', address='г.Петропавловск-Камчатский')
        self.empty_mail = Contractor.objects.create(
            name='ИП Бородин Е.В.',
            address='г.Самара',
            email='',
        )
        self.three_fields = Contractor.objects.create(
            name='ИП Монашев С.В.',
            address='г.Нижний Новгород',
            email='monashev@rambler.ru',
        )
        self.full = Contractor.objects.create(
            name='ООО Лагуна',
            address='г.Самара',
            email='laguna@mail.ru',
            contact_data='Анна +156415111, Василий +516351638163'
        )
        self.num_object = Contractor.objects.create(
            name='111',
            address='111',
            email='111@111.ru',
            contact_data='111'
        )

    def test_labels(self):
        c = self.full

        self.assertEqual(c._meta.get_field('name').verbose_name, 'Название')
        self.assertEqual(c._meta.get_field('address').verbose_name, 'Адрес')
        self.assertEqual(c._meta.get_field('email').verbose_name, 'E-mail')
        self.assertEqual(c._meta.get_field('contact_data').verbose_name, 'Контакты')

        self.assertEqual(c._meta.get_field('date_create').verbose_name, 'Дата создания')
        self.assertEqual(c._meta.get_field('date_update').verbose_name, 'Дата изменения')

    def test_constraints_indication(self):
        c = self.full
        self.assertEqual(c._meta.get_field('name').max_length, 100)
        self.assertEqual(c._meta.get_field('address').max_length, 200)
        self.assertEqual(c._meta.get_field('email').max_length, 50)
        self.assertEqual(c._meta.get_field('contact_data').max_length, None)
        # pprint(c._meta.get_field('contact_data').__dict__)

    def test_objects_created(self):
        queryset_all = Contractor.objects.all()
        self.assertEquals(queryset_all.count(), 6)

    def test_objects_pk_incremented(self):
        self.assertEquals(Contractor.objects.get(name='ООО Алаид').pk, 1)
        self.assertEquals(Contractor.objects.get(name='ООО Камчатка Харвест').pk, 2)
        self.assertEquals(Contractor.objects.get(name='ИП Бородин Е.В.').pk, 3)
        self.assertEquals(Contractor.objects.get(name='ИП Монашев С.В.').pk, 4)
        self.assertEquals(Contractor.objects.get(name='ООО Лагуна').pk, 5)
        self.assertEquals(Contractor.objects.get(name='111').pk, 6)

    # name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Название')
    # address = models.CharField(max_length=200, blank=True, verbose_name='Адрес')
    # email = models.EmailField(max_length=50, blank=True, verbose_name='E-mail')
    # contact_data = models.TextField(blank=True, verbose_name='Контакты')
    # date_create = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    # date_update = models.DateField(auto_now=True, verbose_name='Дата изменения')
    def test_auto_assigning(self):
        c1 = Contractor.objects.get(name='ООО Алаид')
        self.assertEquals(c1.name, 'ООО Алаид')
        self.assertEquals(c1.address, '')
        self.assertEquals(c1.email, '')
        self.assertEquals(c1.contact_data, '')
        self.assertEquals(c1.date_create, date.today())
        self.assertEquals(c1.date_update, date.today())

    def test_numeric_chars(self):
        self.assertTrue(Contractor.objects.filter(name='111').exists())
        c1 = Contractor.objects.get(name='111')
        self.assertEquals(c1.name, '111')
        self.assertEquals(c1.address, '111')
        self.assertEquals(c1.email, '111@111.ru')
        self.assertEquals(c1.contact_data, '111')


    def test_related_objects(self):
        contractor1 = Contractor.objects.create(name='ООО Алаид')
        contractor2 = Contractor.objects.create(name='ИП Бородин')
        product1 = Product.objects.create(fish='Горбуша')
        product2 = Product.objects.create(fish='Кижуч')
        contract1 = Contract.objects.create(
            contract_type='income',
            date_plan=date.today(),
            contractor=contractor1
        )
        contract2 = Contract.objects.create(
            contract_type='outcome',
            date_plan=date.today(),
            contractor=contractor2
        )
        specification1 = Specification.objects.create(
            contract=contract1,
            product=product1,
            variable_weight=18,
            price=500,
            quantity=1000,
        )
        specification2 = Specification.objects.create(
            contract=contract1,
            product=product2,
            variable_weight=1,
            price=700,
            quantity=1000,
        )
        storage_item1 = StorageItem.objects.create(
            product=product1,
            weight=18,
            price=500,
            available=1000,
            stored=1000,
        )
        storage_item2 = StorageItem.objects.create(
            product=product2,
            weight=1,
            price=700,
            available=1000,
            stored=1000,
        )
        specification3 = Specification.objects.create(
            contract=contract2,
            product=product1,
            variable_weight=18,
            price=800,
            quantity=1000,
        )
        specification4 = Specification.objects.create(
            contract=contract2,
            product=product2,
            variable_weight=1,
            price=1000,
            quantity=1000,
        )
        payment1 = Payment.objects.create(
            contract=contract1,
            amount=1_000_000,
        )
        payment2 = Payment.objects.create(
            contract=contract1,
            amount=2_000_000,
        )
        payment3 = Payment.objects.create(
            contract=contract2,
            amount=500_000,
        )
        payment4 = Payment.objects.create(
            contract=contract2,
            amount=200_000,
        )
        self.assertEqual(Contractor.objects.count(), 8)
        self.assertEqual(Payment.objects.count(), 4)
        self.assertEqual(contractor1.contracts.count(), 1)
        self.assertEqual(contractor2.contracts.count(), 1)
        self.assertEqual(contract1.specifications.count(), 2)
        self.assertEqual(contract2.specifications.count(), 2)
        self.assertEqual(contract1.contractor, contractor1)
        self.assertEqual(contract2.contractor, contractor2)
        self.assertEqual(contractor1.contracts.annotate(oplata=Sum('payments__amount'))[0].oplata, 3_000_000)
        self.assertEqual(contractor2.contracts.annotate(oplata=Sum('payments__amount'))[0].oplata, 700_000)
        self.assertEqual(contractor1.contracts.annotate(dolg=Sum(F('specifications__price')*F('specifications__quantity')*F('specifications__variable_weight')))[0].dolg, 9_700_000)
        self.assertEqual(contractor2.contracts.annotate(dolg=Sum(F('specifications__price')*F('specifications__quantity')*F('specifications__variable_weight')))[0].dolg, 15_400_000)

    def test_update_object(self):
        c_before = Contractor.objects.filter(pk=1)[0]
        Contractor.objects.filter(pk=1).update(email='222@222.ru')
        c_after = Contractor.objects.filter(pk=1)[0]
        self.assertTrue(c_before == c_after)
        self.assertEquals(c_before.name, c_after.name)
        self.assertFalse(c_before.email == c_after.email)
        self.assertNotEquals(c_before.email, c_after.email)
        self.assertEquals(c_after.email, '222@222.ru')

    def test_model_save(self):
        c = Contractor.objects.create(name='ИП Шальнов С.В.', contact_data='Сергей Викторович +651351351')
        c.save()
        saved_model = Contractor.objects.get(name='ИП Шальнов С.В.')
        self.assertEqual(saved_model.contact_data, 'Сергей Викторович +651351351')

    def test_delete_object(self):
        c = Contractor.objects.create(name='ИП Шальнов С.В.')
        c.save()
        c_found = Contractor.objects.get(name='ИП Шальнов С.В.')
        self.assertEquals(c_found.pk, 7)
        c_found.delete()
        with self.assertRaises(Contractor.DoesNotExist):
            Contractor.objects.get(name='ИП Шальнов С.В.')

    def test_constraints(self):
        c1 = Contractor.objects.create()
        c2 = Contractor.objects.create(name='wrong email', email='1@1.1')
        c3 = Contractor.objects.create(name='long name' * 12)
        c4 = Contractor.objects.create(name='long address', address='1'*201)
        c5 = Contractor.objects.create(name='long email', email='1' * 50 + '@mail.ru')

        c1_after = Contractor.objects.filter(name='')[0]
        c2_after = Contractor.objects.filter(name='wrong email')[0]
        c3_after = Contractor.objects.filter(name__startswith='long name')[0]
        c4_after = Contractor.objects.filter(name__startswith='long address')[0]
        c5_after = Contractor.objects.filter(name__startswith='long email')[0]

        with self.assertRaises(ValidationError) as e1:
            c1_after.full_clean()
        self.assertEquals(e1.exception.messages, ['Это поле не может быть пустым.'])

        with self.assertRaises(ValidationError) as e2:
            c2_after.full_clean()
        self.assertEquals(e2.exception.messages, ['Введите правильный адрес электронной почты.'])

        with self.assertRaises(ValidationError) as e3:
            c3_after.full_clean()
        self.assertEquals(e3.exception.messages, ['Убедитесь, что это значение содержит не более 100 символов (сейчас 108).'])

        with self.assertRaises(ValidationError) as e4:
            c4.full_clean()
        self.assertEquals(e4.exception.messages,
                          ['Убедитесь, что это значение содержит не более 200 символов (сейчас 201).'])

        with self.assertRaises(ValidationError) as e5:
            c5.full_clean()
        self.assertEquals(e5.exception.messages,
                          ['Убедитесь, что это значение содержит не более 50 символов (сейчас 58).'])

    def test_absolute_url(self):
        self.assertEquals(self.full.get_absolute_url(), '/contractors/' + str(self.full.pk) + '/')

    def test_string_representation(self):
        c = self.full
        self.assertEquals(str(c), f'{c.pk}id: {c.name} {c.address}')


# Корректность создания моделей: Убедиться, что модели создаются без ошибок и все поля определены правильно.
# Валидация данных: Проверить, что встроенные ограничения моделей (constraints) работают должным образом и данные вводятся корректно.
# Методы моделей: Протестировать методы моделей, такие как методы сохранения (save), получения строкового представления (str), получения абсолютного URL (get_absolute_url) и другие пользовательские методы.
# Сигналы моделей: Проверить, что сигналы (signals), связанные с моделями, срабатывают в соответствии с ожиданиями.
# Отношения между моделями: Проверить правильность связей между моделями (ForeignKey, OneToOneField, ManyToManyField) и их работоспособность.
# Доступ к данным: Убедиться, что данные могут быть созданы, обновлены, прочитаны и удалены из базы данных с использованием моделей.
# Административная панель: Проверить, что модели могут корректно отображаться и редактироваться в административной панели Django.
# Безопасность: Проверить, что модели обеспечивают безопасность данных, например, через использование правильных разрешений (permissions) и правильного доступа к данным.
# Контекст выполнения: Тестирование моделей в различных контекстах выполнения, например, при использовании фикстур (fixtures) или при работе с миграциями.
# Производительность: Проверить производительность операций с моделями, чтобы удостовериться, что запросы к базе данных выполняются эффективно.