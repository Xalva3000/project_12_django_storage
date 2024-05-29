import decimal
from datetime import date
from random import choice

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import NOT_PROVIDED, Sum, F, Value, Case, When, ProtectedError
from django.test import TestCase
from django.urls import reverse

from contractors.models import Contractor
from products.models import Product
from contracts.models import Contract, Specification, Payment, decimal_validator, positive_validator
from storage_items.models import StorageItem



class TestContractModel(TestCase):
    # class Contract(models.Model):
    #     class ContractType(models.TextChoices):
    #         INCOME = ('income', 'Покупка')
    #         OUTCOME = ('outcome', 'Продажа')
    #
    #     contract_type = models.CharField(max_length=7, choices=ContractType,
    #                                      default=ContractType.OUTCOME, verbose_name='Тип контракта')
    #     date_plan = models.DateField(default=datetime.date.today, verbose_name='Планируемая дата исполнения')
    #     reserved = models.BooleanField(default=False)
    #     paid = models.BooleanField(default=False)
    #     executed = models.BooleanField(default=False)
    #     note = models.TextField(blank=True, verbose_name='Заметки')
    #     date_create = models.DateField(auto_now_add=True)
    #     date_execution = models.DateField(blank=True, null=True)
    #     date_delete = models.DateField(blank=True, null=True)
    #     manager_share = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True, default=0)
    #
    #     contractor = models.ForeignKey('contractors.Contractor', on_delete=models.PROTECT,
    #                                    null=True, related_name='contracts', verbose_name='Контрагент')
    #     manager = models.ForeignKey(get_user_model(), on_delete=models.PROTECT,
    #                                 related_name='contracts', null=True, default=None)
    #
    #     def __str__(self):
    #         russian_contract_type = 'Продажа' if self.contract_type == 'outcome' else 'Покупка'
    #         return f"{self.pk} {russian_contract_type} {self.contractor.name} " \
    #                f"({'1' if self.reserved else '0'}|{'1' if self.executed else '0'}|{'1' if self.paid else '0'})"

    def setUp(self) -> None:
        self.contractors = [Contractor.objects.create(name=num) for num in range(1, 11)]
        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]

        self.contracts = [Contract.objects.create(
            contractor=Contractor.objects.get(name=num),
        ) for num in range(1, 11)]
        self.min_contract = Contract.objects.create(
            contract_type=Contract.ContractType.INCOME,
            contractor=choice(self.contractors),
        )
    #
    #     self.min = Contractor.objects.create(name='ООО Алаид')
    #     self.two_fields = Contractor.objects.create(name='ООО Камчатка Харвест', address='г.Петропавловск-Камчатский')
    #     self.empty_mail = Contractor.objects.create(
    #         name='ИП Бородин Е.В.',
    #         address='г.Самара',
    #         email='',
    #     )
    #     self.three_fields = Contractor.objects.create(
    #         name='ИП Монашев С.В.',
    #         address='г.Нижний Новгород',
    #         email='monashev@rambler.ru',
    #     )
    #     self.full = Contractor.objects.create(
    #         name='ООО Лагуна',
    #         address='г.Самара',
    #         email='laguna@mail.ru',
    #         contact_data='Анна +156415111, Василий +516351638163'
    #     )
    #     self.num_object = Contractor.objects.create(
    #         name='111',
    #         address='111',
    #         email='111@111.ru',
    #         contact_data='111'
    #     )

    def test_verbose_name(self):
        self.assertEqual(self.min_contract._meta.get_field('contract_type').verbose_name, 'Тип контракта')
        self.assertEqual(self.min_contract._meta.get_field('date_plan').verbose_name, 'Планируемая дата исполнения')
        self.assertEqual(self.min_contract._meta.get_field('reserved').verbose_name, 'reserved')
        self.assertEqual(self.min_contract._meta.get_field('paid').verbose_name, 'paid')
        self.assertEqual(self.min_contract._meta.get_field('executed').verbose_name, 'executed')
        self.assertEqual(self.min_contract._meta.get_field('note').verbose_name, 'Заметки')
        self.assertEqual(self.min_contract._meta.get_field('date_create').verbose_name, 'date create')
        self.assertEqual(self.min_contract._meta.get_field('date_execution').verbose_name, 'date execution')
        self.assertEqual(self.min_contract._meta.get_field('date_delete').verbose_name, 'date delete')
        self.assertEqual(self.min_contract._meta.get_field('manager_share').verbose_name, 'manager share')
        self.assertEqual(self.min_contract._meta.get_field('contractor').verbose_name, 'Контрагент')
        self.assertEqual(self.min_contract._meta.get_field('manager').verbose_name, 'manager')

    def test_field_contract_type(self):
        #   contract_type = models.CharField(max_length=7, choices=ContractType,
        #                                      default=ContractType.OUTCOME, verbose_name='Тип контракта')
        # print(self.min_contract._meta.get_field('contract_type').__dict__)
        self.assertEqual(self.min_contract._meta.get_field('contract_type').verbose_name, 'Тип контракта')
        self.assertEqual(self.min_contract._meta.get_field('contract_type').max_length, 7)
        self.assertFalse(self.min_contract._meta.get_field('contract_type').blank)
        self.assertFalse(self.min_contract._meta.get_field('contract_type').null)
        self.assertTrue(self.min_contract._meta.get_field('contract_type').editable)
        self.assertEqual(self.min_contract._meta.get_field('contract_type').default, Contract.ContractType.OUTCOME)
        self.assertEqual(self.min_contract._meta.get_field('contract_type').help_text, '')

    def test_field_date_plan(self):
        # date_plan = models.DateField(default=datetime.date.today, verbose_name='Планируемая дата исполнения')
        # print(self.min_contract._meta.get_field('date_plan').__dict__)
        self.assertEqual(self.min_contract._meta.get_field('date_plan').verbose_name, 'Планируемая дата исполнения')
        self.assertIsNone(self.min_contract._meta.get_field('date_plan').max_length)
        self.assertFalse(self.min_contract._meta.get_field('date_plan').auto_now)
        self.assertFalse(self.min_contract._meta.get_field('date_plan').auto_now_add)
        self.assertFalse(self.min_contract._meta.get_field('date_plan').blank)
        self.assertFalse(self.min_contract._meta.get_field('date_plan').null)
        self.assertTrue(self.min_contract._meta.get_field('date_plan').editable)
        self.assertEqual(self.min_contract._meta.get_field('date_plan').default, date.today)
        self.assertEqual(self.min_contract._meta.get_field('date_plan').help_text, '')

    def test_field_reserved(self):
        #     reserved = models.BooleanField(default=False)
        # print(self.min_contract._meta.get_field('reserved').__dict__)
        self.assertEqual(self.min_contract._meta.get_field('reserved').verbose_name, 'reserved')
        self.assertIsNone(self.min_contract._meta.get_field('reserved').max_length)
        self.assertFalse(self.min_contract._meta.get_field('reserved').blank)
        self.assertFalse(self.min_contract._meta.get_field('reserved').null)
        self.assertTrue(self.min_contract._meta.get_field('reserved').editable)
        self.assertEqual(self.min_contract._meta.get_field('reserved').default, False)
        self.assertEqual(self.min_contract._meta.get_field('reserved').help_text, '')

    def test_field_paid(self):
        #     paid = models.BooleanField(default=False)
        self.assertEqual(self.min_contract._meta.get_field('paid').verbose_name, 'paid')
        self.assertIsNone(self.min_contract._meta.get_field('paid').max_length)
        self.assertFalse(self.min_contract._meta.get_field('paid').blank)
        self.assertFalse(self.min_contract._meta.get_field('paid').null)
        self.assertTrue(self.min_contract._meta.get_field('paid').editable)
        self.assertEqual(self.min_contract._meta.get_field('paid').default, False)
        self.assertEqual(self.min_contract._meta.get_field('paid').help_text, '')

    def test_field_executed(self):
        #     executed = models.BooleanField(default=False)
        self.assertEqual(self.min_contract._meta.get_field('executed').verbose_name, 'executed')
        self.assertIsNone(self.min_contract._meta.get_field('executed').max_length)
        self.assertFalse(self.min_contract._meta.get_field('executed').blank)
        self.assertFalse(self.min_contract._meta.get_field('executed').null)
        self.assertTrue(self.min_contract._meta.get_field('executed').editable)
        self.assertEqual(self.min_contract._meta.get_field('executed').default, False)
        self.assertEqual(self.min_contract._meta.get_field('executed').help_text, '')

    def test_field_note(self):
        # note = models.TextField(blank=True, verbose_name='Заметки')
        # print(self.min_contract._meta.get_field('note').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('note').verbose_name, 'Заметки')
        self.assertIsNone(self.min_contract._meta.get_field('note').max_length)
        self.assertTrue(self.min_contract._meta.get_field('note').blank)
        self.assertTrue(self.min_contract._meta.get_field('note').null)
        self.assertTrue(self.min_contract._meta.get_field('note').editable)
        self.assertEqual(self.min_contract._meta.get_field('note').default, NOT_PROVIDED)
        self.assertEqual(self.min_contract._meta.get_field('note').help_text, '')

    def test_field_date_create(self):
        # date_create = models.DateField(auto_now_add=True)
        # print(self.min_contract._meta.get_field('date_create').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('date_create').verbose_name, 'date create')
        self.assertIsNone(self.min_contract._meta.get_field('date_create').max_length)
        self.assertFalse(self.min_contract._meta.get_field('date_create').auto_now)
        self.assertTrue(self.min_contract._meta.get_field('date_create').auto_now_add)
        self.assertTrue(self.min_contract._meta.get_field('date_create').blank)
        self.assertFalse(self.min_contract._meta.get_field('date_create').null)
        self.assertFalse(self.min_contract._meta.get_field('date_create').editable)
        self.assertEqual(self.min_contract._meta.get_field('date_create').default, NOT_PROVIDED)
        self.assertEqual(self.min_contract._meta.get_field('date_create').help_text, '')

    def test_field_date_execution(self):
        # date_create = models.DateField(auto_now_add=True)
        # print(self.min_contract._meta.get_field('date_execution').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('date_execution').verbose_name, 'date execution')
        self.assertIsNone(self.min_contract._meta.get_field('date_execution').max_length)
        self.assertFalse(self.min_contract._meta.get_field('date_execution').auto_now)
        self.assertFalse(self.min_contract._meta.get_field('date_execution').auto_now_add)
        self.assertTrue(self.min_contract._meta.get_field('date_execution').blank)
        self.assertTrue(self.min_contract._meta.get_field('date_execution').null)
        self.assertTrue(self.min_contract._meta.get_field('date_execution').editable)
        self.assertEqual(self.min_contract._meta.get_field('date_execution').default, NOT_PROVIDED)
        self.assertEqual(self.min_contract._meta.get_field('date_execution').help_text, '')


    def test_field_date_delete(self):
        # date_create = models.DateField(auto_now_add=True)
        # print(self.min_contract._meta.get_field('date_delete').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('date_delete').verbose_name, 'date delete')
        self.assertIsNone(self.min_contract._meta.get_field('date_delete').max_length)
        self.assertFalse(self.min_contract._meta.get_field('date_delete').auto_now)
        self.assertFalse(self.min_contract._meta.get_field('date_delete').auto_now_add)
        self.assertTrue(self.min_contract._meta.get_field('date_delete').blank)
        self.assertTrue(self.min_contract._meta.get_field('date_delete').null)
        self.assertTrue(self.min_contract._meta.get_field('date_delete').editable)
        self.assertEqual(self.min_contract._meta.get_field('date_delete').default, NOT_PROVIDED)
        self.assertEqual(self.min_contract._meta.get_field('date_delete').help_text, '')

    def test_field_manager_share(self):
        # manager_share = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True, default=0)
        # print(self.min_contract._meta.get_field('manager_share').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('manager_share').verbose_name, 'manager share')
        self.assertIsNone(self.min_contract._meta.get_field('manager_share').max_length)
        self.assertEqual(self.min_contract._meta.get_field('manager_share').max_digits, 12)
        self.assertEqual(self.min_contract._meta.get_field('manager_share').decimal_places, 2)
        self.assertTrue(self.min_contract._meta.get_field('manager_share').blank)
        self.assertTrue(self.min_contract._meta.get_field('manager_share').null)
        self.assertTrue(self.min_contract._meta.get_field('manager_share').editable)
        self.assertEqual(self.min_contract._meta.get_field('manager_share').default, 0)
        self.assertEqual(self.min_contract._meta.get_field('manager_share').help_text, '')


    def test_field_contractor(self):
        # contractor = models.ForeignKey('contractors.Contractor', on_delete=models.PROTECT,
        #                                    null=True, related_name='contracts', verbose_name='Контрагент')
        # print(self.min_contract._meta.get_field('contractor').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('contractor').verbose_name, 'Контрагент')
        self.assertIsNone(self.min_contract._meta.get_field('contractor').max_length)
        self.assertFalse(self.min_contract._meta.get_field('contractor').blank)
        self.assertTrue(self.min_contract._meta.get_field('contractor').null)
        self.assertTrue(self.min_contract._meta.get_field('contractor').editable)
        self.assertEqual(self.min_contract._meta.get_field('contractor').related_model, Contractor)
        self.assertEqual(self.min_contract._meta.get_field('contractor')._related_name, 'contracts')
        self.assertEqual(self.min_contract._meta.get_field('contractor').default, NOT_PROVIDED)
        self.assertEqual(self.min_contract._meta.get_field('contractor').help_text, '')

    def test_field_manager(self):
        #     manager = models.ForeignKey(get_user_model(), on_delete=models.PROTECT,
        #                                 related_name='contracts', null=True, default=None)
        # print(self.min_contract._meta.get_field('manager').__dict__)

        self.assertEqual(self.min_contract._meta.get_field('manager').verbose_name, 'manager')
        self.assertIsNone(self.min_contract._meta.get_field('manager').max_length)
        self.assertTrue(self.min_contract._meta.get_field('manager').blank)
        self.assertTrue(self.min_contract._meta.get_field('manager').null)
        self.assertIsNone(self.min_contract._meta.get_field('manager').default)
        self.assertTrue(self.min_contract._meta.get_field('manager').editable)
        self.assertEqual(self.min_contract._meta.get_field('manager').related_model, get_user_model())
        self.assertEqual(self.min_contract._meta.get_field('manager')._related_name, 'contracts')
        self.assertEqual(self.min_contract._meta.get_field('manager').help_text, '')

    def test_objects_created(self):
        queryset_all = Contractor.objects.all()
        self.assertEquals(queryset_all.count(), 10)
#
    def test_objects_pk_incremented(self):
        for i in range(1, 11):
            self.assertEquals(Contract.objects.get(
                contract_type=Contract.ContractType.OUTCOME,
                contractor=Contractor.objects.get(name=i),).pk, i)

    def test_auto_assigning(self):
        contractor = self.contractors[0]
        c = Contract.objects.create(contractor=contractor)
        self.assertEquals(c.contract_type, Contract.ContractType.OUTCOME)
        self.assertEquals(c.date_plan, date.today())
        self.assertFalse(c.reserved)
        self.assertFalse(c.paid)
        self.assertFalse(c.executed)
        self.assertIsNone(c.note, '')
        self.assertEquals(c.date_create, date.today())
        self.assertIsNone(c.date_execution)
        self.assertIsNone(c.date_delete)
        self.assertEquals(c.manager_share, 0)
        self.assertEquals(c.contractor, contractor)
        self.assertIsNone(c.manager)

    def test_model_absolute_url(self):
        contractor = self.contractors[0]
        c = Contract.objects.create(contractor=contractor)
        self.assertEqual(c.get_absolute_url(), reverse('contracts:contract', args=[c.pk]))

    def test_absolute_url(self):
        c = self.min_contract
        self.assertEqual(c.get_absolute_url(), reverse('contracts:contract', kwargs={'pk': c.pk}))

#
    def test_contract_type_choices(self):
        income_type = Contract.ContractType.INCOME
        outcome_type = Contract.ContractType.OUTCOME

        self.assertEqual(income_type.label, 'Покупка')
        self.assertEqual(outcome_type.label, 'Продажа')
        self.assertEqual(income_type.value, 'income')
        self.assertEqual(outcome_type.value, 'outcome')

    def test_string_representation(self):
        c = self.min_contract
        russian_contract_type = 'Продажа' if c.contract_type == 'outcome' else 'Покупка'
        r = f"{c.pk} {russian_contract_type} {c.contractor.name} "\
            f"({'1' if c.reserved else '0'}|{'1' if c.executed else '0'}|{'1' if c.paid else '0'})"
        self.assertEquals(str(c), r)

    def test_model_save(self):
        contractor = Contractor.objects.create(name='Never created')
        c = Contract.objects.create(contractor=contractor)
        c.save()
        saved_model_exists = Contract.objects.filter(contractor__name='Never created').exists()
        self.assertTrue(saved_model_exists)

    def test_update_object(self):
        contractor = Contractor.objects.create(name='Never created')
        c = Contract.objects.create(contractor=contractor)
        c_before = Contract.objects.filter(contractor__name='Never created')[0]
        Contract.objects.filter(pk=c.pk).update(date_plan='2020-02-20')
        c_after = Contract.objects.filter(date_plan='2020-02-20')
        self.assertTrue(c_after.exists())
        self.assertNotEqual(c_before.date_plan, c_after[0].date_plan)
        self.assertEqual(c_before.date_plan, date.today())
        self.assertEqual(c_after[0].date_plan, date(2020, 2, 20))

    def test_delete_object(self):
        contractor = Contractor.objects.create(name='Never created')
        c = Contract.objects.create(contractor=contractor)
        c.save()
        c_search = Contract.objects.filter(contractor__name='Never created')
        self.assertTrue(c_search.exists())
        if c_search.exists():
            c_search[0].delete()

            with self.assertRaises(Contract.DoesNotExist):
                Contract.objects.get(pk=c.pk)

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
        self.assertEqual(Contractor.objects.count(), 12)
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
        self.assertEqual(Contract.objects.filter(pk__in=[12, 13]).annotate(
            products=Case(When(specifications__product__isnull=True, then=F('specifications__storage_item__product')),
                          default=F('specifications__product'))).values('products').distinct().count(), 2)

    def test_contractor_protection(self):
        contractor = self.contractors[0]
        c = Contract.objects.create(contractor=contractor)
        with self.assertRaises(ProtectedError):
            contractor.delete()
        self.assertEqual(c.contractor, contractor)

    def test_manager_protection(self):
        contractor = self.contractors[0]
        manager = get_user_model().objects.create_user('homer', 'homer@simpson.net', 'simpson')
        c = Contract.objects.create(contractor=contractor, manager=manager)
        with self.assertRaises(ProtectedError):
            manager.delete()
        self.assertEqual(c.manager, manager)

    def test_constraints_empty_contractor(self):
        c = Contract.objects.create()
        with self.assertRaises(ValidationError) as e1:
            c.full_clean()
        self.assertEquals(e1.exception.messages, ['Это поле не может быть пустым.'])

    def test_contract_type_not_valid_value(self):
        contractor = self.contractors[0]
        c = Contract.objects.create(contractor=contractor, contract_type='111')
        with self.assertRaises(ValidationError) as e1:
            c.full_clean()
        self.assertEqual(e1.exception.messages, ["Значения '111' нет среди допустимых вариантов."])

    def test_date_plan_default_value(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertEqual(c.date_plan, date.today())

    def test_date_plan_set_valid_date(self):
        c = Contract.objects.create(contractor=self.contractors[0], date_plan=date(2020, 2, 2))
        c.save()
        c_found = Contract.objects.get(pk=c.pk)
        self.assertEqual(c_found.date_plan, date(2020, 2, 2))

    def test_date_plan_not_valid(self):
        with self.assertRaises(ValidationError) as e1:
            Contract.objects.create(contractor=self.contractors[0], date_plan='uyyjdghmfhgjmfhjmfhjmgfhjm')
        self.assertEqual(e1.exception.messages, ['Значение “uyyjdghmfhgjmfhjmfhjmgfhjm” имеет неверный формат даты. Оно должно быть в формате YYYY-MM-DD.'])

    def test_date_plan_not_valid2(self):
        with self.assertRaises(ValidationError) as e1:
            Contract.objects.create(contractor=self.contractors[0], date_plan='9999-99-99')
        self.assertEqual(e1.exception.messages, ['Значение “9999-99-99” имеет корректный формат (YYYY-MM-DD), но это недействительная дата.'])

    def test_date_plan_not_valid3(self):
        with self.assertRaises(ValidationError) as e1:
            Contract.objects.create(contractor=self.contractors[0], date_plan='2999-13-01')
        self.assertEqual(e1.exception.messages, ['Значение “2999-13-01” имеет корректный формат (YYYY-MM-DD), но это недействительная дата.'])

    def test_date_plan_not_valid4(self):
        with self.assertRaises(ValidationError) as e1:
            Contract.objects.create(contractor=self.contractors[0], date_plan='2999-12-32')
        self.assertEqual(e1.exception.messages, [
            'Значение “2999-12-32” имеет корректный формат (YYYY-MM-DD), но это недействительная дата.'])

    def test_rpe_default(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertFalse(c.reserved)
        self.assertFalse(c.paid)
        self.assertFalse(c.executed)

    def test_rpe_custom(self):
        c = Contract.objects.create(contractor=self.contractors[0], reserved=True, paid=True, executed=True)
        c.save()
        c.full_clean()
        self.assertTrue(c.reserved)
        self.assertTrue(c.paid)
        self.assertTrue(c.executed)

    def test_note_default(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertIsNone(c.note)

    def test_note_custom(self):
        c = Contract.objects.create(contractor=self.contractors[0], note='12321dvcsdvd мвуамва $#@!$@')
        c.save()
        c.full_clean()
        self.assertEqual(c.note, '12321dvcsdvd мвуамва $#@!$@')

    def test_date_create_default(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertEqual(c.date_create, date.today())

    def test_date_execution_default(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertIsNone(c.date_execution)

    def test_date_delete_default(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertIsNone(c.date_delete)

    def test_manager_share_default(self):
        c = Contract.objects.create(contractor=self.contractors[0])
        self.assertEqual(c.manager_share, 0)

    def test_manager_share_valid(self):
        c = Contract.objects.create(contractor=self.contractors[0], manager_share=200_000)
        c.save()
        c.full_clean()
        self.assertEqual(c.manager_share, 200_000)

    def test_manager_share_overflow_decimal_places(self):
        with self.assertRaises(ValidationError) as e1:
            c = Contract.objects.create(contractor=self.contractors[0], manager_share=200_000.1567)
            c.save()
            c.full_clean()
        self.assertEqual(e1.exception.messages, ['Убедитесь, что вы ввели не более 2 цифр после запятой.'])

    def test_manager_share_overflow(self):
        with self.assertRaises(decimal.InvalidOperation) as e1:
            Contract.objects.create(contractor=self.contractors[0], manager_share=20_000_000_000.15)






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