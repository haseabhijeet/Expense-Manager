from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home,
    ExpenseListView,
    ExpenseCreateView,
    ExpenseUpdateView,
    ExpenseDeleteView,
    dashboard,
    signup,
    expense_summary,
    export_csv,
    logout_view,
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True), name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('expense/add/', ExpenseCreateView.as_view(), name='expense-add'),
    path('expense/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense-edit'),
    path('expense/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense-delete'),
    path('summary/', expense_summary, name='expense-summary'),
    path('export_csv/', export_csv, name='export_csv'),
]
