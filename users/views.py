from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseForbidden
from django.views.generic.edit import FormView

from .forms import RegisterUserForm, CreateListForm
from .models import ListItem, UserList


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


@login_required
def profile(request):
    user = request.user
    user_lists = UserList.objects.filter(user=user)
    return render(
        request,
        'users/accounts/profile.html',
        {"user": user, "user_lists": user_lists})


@login_required
def create_list(request):
    user = request.user
    if request.method == 'POST':
        form = CreateListForm(request.POST)
        if form.is_valid():
            user_list = form.save(commit=False)
            user_list.user = user
            user_list.save()
            user_lists = UserList.objects.filter(user=user)
            return render(
                request,
                "users/lists/partials/_user_lists.html",
                {"user_lists": user_lists}
            )
        return render(
        request, "users/lists/partials/_create_list_form.html",
        {"form": form}, status=400
    )
    form = CreateListForm()
    return render(
        request, "users/lists/partials/_create_list_form.html",
        {"form": form}
    )


@login_required
def delete_list(request, list_id):
    user_list = get_object_or_404(UserList, id=list_id, user=request.user)
    if request.method == 'POST':
        user_list.delete()
        user_lists = UserList.objects.filter(user=request.user)
        return render(
                request,
                "users/lists/partials/_user_lists.html",
                {"user_lists": user_lists}
                )
    return HttpResponseForbidden


@login_required
def add_to_list(request, movie_id, movie_name, list_id):
    user_list = get_object_or_404(UserList, id=list_id, user=request.user)

    if ListItem.objects.filter(movie_id=movie_id, list=user_list).exists():
        message = f"{movie_name} is already in the {user_list}"
        status = "danger"
    else:
        ListItem.objects.create(movie_id=movie_id, movie_name=movie_name list=user_list)
        message = f"{movie_name} was added to {user_list}"
        status = "sucdess"
    return render(
                request,
                "users/toasts/confim_toasts.html",
                {"user_lists": user_lists}
                )