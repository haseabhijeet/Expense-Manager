from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import ExpenseForm, SignUpForm
from .models import Expense
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
import csv
import json
import datetime

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user).order_by('-date')
        category = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if category:
            queryset = queryset.filter(category=category)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'expenses'
        return context

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Expense added successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'expense-add'
        return context

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Expense updated successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'expense-edit'
        return context

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expense-list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Expense deleted successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'expense-delete'
        return context

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)

    category_data = list(expenses.values('category').annotate(total=Sum('amount')))
    for item in category_data:
        item['total'] = float(item['total'])

    monthly_data = list(expenses.extra({'month': "strftime('%%m', date)"}).values('month').annotate(total=Sum('amount')).order_by('month'))
    for item in monthly_data:
        item['total'] = float(item['total'])

    current_month = datetime.date.today().month
    current_month_total = expenses.filter(date__month=current_month).aggregate(total=Sum('amount'))['total'] or 0
    budget_limit = settings.BUDGET_LIMIT
    budget_usage = (current_month_total / budget_limit) * 100 if budget_limit else 0
    if budget_usage > 100:
        budget_usage = 100
        messages.warning(request, f"Warning: Your expenses for this month (${current_month_total:.2f}) exceed your budget limit of ${budget_limit}!")

    context = {
        'category_data': json.dumps(category_data),
        'monthly_data': json.dumps(monthly_data),
        'current_month_total': current_month_total,
        'budget_usage': round(budget_usage, 2),
        'settings': settings,
        'current_page': 'dashboard',
    }
    return render(request, 'expenses/dashboard.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form, 'current_page': 'signup'})

@login_required
def expense_summary(request):
    daily_summary = Expense.objects.filter(user=request.user).values('category', 'date').annotate(total=Sum('amount')).order_by('category', 'date')
    monthly_summary = Expense.objects.filter(user=request.user).extra({'month': "strftime('%%m', date)"}).values('category', 'month').annotate(total=Sum('amount')).order_by('category', 'month')

    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if category:
        daily_summary = daily_summary.filter(category=category)
        monthly_summary = monthly_summary.filter(category=category)
    if start_date:
        daily_summary = daily_summary.filter(date__gte=start_date)
    if end_date:
        daily_summary = daily_summary.filter(date__lte=end_date)

    context = {
        'daily_summary': daily_summary,
        'monthly_summary': monthly_summary,
        'current_page': 'summary',
    }
    return render(request, 'expenses/expense_summary.html', context)

@login_required
def export_csv(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Category', 'Amount'])
    for expense in expenses:
        writer.writerow([expense.date, expense.description, expense.category, expense.amount])
    messages.success(request, "CSV export generated successfully!")
    return response

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')
