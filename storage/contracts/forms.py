from django.forms import models, inlineformset_factory
from django import forms

from .models import Contract, Specification


class AddContractForm(models.ModelForm):
	date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), )

	class Meta:
		model = Contract
		fields = ['contract_type', 'date_plan', 'contractor', 'note']
		# widgets = {'date_plan': forms.DateInput(attrs={'type': 'date'})}


class AddSpecificationForm(models.ModelForm):
	class Meta:
		model = Specification
		fields = ['product', 'storage_item', 'variable_weight', 'quantity', 'price']


SpecificationFormSet = inlineformset_factory(
	Contract,
	Specification,
	form=AddSpecificationForm,
	extra=1,
	can_delete=False)