from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Sum, F
from django.forms import inlineformset_factory
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import AddContractForm, AddSpecificationForm, SpecificationFormSet
from .models import Contract, Specification, Payments
from products.utils import DataMixin, tools, menu
from .filters import ContractFilter


# Create your views here.
def index(request):
    return render(request, 'base.html', {'title': 'Contracts'})


class ContractsPlusList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts_plus.html"
    context_object_name = "contracts"
    title_page = "Контракты"
    category_page = "contracts"
    paginate_by = 10
    queryset = Contract.objects.filter(date_delete__isnull=True).order_by('-date_plan', '-pk')
    # allow_empty =

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ContractFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context

class ContractsMinimalList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts_minimal.html"
    context_object_name = "contracts"
    title_page = "Контракты"
    category_page = "contracts"
    paginate_by = 50
    queryset = Contract.objects.filter(date_delete__isnull=True).order_by('-date_plan', '-pk')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ContractFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context

class DeletedContractsMinimalList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts_minimal.html"
    context_object_name = "contracts"
    title_page = "Контракты"
    category_page = "contracts"
    paginate_by = 50
    queryset = Contract.objects.filter(date_delete__isnull=False).order_by('-date_plan', '-pk')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ContractFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context


class AddContract(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddContractForm
    template_name = 'products/add_product.html'
    title_page = 'Добавление контракта'
    category_page = 'contracts'

    def get_success_url(self):
        return reverse("contracts:contract", args=[self.object.id,])

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.manager = self.request.user
        return super().form_valid(form)

class ShowContract(LoginRequiredMixin, DataMixin, DetailView):
    model = Contract
    template_name = 'contract.html'
    context_object_name = 'contract'
    pk_url_kwarg = 'pk'
    title_page = 'Детали контракта'
    category_page = 'contracts'

    def get_object(self, queryset=None):
        return get_object_or_404(Contract.objects, pk=self.kwargs[self.pk_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = Contract.objects.get(pk=self.kwargs[self.pk_url_kwarg])
        if contract.specifications.all():
            tonnage = contract.specifications.aggregate(ton=Sum(F('quantity') * F('variable_weight')))
            context['tonnage'] = tonnage['ton']
            total = contract.specifications.aggregate(summa=Sum(F('quantity') * F('variable_weight') * F('price')))
            context['total'] = total['summa']
            if contract.contract_type == Contract.ContractType.OUTCOME:
                purchase = contract.specifications.aggregate(summa=Sum(F('quantity') * F('variable_weight') * F('storage_item__price')))
                context['purchase'] = purchase['summa']
                context['profit'] = total['summa'] - purchase['summa']

        payments = contract.payments.all()
        if payments:
            context['payments'] = payments
            payments_sum = contract.payments.aggregate(summa=Sum('amount'))
            context['payments_sum'] = payments_sum['summa']
            context['balance'] = total['summa'] - payments_sum['summa']

        return context


@login_required
def add_specifications(request, pk):
    spec_amount = int(request.POST.get('spec_amount', 3))
    contract = get_object_or_404(Contract, pk=pk)
    if contract.contract_type == Contract.ContractType.INCOME:
        fields = ['product', 'variable_weight', 'quantity', 'price', 'contract']
    else:
        fields = ['storage_item', 'variable_weight', 'quantity', 'price', 'contract']

    SpecificationFormSet = inlineformset_factory(
        Contract, Specification,
        fields=fields,
        extra=spec_amount)
    formset = SpecificationFormSet(instance=contract)
    if request.method == 'POST' and 'spec_amount' not in request.POST.keys():
        formset = SpecificationFormSet(request.POST, instance=contract)
        if formset.is_valid():
            formset.save()
            uri = reverse('contracts:contract', kwargs={'pk': pk})
            return redirect(uri)
    context = {'formset': formset, 'contract': contract, 'tools': tools['contracts'], 'menu': menu}
    return render(request, 'add_specifications.html', context)


class UpdateContract(LoginRequiredMixin, DataMixin, UpdateView):
    model = Contract
    form_class = AddContractForm
    # fields = ['contract_type', 'date_plan','contractor', 'note',]
    template_name = 'products/add_product.html'
    title_page = 'Редактирование контракта'
    category_page = 'contracts'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse('contracts:contract', kwargs={"pk": pk})

def change_manager_share(request, pk):
    new_share = int(request.POST.get('new_share', 0))
    contract = Contract.objects.get(pk=pk)
    contract.manager_share = new_share
    contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)

def change_note(request, pk):
    new_note = request.POST.get('new_note', '')
    contract = Contract.objects.get(pk=pk)
    contract.note = new_note
    contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)

def add_payment(request, pk):
    new_payment = int(request.POST.get('new_payment', 0))
    payment = Payments.objects.create(contract_id=pk, amount=new_payment)
    payment.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)

# def delete_payment(request, pk):
#     new_share = int(request.POST.get('new_share', 0))
#     contract = Contract.objects.get(pk=pk)
#     contract.
#     contract.save()
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)