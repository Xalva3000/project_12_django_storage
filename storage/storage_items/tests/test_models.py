import decimal
from datetime import date
from pprint import pprint
from random import choice, seed

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError, Q, Max, F
from django.test import TestCase

from products.models import Product
from storage_items.models import StorageItem
from contractors.models import Contractor
from contracts.models import Contract, Specification, Payment

fish_list = ('Tuna', 'Trout', 'Cod', 'Sardine', 'Carp',
             'Mackerel', 'Catfish', 'Tilapia', 'Flounder', 'Halibut',
             'Haddock', 'Perch', 'Swordfish', 'Snapper', 'Herring',
             'Salmon', 'Pickle', 'Лосось', 'Камбала', 'Минтай',
             'Горбуша', 'Кижуч')
cutting_list = ('НР', 'БГ', 'ПБГ', 'филе', '')
size_list = ('S', 'M', 'L', '2L', '')
producer_list = ('Алаид', 'Камчатка Харвест', 'Акрос', 'Скат', '')
price_list = (300,400,500)
quantity_list = (500, 1000)
weight_list = (1, 15, 18, 22)


class TestStorageItemModel(TestCase):
    def setUp(self) -> None:
        seed(1)
        self.products = [Product.objects.create(fish=choice(fish_list),
                                                cutting=choice(cutting_list),
                                                size=choice(size_list),
                                                producer=choice(producer_list)) for _ in range(10)]
        [StorageItem.objects.get_or_create(product=choice(Product.objects.all()),
                                           weight=choice(weight_list),
                                           price=choice(price_list)) for _ in range(100)]

        for si in StorageItem.objects.all():
            si.available = choice(quantity_list)
            si.stored = choice(quantity_list)
            si.save()

    def test_save(self):
        for si in StorageItem.objects.all():
            self.assertNotEqual(si.available, 0)
            self.assertNotEqual(si.stored, 0)

    def test_unique_constraint(self):
        si = choice(StorageItem.objects.all())
        self.assertEqual(si._meta.unique_together[0], ('product', 'price', 'weight'))
        self.assertEqual(StorageItem.objects.all().count(), StorageItem.objects.distinct().count())
        self.assertNotEqual(StorageItem.objects.all(), 100)

        with self.assertRaises(IntegrityError) as e1:
            p = Product.objects.get(pk=1)
            [StorageItem.objects.create(product=p) for _ in range(2)]

    def test_unique_constraint2(self):
        self.assertNotEqual(StorageItem.objects.all(), 73)
        for si in StorageItem.objects.all():
            self.assertEqual(StorageItem.objects.filter(product=si.product, weight=si.weight, price=si.price).count(), 1)

    def test_delete_protection_constraint(self):
        p = Product.objects.get(pk=1)
        with self.assertRaises(ProtectedError) as e1:
            p.delete()

    def test_string_representation(self):
        p = StorageItem.objects.get(pk=1)
        self.assertEqual(str(p), f"{p.product} {p.weight}кг {p.price}руб: {p.available}/{p.stored}")

        # self.assertEqual(field_fish, 50)
        # si = choice(StorageItem.objects.all())
        # pprint(si._meta.get_field('product').__dict__)

    def test_field_product(self):
        si = choice(StorageItem.objects.all())
        self.assertTrue(si._meta.get_field('product').null)
        self.assertFalse(si._meta.get_field('product').blank)
        # self.assertFalse(si._meta.get_field('product'))

    def test_field_weight(self):
        si = choice(StorageItem.objects.all())
        # pprint(si._meta.get_field('weight').__dict__)
        self.assertFalse(si._meta.get_field('weight').blank)
        self.assertFalse(si._meta.get_field('weight').null)
        self.assertEqual(si._meta.get_field('weight').decimal_places, 2)
        self.assertEqual(si._meta.get_field('weight').default, 1)
        self.assertEqual(si._meta.get_field('weight').help_text, '')
        self.assertEqual(si._meta.get_field('weight').max_digits, 7)
        self.assertEqual(si._meta.get_field('weight').name, 'weight')
        self.assertEqual(si._meta.get_field('weight').verbose_name, 'weight')

    def test_field_price(self):
        si = choice(StorageItem.objects.all())
        # pprint(si._meta.get_field('price').__dict__)
        self.assertFalse(si._meta.get_field('price').blank)
        self.assertFalse(si._meta.get_field('price').null)
        self.assertEqual(si._meta.get_field('price').decimal_places, 2)
        self.assertEqual(si._meta.get_field('price').default, 0)
        self.assertEqual(si._meta.get_field('price').help_text, '')
        self.assertEqual(si._meta.get_field('price').max_digits, 7)
        self.assertEqual(si._meta.get_field('price').name, 'price')
        self.assertEqual(si._meta.get_field('price').verbose_name, 'price')

    def test_field_available(self):
        si = choice(StorageItem.objects.all())
        # pprint(si._meta.get_field('available').__dict__)
        self.assertFalse(si._meta.get_field('available').blank)
        self.assertFalse(si._meta.get_field('available').null)
        self.assertEqual(si._meta.get_field('available').decimal_places, 2)
        self.assertEqual(si._meta.get_field('available').default, 0)
        self.assertEqual(si._meta.get_field('available').help_text, '')
        self.assertEqual(si._meta.get_field('available').max_digits, 12)
        self.assertEqual(si._meta.get_field('available').name, 'available')
        self.assertEqual(si._meta.get_field('available').verbose_name, 'available')

    def test_field_stored(self):
        si = choice(StorageItem.objects.all())
        # pprint(si._meta.get_field('stored').__dict__)
        self.assertFalse(si._meta.get_field('stored').blank)
        self.assertFalse(si._meta.get_field('stored').null)
        self.assertEqual(si._meta.get_field('stored').decimal_places, 2)
        self.assertEqual(si._meta.get_field('stored').default, 0)
        self.assertEqual(si._meta.get_field('stored').help_text, '')
        self.assertEqual(si._meta.get_field('stored').max_digits, 12)
        self.assertEqual(si._meta.get_field('stored').name, 'stored')
        self.assertEqual(si._meta.get_field('stored').verbose_name, 'stored')

    def test_available_manager(self):
        p = Product.objects.create(fish='Терпуг')
        si = StorageItem.objects.create(product=p, weight=18, price=99)
        si.save()
        self.assertQuerySetEqual(StorageItem.objects.filter(~Q(available=0)).order_by('pk'),
                                 StorageItem.sellable.all().order_by('pk'))

    def test_not_zero_manager(self):
        p = Product.objects.create(fish='Терпуг')
        si1 = StorageItem.objects.create(product=p, weight=18, price=99, available=0, stored=0)
        si2 = StorageItem.objects.create(product=p, weight=18, price=100, available=1, stored=0)
        si3 = StorageItem.objects.create(product=p, weight=18, price=101, available=0, stored=1)
        si1.save()
        si2.save()
        si3.save()
        self.assertQuerySetEqual(StorageItem.objects.filter(~Q(available=0) | ~Q(stored=0)).order_by('pk'),
                                 StorageItem.not_zero.all().order_by('pk'))

    def test_objects_created(self):
        queryset_all = StorageItem.objects.all()
        self.assertEquals(queryset_all.count(), 72)

    def test_object_delete(self):
        si1 = StorageItem.objects.get(pk=1)
        si1.delete()
        with self.assertRaises(StorageItem.DoesNotExist) as e1:
            StorageItem.objects.get(pk=1)

    def test_delete_all(self):
        StorageItem.objects.all().delete()
        self.assertEqual(StorageItem.objects.all().count(), 0)

    def test_objects_pk_incremented(self):
        start = StorageItem.objects.aggregate(Max('pk'))['pk__max']

        [StorageItem.objects.create(product=Product.objects.create(fish=num)) for num in range(start + 1, start + 6)]
        for i in range(start + 1, start + 6):
            self.assertEquals(StorageItem.objects.get(product__fish=i).pk, i)

    def test_auto_assigning(self):
        p1 = Product.objects.create(fish='1')
        StorageItem.objects.create(product=p1)
        si1 = StorageItem.objects.get(product=p1)
        self.assertEquals(si1.product, p1)
        self.assertEquals(si1.weight, 1)
        self.assertEquals(si1.price, 0)
        self.assertEquals(si1.available, 0)
        self.assertEquals(si1.stored, 0)


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
            storage_item=storage_item1,
            variable_weight=18,
            price=800,
            quantity=1000,
        )
        specification4 = Specification.objects.create(
            contract=contract2,
            storage_item=storage_item2,
            variable_weight=1,
            price=1000,
            quantity=1000,
        )

        self.assertEqual(storage_item1.available - specification3.quantity, 0)
        self.assertEqual(storage_item2.available - specification4.quantity, 0)
        self.assertQuerySetEqual(
            Specification.objects.filter(Q(storage_item__product=product1) | Q(storage_item__product=product2)).order_by('pk'),
            contract2.specifications.all().order_by('pk')
        )
        qs = contract2.specifications.all().annotate(product_ids=F('storage_item__product'))
        self.assertEqual(qs[0].product_ids, 11)
        self.assertIn(specification3, storage_item1.specifications.all())
        self.assertIn(specification4, storage_item2.specifications.all())

    def test_update_object(self):
        new_value = 618
        si_before = StorageItem.objects.get(pk=1)
        StorageItem.objects.filter(pk=1).update(available=new_value, stored=new_value)
        si_after = StorageItem.objects.filter(pk=1)[0]
        self.assertEqual(si_before.product, si_after.product)
        self.assertNotEquals(si_before.available, si_after.available)
        self.assertNotEquals(si_before.stored, si_after.stored)
        self.assertEquals(si_after.available, new_value)
        self.assertEquals(si_after.stored, new_value)

    def test_field_constraints_weight_overflow(self):
        with self.assertRaises(decimal.InvalidOperation) as e1:
            StorageItem.objects.create(product=choice(self.products), weight=100000)

    def test_field_constraints_weight_none(self):
        with self.assertRaises(IntegrityError) as e1:
            StorageItem.objects.create(product=choice(self.products), weight=None)

    def test_field_constraints_weight_overflow_dec_places(self):
        si = StorageItem.objects.create(product=choice(self.products), weight=100.1234)
        self.assertEqual(si.weight, 100.1234)
        with self.assertRaises(ValidationError) as e1:
            si.full_clean()
        self.assertEqual(e1.exception.messages, ['Убедитесь, что вы ввели не более 2 цифр после запятой.'])

    def test_field_constraints_price_overflow(self):
        with self.assertRaises(decimal.InvalidOperation) as e1:
            StorageItem.objects.create(product=choice(self.products), price=100000)

    def test_field_constraints_price_none(self):
        with self.assertRaises(IntegrityError) as e1:
            StorageItem.objects.create(product=choice(self.products), price=None)

    def test_field_constraints_price_overflow_dec_places(self):
        si = StorageItem.objects.create(product=choice(self.products), price=100.1234)
        self.assertEqual(si.price, 100.1234)
        with self.assertRaises(ValidationError) as e1:
            si.full_clean()
        self.assertEqual(e1.exception.messages, ['Убедитесь, что вы ввели не более 2 цифр после запятой.'])

    def test_field_constraints_available_overflow(self):
        with self.assertRaises(decimal.InvalidOperation) as e1:
            StorageItem.objects.create(product=choice(self.products), available=10_000_000_000)

    def test_field_constraints_available_none(self):
        with self.assertRaises(IntegrityError) as e1:
            StorageItem.objects.create(product=choice(self.products), available=None)

    def test_field_constraints_available_overflow_dec_places(self):
        si = StorageItem.objects.create(product=choice(self.products), available=100.1234)
        self.assertEqual(si.available, 100.1234)
        with self.assertRaises(ValidationError) as e1:
            si.full_clean()
        self.assertEqual(e1.exception.messages, ['Убедитесь, что вы ввели не более 2 цифр после запятой.'])

    def test_field_constraints_stored_overflow(self):
        with self.assertRaises(decimal.InvalidOperation) as e1:
            StorageItem.objects.create(product=choice(self.products), stored=10_000_000_000)

    def test_field_constraints_stored_none(self):
        with self.assertRaises(IntegrityError) as e1:
            StorageItem.objects.create(product=choice(self.products), stored=None)

    def test_field_constraints_stored_overflow_dec_places(self):
        si = StorageItem.objects.create(product=choice(self.products), stored=100.1234)
        self.assertEqual(si.stored, 100.1234)
        with self.assertRaises(ValidationError) as e1:
            si.full_clean()
        self.assertEqual(e1.exception.messages, ['Убедитесь, что вы ввели не более 2 цифр после запятой.'])

