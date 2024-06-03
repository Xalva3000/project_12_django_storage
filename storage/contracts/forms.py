from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import models, inlineformset_factory
from django import forms

from .models import Contract, Specification


class AddContractForm(models.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('внести', 'Внести', css_class="btn btn-success mt-3"))

    contract_type = forms.ChoiceField(choices=Contract.ContractType.choices,
                                      widget=forms.Select(attrs={'class': 'form-select'}),
                                      label='Тип контракта')
    date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }),
                                label='Планируемая дата исполнения')
    note = forms.Textarea()

    class Meta:
        model = Contract
        fields = ['contract_type', 'date_plan', 'contractor', 'note']
        widgets = {'contractor': forms.Select(attrs={'class': 'form-select'})}


class UpdateContractForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('внести', 'Внести', css_class="btn btn-success mt-3"))

    date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }),
                                label='Планируемая дата исполнения')

    class Meta:
        model = Contract
        fields = ['date_plan', 'contractor', 'note']
        widgets = {'contractor': forms.Select(attrs={'class': 'form-select'})}


class AddSpecificationForm(models.ModelForm):
    class Meta:
        model = Specification
        fields = ['product', 'storage_item', 'variable_weight', 'quantity', 'price', 'contract']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        storage_item = cleaned_data.get('storage_item')

        if not product and not storage_item:
            raise forms.ValidationError("Необходимо заполнить хотя бы одно из полей: product или storage_item")

        if product and storage_item:
            raise forms.ValidationError("Можно заполнить только одно из полей: product или storage_item")

        return cleaned_data


SpecificationFormSet = inlineformset_factory(
    Contract,
    Specification,
    form=AddSpecificationForm,
    extra=1,
    can_delete=False)
