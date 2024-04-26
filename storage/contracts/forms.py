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

	contract_type = forms.ChoiceField(choices=Contract.ContractType.choices)
	date_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), )
	note = forms.Textarea()

	class Meta:
		model = Contract
		fields = ['contract_type', 'date_plan', 'contractor', 'note']
		# widgets = {'date_plan': forms.DateInput(attrs={'type': 'date'})}


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