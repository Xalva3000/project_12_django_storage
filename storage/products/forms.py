from django.forms import models

from .models import Product


class AddProductForm(models.ModelForm):
	class Meta:
		model = Product
		fields = ['fish', 'cutting','size','producer','package',
		          'fixed_weight','weight', 'note']

