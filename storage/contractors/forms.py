from django.forms import models

from .models import Contractor


class AddContractorForm(models.ModelForm):
	class Meta:
		model = Contractor
		fields = ['name', 'address', 'email', 'contact_data']


