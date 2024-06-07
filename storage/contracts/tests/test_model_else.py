from datetime import date
from random import choice


from _decimal import InvalidOperation
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db.models import NOT_PROVIDED, ProtectedError, Sum
from django.test import TestCase

from contracts.models import Payment
from contracts.models import Contract, Action
from contractors.models import Contractor



class TestPaymentModel(TestCase):
    def setUp(self) -> None:
        self.contractor = Contractor.objects.create(name='ООО Алаид')
        self.contract = Contract.objects.create(contractor=self.contractor)
        self.min_payment = Payment.objects.create(contract=self.contract, amount=1_000_000)
        # self.min_payment.save()


    def test_object_create(self):
        self.assertTrue(Payment.objects.filter(contract=self.contract).exists())

    def test_object_update(self):
        p = Payment.objects.get(pk=1)
        p.amount = 100
        p.save()
        self.assertTrue(Payment.objects.filter(amount=100).exists())

    def test_object_delete(self):
        p = Payment.objects.get(pk=1)
        p.delete()
        self.assertFalse(Payment.objects.all().exists())

    def str_representation(self):
        p = self.min_payment
        self.assertEqual(str(p), f"{p.contract.pk} {p.date_payment} {p.amount}руб.")


    def test_field_contract(self):
        # print(self.min_payment._meta.get_field('contract').__dict__)
        self.assertEqual(self.min_payment._meta.get_field('contract').verbose_name, 'Платежи')
        self.assertIsNone(self.min_payment._meta.get_field('contract').max_length)
        self.assertFalse(self.min_payment._meta.get_field('contract').blank)
        self.assertTrue(self.min_payment._meta.get_field('contract').null)
        self.assertTrue(self.min_payment._meta.get_field('contract').editable)
        self.assertEqual(self.min_payment._meta.get_field('contract').default, NOT_PROVIDED)
        self.assertEqual(self.min_payment._meta.get_field('contract').help_text, '')
        self.assertEqual(self.min_payment._meta.get_field('contract').related_model, Contract)

    def test_field_date_create(self):
        # print(self.min_payment._meta.get_field('date_payment').__dict__)
        self.assertEqual(self.min_payment._meta.get_field('date_payment').verbose_name, 'date payment')
        self.assertIsNone(self.min_payment._meta.get_field('date_payment').max_length)
        self.assertFalse(self.min_payment._meta.get_field('date_payment').auto_now)
        self.assertTrue(self.min_payment._meta.get_field('date_payment').auto_now_add)
        self.assertTrue(self.min_payment._meta.get_field('date_payment').blank)
        self.assertFalse(self.min_payment._meta.get_field('date_payment').null)
        self.assertFalse(self.min_payment._meta.get_field('date_payment').editable)
        self.assertEqual(self.min_payment._meta.get_field('date_payment').default, NOT_PROVIDED)
        self.assertEqual(self.min_payment._meta.get_field('date_payment').help_text, '')

    def test_field_quantity(self):
        # amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False, default=0)
        # print(self.min_payment._meta.get_field('amount').__dict__)
        self.assertEqual(self.min_payment._meta.get_field('amount').verbose_name, 'amount')
        self.assertEqual(self.min_payment._meta.get_field('amount').max_digits, 10)
        self.assertEqual(self.min_payment._meta.get_field('amount').decimal_places, 2)
        self.assertIsNone(self.min_payment._meta.get_field('amount').max_length)
        self.assertFalse(self.min_payment._meta.get_field('amount').blank)
        self.assertFalse(self.min_payment._meta.get_field('amount').null)
        self.assertTrue(self.min_payment._meta.get_field('amount').editable)
        self.assertEqual(self.min_payment._meta.get_field('amount').default, 0)
        # self.assertEqual(self.min_payment._meta.get_field('amount').validators, [DecimalValidator])
        self.assertEqual(self.min_payment._meta.get_field('amount').help_text, '')


    # class Payment(models.Model):
    #     contract = models.ForeignKey(
    #         'contracts.Contract',
    #         on_delete=models.PROTECT, null=True,
    #         related_name='payments',
    #         verbose_name='Платежи')
    #     date_payment = models.DateField(auto_now_add=True, null=False)
    #     amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False, default=0)
    #
    #     def __str__(self):
    #         return f"{self.contract.pk} {self.date_payment} {self.amount}руб."

    def test_contract_protection(self):
        with self.assertRaises(ProtectedError) as e1:
            self.contract.delete()
        self.assertTrue(Contract.objects.filter(pk=self.contract.pk).exists())

    def test_contract_update(self):
        new_contract = Contract.objects.create(contractor=self.contractor)
        p = Payment.objects.get(pk=1)
        p.contract = new_contract
        p.save()
        self.assertEqual(Payment.objects.get(pk=1).contract, new_contract)

    def test_date_payment_auto_add(self):
        p = Payment.objects.create(contract=self.contract, date_payment=None, amount=100)
        self.assertEqual(p.date_payment, date.today())

    def test_default_amount(self):
        p = Payment.objects.create(contract=self.contract)
        p.save()
        self.assertEqual(Payment.objects.get(pk=2).amount, 0)

    def test_negative_amount(self):
        p = Payment.objects.create(contract=self.contract, amount=-100)
        p.save()
        self.assertTrue(Payment.objects.filter(amount=-100).exists())
        p = Payment.objects.get(pk=2)
        self.assertEqual(p.amount, -100)

    def test_overflow_amount_decimal_places(self):
        p = Payment.objects.create(contract=self.contract, amount=10.12345)
        with self.assertRaises(ValidationError) as e1:
            p.full_clean()

        self.assertEqual(e1.exception.messages, ['Убедитесь, что вы ввели не более 2 цифр после запятой.'])

    def test_overflow_amount_decimal_numbers(self):
        p = self.min_payment
        with self.assertRaises(InvalidOperation) as e1:
            p.amount = 100_000_000.12
            p.save()

        with self.assertRaises(InvalidOperation) as e2:
            Payment.objects.create(contract=self.contract, amount=100_000_000.12)

    # def test_not_existing_contract(self):
    #     with self.assertRaises(Exception) as e1:
    #         payment = Payment.objects.create(contract_id=1000, amount=10_000)
    #         payment.full_clean()
    #     self.assertEqual(e1.exception.messages, ['Объект модели contract со значением поля id, равным 1000, не существует.'])

    def test_date_update(self):
        new_date = date(2020, 2, 2)
        p = self.min_payment
        p.date_payment = new_date
        p.save()
        self.assertEqual(Payment.objects.get(pk=1).date_payment, new_date)

    def test_relations(self):
        contractor2 = Contractor.objects.create(name='ИП Бородин')
        contract1 = self.contract
        contract2 = Contract.objects.create(contractor=contractor2)
        payment1 = Payment.objects.create(contract=contract1, amount=1000)
        payment2 = Payment.objects.create(contract=contract2, amount=1000)
        payments = [Payment.objects.create(contract=choice((contract1, contract2)),
                                           amount=num) for num in range(1_000_000, 2_000_001, 200_000)]

        self.assertEqual(Payment.objects.filter(contract=contract1).aggregate(s=Sum('amount'))['s'],
                         contract1.payments.aggregate(s=Sum('amount'))['s'])
        self.assertEqual(Payment.objects.filter(contract=contract2).aggregate(s=Sum('amount'))['s'],
                         contract2.payments.aggregate(s=Sum('amount'))['s'])
        self.assertNotEqual(payment1.contract.contractor.name, payment2.contract.contractor.name)
        self.assertEqual(contractor2.contracts.aggregate(s=Sum('payments__amount'))['s'],
                         Payment.objects.filter(contract=contract2).aggregate(s=Sum('amount'))['s'])


class TestActionModel(TestCase):
    # class Action(models.Model):
    #     contract = models.ForeignKey(
    #         'contracts.Contract',
    #         on_delete=models.PROTECT, null=True,
    #         related_name='actions',
    #         verbose_name='Действия')
    #
    #     action = models.TextField(max_length=100)
    #     date_action = models.DateField(auto_now_add=True, null=False)


    def setUp(self) -> None:
        self.contractor = Contractor.objects.create(name='ООО Алаид')
        self.contract = Contract.objects.create(contractor=self.contractor)
        self.action = Action.objects.create(contract=self.contract)

    def test_object_create(self):
        self.assertTrue(Action.objects.filter(contract=self.contract).exists())

    def test_object_update(self):
        a = Action.objects.get(pk=1)
        a.action = 'contract 1 created'
        a.save()
        self.assertTrue(Action.objects.filter(action='contract 1 created').exists())

    def test_object_delete(self):
        a = Action.objects.get(pk=1)
        a.delete()
        self.assertFalse(Action.objects.all().exists())

    def str_representation(self):
        a = self.action
        self.assertEqual(str(a), f"{a.date_action}--{a.action}")

    def test_field_contract(self):
        # print(self.action._meta.get_field('contract').__dict__)
        self.assertEqual(self.action._meta.get_field('contract').verbose_name, 'Действия')
        self.assertIsNone(self.action._meta.get_field('contract').max_length)
        self.assertFalse(self.action._meta.get_field('contract').blank)
        self.assertTrue(self.action._meta.get_field('contract').null)
        self.assertTrue(self.action._meta.get_field('contract').editable)
        self.assertEqual(self.action._meta.get_field('contract').default, NOT_PROVIDED)
        self.assertEqual(self.action._meta.get_field('contract').help_text, '')
        self.assertEqual(self.action._meta.get_field('contract').related_model, Contract)

    def test_field_date_action(self):
        # print(self.action._meta.get_field('date_action').__dict__)
        self.assertEqual(self.action._meta.get_field('date_action').verbose_name, 'date action')
        self.assertIsNone(self.action._meta.get_field('date_action').max_length)
        self.assertFalse(self.action._meta.get_field('date_action').auto_now)
        self.assertTrue(self.action._meta.get_field('date_action').auto_now_add)
        self.assertTrue(self.action._meta.get_field('date_action').blank)
        self.assertFalse(self.action._meta.get_field('date_action').null)
        self.assertFalse(self.action._meta.get_field('date_action').editable)
        self.assertEqual(self.action._meta.get_field('date_action').default, NOT_PROVIDED)
        self.assertEqual(self.action._meta.get_field('date_action').help_text, '')

    def test_field_action(self):
        # print(self.action._meta.get_field('action').__dict__)
        self.assertEqual(self.action._meta.get_field('action').verbose_name, 'action')
        self.assertEqual(self.action._meta.get_field('action').max_length, 100)
        self.assertFalse(self.action._meta.get_field('action').blank)
        self.assertFalse(self.action._meta.get_field('action').null)
        self.assertTrue(self.action._meta.get_field('action').editable)
        self.assertEqual(self.action._meta.get_field('action').default, NOT_PROVIDED)
        self.assertEqual(self.action._meta.get_field('action').help_text, '')

    def test_contract_protection(self):
        with self.assertRaises(ProtectedError) as e1:
            self.contract.delete()
        self.assertTrue(Contract.objects.filter(pk=self.contract.pk).exists())

    def test_contract_update(self):
        new_contract = Contract.objects.create(contractor=self.contractor)
        a = Action.objects.get(pk=1)
        a.contract = new_contract
        a.save()
        self.assertEqual(Action.objects.get(pk=1).contract, new_contract)

    def test_date_payment_auto_add(self):
        a = Action.objects.create(contract=self.contract, date_action=None, action='test')
        self.assertEqual(a.date_action, date.today())

    def test_default_action(self):
        a = Action.objects.create(contract=self.contract)
        a.save()
        self.assertEqual(Action.objects.get(pk=2).action, '')

    def test_overflow_action(self):
        a = Action.objects.create(contract=self.contract, action='a'*101)
        a.save()
        a.full_clean()
        a = Action.objects.get(pk=2)
        self.assertEqual(len(a.action), 101)

    def test_date_update(self):
        new_date = date(2020, 2, 2)
        a = self.action
        a.date_action = new_date
        a.save()
        self.assertEqual(Action.objects.get(pk=1).date_action, new_date)
