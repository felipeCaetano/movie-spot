from http import HTTPStatus

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from movies.views import BASE_URL, API_KEY
from .forms import RegisterUserForm, CreateListForm
from .models import ListItem, UserList


# Create your views here.
class Login(LoginView):
    template_name = "users/accounts/login.html"
    def get_success_url(self):
        return reverse_lazy("profile")

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
    user_lists = get_object_or_404(UserList, id=list_id, user=request.user)

    if ListItem.objects.filter(movie_id=movie_id, list=user_lists).exists():
        message = f"{movie_name} is already in the "
        status = "danger"
    else:
        ListItem.objects.create(
            movie_id=movie_id, movie_name=movie_name, list=user_lists)
        message = f"{movie_name} was added to "
        status = "success"
    return render(
                request,
                "users/toasts/confirm_toast.html",
                {"message": message,
                 'status': status, 'user_lists':user_lists}
                )

def list_detail(request, list_id):
    user_list = get_object_or_404(UserList, id=list_id)
    list_items = ListItem.objects.filter(list=user_list)
    movies = []
    for item in list_items:
        movie_id = item.movie_id
        url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            movie = response.json()
            movies.append(movie)
    return render(request, 'users/lists/users_lists_detail.html',
                  {'movies':movies,
                   'user_list': user_list,
                   'is_owner':request.user.is_authenticated
                              and request.user==user_list.user})

@login_required
def delete_movie(request, movie_id, list_id):
    user_list = get_object_or_404(UserList, id=list_id, user=request.user)
    movie = get_object_or_404(ListItem, movie_id=movie_id, list=user_list)
    if request.method == 'POST':
        movie.delete()
        list_items = ListItem.objects.filter(list=user_list)
        movies = []
        for item in list_items:
            movie_id = item.movie_id
            url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}"
            response = requests.get(url)
            if response.status_code == HTTPStatus.OK:
                movie = response.json()
                movies.append(movie)
        return render(
            request,
            "users/lists/partials/_updated_list.html",
            {
                'movies': movies,
                "is_owner": request.user.is_authenticated and request.user ==
                            user_list.user}
        )
    return HttpResponseForbidden