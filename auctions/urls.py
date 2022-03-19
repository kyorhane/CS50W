from unicodedata import name
from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing/", views.create_listing, name="create"),
    path("listing/<int:id>/", views.listing_page, name="listing"),
    path("inventory/<int:id>/", views.inventory, name="inventory"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>/", views.categories_page, name="categories_page")
]
