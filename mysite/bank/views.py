
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from bank.models import Customers,Transfer
from bank.forms import Trans_form
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views.generic.detail import DetailView
class MainView(LoginRequiredMixin, View) :
    def get(self, request):
        return render(request, 'bank/bank_main.html')
class CustView(LoginRequiredMixin, View):
    def get(self, request):
        mc = Customers.objects.all();
        ctx = { 'cust_list': mc };
        return render(request, 'bank/customers_list.html',ctx)

class TransView(LoginRequiredMixin, View):
    def get(self, request):
        mc = Transfer.objects.all();
        al = Transfer.objects.all().count();
        ctx = { 'trans_list': mc,'trans_count':al};
        return render(request, 'bank/trans_list.html',ctx)
class CustCreate(LoginRequiredMixin, CreateView):
    model = Customers
    fields = '__all__'
    success_url = reverse_lazy('bank:all')
class  CustUpdate(LoginRequiredMixin, UpdateView):
    model = Customers
    fields = ['name','email']
    success_url = reverse_lazy('bank:all')
class CustDelete(LoginRequiredMixin, DeleteView):
    model = Customers
    fields = '__all__'
    success_url = reverse_lazy('bank:all')

class CustomersDetailView(LoginRequiredMixin,DetailView):
    model = Customers
    template_name="bank/customers_detail.html"
    def get(self, request, pk) :
        x = Customers.objects.get(id=pk)
        context = { 'cust' : x}
        return render(request, self.template_name,context)


class TransferToView(LoginRequiredMixin,View):
    template_name = "bank/transfer_to.html"
    success_url = reverse_lazy('bank:all')
    def get(self, request, pk):
        custse = get_object_or_404(Customers, id=pk)
        mc = Customers.objects.all();
        form = Trans_form()
        ctx = {'form': form,'custse':custse,'cust_list':mc}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        sen = get_object_or_404(Customers, id=pk)
        form = Trans_form(request.POST, request.FILES or None)

        if not form.is_valid():
            custse = get_object_or_404(Customers, id=pk)
            mc = Customers.objects.all();
            ctx = {'form': form,'custse':custse,'cust_list':mc}
            return render(request, self.template_name, ctx)

        recid=request.POST['receiver']
        amt=request.POST['Amount']
        if float(amt)>sen.balance:
            custse = get_object_or_404(Customers, id=pk)
            mc = Customers.objects.all();
            ctx = {'form': form,'custse':custse,'cust_list':mc,'error':True}
            return render(request, self.template_name, ctx)
        rec= get_object_or_404(Customers, id=recid)
        if sen.id==rec.id:
            custse = get_object_or_404(Customers, id=pk)
            mc = Customers.objects.all();
            ctx = {'form': form,'custse':custse,'cust_list':mc,'error1':True}
            return render(request, self.template_name, ctx)
        sen.balance=sen.balance-float(amt)
        rec.balance=rec.balance+float(amt)
        trans=Transfer()
        trans.sender=sen.name
        trans.receiver=rec.name
        trans.amount=float(amt)
        trans.time = naturaltime(trans.time)
        sen.save()
        rec.save()
        trans.save()
        return redirect(reverse('bank:trans_list'))




