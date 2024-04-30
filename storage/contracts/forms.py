from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import models, inlineformset_factory
from django import forms
from decimal import Decimal

from .models import Contract, Specification


class AddContractForm(models.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('внести', 'Внести', css_class="btn btn-success mt-3"))

	contract_type = forms.ChoiceField(choices=Contract.ContractType.choices, widget=forms.Select(attrs={ 'class': 'form-select'}))
	date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',}), )
	note = forms.Textarea()
	# 'class': 'form-select'
	class Meta:
		model = Contract
		fields = ['contract_type', 'date_plan', 'contractor', 'note']
		widgets = {'contractor': forms.Select(attrs={'class': 'form-select'})}


class AddSpecificationForm(models.ModelForm):
	class Meta:
		model = Specification
		fields = ['product', 'storage_item', 'quantity', 'price']


SpecificationFormSet = inlineformset_factory(
	Contract,
	Specification,
	form=AddSpecificationForm,
	extra=1,
	can_delete=False)