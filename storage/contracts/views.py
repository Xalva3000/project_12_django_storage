from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, Q
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from sql_util.aggregates import SubquerySum

from .forms import AddContractForm, UpdateContractForm
from .models import Contract, Specification, Payment
from products.utils import DataMixin, tools, menu, insert_action_notification
from .filters import ContractFilter
from datetime import date



def index(request):
    return render(request, 'base.html', {'title': 'Contracts'})


class ContractsTodayList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts/contracts_today.html"
    context_object_name = "contracts"
    title_page = "Отгрузки сегодня"
    category_page = "contracts"
    paginate_by = 20
    queryset = Contract.objects.filter(Q(date_delete__isnull=True), Q(date_plan=date.today())).order_by('-pk')


class ContractsPlusList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts/contracts_plus.html"
    context_object_name = "contracts"
    title_page = "Контракты+"
    category_page = "contracts"
    paginate_by = 10
    queryset = Contract.objects.filter(date_delete__isnull=True).order_by('-date_plan', '-pk')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ContractFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        context['mod'] = 'plus'
        return context


class ContractsMinimalList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts/contracts_minimal.html"
    context_object_name = "contracts"
    title_page = "Контракты"
    category_page = "contracts"
    paginate_by = 50
    # queryset = Contract.objects.filter(date_delete__isnull=True).order_by('-date_plan', '-pk')

    queryset = Contract.objects.filter(
        date_delete__isnull=True
    ).annotate(
        total_weight=SubquerySum(F('specifications__variable_weight') * F('specifications__quantity')),
        total_sum=SubquerySum(F('specifications__variable_weight') * F('specifications__quantity') * F('specifications__price')),
        total_payments=SubquerySum(F('payments__amount'))).order_by('-date_plan', '-pk')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ContractFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        context['query_length'] = self.get_queryset().count()
        context['income_stats'] = self.get_stats(self.get_queryset(), Contract.ContractType.INCOME)
        context['outcome_stats'] = self.get_stats(self.get_queryset(), Contract.ContractType.OUTCOME)
        return context

    @staticmethod
    def get_stats(queryset, contract_type=Contract.ContractType.INCOME):
        qs = queryset.filter(contract_type=contract_type)
        result = {}
        weight = qs.aggregate(w=Sum(F('total_weight')))
        result['weight'] = weight['w']
        cost = qs.aggregate(s=Sum(F('total_sum')))
        result['cost'] = cost['s']
        payments = qs.aggregate(p=Sum(F('total_payments')))
        result['payments'] = payments['p']

        bonuses_qs = qs.values('id', 'manager__username', 'manager_share')
        lst = []
        bonuses = {}
        for dct in bonuses_qs:
            if dct['id'] not in lst and dct['manager_share']:
                lst.append(dct['id'])
                bonuses[dct['manager__username']] = bonuses.get(dct['manager__username'], 0) + dct['manager_share']

        result['bonuses'] = bonuses

        if contract_type == Contract.ContractType.OUTCOME:
            expenses = [c.specifications.aggregate(cost=Sum(F('quantity') * F('variable_weight') * F('storage_item__price'))) for c in qs if c.specifications.all()]
            result['expenses'] = sum([dct['cost'] for dct in expenses])
            if result['expenses']:
                result['expected'] = result['cost'] - result['expenses']
        return result


class DeletedContractsMinimalList(LoginRequiredMixin, DataMixin, ListView):
    model = Contract
    template_name = "contracts/contracts_deleted.html"
    context_object_name = "contracts"
    title_page = "Удаленные контракты"
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
        context['mod'] = 'deleted'
        return context


class AddContract(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddContractForm
    template_name = 'contracts/add_contract.html'
    title_page = 'Добавление контракта'
    category_page = 'contracts'

    def get_success_url(self):
        insert_action_notification(contract=self.object.id, action='created', extra_info=self.request.user)
        return reverse("contracts:contract", args=[self.object.id,])

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.manager = self.request.user
        return super().form_valid(form)


class ShowContract(LoginRequiredMixin, DataMixin, DetailView):
    model = Contract
    template_name = 'contracts/contract.html'
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
    # формирование группы форм
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

    # сохранение данных группы форм
    if request.method == 'POST' and 'spec_amount' not in request.POST.keys():
        formset = SpecificationFormSet(request.POST, instance=contract)
        # print(request.POST)
        if formset.is_valid():
            formset.save()
            insert_action_notification(contract=contract, action='new_change')  # сообщение об изменении
            uri = reverse('contracts:contract', kwargs={'pk': pk})
            return redirect(uri)
    context = {'formset': formset, 'contract': contract, 'tools': tools['contracts'], 'menu': menu}
    return render(request, 'contracts/add_specifications.html', context)


class UpdateContract(LoginRequiredMixin, DataMixin, UpdateView):
    model = Contract
    form_class = UpdateContractForm
    template_name = 'contracts/add_contract.html'
    title_page = 'Редактирование контракта'
    category_page = 'contracts'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse('contracts:contract', kwargs={"pk": pk})
