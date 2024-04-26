from crispy_forms.layout import Submit
from django.forms import models

from .models import Product
from crispy_forms.helper import FormHelper


class AddProductForm(models.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('внести', 'Внести', css_class="btn btn-success mt-3"))

	class Meta:
		model = Product
		fields = ['fish', 'cutting', 'size', 'producer', 'package', 'note']

