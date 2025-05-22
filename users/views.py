from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView

from .forms import RegisterUserForm

# Create your views here.
class Login(LoginView):
    template_name = "users/accounts/login.html"
    success_url = "/"

class Logout(LogoutView):
    next_page = "/"

class RegisterUser(FormView):
    template_name = "users/accounts/register.html"
    form_class = RegisterUserForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)