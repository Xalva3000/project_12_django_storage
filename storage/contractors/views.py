from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from .forms import AddContractorForm
from .models import Contractor
from products.utils import DataMixin


class ContractorsList(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'contractors/contractors.html'
    context_object_name = 'contractors'
    # allow_empty = False
    title_page = 'Контрагенты'
    category_page = 'contractors'
    paginate_by = 20

    def get_queryset(self):
        return Contractor.objects.all()


class AddContractor(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddContractorForm
    template_name = 'contractors/add_contractor.html'
    title_page = 'Добавление контрагента'
    category_page = 'contractors'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class UpdateContractor(LoginRequiredMixin, DataMixin, UpdateView):
    model = Contractor
    form_class = AddContractorForm
    template_name = 'contractors/add_contractor.html'
    title_page = 'Редактирование контрагента'
    category_page = 'contractors'

    def get_success_url(self):
        pk = self.kwargs[self.pk_url_kwarg]
        return reverse('contractors:contractor', kwargs={"pk": pk})


class ShowContractor(LoginRequiredMixin, DataMixin, DetailView):
    model = Contractor
    template_name = 'contractors/contractor.html'
    context_object_name = 'contractor'
    category_page = 'contractors'
    pk_url_kwarg = 'pk'
    title_page = 'Детали контрагента'

    def get_object(self, queryset=None):
        return get_object_or_404(Contractor.objects, pk=self.kwargs[self.pk_url_kwarg])
