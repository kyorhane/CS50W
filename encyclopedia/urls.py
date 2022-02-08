from django.urls import path

from . import views

app_name = 'encyclopedia'

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/random-entry/", views.random_entry, name="random_entry"),
    path("wiki/create-entry/", views.create_entry, name="create_entry"),
    path("wiki/edit-entry/<str:entry_name>/", views.edit_entry, name="edit_entry"),
    path("wiki/<str:entry_name>/", views.entry_page, name="entry_page")
]
