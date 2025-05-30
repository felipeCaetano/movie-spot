from http.client import responses

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3/"
API_KEY = settings.TMDB_API_KEY

# Create your views here.
def landing_page(request):
    category = request.GET.get("category", "popular")
    search_query = request.GET.get("search", "")

    page = int(request.GET.get("page", 1))
    next_page = page + 1
    error_message = ""
    if search_query:
        url = f"{BASE_URL}search/movie?api_key={API_KEY}&query={search_query}&page={page}"
    else:
        url = f"{BASE_URL}movie/{category}?api_key={API_KEY}&page={page}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('results', [])
    except Exception as e:
        data = []
        error_message = "Something went wrong."
    if request.headers.get("HX-Request"):
        return render(
            request,
            "movies/partials/_movie_list.html",
            {"movies": data, "category": category,
             "search_query": search_query, "error_message": error_message,
             "next_page": next_page}
        )
    return  render(
        request,
        "movies/landing.html",
        {"movies":data,"category": category,
         "search_query": search_query, "error_message":error_message,
         "next_page": next_page}
    )

def movie_detail(request, movie_id):
    movie_details_url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}"
    movie_credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    error_message = ""
    try:
        movie_detail_response = requests.get(movie_details_url)
        movie_detail_response.raise_for_status()
        movie_data = movie_detail_response.json()
    except Exception as e:
        movie_data = []
        error_message = f"Something went wrong!"
    try:
        movie_credits_response = requests.get(movie_credits_url)
        movie_credits_response.raise_for_status()
        credits_data = movie_credits_response.json()
    except Exception as e:
        print(e)
        credits_data = []
        error_message = f"Something went wrong!"
    return render(
        request, "movies/movie_detail.html",
        {
            "movie": movie_data,
            "error_message": error_message,
            "credits": credits_data
        })
