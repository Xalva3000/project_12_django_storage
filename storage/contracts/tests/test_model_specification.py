from datetime import date
from random import choice

from django.core.exceptions import ValidationError
from django.db.models import NOT_PROVIDED, Case, When, F, Sum, ProtectedError
from django.test import TestCase
from products.models import Product
from storage_items.models import StorageItem
from contracts.models import Specification, Contract, Payment, decimal_validator, positive_validator
from contractors.models import Contractor
from decimal import Decimal

quantity_list = (500, 800, 1000)
weight_list = (1, 15, 18, 20, 22)
price_list = (300, 400, 500, 600)


class TestSpecificationModel(TestCase):
    def setUp(self) -> None:
        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.storage_item = StorageItem.objects.create(product=self.products[0],
                                                       weight=18, price=100,
                                                       available=1000, stored=1000)

        self.spec_income = Specification.objects.create(product=self.products[0], price=80,
                                                        quantity=1000, variable_weight=18)
        # self.spec_income.save()
        self.spec_outcome = Specification.objects.create(storage_item=self.storage_item, price=150,
                                                         quantity=500, variable_weight=18)
        # self.spec_outcome.save()

    def test_str_representation(self):
        spec_income = self.spec_income
        spec_outcome = self.spec_outcome

        income_look = f"{spec_income.product.fish} {spec_income.product.cutting} " \
                f"{spec_income.product.size} {spec_income.product.producer}:: " \
                f"({spec_income.variable_weight}кг) x {spec_income.quantity} = " \
                f"{spec_income.variable_weight * spec_income.quantity:,.2f}кг по {spec_income.price}р"

        outcome_look = f"{spec_outcome.storage_item.product.fish} {spec_outcome.storage_item.product.cutting} " \
                   f"{spec_outcome.storage_item.product.size} {spec_outcome.storage_item.product.producer}" \
                   f" (закуп:{spec_outcome.storage_item.price})::({spec_outcome.variable_weight}кг) X {spec_outcome.quantity}=" \
                   f"{spec_outcome.variable_weight*spec_outcome.quantity:,.2f}кг по {spec_outcome.price}р"

        self.assertEqual(str(spec_income), income_look)
        self.assertEqual(str(spec_outcome), outcome_look)

    def test_verbose_name(self):
        # product, storage_item, variable_weight, quantity, price, contract, date_create, date_update
        self.assertEqual(self.spec_income._meta.get_field('product').verbose_name, 'Закупка')
        self.assertEqual(self.spec_income._meta.get_field('storage_item').verbose_name, 'Товар со клада')
        self.assertEqual(self.spec_income._meta.get_field('contract').verbose_name, 'Контракт')
        self.assertEqual(self.spec_income._meta.get_field('variable_weight').verbose_name, 'variable weight')
        self.assertEqual(self.spec_income._meta.get_field('quantity').verbose_name, 'quantity')
        self.assertEqual(self.spec_income._meta.get_field('price').verbose_name, 'price')
        self.assertEqual(self.spec_income._meta.get_field('date_create').verbose_name, 'date create')
        self.assertEqual(self.spec_income._meta.get_field('date_update').verbose_name, 'date update')

    def test_field_contract(self):
        # contract = models.ForeignKey(
        #         'contracts.Contract',
        #         on_delete=models.PROTECT, null=True,
        #         related_name='specifications',
        #         verbose_name='Контракт')
        # print(self.spec_income._meta.get_field('contract').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('contract').verbose_name, 'Контракт')
        self.assertIsNone(self.spec_income._meta.get_field('contract').max_length)
        self.assertFalse(self.spec_income._meta.get_field('contract').blank)
        self.assertTrue(self.spec_income._meta.get_field('contract').null)
        self.assertTrue(self.spec_income._meta.get_field('contract').editable)
        self.assertEqual(self.spec_income._meta.get_field('contract').default, NOT_PROVIDED)
        self.assertEqual(self.spec_income._meta.get_field('contract').help_text, '')

    def test_field_product(self):
        # product = models.ForeignKey(
        #         'products.Product',
        #         on_delete=models.PROTECT, null=True,
        #         related_name='specifications',
        #         verbose_name='Закупка')
        # print(self.spec_income._meta.get_field('product').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('product').verbose_name, 'Закупка')
        self.assertIsNone(self.spec_income._meta.get_field('product').max_length)
        self.assertFalse(self.spec_income._meta.get_field('product').blank)
        self.assertTrue(self.spec_income._meta.get_field('product').null)
        self.assertTrue(self.spec_income._meta.get_field('product').editable)
        self.assertEqual(self.spec_income._meta.get_field('product').default, NOT_PROVIDED)
        self.assertEqual(self.spec_income._meta.get_field('product').help_text, '')

    def test_field_storage_item(self):
        # storage_item = models.ForeignKey(
        #         'storage_items.StorageItem',
        #         on_delete=models.PROTECT, null=True,
        #         related_name='specifications',
        #         verbose_name='Товар со клада')
        # print(self.spec_income._meta.get_field('storage_item').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('storage_item').verbose_name, 'Товар со клада')
        self.assertIsNone(self.spec_income._meta.get_field('storage_item').max_length)
        self.assertFalse(self.spec_income._meta.get_field('storage_item').blank)
        self.assertTrue(self.spec_income._meta.get_field('storage_item').null)
        self.assertTrue(self.spec_income._meta.get_field('storage_item').editable)
        self.assertEqual(self.spec_income._meta.get_field('storage_item').default, NOT_PROVIDED)
        self.assertEqual(self.spec_income._meta.get_field('storage_item').help_text, '')

    def test_field_variable_weight(self):
        # variable_weight = models.DecimalField(validators=[decimal_validator, positive_validator],
        # decimal_places=2, max_digits=7, blank=False, null=False, default=1)
        # print(self.spec_income._meta.get_field('variable_weight').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('variable_weight').verbose_name, 'variable weight')
        self.assertEqual(self.spec_income._meta.get_field('variable_weight').max_digits, 7)
        self.assertEqual(self.spec_income._meta.get_field('variable_weight').decimal_places, 2)
        self.assertIsNone(self.spec_income._meta.get_field('variable_weight').max_length)
        self.assertFalse(self.spec_income._meta.get_field('variable_weight').blank)
        self.assertFalse(self.spec_income._meta.get_field('variable_weight').null)
        self.assertTrue(self.spec_income._meta.get_field('variable_weight').editable)
        self.assertEqual(self.spec_income._meta.get_field('variable_weight').default, 1)
        self.assertIn(positive_validator, self.spec_income._meta.get_field('variable_weight').validators)
        self.assertIn(decimal_validator, self.spec_income._meta.get_field('variable_weight').validators)
        self.assertEqual(self.spec_income._meta.get_field('variable_weight').help_text, '')

    def test_field_price(self):
        # price = models.DecimalField(validators=[decimal_validator, positive_validator],
        # decimal_places=2, max_digits=7, blank=False, null=False, default=0)
        # print(self.spec_income._meta.get_field('price').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('price').verbose_name, 'price')
        self.assertEqual(self.spec_income._meta.get_field('price').max_digits, 7)
        self.assertEqual(self.spec_income._meta.get_field('price').decimal_places, 2)
        self.assertIsNone(self.spec_income._meta.get_field('price').max_length)
        self.assertFalse(self.spec_income._meta.get_field('price').blank)
        self.assertFalse(self.spec_income._meta.get_field('price').null)
        self.assertTrue(self.spec_income._meta.get_field('price').editable)
        self.assertEqual(self.spec_income._meta.get_field('price').default, 0)
        self.assertIn(positive_validator, self.spec_income._meta.get_field('price').validators)
        self.assertIn(decimal_validator, self.spec_income._meta.get_field('price').validators)
        self.assertEqual(self.spec_income._meta.get_field('price').help_text, '')

    def test_field_quantity(self):
        # quantity = models.DecimalField(validators=[decimal_validator, positive_validator],
        # decimal_places=2, max_digits=10, blank=False, null=False, default=1)
        # print(self.spec_income._meta.get_field('quantity').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('quantity').verbose_name, 'quantity')
        self.assertEqual(self.spec_income._meta.get_field('quantity').max_digits, 10)
        self.assertEqual(self.spec_income._meta.get_field('quantity').decimal_places, 2)
        self.assertIsNone(self.spec_income._meta.get_field('quantity').max_length)
        self.assertFalse(self.spec_income._meta.get_field('quantity').blank)
        self.assertFalse(self.spec_income._meta.get_field('quantity').null)
        self.assertTrue(self.spec_income._meta.get_field('quantity').editable)
        self.assertEqual(self.spec_income._meta.get_field('quantity').default, 1)
        self.assertIn(positive_validator, self.spec_income._meta.get_field('quantity').validators)
        self.assertIn(decimal_validator, self.spec_income._meta.get_field('quantity').validators)
        self.assertEqual(self.spec_income._meta.get_field('quantity').help_text, '')

    def test_field_date_create(self):
        # date_create = models.DateField(auto_now_add=True)
        # print(self.spec_income._meta.get_field('date_create').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('date_create').verbose_name, 'date create')
        self.assertIsNone(self.spec_income._meta.get_field('date_create').max_length)
        self.assertFalse(self.spec_income._meta.get_field('date_create').auto_now)
        self.assertTrue(self.spec_income._meta.get_field('date_create').auto_now_add)
        self.assertTrue(self.spec_income._meta.get_field('date_create').blank)
        self.assertFalse(self.spec_income._meta.get_field('date_create').null)
        self.assertFalse(self.spec_income._meta.get_field('date_create').editable)
        self.assertEqual(self.spec_income._meta.get_field('date_create').default, NOT_PROVIDED)
        self.assertEqual(self.spec_income._meta.get_field('date_create').help_text, '')

    def test_field_date_update(self):
        # date_update = models.DateField(auto_now=True)
        # print(self.spec_income._meta.get_field('date_create').__dict__)
        self.assertEqual(self.spec_income._meta.get_field('date_update').verbose_name, 'date update')
        self.assertIsNone(self.spec_income._meta.get_field('date_update').max_length)
        self.assertTrue(self.spec_income._meta.get_field('date_update').auto_now)
        self.assertFalse(self.spec_income._meta.get_field('date_update').auto_now_add)
        self.assertTrue(self.spec_income._meta.get_field('date_update').blank)
        self.assertFalse(self.spec_income._meta.get_field('date_update').null)
        self.assertFalse(self.spec_income._meta.get_field('date_update').editable)
        self.assertEqual(self.spec_income._meta.get_field('date_update').default, NOT_PROVIDED)
        self.assertEqual(self.spec_income._meta.get_field('date_update').help_text, '')

    def test_objects_created(self):
        queryset_all = Specification.objects.all()
        self.assertEquals(queryset_all.count(), 2)

    def test_objects_pk_incremented(self):
        new_specs = [Specification.objects.create(product=choice(self.products), variable_weight=choice(weight_list),
                                      price=choice(price_list), quantity=choice(quantity_list)) for _ in range(10)]
        for s in new_specs:
            s.save()
        for i, s in enumerate(new_specs, 3):
            spec_search = Specification.objects.get(pk=s.pk)
            self.assertEquals(spec_search, s)

    def test_auto_assigning(self):
        storage_item = StorageItem.objects.create(product=self.products[1],
                                                  weight=22, price=300,
                                                  available=100, stored=100)
        new_spec1 = Specification.objects.create(product=self.products[0])
        new_spec2 = Specification.objects.create(storage_item=storage_item)
        new_spec1.save()
        new_spec2.save()
        self.assertEqual(new_spec1.variable_weight, 1)
        self.assertEqual(new_spec1.quantity, 1)
        self.assertEqual(new_spec1.price, 0)
        self.assertIsNone(new_spec1.storage_item)
        self.assertEqual(new_spec1.date_create, date.today())
        self.assertEqual(new_spec1.date_update, date.today())
        self.assertIsNone(new_spec1.contract)

        self.assertIsNone(new_spec2.product)

#
    def test_string_representation(self):
        s_i = self.spec_income
        s_o = self.spec_outcome

        look_i = f"{s_i.product.fish} {s_i.product.cutting} " \
               f"{s_i.product.size} {s_i.product.producer}:: " \
                f"({s_i.variable_weight}кг) x {s_i.quantity} = {s_i.variable_weight * s_i.quantity:,.2f}кг по {s_i.price}р"
        look_o = f"{s_o.storage_item.product.fish} {s_o.storage_item.product.cutting} " \
               f"{s_o.storage_item.product.size} {s_o.storage_item.product.producer}" \
               f" (закуп:{s_o.storage_item.price})::({s_o.variable_weight}кг) X {s_o.quantity}=" \
               f"{s_o.variable_weight*s_o.quantity:,.2f}кг по {s_o.price}р"

        self.assertEqual(str(s_i), look_i)
        self.assertEqual(str(s_o), look_o)


    def test_model_save(self):
        p = choice(self.products)
        s = Specification.objects.create(product=p)
        s.save()
        saved_model_exists = Specification.objects.filter(pk=3)
        self.assertTrue(saved_model_exists)

    def test_update_object(self):
        p = choice(self.products)
        s = Specification.objects.create(product=p)
        s.save()
        Specification.objects.filter(pk=3).update(price=399)

        self.assertTrue(Specification.objects.filter(price=399).exists())


    def test_delete_object(self):
        p = choice(self.products)
        s = Specification.objects.create(product=p)
        s.save()
        s_search = Specification.objects.filter(pk=3)
        self.assertTrue(s_search.exists())
        if s_search.exists():
            s_search[0].delete()

            with self.assertRaises(Specification.DoesNotExist):
                Specification.objects.get(pk=s.pk)


    def test_related_objects(self):
        contractor1 = Contractor.objects.create(name='ООО Алаид')
        contractor2 = Contractor.objects.create(name='ИП Бородин')
        product1 = Product.objects.create(fish='Горбуша')
        product2 = Product.objects.create(fish='Кижуч')
        contract1 = Contract.objects.create(
            contract_type='income',
            contractor=contractor1
        )
        contract2 = Contract.objects.create(
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
        self.assertEqual(Contractor.objects.count(), 2)
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
        self.assertEqual(contract1.specifications.values('product').distinct().count(), 2)
        self.assertEqual(Contract.objects.filter(pk__in=[1,2]).annotate(
            products=Case(When(specifications__product__isnull=True, then=F('specifications__storage_item__product')),
                          default=F('specifications__product'))).values('products').distinct().count(), 2)

    # def decimal_validator(value):
    #     if not isinstance(value, Decimal):
    #         raise ValidationError("Variable must be Decimal")
    # def positive_validator(value):
    #     if value < 0:
    #         raise ValidationError("Variable must be positive")

    # class Specification(models.Model):
    #     product = models.ForeignKey(
    #         'products.Product',
    #         on_delete=models.PROTECT, null=True,
    #         related_name='specifications',
    #         verbose_name='Закупка')
    #     storage_item = models.ForeignKey(
    #         'storage_items.StorageItem',
    #         on_delete=models.PROTECT, null=True,
    #         related_name='specifications',
    #         verbose_name='Товар со клада')
    #     variable_weight = models.DecimalField(validators=[decimal_validator, positive_validator],
    #                                           decimal_places=2, max_digits=7, blank=False, null=False, default=1)
    #     quantity = models.DecimalField(validators=[decimal_validator, positive_validator],
    #                                    decimal_places=2, max_digits=10, blank=False, null=False, default=1)
    #     price = models.DecimalField(validators=[decimal_validator, positive_validator],
    #                                 decimal_places=2, max_digits=7, blank=False, null=False, default=0)
    #     contract = models.ForeignKey(
    #         'contracts.Contract',
    #         on_delete=models.PROTECT, null=True,
    #         related_name='specifications',
    #         verbose_name='Контракт')
    #     date_create = models.DateField(auto_now_add=True)
    #     date_update = models.DateField(auto_now=True)

    def test_product_protection(self):

        with self.assertRaises(ProtectedError):
            self.products[0].delete()

        self.assertEqual(self.spec_income.product, self.products[0])

    def test_storage_item_protection(self):
        with self.assertRaises(ProtectedError):
            self.storage_item.delete()
        self.assertEqual(self.spec_outcome.storage_item, self.storage_item)

    def test_contract_protection(self):
        contractor = Contractor.objects.create(name='ИП Витюгова')
        contract = Contract.objects.create(contractor=contractor)
        self.spec_income.contract = contract
        self.spec_income.save()
        self.assertTrue(Specification.objects.filter(contract__contractor__name='ИП Витюгова').exists())

        with self.assertRaises(ProtectedError):
            self.storage_item.delete()
        self.assertEqual(self.spec_income.contract, contract)

    def test_contractor_of_contract_protection(self):
        contractor = Contractor.objects.create(name='ИП Витюгова')
        contract = Contract.objects.create(contractor=contractor)
        self.spec_income.contract = contract
        self.spec_income.save()
        self.assertTrue(Specification.objects.filter(contract__contractor__name='ИП Витюгова').exists())

        with self.assertRaises(ProtectedError):
            contractor.delete()
        self.assertEqual(self.spec_income.contract, contract)
        self.assertTrue(Contractor.objects.filter(name='ИП Витюгова').exists())

    def test_empty_object(self):
        spec = Specification.objects.create()

        with self.assertRaises(ValidationError) as e1:
            spec.clean()
        self.assertEqual(e1.exception.messages, ['Невозможно создание спецификации без указания продукта или скалдского обекта.'])
        with self.assertRaises(ValidationError) as e2:
            spec.full_clean()
        self.assertEqual(len(e2.exception.messages), 4)

    def test_minimal_object(self):
        contractor = Contractor.objects.create(name='ИП Витюгова')
        contract = Contract.objects.create(contractor=contractor)
        spec = Specification.objects.create(product=self.products[0], contract=contract)
        with self.assertRaises(ValidationError) as e1:
            spec.full_clean()
        self.assertEqual(len(e1.exception.messages), 1)

    def test_none_parameters(self):
        # price = models.DecimalField(validators=[decimal_validator, positive_validator],
        #  decimal_places=2, max_digits=7, blank=False, null=False, default=0)
        # variable_weight = models.DecimalField(validators=[decimal_validator, positive_validator],
        #  decimal_places=2, max_digits=7, blank=False, null=False, default=1)
        # quantity = models.DecimalField(validators=[decimal_validator, positive_validator],
        #  decimal_places=2, max_digits=10, blank=False, null=False, default=1)
        spec = self.spec_income
        spec.price = None
        spec.variable_weight = None
        spec.quantity = None
        with self.assertRaises(ValidationError) as e1:
            spec.full_clean()
        messages = dict(e1.exception)
        expected = ['Это поле не может иметь значение NULL.']
        self.assertEqual(messages['price'], expected)
        self.assertEqual(messages['variable_weight'], expected)
        self.assertEqual(messages['quantity'], expected)

    def test_max_digits_of_parameters(self):
        spec = self.spec_income
        spec.price = 1_000_000.15
        spec.variable_weight = 1_000_000.15
        spec.quantity = 1_000_000_000.15

        with self.assertRaises(ValidationError) as e1:
            spec.full_clean()

        messages = dict(e1.exception)
        self.assertEqual(messages['price'], ['Убедитесь, что вы ввели не более 5 цифр перед запятой.'])
        self.assertEqual(messages['variable_weight'], ['Убедитесь, что вы ввели не более 5 цифр перед запятой.'])
        self.assertEqual(messages['quantity'], ['Убедитесь, что вы ввели не более 8 цифр перед запятой.'])

    def test_decimal_places_of_parameters(self):
        spec = self.spec_income
        spec.price = 1.12345
        spec.variable_weight = 1.12345
        spec.quantity = 1.12345

        with self.assertRaises(ValidationError) as e1:
            spec.full_clean()

        messages = dict(e1.exception)
        expected = ['Убедитесь, что вы ввели не более 2 цифр после запятой.']

        self.assertEqual(messages['price'], expected)
        self.assertEqual(messages['variable_weight'], expected)
        self.assertEqual(messages['quantity'], expected)

    def test_decimal_validator_of_parameters(self):
        spec = self.spec_income
        spec.price = 100
        spec.variable_weight = 100
        spec.quantity = 100
        spec.save()
        spec_after = Specification.objects.filter(price=100)[0]
        self.assertTrue(isinstance(spec_after.price, Decimal))
        self.assertTrue(isinstance(spec_after.variable_weight, Decimal))
        self.assertTrue(isinstance(spec_after.quantity, Decimal))

    def test_positive_validator_of_parameters(self):
        spec = self.spec_income
        spec.price = -100
        spec.variable_weight = -100
        spec.quantity = -100
        with self.assertRaises(ValidationError) as e1:
            spec.full_clean()

        messages = dict(e1.exception)
        expected = ['Variable must be positive']

        self.assertEqual(messages['price'], expected)
        self.assertEqual(messages['variable_weight'], expected)
        self.assertEqual(messages['quantity'], expected)



