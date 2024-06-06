from datetime import date
from pprint import pprint
from random import choice, seed

from django.forms import Select, DateInput, Textarea, NumberInput, inlineformset_factory
from django.test import TestCase

from contracts.forms import AddContractForm, UpdateContractForm, AddSpecificationForm, SpecificationFormSet
from contracts.models import Contract, Specification
from contractors.models import Contractor
from products.models import Product
from storage_items.models import StorageItem

data_dct = {
    'minimal_data': {
        'contract_type': Contract.ContractType.INCOME,
        'contractor': 1,
        'date_plan': date.today(),
        'note': '',
    },
    'full_data': {
        'contract_type': Contract.ContractType.INCOME,
        'contractor': 1,
        'date_plan': date.today(),
        'note': 'авто 241',
    },
    'empty_data': {
        'contractor': '',
    },
    'no_data': {},
}


class TestAddContractForm(TestCase):
    # class AddContractForm(models.ModelForm):
    #     def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         self.helper = FormHelper(self)
    #         self.helper.add_input(Submit('внести', 'Внести', css_class="btn btn-success mt-3"))
    #
    #     contract_type = forms.ChoiceField(choices=Contract.ContractType.choices,
    #                                       widget=forms.Select(attrs={'class': 'form-select'}),
    #                                       label='Тип контракта')
    #     date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }),
    #                                 label='Планируемая дата исполнения')
    #     note = forms.Textarea()
    #
    #     class Meta:
    #         model = Contract
    #         fields = ['contract_type', 'date_plan', 'contractor', 'note']
    #         widgets = {'contractor': forms.Select(attrs={'class': 'form-select'})}

    def test_contract_type_field(self):
        form = AddContractForm()

        self.assertEqual(form.fields['contract_type'].label, 'Тип контракта')
        self.assertTrue(form.fields['contract_type'].required)
        self.assertEqual(form.fields['contract_type'].help_text, '')
        self.assertIsInstance(form.fields['contract_type'].widget, Select)
        self.assertEqual(len(form.fields['contract_type'].error_messages), 2)
        self.assertEqual(len(form.fields['contract_type'].validators), 0)
        self.assertEqual(form.fields['contract_type']._choices, [('income', 'Покупка'), ('outcome', 'Продажа')])

    def test_date_plan_field(self):
        form = AddContractForm()
        self.assertEqual(form.fields['date_plan'].label, 'Планируемая дата исполнения')
        self.assertTrue(form.fields['date_plan'].required)
        self.assertEqual(form.fields['date_plan'].help_text, '')
        self.assertIsInstance(form.fields['date_plan'].widget, DateInput)
        self.assertEqual(len(form.fields['date_plan'].error_messages), 2)
        self.assertEqual(len(form.fields['date_plan'].validators), 0)

    def test_contractor_field(self):
        contractor = Contractor.objects.create(name="ИП Бородин")
        form = AddContractForm()

        self.assertEqual(form.fields['contractor'].label, 'Контрагент')
        self.assertTrue(form.fields['contractor'].required)
        self.assertEqual(form.fields['contractor'].help_text, '')
        self.assertEqual(form.fields['contractor']._queryset[0], contractor)
        self.assertEqual(form.fields['contractor']._queryset.count(), 1)
        self.assertIsInstance(form.fields['contractor'].widget, Select)
        self.assertEqual(len(form.fields['contractor'].error_messages), 2)
        self.assertEqual(len(form.fields['contractor'].validators), 0)

    def test_note_field(self):
        form = AddContractForm()
        # print(form.fields['note'].__dict__)
        self.assertEqual(form.fields['note'].label, 'Заметки')
        self.assertIsNone(form.fields['note'].max_length)
        self.assertIsNone(form.fields['note'].min_length)
        self.assertTrue(form.fields['note'].strip)
        self.assertEqual(form.fields['note'].empty_value, '')
        self.assertFalse(form.fields['note'].required)
        self.assertEqual(form.fields['note'].help_text, '')
        self.assertIsInstance(form.fields['note'].widget, Textarea)
        self.assertEqual(len(form.fields['note'].error_messages), 1)
        self.assertEqual(len(form.fields['note'].validators), 1)

    def test_valid_data(self):
        contractor = Contractor.objects.create(name="ИП Бородин")

        form_minimail = AddContractForm(data=data_dct['minimal_data'])
        form_full = AddContractForm(data=data_dct['full_data'])

        self.assertTrue(form_minimail.is_valid())
        self.assertTrue(form_full.is_valid())

    def test_invalid_data(self):
        contractor = Contractor.objects.create(name="ИП Бородин")
        form_empty = AddContractForm(data=data_dct['empty_data'])
        form_no_data = AddContractForm(data=data_dct['no_data'])
        self.assertFalse(form_empty.is_valid())
        self.assertFalse(form_no_data.is_valid())

    # def test_helper(self):
    #     contractor = Contractor.objects.create(name="ИП Бородин")
    #     form_full = AddContractForm(data=data_dct['full_data'])
    #     print(form_full.helper.__dict__)


class TestUpdateContractForm(TestCase):
    def setUp(self) -> None:
        self.data_dct = {
            'minimal_data': {
                'contractor': 1,
                'date_plan': date.today(),
                'note': '',
            },
            'full_data': {
                'contractor': 1,
                'date_plan': date.today(),
                'note': 'авто 241',
            },
            'empty_data': {
                'contractor': '',
            },
            'no_data': {},
        }

    # class UpdateContractForm(forms.ModelForm):
    #     def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         self.helper = FormHelper(self)
    #         self.helper.add_input(Submit('внести', 'Внести', css_class="btn btn-success mt-3"))
    #
    #     date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }),
    #                                 label='Планируемая дата исполнения')
    #
    #     class Meta:
    #         model = Contract
    #         fields = ['date_plan', 'contractor', 'note']
    #         widgets = {'contractor': forms.Select(attrs={'class': 'form-select'})}

    def test_date_plan_field(self):
        form = UpdateContractForm()
        self.assertEqual(form.fields['date_plan'].label, 'Планируемая дата исполнения')
        self.assertTrue(form.fields['date_plan'].required)
        self.assertEqual(form.fields['date_plan'].help_text, '')
        self.assertIsInstance(form.fields['date_plan'].widget, DateInput)
        self.assertEqual(len(form.fields['date_plan'].error_messages), 2)
        self.assertEqual(len(form.fields['date_plan'].validators), 0)

    def test_contractor_field(self):
        contractor = Contractor.objects.create(name="ИП Бородин")
        form = UpdateContractForm()

        self.assertEqual(form.fields['contractor'].label, 'Контрагент')
        self.assertTrue(form.fields['contractor'].required)
        self.assertEqual(form.fields['contractor'].help_text, '')
        self.assertEqual(form.fields['contractor']._queryset[0], contractor)
        self.assertEqual(form.fields['contractor']._queryset.count(), 1)
        self.assertIsInstance(form.fields['contractor'].widget, Select)
        self.assertEqual(len(form.fields['contractor'].error_messages), 2)
        self.assertEqual(len(form.fields['contractor'].validators), 0)

    def test_note_field(self):
        form = UpdateContractForm()
        # print(form.fields['note'].__dict__)
        self.assertEqual(form.fields['note'].label, 'Заметки')
        self.assertIsNone(form.fields['note'].max_length)
        self.assertIsNone(form.fields['note'].min_length)
        self.assertTrue(form.fields['note'].strip)
        self.assertEqual(form.fields['note'].empty_value, '')
        self.assertFalse(form.fields['note'].required)
        self.assertEqual(form.fields['note'].help_text, '')
        self.assertIsInstance(form.fields['note'].widget, Textarea)
        self.assertEqual(len(form.fields['note'].error_messages), 1)
        self.assertEqual(len(form.fields['note'].validators), 1)

    def test_valid_data(self):
        contractor = Contractor.objects.create(name="ИП Бородин")

        form_minimail = UpdateContractForm(data=self.data_dct['minimal_data'])
        form_full = UpdateContractForm(data=self.data_dct['full_data'])

        self.assertTrue(form_minimail.is_valid())
        self.assertTrue(form_full.is_valid())

    def test_invalid_data(self):
        contractor = Contractor.objects.create(name="ИП Бородин")
        form_empty = UpdateContractForm(data=self.data_dct['empty_data'])
        form_no_data = UpdateContractForm(data=self.data_dct['no_data'])
        self.assertFalse(form_empty.is_valid())
        self.assertFalse(form_no_data.is_valid())


class TestAddSpecificationForm(TestCase):
    # def setUp(self) -> None:

    # class AddSpecificationForm(models.ModelForm):
    #     class Meta:
    #         model = Specification
    #         fields = ['product', 'storage_item', 'quantity', 'price']

    def test_product_field(self):
        product = Product.objects.create(fish='Salmon')
        form = AddSpecificationForm()

        # print(form.fields['product'].__dict__)
        self.assertTrue(form.fields['product'].required)
        self.assertEqual(form.fields['product'].label, 'Закупка')
        self.assertIsNone(form.fields['product'].initial)
        self.assertFalse(form.fields['product'].show_hidden_initial)
        self.assertEqual(form.fields['product'].help_text, '')
        self.assertFalse(form.fields['product'].disabled)
        self.assertIsNone(form.fields['product'].label_suffix)
        self.assertFalse(form.fields['product'].localize)
        self.assertIsInstance(form.fields['product'].widget, Select)
        self.assertEqual(len(form.fields['product'].error_messages), 2)
        self.assertIsNone(form.fields['product'].template_name)
        self.assertEqual(len(form.fields['product'].validators), 0)
        self.assertEqual(form.fields['product'].empty_label, '---------')
        self.assertEqual(form.fields['product'].limit_choices_to, {})
        self.assertEqual(form.fields['product'].to_field_name, 'id')
        self.assertEqual(form.fields['product']._queryset[0], product)
        self.assertEqual(form.fields['product']._queryset.count(), 1)

    def test_storage_item_field(self):
        product = Product.objects.create(fish='Salmon')
        storage_item = StorageItem.objects.create(product=product, price=100, weight=15, available=1000, stored=1000)
        form = AddSpecificationForm()

        # print(form.fields['storage_item'].__dict__)
        self.assertEqual(form.fields['storage_item'].label, 'Товар со клада')
        self.assertIsNone(form.fields['storage_item'].initial)
        self.assertFalse(form.fields['storage_item'].show_hidden_initial)
        self.assertEqual(form.fields['storage_item'].help_text, '')
        self.assertFalse(form.fields['storage_item'].disabled)
        self.assertIsNone(form.fields['storage_item'].label_suffix)
        self.assertFalse(form.fields['storage_item'].localize)
        self.assertIsInstance(form.fields['storage_item'].widget, Select)
        self.assertEqual(len(form.fields['storage_item'].error_messages), 2)
        self.assertIsNone(form.fields['storage_item'].template_name)
        self.assertEqual(len(form.fields['storage_item'].validators), 0)
        self.assertEqual(form.fields['storage_item'].empty_label, '---------')
        self.assertEqual(form.fields['storage_item'].limit_choices_to, {})
        self.assertEqual(form.fields['storage_item'].to_field_name, 'id')
        self.assertEqual(form.fields['storage_item']._queryset[0], storage_item)
        self.assertEqual(form.fields['storage_item']._queryset.count(), 1)

    def test_quantity_field(self):
        form = AddSpecificationForm()
        # print(form.fields['quantity'].__dict__)
        self.assertEqual(form.fields['quantity'].max_digits, 10)
        self.assertEqual(form.fields['quantity'].decimal_places, 2)
        self.assertIsNone(form.fields['quantity'].max_value)
        self.assertIsNone(form.fields['quantity'].min_value)
        self.assertIsNone(form.fields['quantity'].step_size)
        self.assertEqual(form.fields['quantity'].label, 'Quantity')
        self.assertEqual(form.fields['quantity'].initial, 1)
        self.assertTrue(form.fields['quantity'].required)
        self.assertFalse(form.fields['quantity'].show_hidden_initial)
        self.assertEqual(form.fields['quantity'].help_text, '')
        self.assertFalse(form.fields['quantity'].disabled)
        self.assertFalse(form.fields['quantity'].localize)
        self.assertIsNone(form.fields['quantity'].label_suffix)
        self.assertIsInstance(form.fields['quantity'].widget, NumberInput)
        self.assertEqual(len(form.fields['quantity'].error_messages), 2)
        self.assertEqual(len(form.fields['quantity'].validators), 1)
        self.assertIsNone(form.fields['quantity'].template_name)

    def test_price_field(self):
        form = AddSpecificationForm()
        # print(form.fields['price'].__dict__)
        self.assertEqual(form.fields['price'].max_digits, 7)
        self.assertEqual(form.fields['price'].decimal_places, 2)
        self.assertIsNone(form.fields['price'].max_value)
        self.assertIsNone(form.fields['price'].min_value)
        self.assertIsNone(form.fields['price'].step_size)
        self.assertEqual(form.fields['price'].label, 'Price')
        self.assertEqual(form.fields['price'].initial, 0)
        self.assertTrue(form.fields['price'].required)
        self.assertFalse(form.fields['price'].show_hidden_initial)
        self.assertEqual(form.fields['price'].help_text, '')
        self.assertFalse(form.fields['price'].disabled)
        self.assertFalse(form.fields['price'].localize)
        self.assertIsNone(form.fields['price'].label_suffix)
        self.assertIsInstance(form.fields['price'].widget, NumberInput)
        self.assertEqual(len(form.fields['price'].error_messages), 2)
        self.assertEqual(len(form.fields['price'].validators), 1)
        self.assertIsNone(form.fields['price'].template_name)

    def test_variable_weight_field(self):
        form = AddSpecificationForm()
        # print(form.fields['variable_weight'].__dict__)
        self.assertEqual(form.fields['variable_weight'].max_digits, 7)
        self.assertEqual(form.fields['variable_weight'].decimal_places, 2)
        self.assertIsNone(form.fields['variable_weight'].max_value)
        self.assertIsNone(form.fields['variable_weight'].min_value)
        self.assertIsNone(form.fields['variable_weight'].step_size)
        self.assertEqual(form.fields['variable_weight'].label, 'Variable weight')
        self.assertEqual(form.fields['variable_weight'].initial, 1)
        self.assertTrue(form.fields['variable_weight'].required)
        self.assertFalse(form.fields['variable_weight'].show_hidden_initial)
        self.assertEqual(form.fields['variable_weight'].help_text, '')
        self.assertFalse(form.fields['variable_weight'].disabled)
        self.assertFalse(form.fields['variable_weight'].localize)
        self.assertIsNone(form.fields['variable_weight'].label_suffix)
        self.assertIsInstance(form.fields['variable_weight'].widget, NumberInput)
        self.assertEqual(len(form.fields['variable_weight'].error_messages), 2)
        self.assertEqual(len(form.fields['variable_weight'].validators), 1)
        self.assertIsNone(form.fields['variable_weight'].template_name)

    def test_contract_field(self):
        contractor = Contractor.objects.create(name="ИП Бородин")
        contract = Contract.objects.create(contractor=contractor, contract_type=Contract.ContractType.INCOME)

        form = AddSpecificationForm()
        # print(form.fields['contract'].__dict__)
        self.assertTrue(form.fields['contract'].required)
        self.assertEqual(form.fields['contract'].label, 'Контракт')
        self.assertIsNone(form.fields['contract'].initial)
        self.assertFalse(form.fields['contract'].show_hidden_initial)
        self.assertEqual(form.fields['contract'].help_text, '')
        self.assertFalse(form.fields['contract'].disabled)
        self.assertFalse(form.fields['contract'].localize)
        self.assertIsNone(form.fields['contract'].label_suffix)
        self.assertIsInstance(form.fields['contract'].widget, Select)
        self.assertEqual(len(form.fields['contract'].error_messages), 2)
        self.assertEqual(len(form.fields['contract'].validators), 0)
        self.assertIsNone(form.fields['contract'].template_name)
        self.assertEqual(form.fields['contract'].empty_label, '---------')
        self.assertEqual(form.fields['contract']._queryset.count(), 1)
        self.assertEqual(form.fields['contract']._queryset[0], contract)
        self.assertEqual(form.fields['contract'].limit_choices_to, {})
        self.assertEqual(form.fields['contract'].to_field_name, 'id')

    def test_income_valid_data(self):
        product = Product.objects.create(fish='Salmon')
        contractor = Contractor.objects.create(name="ИП Бородин")
        contract = Contract.objects.create(contractor=contractor, contract_type=Contract.ContractType.INCOME,
                                           date_plan=date.today())
        storage_item = StorageItem.objects.create(product=product, price=100, weight=15, available=1000, stored=1000)
        income = {
            'product': product.pk,
            'storage_item': storage_item.pk,
            'variable_weight': 15,
            'quantity': 1000,
            'price': 800,
            'contract': contract.pk,
        }

        form = AddSpecificationForm(data=income)

        self.assertFalse(form.is_valid())

        income = {
            'product': product.pk,
            # 'storage_item': storage_item.pk,
            'variable_weight': 15,
            'quantity': 1000,
            'price': 800,
            'contract': contract.pk,
        }

        form = AddSpecificationForm(data=income)

        self.assertFalse(form.is_valid())

        income = {
            # 'product': product.pk,
            'storage_item': storage_item.pk,
            'variable_weight': 15,
            'quantity': 1000,
            'price': 800,
            'contract': contract.pk,
        }

        form = AddSpecificationForm(data=income)

        self.assertFalse(form.is_valid())
        errors = {}
        for field in form:
            if field.errors:
                errors[field.name] = field.errors.as_text()

    def test_invalid_data(self):
        product = Product.objects.create(fish='Salmon')
        contractor = Contractor.objects.create(name="ИП Бородин")
        contract = Contract.objects.create(contractor=contractor, contract_type=Contract.ContractType.INCOME,
                                           date_plan=date.today())
        storage_item = StorageItem.objects.create(product=product, price=100, weight=15, available=1000, stored=1000)
        income = {
            'product': product.pk,
            'storage_item': storage_item.pk,
            'variable_weight': 15,
            'quantity': 1000_000_000,
            'price': 800,
            'contract': contract.pk,
        }

        form = AddSpecificationForm(data=income)

        self.assertFalse(form.is_valid())

        errors = {}
        for field in form:
            if field.errors:
                errors[field.name] = field.errors.as_text()

        self.assertEqual(len(errors), 1)


class TestSpecificationFormSet(TestCase):

    # SpecificationFormSet = inlineformset_factory(
    #     Contract,
    #     Specification,
    #     form=AddSpecificationForm,
    #     extra=1,
    #     can_delete=False)

    def setUp(self) -> None:
        seed(1)
        spec_amount_income = 1
        spec_amount_outcome = 2

        contractor_income = Contractor.objects.create(name='ООО Алаид')
        contractor_outcome = Contractor.objects.create(name='ИП Бородин')

        self.contract_income = Contract.objects.create(contractor=contractor_income,
                                                       contract_type=Contract.ContractType.INCOME)
        self.contract_outcome = Contract.objects.create(contractor=contractor_outcome)

        fields_income = ['product', 'variable_weight', 'quantity', 'price', 'contract']
        fields_outcome = ['storage_item', 'variable_weight', 'quantity', 'price', 'contract']

        self.products = [Product.objects.create(fish=num) for num in range(1, 11)]
        self.storage_items = [StorageItem.objects.create(product=choice(self.products), weight=1, price=num) for num in range(5)]

        self.fs_income = inlineformset_factory(
            Contract, Specification,
            fields=fields_income,
            extra=spec_amount_income)

        self.fs_outcome = inlineformset_factory(
            Contract, Specification,
            fields=fields_outcome,
            extra=spec_amount_outcome)

    def test_form_set_income_parameters(self):
        form_set = self.fs_income(instance=self.contract_income)
        self.assertEqual(form_set.instance, self.contract_income)
        self.assertEqual(len(form_set.forms), 1)
        self.assertIn('product', form_set.forms[0].fields)


    def test_form_set_outcome_parameters(self):
        form_set = self.fs_outcome(instance=self.contract_outcome)

        self.assertEqual(form_set.instance, self.contract_outcome)
        self.assertEqual(len(form_set.forms), 2)
        self.assertIn('storage_item', form_set.forms[0].fields)

    def test_form_set_update_valid_data(self):
        spec = Specification.objects.create(product=self.products[0])

        formset_data = {
            'specifications-TOTAL_FORMS': 1,
            'specifications-INITIAL_FORMS': 1,
            'specifications-MIN_NUM_FORMS': 0,
            'specifications-MAX_NUM_FORMS': 1000,
            'specifications-0-contract': 1,
            'specifications-0-id': 1,
            'specifications-0-product': 1,
            'specifications-0-variable_weight': 1,
            'specifications-0-quantity': 2200,
            'specifications-0-price': 950,
        }

        form_set = self.fs_income(formset_data, instance=self.contract_income)
        self.assertEqual(form_set.instance, self.contract_income)
        self.assertEqual(len(form_set.forms), 1)
        self.assertTrue(form_set.is_valid())

        form_set.save()

        self.assertEqual(Specification.objects.all().count(), 1)

    def test_form_set_new_valid_data(self):

        formset_data = {
            'specifications-TOTAL_FORMS': 1,
            'specifications-INITIAL_FORMS': 0,
            'specifications-MIN_NUM_FORMS': 0,
            'specifications-MAX_NUM_FORMS': 1000,
            'specifications-0-contract': 1,
            'specifications-0-id': '',
            'specifications-0-product': 1,
            'specifications-0-variable_weight': 1,
            'specifications-0-quantity': 2200,
            'specifications-0-price': 950,
        }

        form_set = self.fs_income(formset_data, instance=self.contract_income)
        self.assertEqual(form_set.instance, self.contract_income)
        self.assertEqual(len(form_set.forms), 1)
        self.assertTrue(form_set.is_valid())
        form_set.save()

        self.assertEqual(Specification.objects.all().count(), 1)
        spec1 = Specification.objects.all()[0]
        self.assertEqual(spec1.quantity, 2200)
        self.assertEqual(spec1.price, 950)
