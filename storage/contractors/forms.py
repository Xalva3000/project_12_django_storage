from crispy_forms.layout import Submit
from django.forms import models

from .models import Contractor
from crispy_forms.helper import FormHelper

class AddContractorForm(models.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('внести', 'Внести'))

	class Meta:
		model = Contractor
		fields = ['name', 'address', 'email', 'contact_data']


